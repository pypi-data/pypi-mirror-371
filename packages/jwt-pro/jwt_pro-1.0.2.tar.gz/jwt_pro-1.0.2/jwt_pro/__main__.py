import argparse
import json
import sys
from jwt_pro import decode_token, decode_all


def main():
    parser = argparse.ArgumentParser(
        description="Decode JWT tokens (without verification).\n"
                    "WARNING: This tool does NOT verify JWT signatures. Do not use for security!"
    )
    parser.add_argument("token", help="The JWT token string to decode")
    parser.add_argument(
        "--header", action="store_true", help="Decode only the header"
    )
    parser.add_argument(
        "--all", action="store_true", help="Decode header, payload, and signature"
    )
    parser.add_argument(
        "--get", metavar="FIELD", help="Extract a specific claim from the payload"
    )

    args = parser.parse_args()

    print("WARNING: This tool does NOT verify JWT signatures. Do not use for security!\n")

    try:
        if args.all:
            decoded = decode_all(args.token)
            print(json.dumps(decoded, indent=2))

        elif args.header:
            decoded = decode_token(args.token, header=True)
            print(json.dumps(decoded, indent=2))

        elif args.get:
            payload = decode_token(args.token)
            if args.get in payload:
                print(payload[args.get])
            else:
                print(f"Claim '{args.get}' was not found in the token payload.\n"
                      f"Available claims are: {', '.join(payload.keys()) if payload else 'None'}")
                sys.exit(1)

        else:
            decoded = decode_token(args.token)
            print(json.dumps(decoded, indent=2))

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Token part is not valid JSON. This usually means the token is malformed.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
