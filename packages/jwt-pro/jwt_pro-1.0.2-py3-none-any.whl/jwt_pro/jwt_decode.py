import base64
import json


def decode_base64url(encoded_str: str) -> str:
    """
    Decode a Base64URL string into plain UTF-8 text.
    """
    # Convert from URL-safe Base64
    base64_str = encoded_str.replace("-", "+").replace("_", "/")

    # Add padding if required
    while len(base64_str) % 4 != 0:
        base64_str += "="

    try:
        decoded_bytes = base64.b64decode(base64_str)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {e}")


def decode_token(token: str, header: bool = False) -> dict:
    """
    Decode a JWT header or payload without verifying signature.

    :param token: The JWT string (format: header.payload.signature)
    :param header: If True → decode header, else → decode payload
    :return: dict with decoded JSON

    WARNING:
    This function ONLY decodes the JWT header or payload.
    It does NOT verify the token's signature or validate authenticity.
    Do not use this for security decisions!
    """
    if not isinstance(token, str):
        raise TypeError("Token must be a string")

    token_parts = token.split(".")
    target_index = 0 if header else 1

    if target_index >= len(token_parts):
        raise ValueError(f"Token is missing part #{target_index + 1}")

    try:
        decoded_str = decode_base64url(token_parts[target_index])
        return json.loads(decoded_str)
    except Exception as e:
        raise ValueError(f"Failed to decode token part #{target_index + 1}: {e}")


def decode_all(token: str) -> dict:
    """
    Decode the entire JWT: header, payload, and signature.

    :param token: The JWT string (format: header.payload.signature)
    :return: dict with {header, payload, signature}

    NOTE:
    Signature is returned as-is (Base64URL string).
    This does NOT validate the signature!
    """
    if not isinstance(token, str):
        raise TypeError("Token must be a string")

    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError(f"Invalid JWT: expected at least 2 parts, got {len(parts)}")

    header = decode_token(token, header=True)
    payload = decode_token(token, header=False)
    signature = parts[2] if len(parts) > 2 else None

    return {
        "header": header,
        "payload": payload,
        "signature": signature,
    }
