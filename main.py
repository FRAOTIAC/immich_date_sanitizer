import argparse

from date_sanitizer import DateSanitizer


def parse_args():
    """
    Parse command line arguments using argparse and return the arguments.
    """
    parser = argparse.ArgumentParser(description="Process API configuration.")
    parser.add_argument("--host", type=str, required=True,
                        help="Host IP and port (e.g., 192.168.2.3:8080)")
    parser.add_argument("--api_key", type=str,
                        help="API key for authentication")
    args = parser.parse_args()
    return args


def construct_api_url(host):
    """
    Construct the API URL by appending the base path to the host.
    """
    return f"http://{host}/api/asset"


if __name__ == "__main__":
    args = parse_args()
    API_URL = construct_api_url(args.host)
    API_KEY = args.api_key

    updater = DateSanitizer(API_URL, API_KEY)
    updater.process_records()
