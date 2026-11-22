"""Shared AWS error messages and a small diagnostic command."""
import sys
from botocore.exceptions import (
    BotoCoreError, ClientError, ConnectTimeoutError, EndpointConnectionError,
    NoCredentialsError, NoRegionError, PartialCredentialsError, ProfileNotFound, SSLError,
)
from aws_config import create_client, resolve_region

EXPIRED_TOKEN_CODES = {"ExpiredToken", "ExpiredTokenException", "RequestExpired"}
ACCESS_DENIED_CODES = {"AccessDenied", "AccessDeniedException", "UnauthorizedOperation"}

def describe_error(error):
    """Return a short, actionable explanation for common Boto3 errors."""
    if isinstance(error, NoCredentialsError):
        return "No AWS credentials found. Configure an AWS profile or attach an IAM role."
    if isinstance(error, PartialCredentialsError):
        return "AWS credentials are incomplete. Check the configured profile or environment."
    if isinstance(error, ProfileNotFound):
        return "The selected AWS profile was not found. Check AWS_PROFILE and your profile names."
    if isinstance(error, NoRegionError):
        return "No AWS region is configured. Set AWS_REGION or AWS_DEFAULT_REGION."
    if isinstance(error, SSLError):
        return "TLS/SSL error. Check the system clock and CA certificates; do not disable verification."
    if isinstance(error, (EndpointConnectionError, ConnectTimeoutError)):
        return "Cannot reach the AWS endpoint. Check the region and network connection."
    if isinstance(error, ClientError):
        code = error.response.get("Error", {}).get("Code", "Unknown")
        if code in EXPIRED_TOKEN_CODES:
            return f"Temporary AWS credentials expired ({code}). Refresh the session."
        if code in ACCESS_DENIED_CODES:
            return f"AWS denied the operation ({code}). Review the IAM permissions."
        return f"AWS returned service error {code}."
    if isinstance(error, BotoCoreError):
        return f"Boto3 configuration or client error: {type(error).__name__}."
    return f"Unexpected error: {type(error).__name__}."

def report_aws_error(operation, error):
    """Print a consistent error message without dumping sensitive details."""
    print(f"ERROR: {operation}: {describe_error(error)}", file=sys.stderr)

def run_checked(operation, func, *args, **kwargs):
    """Run an AWS operation, returning None after a handled SDK error."""
    try:
        return func(*args, **kwargs)
    except (BotoCoreError, ClientError) as error:
        report_aws_error(operation, error)
        return None

def list_bucket_names(s3):
    """Return sorted S3 bucket names."""
    return sorted(bucket["Name"] for bucket in s3.list_buckets().get("Buckets", []))

def list_instance_summaries(ec2):
    """Return instance ID/state pairs, reading every EC2 result page."""
    rows = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                rows.append((instance["InstanceId"], instance["State"]["Name"]))
    return sorted(rows)

def main():
    try:
        region = resolve_region()
        sts = create_client("sts", region)
        s3 = create_client("s3", region)
        ec2 = create_client("ec2", region)
        identity = run_checked("AWS identity check", sts.get_caller_identity)
        if identity is None:
            return 1
        print(f"Authenticated as: {identity['Arn']}")
        buckets = run_checked("S3 bucket inventory", list_bucket_names, s3)
        if buckets is not None:
            print(f"Buckets ({len(buckets)}): {', '.join(buckets) or '(none)'}")
        instances = run_checked("EC2 instance inventory", list_instance_summaries, ec2)
        if instances is not None:
            print(f"Instances ({len(instances)}):")
            for instance_id, state in instances:
                print(f"  {instance_id}  {state}")
        print(f"Region: {region}")
        return 0
    except (BotoCoreError, ClientError) as error:
        report_aws_error("AWS client setup", error)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
