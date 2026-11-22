"""List running EC2 instances using paginated DescribeInstances calls."""
from botocore.exceptions import BotoCoreError, ClientError
from aws_config import create_client, resolve_region
from aws_errors import report_aws_error

def get_instances(ec2, states=("running",)):
    """Return sorted running-instance details from every result page."""
    rows = []
    paginator = ec2.get_paginator("describe_instances")
    pagination_args = {}
    if states:
        pagination_args["Filters"] = [
            {"Name": "instance-state-name", "Values": list(states)}
        ]
    for page in paginator.paginate(**pagination_args):
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

def main():
    try:
        region = resolve_region()
        ec2 = create_client("ec2", region)
        rows = get_instances(ec2)
    except (BotoCoreError, ClientError) as error:
        report_aws_error("EC2 instance inventory", error)
        return 1
    print(f"RUNNING EC2 INSTANCES | {region}")
    if not rows:
        print("No running instances found.")
        return 0
    print(f"  {'NAME':<16} {'INSTANCE ID':<21} {'STATE':<12} {'TYPE':<10} PUBLIC IP")
    for name, instance_id, state, instance_type, public_ip in rows:
        print(f"  {name:<16} {instance_id:<21} {state:<12} {instance_type:<10} {public_ip}")
    print(f"Total: {len(rows)} running instances")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
