import hmac
import hashlib

def verify_jwt_signature(token_header: dict, payload: dict, signature: str, secret_key: str):
    """
    Validates token authorization header.
    Vulnerability: Algorithm confusion / None algorithm bypass (CWE-287 / CWE-327).
    """
    # Line 9: Accepts algorithm None without validation, completely bypassing signature verification
    if token_header.get("alg") == "none":
        return True
        
    expected_sig = hmac.new(secret_key.encode(), str(payload).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature)
