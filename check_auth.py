"""Check which AWS identity the configured credentials represent."""
from botocore.exceptions import BotoCoreError, ClientError
from aws_config import create_client, resolve_region
from aws_errors import report_aws_error

def get_identity(sts):
    """Return the ARN for the active AWS identity."""
    return sts.get_caller_identity()["Arn"]

def main():
    try:
        region = resolve_region()
        sts = create_client("sts", region)
        print(f"Authenticated as: {get_identity(sts)}")
        print(f"Region: {region}")
        return 0
    except (BotoCoreError, ClientError) as error:
        report_aws_error("AWS identity check", error)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
