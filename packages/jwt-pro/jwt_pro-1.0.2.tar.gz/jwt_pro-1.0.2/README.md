![PyPI Version](https://img.shields.io/pypi/v/jwt-pro.svg)
![Dependencies](https://img.shields.io/librariesio/release/pypi/jwt-pro)
![PyPI - License](https://img.shields.io/pypi/l/jwt-pro)


# JWT Pro - JWT Generation & Verification with AES Encryption

Welcome to `JWT Pro`, your go-to Python package for creating and verifying JSON Web Tokens (JWTs). With support for AES encryption and HMAC signatures, it ensures your user authentication and data transmission are as secure as possible. The package is highly customizable, letting you tweak encryption settings, headers, payloads and validation to fit your needs perfectly.

**JWT Pro** is your all-in-one tool for working with **JSON Web Tokens (JWTs)** in Python. Whether you need to generate, decode, or inspect tokens, JWT Pro makes it simple, safe, and developer-friendly.  


---

## Features

- **Generate JWTs Easily**: Create tokens with custom payloads, headers, and algorithms like HS256. You can even encrypt sensitive data using AES.  
- **Decode Tokens Instantly**: Peek inside JWTs to see headers, payloads, and signatures—no secret key needed.  
- **Extract Specific Claims**: Quickly pull out fields like `email`, `role`, `permissions`, or any custom claim without manually parsing the token.  
- **CLI Ready**: Use the command-line interface to decode tokens, extract claims, or inspect JWT structure—perfect for development and debugging.  
- **SSO Friendly**: Works seamlessly with `id_token` or access tokens from providers like Okta, Auth0, Azure AD, and Google OAuth.  
- **Human-Friendly Errors**: If a token is malformed or a claim is missing, the CLI provides clear, readable error messages.  
- **Debug & Learn**: Inspect real-world JWTs to understand their structure, making it an excellent tool for learning and testing authentication flows.  
- **Security Disclaimer Built-In**: JWT Pro clearly warns users that it **does not verify signatures**, keeping you aware that it’s meant for decoding and debugging only.  

---

## Benefits

- **Save Time During Development**: Quickly decode, inspect, and understand JWTs without writing extra code.  
- **Simplify Debugging**: Easily spot missing claims, malformed tokens, or issues in SSO/OAuth flows.  
- **Safe Testing Environment**: Work with tokens safely without exposing real secrets, thanks to clear warnings and decoding-only functionality.  
- **Better Understanding of JWTs**: Learn how headers, payloads, and signatures work by seeing them in real-time.  
- **Support for Real-World SSO**: Perfect for developers integrating with identity providers like Okta, Auth0, Azure AD, or Google OAuth.  
- **Flexible and Versatile**: Use it in scripts, CI/CD pipelines, command-line workflows, or interactive development.  
- **Human-Friendly**: Clear error messages and CLI output make it easy to understand, even for those new to JWTs.  

---

## Installation

This package is available through the [PyPI registry](__https://pypi.org/project/random-password-toolkit/__).

Before installing, ensure you have Python 3.6 or higher installed. You can download and install Python from [python.org](__https://www.python.org/downloads/__).

You can install the package using `pip`:

```bash
pip install jwt-pro

```

---

## Methods
| Method                    | Description                                                               |
|---------------------------|---------------------------------------------------------------------------|
| `generate_token()`        | Generates a JWT with a custom header, payload, and optional encryption.   |
| `verify_token()`          | Verifies a JWT token and checks its validity, expiration, and integrity.  |


---

## Encrypt Option (encrypt=True vs encrypt=False)

The `encrypt` parameter in the `generate_token()` and `verify_token()` methods controls whether the payload is encrypted using AES. Here’s how it behaves:

| Parameter / Command | Behavior                                                                 | Use Case                                                                 |
|---------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `encrypt=True`      | - The payload is encrypted using AES with CBC mode.                      | Use when sensitive data in the payload needs to be protected.             |
|                     | - The token payload is stored in encrypted form and cannot be read directly. | Ideal for protecting data like passwords, user data, etc.              |
| `encrypt=False`     | - The payload is stored in plain text (unencrypted).                     | Use when the data in the payload does not require encryption.             |
|                     | - The payload can be directly read and is visible in the token.          | Suitable for non-sensitive, public data (e.g., user ID, session info).   |
| `decode`            | - Decodes either **header** or **payload** (based on options).           | Quickly inspect claims (`email`, `role`, `exp`, etc.) inside a JWT.      |
| `decode_all`        | - Decodes **header, payload, and signature** (no verification).          | Get a complete breakdown of a JWT for debugging or learning purposes.    |


---

## CLI Features

| Command / Option             | Behavior                                               | Use Case                                                   |
|-------------------------------|-------------------------------------------------------|------------------------------------------------------------|
| `jwt-pro <token>`             | Decodes **payload** (default)                         | Quickly inspect the claims inside a JWT token              |
| `jwt-pro <token> --header`    | Decodes **header** only                               | Check algorithm, type, and key ID of the token             |
| `jwt-pro <token> --all`       | Decodes **header, payload, and signature** (no verify)| Full breakdown of a JWT for debugging/learning             |
| `jwt-pro <token> --get FIELD` | Extracts a specific claim value (error if not found)  | Pull just `email`, `role`, etc. without dumping everything |
| `--help`                      | Shows help, usage instructions, and security warning | Guide users on how to use CLI safely                       |


---

# Usage
## Importing the Package

```python
from jwt_pro import generate_token, verify_token
```

---

## Generate a JWT (Without Encryption)

```python
from jwt_pro import generate_token

# Define Header and Payload
header = {
    "alg": "HS256",  # HMAC-SHA256 algorithm
    "typ": "JWT"
}
payload = {
    "user_id": "12345",
    "name": "John Doe"
}
secret = "your-secret-key"
expiry = 3600 (default 3600)

# Generate JWT (without encryption)
token = generate_token(header, payload, secret, expiry, encrypt=False)

print(f"Generated Token: {token}")
```

---

## Verify a JWT (Without Encryption)
```python
from jwt_pro import verify_token

# Secret key used for signing
secret = "your-secret-key"

# Token to verify (use token from previous example)
token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9..."

try:
    verified_payload = verify_token(token, secret, encrypt=False)
    print(f"Verified Payload: {verified_payload}")
except ValueError as e:
    print(f"Verification Error: {e}")
```

---

## Generate JWT with AES Encryption
```python
from jwt_pro import generate_token

# Define Header and Payload
header = {
    "alg": "HS256",  # HMAC-SHA256 algorithm
    "typ": "JWT"
}
payload = {
    "user_id": "12345",
    "name": "John Doe"
}
secret = "your-secret-key"

# Generate JWT with AES encryption
token_encrypted = generate_token(header, payload, secret, expires_in=3600, encrypt=True)

print(f"Generated Encrypted Token: {token_encrypted}")
```

---

## Verify Encrypted JWT
```python
from jwt_pro import verify_token

# Secret key used for signing
secret = "your-secret-key"

# Encrypted token to verify (use token from previous example)
token_encrypted = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9..."

try:
    verified_payload_encrypted = verify_token(token_encrypted, secret, encrypt=True)
    print(f"Verified Encrypted Payload: {verified_payload_encrypted}")
except ValueError as e:
    print(f"Verification Error: {e}")
```

---

## Decode Payload
```python
from jwt_pro import decode_token

token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9..."

print("Payload:", decode_token(token))

```

---


## Decode only header
```python
from jwt_pro import decode_token

token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9..."

print("Header:", decode_token(token, header=True))

```

---


## Decode all from token
```python
from jwt_pro import decode_all

token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9..."

print("Header:", decode_all(token))

```

---
## Token Expiration
The default expiration time for the token is **1 hour** (3600 seconds). If not explicitly specified during token generation, the token will automatically expire 1 hour from the time it was created.

You can change the expiration time by passing the `expiry` claim during the token generation process.

```python
from jwt_pro import generate_token
token = generate_token(payload, secret, expiry=7200)  # Token will expire in 2 hours

```

---

# Common Errors

| Error Type                           | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| **ValueError: Token has expired.**   | Raised when the token has expired based on the `exp` field.                 |
| **ValueError: Invalid token format.**| Raised when the token format does not match the expected header.payload.signature format. |
| **ValueError: Invalid token header.**| Raised when the header is malformed or missing required fields.             |
| **ValueError: Invalid token payload.**| Raised when the payload cannot be decrypted or parsed.                     |
| **ValueError: Unsupported algorithm.**| Raised if the algorithm specified in the token header is unsupported.       |


---

# Use Cases

- **User Authentication**: Securely authenticate users in web applications by generating and verifying tokens.
- **Data Protection**: Encrypt sensitive data in the token payload and ensure its integrity during transmission.
- **Session Management**: Manage user sessions using JWTs with automatic expiration handling.
- **API Authentication**: Secure communication between microservices using JWTs for API authentication.
- **SSO Token Inspection**: Decode and analyze **SSO identity tokens (`id_token`)** or access tokens from providers like Okta, Auth0, Azure AD, or Google OAuth.
- **Debugging and Development**: Inspect and decode JWTs easily to verify payloads, headers, and signatures during development.
- **Claim Extraction**: Quickly extract specific claims (like `email`, `role`, `permissions`) from JWTs without manually parsing the token.
- **Token Analysis**: Decode and review the structure of JWTs from SSO providers, OAuth, or custom APIs for troubleshooting and learning.
- **Educational Purposes**: Teach and understand JWT internals by seeing how payloads, headers, and signatures are represented.
- **CLI Automation**: Use command-line decoding for scripts, automated tests, or CI/CD pipelines to inspect tokens programmatically.

---
## Discussions
- **GitHub Discussions**: Share use cases, report bugs, and suggest features.

We'd love to hear from you and see how you're using **JWT PRO** in your projects!

---

## Requesting Features
If you have an idea for a new feature, please open a feature request in the Issues section with:
- A clear description of the feature
- Why it would be useful

---

## Issues and Feedback
For issues, feedback, and feature requests, please open an issue on our [GitHub Issues page](http://github.com/krishnatadi/jwt-pro-python/issues). We actively monitor and respond to community feedback.

---

## FAQ (Frequently Asked Questions)

For detailed answers to common questions, click [here](https://github.com/krishnatadi/jwt-pro-python#faq-frequently-asked-questions) to visit our FAQ section.


## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Krishnatadi/jwt-pro-python/blob/main/LICENSE) file for details.
