# AWS Inventory Report

A read-only Python command-line inventory tool built with Boto3, the AWS SDK for Python. It retrieves information about S3 buckets and EC2 instances, verifies the active AWS identity, and reports common AWS errors.

## Features

- Lists S3 bucket names and creation dates.
- Retrieves EC2 instance names, IDs, states, types, and public IP addresses.
- Uses paginators for EC2 instance and S3 object listings.
- Verifies the active AWS identity through STS.
- Uses one shared AWS region configuration across all scripts.
- Provides consistent, actionable AWS error messages.
- Includes offline unit tests using mocked AWS clients.
- Uses read-only AWS API operations.

## Technologies

Python 3 · Boto3 · AWS STS · Amazon S3 · Amazon EC2 · AWS IAM · `unittest`

## Project Structure

```text
aws-inventory-report/
├── README.md
├── requirements.txt
├── .gitignore
├── aws_config.py
├── aws_report.py
├── aws_errors.py
├── check_auth.py
├── list_buckets.py
├── list_instances.py
├── list_objects.py
└── tests/
    └── test_aws_inventory.py
```

## Requirements

- Python 3
- An AWS account and credentials configured through a supported Boto3 credential provider
- Read permissions for the S3 and EC2 inventory operations you intend to run

## Installation

Clone the repository:

```bash
git clone https://github.com/junnybonz-dotcom/aws-inventory-report.git
cd aws-inventory-report
```

Create a virtual environment:

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / Ubuntu**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Region Configuration

All project scripts use the same region resolver. The precedence is:

1. An explicit region supplied to the helper.
2. `AWS_REGION`.
3. `AWS_DEFAULT_REGION`.
4. The region from the configured Boto3 session/profile.
5. The project fallback, `us-east-1`.

Set a region before running the scripts when you want to override the default.

**Windows PowerShell**

```powershell
$env:AWS_REGION = "ap-southeast-1"
```

**Linux / Ubuntu**

```bash
export AWS_REGION=ap-southeast-1
```

The region setting controls the regional AWS clients. S3 bucket listing is an account-level operation, while S3 object listing uses the bucket's configured region and endpoint behavior.

## AWS Authentication

Boto3 uses its standard credential provider chain.

- On EC2, prefer an attached IAM role.
- For local development, use a configured AWS CLI profile.
- Do not hardcode credentials or commit credential files.

Check the active identity:

```bash
python check_auth.py
```

The script uses STS `GetCallerIdentity`. AWS documents that this operation does not require an IAM permission: [GetCallerIdentity API reference](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html).

## Running the Project

Generate the combined S3 and EC2 report:

```bash
python aws_report.py
```

List S3 buckets:

```bash
python list_buckets.py
```

List running EC2 instances:

```bash
python list_instances.py
```

The EC2 listing uses a paginator and filters for instances in the `running` state.

List objects in a bucket:

```bash
python list_objects.py YOUR_BUCKET_NAME
```

Optionally specify an object prefix:

```bash
python list_objects.py YOUR_BUCKET_NAME YOUR_PREFIX
```

Run the AWS error-handling demonstration:

```bash
python aws_errors.py
```

## IAM Permissions

Grant only the actions needed for the operations being used. The main inventory scripts use these actions:

| Operation | IAM action | Resource guidance |
|---|---|---|
| List all buckets | `s3:ListAllMyBuckets` | `*` |
| List objects in a selected bucket | `s3:ListBucket` | The specific bucket ARN, such as `arn:aws:s3:::YOUR_BUCKET_NAME` |
| Describe EC2 instances | `ec2:DescribeInstances` | `*` |

`sts:GetCallerIdentity` does not require an IAM allow permission.

The exact policy needed depends on which scripts are run. For example, users who only run the EC2 inventory do not need the S3 permissions. Review the official service authorization references before attaching a policy:

- [Amazon S3 actions and resource types](https://docs.aws.amazon.com/service-authorization/latest/reference/list_s3.html)
- [Amazon EC2 actions and resource types](https://docs.aws.amazon.com/service-authorization/latest/reference/list_ec2.html)

## Error Handling

The shared error helper provides consistent explanations for common issues such as:

- Missing or incomplete AWS credentials.
- Missing AWS profile or region configuration.
- Expired temporary credentials.
- Access denied responses.
- Endpoint and connection problems.
- Other Boto3 client or service errors.

Error output avoids printing full exception payloads, which may contain unnecessary account or resource details.

## Tests

The unit tests use Python's built-in `unittest` framework and mocked clients. They do not contact AWS and do not require AWS credentials.

Run them from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover region selection, sorted bucket data, EC2 pagination, the running-instance filter, S3 object pagination, identity retrieval, object-size formatting, and common AWS error messages.

## Sanitized Example Output

Historical example captured on October 28, 2026. Account and resource identifiers have been redacted.

```text
=================================================================
AWS REPORT | 2026-10-28 01:47 UTC
Identity: arn:aws:sts::<ACCOUNT-ID>:assumed-role/report-script-role/<SESSION>
Region:   us-east-1
=================================================================

S3 BUCKETS
  NAME                                     CREATED
  <BUCKET-NAME>                            2026-10-09
  Total: 1

EC2 INSTANCES
  NAME             INSTANCE ID           STATE        TYPE       PUBLIC IP
  study-vm-01      i-<INSTANCE-ID>        running      t3.micro   <PUBLIC-IP>
  Total: 1
```

This is a historical sanitized sample, not a live result from the current code revision. The inventory changes according to the resources visible to the configured AWS identity.

## Security Considerations

- The project is intended for read-only inventory operations.
- It does not create, modify, or delete AWS resources.
- Use least-privilege IAM permissions.
- Never commit access keys, secret keys, private keys, credential files, or unredacted runtime output.
- Redact account IDs, bucket names, instance IDs, and public IP addresses before sharing output.

## Current Limitations

- The default region is `us-east-1` unless overridden by the supported region configuration.
- The standalone `list_instances.py` script currently displays only running instances.
- The scripts are small command-line utilities rather than an installed Python package.
- The tests validate helper functions with mocked responses; they do not replace an integration test against an AWS account.
- No license has been selected for this repository yet.

## What I Learned

This project helped me practice using Python to interact with AWS services through Boto3. I worked with AWS identity verification, S3 and EC2 inventory, pagination, region configuration, exception handling, IAM permissions, and read-only cloud operations.

It also reinforced the importance of testing code without depending on live cloud resources and keeping credentials out of source control.
