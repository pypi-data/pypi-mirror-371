import argparse
from .client import ObservabilityClient


def main():
    parser = argparse.ArgumentParser(description="Platform Observability CLI")
    parser.add_argument("message", nargs="?", help="Log message to send")
    parser.add_argument(
        "--api-key", dest="api_key", help="API key", required=True
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default="https://observability.redducklabs.com/api/v1",
        help="Base API URL",
    )
    args = parser.parse_args()

    client = ObservabilityClient(api_key=args.api_key, base_url=args.base_url)
    if args.message:
        client.ingest_logs([{"message": args.message, "level": "INFO"}])
        print("Log sent")
    else:
        # Health check
        try:
            client._make_request("GET", "/health")
            print("Service healthy")
        except Exception as e:
            print(f"Health check failed: {e}")


if __name__ == "__main__":
    main()
