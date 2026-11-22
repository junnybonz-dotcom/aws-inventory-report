"""List S3 buckets visible to the configured AWS identity."""
from botocore.exceptions import BotoCoreError, ClientError
from aws_config import create_client, resolve_region
from aws_errors import report_aws_error

def get_buckets(s3):
    """Return sorted (bucket name, creation date) rows."""
    rows = [
        (bucket["Name"], bucket["CreationDate"].strftime("%Y-%m-%d"))
        for bucket in s3.list_buckets().get("Buckets", [])
    ]
    return sorted(rows)

def main():
    try:
        region = resolve_region()
        s3 = create_client("s3", region)
        buckets = get_buckets(s3)
    except (BotoCoreError, ClientError) as error:
        report_aws_error("S3 bucket inventory", error)
        return 1
    if not buckets:
        print("No buckets found in this account.")
    else:
        for name, created in buckets:
            print(f"{name} (created {created})")
    print(f"Total: {len(buckets)} buckets")
    print(f"Region: {region}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
