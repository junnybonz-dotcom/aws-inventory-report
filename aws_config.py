"""Shared AWS region and client configuration."""
import os
import boto3

DEFAULT_REGION = "us-east-1"

def resolve_region(region=None):
    """Precedence: argument, AWS_REGION, AWS_DEFAULT_REGION, Boto3 profile, default."""
    if region:
        return region
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or boto3.Session().region_name
        or DEFAULT_REGION
    )

def create_client(service_name, region=None):
    """Create a client using the shared region setting."""
    return boto3.client(service_name, region_name=resolve_region(region))
