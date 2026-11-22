
# AWS Inventory Report

A read-only Python command-line inventory tool built with Boto3, the AWS SDK for Python.

The project retrieves information about Amazon S3 buckets and EC2 instances, verifies the active AWS identity, and reports common AWS authentication, permission, and connection errors.

## Features

- Lists S3 bucket names and creation dates.
- Retrieves EC2 instance names, IDs, states, types, and public IP addresses.
- Uses an EC2 paginator in the consolidated report.
- Verifies the active AWS identity through STS.
- Handles AWS credential, service, and connection errors.
- Lists S3 objects using pagination.
- Formats object sizes for readable terminal output.
- Uses read-only AWS operations.

## Technologies

- Python 3
- Boto3
- AWS STS
- Amazon S3
- Amazon EC2
- AWS IAM

## Project Structure

```text
aws-inventory-report/
├── README.md
├── requirements.txt
├── .gitignore
├── aws_report.py
├── aws_errors.py
├── check_auth.py
├── list_buckets.py
├── list_instances.py
└── list_objects.py
```

## Requirements

- Python 3
- An AWS account with the required read permissions
- AWS credentials configured through a supported credential provider

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

## AWS Authentication

The scripts use Boto3's standard AWS credential provider chain.

For an EC2 deployment, an attached IAM role is preferred over storing long-term access keys.

For local development, use an appropriately configured AWS CLI profile.

Never hardcode AWS access keys or commit credentials into this repository.

## Running the Project

Run the consolidated inventory report:

```bash
python aws_report.py
```

Check the current AWS identity:

```bash
python check_auth.py
```

List S3 buckets:

```bash
python list_buckets.py
```

List EC2 instances:

```bash
python list_instances.py
```

List objects inside an S3 bucket:

```bash
python list_objects.py YOUR_BUCKET_NAME
```

Specify an optional S3 prefix:

```bash
python list_objects.py YOUR_BUCKET_NAME YOUR_PREFIX
```

Run the AWS error-handling demonstration:

```bash
python aws_errors.py
```

## AWS Permissions

The relevant AWS API operations require permissions such as:

| Service | IAM Action |
|---|---|
| Amazon S3 | s3:ListAllMyBuckets |
| Amazon S3 | s3:ListBucket |
| Amazon EC2 | ec2:DescribeInstances |

The identity check uses STS GetCallerIdentity.

Use an appropriately scoped IAM policy rather than granting unnecessary permissions.

## Region Configuration

The consolidated `aws_report.py` script currently uses `us-east-1`.

Other individual scripts use the region configured through Boto3's default configuration.

## Security Considerations

- This project is designed for read-only inventory operations.
- It does not create, modify, or delete AWS resources.
- Use least-privilege IAM permissions.
- Never commit AWS credentials, private keys, or sensitive configuration files.
- Redact AWS account IDs, bucket names, instance IDs, and public IP addresses before sharing real output.

## Current Limitations

- The consolidated report currently uses a configured region rather than accepting a region argument.
- Individual scripts have different region configuration behavior.
- Automated test coverage has not yet been added.
- The project is still being improved through ongoing practice.

## What I Learned

This project helped me practice connecting Python to AWS services through Boto3.

I worked with AWS identity verification, S3 and EC2 inventory, pagination, exception handling, IAM permissions, and read-only cloud operations.

The project also reinforced the importance of secure credential management and understanding the permissions required by each AWS service.
