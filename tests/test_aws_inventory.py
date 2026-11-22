"""Offline unit tests for AWS inventory helpers; no AWS account is needed."""
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError, NoCredentialsError

from aws_config import DEFAULT_REGION, resolve_region
from aws_errors import describe_error, list_instance_summaries
from aws_report import get_buckets, get_instances as get_report_instances
from check_auth import get_identity
from list_instances import get_instances as get_running_instances
from list_objects import format_size, get_objects


class RegionConfigurationTests(unittest.TestCase):
    def test_explicit_region_has_highest_priority(self):
        self.assertEqual(resolve_region("ap-southeast-2"), "ap-southeast-2")

    def test_aws_region_environment_variable_is_used(self):
        with patch.dict(os.environ, {"AWS_REGION": "ap-southeast-1"}, clear=True):
            self.assertEqual(resolve_region(), "ap-southeast-1")

    def test_aws_default_region_is_used_as_fallback(self):
        with patch.dict(os.environ, {"AWS_DEFAULT_REGION": "ap-southeast-2"}, clear=True):
            self.assertEqual(resolve_region(), "ap-southeast-2")

    def test_project_default_region_is_used_when_unconfigured(self):
        with patch.dict(os.environ, {}, clear=True), patch("aws_config.boto3.Session") as session:
            session.return_value.region_name = None
            self.assertEqual(resolve_region(), DEFAULT_REGION)


class InventoryFunctionTests(unittest.TestCase):
    def test_bucket_rows_are_sorted(self):
        s3 = MagicMock()
        s3.list_buckets.return_value = {
            "Buckets": [
                {"Name": "zeta-bucket", "CreationDate": datetime(2026, 1, 2, tzinfo=timezone.utc)},
                {"Name": "alpha-bucket", "CreationDate": datetime(2026, 1, 1, tzinfo=timezone.utc)},
            ]
        }
        self.assertEqual(
            get_buckets(s3),
            [("alpha-bucket", "2026-01-01"), ("zeta-bucket", "2026-01-02")],
        )

    def test_consolidated_report_reads_multiple_ec2_pages(self):
        ec2 = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-002",
                "State": {"Name": "stopped"},
                "InstanceType": "t3.micro",
                "Tags": [{"Key": "Name", "Value": "second"}],
            }]}]},
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-001",
                "State": {"Name": "running"},
                "InstanceType": "t3.small",
                "Tags": [{"Key": "Name", "Value": "first"}],
                "PublicIpAddress": "203.0.113.10",
            }]}]},
        ]
        ec2.get_paginator.return_value = paginator
        rows = get_report_instances(ec2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], "i-001")
        self.assertEqual(rows[0][4], "203.0.113.10")
        paginator.paginate.assert_called_once_with()

    def test_running_instance_script_uses_paginator_and_running_filter(self):
        ec2 = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-101",
                "State": {"Name": "running"},
                "InstanceType": "t3.micro",
                "Tags": [],
            }]}]},
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-102",
                "State": {"Name": "running"},
                "InstanceType": "t3.small",
                "Tags": [{"Key": "Name", "Value": "worker"}],
            }]}]},
        ]
        ec2.get_paginator.return_value = paginator
        rows = get_running_instances(ec2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], "i-101")
        paginator.paginate.assert_called_once_with(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )

    def test_diagnostic_instance_summary_uses_paginator(self):
        ec2 = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-200", "State": {"Name": "pending"}
            }]}]},
            {"Reservations": [{"Instances": [{
                "InstanceId": "i-201", "State": {"Name": "running"}
            }]}]},
        ]
        ec2.get_paginator.return_value = paginator
        self.assertEqual(
            list_instance_summaries(ec2),
            [("i-200", "pending"), ("i-201", "running")],
        )

    def test_identity_helper_returns_arn(self):
        sts = MagicMock()
        sts.get_caller_identity.return_value = {
            "Arn": "arn:aws:iam::123456789012:user/test"
        }
        self.assertEqual(get_identity(sts), "arn:aws:iam::123456789012:user/test")

    def test_s3_objects_are_paginated_and_prefix_is_passed(self):
        s3 = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Contents": [{
                "Key": "reports/a.csv",
                "Size": 512,
                "LastModified": datetime(2026, 2, 3, tzinfo=timezone.utc),
            }]},
            {"Contents": [{
                "Key": "reports/b.csv",
                "Size": 2048,
                "LastModified": datetime(2026, 2, 4, tzinfo=timezone.utc),
            }]},
        ]
        s3.get_paginator.return_value = paginator
        rows = get_objects(s3, "example-bucket", "reports/")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "reports/a.csv")
        self.assertEqual(rows[1][1], "2 KB")
        paginator.paginate.assert_called_once_with(
            Bucket="example-bucket", Prefix="reports/"
        )

    def test_format_size(self):
        self.assertEqual(format_size(512), "512 B")
        self.assertEqual(format_size(1024), "1 KB")
        self.assertEqual(format_size(1024 * 1024), "1 MB")


class ErrorMessageTests(unittest.TestCase):
    def test_missing_credentials_has_actionable_message(self):
        self.assertIn("No AWS credentials found", describe_error(NoCredentialsError()))

    def test_access_denied_has_permission_message(self):
        error = ClientError({"Error": {"Code": "AccessDenied"}}, "DescribeInstances")
        self.assertIn("Review the IAM permissions", describe_error(error))


if __name__ == "__main__":
    unittest.main()
