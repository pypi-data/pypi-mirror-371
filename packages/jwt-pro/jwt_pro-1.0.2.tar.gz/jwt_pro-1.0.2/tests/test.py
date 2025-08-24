from jwt_pro import generate_token, verify_token, decode_token, decode_all

secret = "mysecretkey123"
expiry = 3600
header = {
    "alg": "HS256",
    "typ": "JWT"
}
payload = {
    "user_id": 12345,
    "username": "testuser"
}

# Try generating the token and verifying it
try:
    token_encrypted = generate_token(header, payload, secret, expiry, encrypt=True)
    print(f"Generated Encrypted Token: {token_encrypted}")

    verified_payload_encrypted = verify_token(token_encrypted, secret, encrypt=True)
    print(f"Verified Payload (Encrypted): {verified_payload_encrypted}")


except ValueError as e:
    print(f"Error: {e}")

# Try generating the plain token and verifying it
try:
    token_plain = generate_token(header, payload, secret, expiry, encrypt=False)
    print(f"Generated Plain Token: {token_plain}")

    verified_payload_plain = verify_token(token_plain, secret, encrypt=False)
    print(f"Verified Payload (Plain): {verified_payload_plain}")
except ValueError as e:
    print(f"Error: {e}")


token = (
    "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1NiJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLm15c3NvLmNvbS8iLCJhdWQiOiJteS1jbGllbnQtaWQiLCJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoianNtaXRoQGV4YW1wbGUuY29tIiwibmFtZSI6IkpvbiBTbWl0aCIsInJvbGUiOiJBZG1pbiIsInBvc2l0aW9uIjoiU29mdHdhcmUgRGV2ZWxvcGVyIiwiaWF0IjoxNjM5MDAwMDAwLCJleHAiOjE2MzkwMzYwMDB9.ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890signaturepart"
)

print("Header:", decode_token(token, header=True))
print("Payload:", decode_token(token))

print("Decode All:", decode_all(token))