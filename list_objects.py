"""List objects in an S3 bucket using paginated ListObjectsV2 calls."""
import sys
from botocore.exceptions import BotoCoreError, ClientError
from aws_config import create_client, resolve_region
from aws_errors import report_aws_error

def format_size(num_bytes):
    """Format bytes using readable binary units."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def get_objects(s3, bucket, prefix=""):
    """Return S3 object key, formatted size, and modified timestamp rows."""
    rows = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            modified = obj["LastModified"].strftime("%Y-%m-%d %H:%M UTC")
            rows.append((obj["Key"], format_size(obj["Size"]), modified))
    return rows

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Usage: python list_objects.py <bucket-name> [prefix]", file=sys.stderr)
        return 2
    bucket = args[0]
    prefix = args[1] if len(args) > 1 else ""
    try:
        region = resolve_region()
        s3 = create_client("s3", region)
        rows = get_objects(s3, bucket, prefix)
    except (BotoCoreError, ClientError) as error:
        report_aws_error("S3 object listing", error)
        return 1
    print(f"S3 OBJECTS | bucket={bucket} | prefix={prefix or '(all)'} | region={region}")
    if not rows:
        print("No objects found.")
        return 0
    for key, size, modified in rows:
        print(f"{key:<40} {size:>9}   {modified}")
    print(f"Total: {len(rows)} objects")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
