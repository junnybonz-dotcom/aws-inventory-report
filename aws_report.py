"""Generate a read-only inventory report for S3 buckets and EC2 instances."""
import datetime
from botocore.exceptions import BotoCoreError, ClientError
from aws_config import create_client, resolve_region
from aws_errors import report_aws_error

def get_buckets(s3):
    """Return sorted (bucket name, creation date) rows."""
    response = s3.list_buckets()
    rows = [
        (bucket["Name"], bucket["CreationDate"].strftime("%Y-%m-%d"))
        for bucket in response.get("Buckets", [])
    ]
    return sorted(rows)

def get_instances(ec2):
    """Return sorted instance details, reading every EC2 result page."""
    rows = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                rows.append((
                    tags.get("Name", "(no name)"),
                    instance["InstanceId"],
                    instance["State"]["Name"],
                    instance["InstanceType"],
                    instance.get("PublicIpAddress", "-"),
                ))
    return sorted(rows)

def report_buckets(s3):
    print("\nS3 BUCKETS")
    try:
        rows = get_buckets(s3)
    except (BotoCoreError, ClientError) as error:
        report_aws_error("S3 bucket inventory", error)
        return False
    if not rows:
        print("  (none)")
        return True
    print(f"  {'NAME':<40} {'CREATED':<12}")
    for name, created in rows:
        print(f"  {name:<40} {created:<12}")
    print(f"  Total: {len(rows)}")
    return True

def report_instances(ec2):
    print("\nEC2 INSTANCES")
    try:
        rows = get_instances(ec2)
    except (BotoCoreError, ClientError) as error:
        report_aws_error("EC2 instance inventory", error)
        return False
    if not rows:
        print(f"  (none in {ec2.meta.region_name})")
        return True
    print(
        f"  {'NAME':<16} {'INSTANCE ID':<21} "
        f"{'STATE':<12} {'TYPE':<10} PUBLIC IP"
    )
    for name, instance_id, state, instance_type, public_ip in rows:
        print(
            f"  {name:<16} {instance_id:<21} "
            f"{state:<12} {instance_type:<10} {public_ip}"
        )
    print(f"  Total: {len(rows)}")
    return True

def main():
    try:
        region = resolve_region()
        sts = create_client("sts", region)
        s3 = create_client("s3", region)
        ec2 = create_client("ec2", region)
        identity = sts.get_caller_identity()["Arn"]
    except (BotoCoreError, ClientError) as error:
        report_aws_error("AWS identity or client setup", error)
        return 1
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print("=" * 65)
    print(f"AWS REPORT | {now}")
    print(f"Identity: {identity}")
    print(f"Region:   {region}")
    print("=" * 65)
    buckets_ok = report_buckets(s3)
    instances_ok = report_instances(ec2)
    return 0 if buckets_ok and instances_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
