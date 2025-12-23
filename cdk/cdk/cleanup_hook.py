"""
Pre-deployment cleanup for ACM certificates and Route53 validation records.

This module deletes existing ACM certificates and their Route53 validation records
BEFORE deployment so CDK can create fresh ones without conflicts.

This solves the problem: ACM certificates cannot be imported into CloudFormation,
so we must delete existing ones before CDK creates new ones.

Usage:
    from cdk.cleanup_hook import cleanup_before_deploy
    
    cleanup_before_deploy(
        domain_names=["api.dev.kernelworx.app", "login.dev.kernelworx.app"],
        environment_name="dev"
    )
"""

import os
from typing import Any

import boto3


def cleanup_before_deploy(
    domain_names: list[str],
    environment_name: str = "dev",
) -> None:
    """
    Delete unmanaged (orphaned) ACM certificates before deployment.
    
    Unmanaged certificates are those not created/managed by CloudFormation.
    These should be cleaned up so CDK can create and manage fresh certificates.
    
    Args:
        domain_names: List of domain names to find and delete certificates for
                      (e.g., ["api.dev.kernelworx.app", "login.dev.kernelworx.app"])
        environment_name: Environment name (dev, prod) for logging
    """
    region = os.getenv("AWS_REGION") or "us-east-1"
    
    # Initialize AWS clients
    acm_client = boto3.client("acm", region_name=region)
    cognito_client = boto3.client("cognito-idp", region_name=region)
    route53_client = boto3.client("route53", region_name=region)
    
    try:
        print("\n🧹 Pre-deployment cleanup: Removing orphaned (unmanaged) ACM certificates...")
        
        # Find and delete unmanaged certificates for each domain
        for domain in domain_names:
            cert_arn = _find_certificate_arn(acm_client, domain)
            if cert_arn:
                if _is_unmanaged_certificate(cert_arn):
                    print(f"   🗑️  Found unmanaged certificate: {domain}")
                    
                    # Check if Cognito is using this domain
                    if "login" in domain:
                        _disconnect_cognito_domain(cognito_client, domain)
                    
                    _delete_acm_certificate(acm_client, cert_arn)
                    print(f"   ✅ Deleted orphaned certificate")
                else:
                    print(f"   ℹ️  Certificate exists but is managed: {domain}")
            else:
                print(f"   ℹ️  No certificate found for: {domain}")
        
        # Clean up orphaned Route53 validation records
        print("\n🧹 Cleaning up orphaned Route53 validation records...")
        _cleanup_orphaned_route53_records(route53_client, domain_names)
        print("   ✅ Route53 cleanup complete")
        
    except Exception as e:
        print(f"⚠️  Warning: Cleanup error (proceeding anyway): {e}")
        # Don't fail the deployment - cleanup is optional


def _find_certificate_arn(client: Any, domain_name: str) -> str | None:
    """Find an ACM certificate ARN by domain name."""
    try:
        paginator = client.get_paginator("list_certificates")
        for page in paginator.paginate(CertificateStatuses=["ISSUED", "PENDING_VALIDATION"]):
            for cert in page.get("CertificateSummaryList", []):
                cert_arn = cert.get("CertificateArn")
                cert_domain = cert.get("DomainName")
                
                # Check main domain and SANs
                if cert_domain == domain_name:
                    return cert_arn
                
                # Check subject alternative names
                try:
                    detail = client.describe_certificate(CertificateArn=cert_arn)
                    sans = detail.get("Certificate", {}).get("SubjectAlternativeNames", [])
                    if domain_name in sans:
                        return cert_arn
                except Exception:
                    pass
    except Exception as e:
        print(f"   ⚠️  Could not list certificates: {e}")
    
    return None


def _is_unmanaged_certificate(cert_arn: str) -> bool:
    """Check if a certificate is unmanaged (not by CloudFormation)."""
    # A certificate is managed if it was created by CloudFormation
    # We can detect this by checking if the certificate has CloudFormation tags
    # Or if it's used by CloudFormation-created resources
    # For now, we assume unmanaged if it's manually created
    # In practice, if it's being used by Cognito/CloudFront that's set up outside CDK, it's unmanaged
    
    acm_client = boto3.client("acm", region_name=os.getenv("AWS_REGION", "us-east-1"))
    try:
        cert_detail = acm_client.describe_certificate(CertificateArn=cert_arn)
        
        # Check if it was created/managed by CloudFormation
        # CloudFormation-managed resources typically have a specific tag or naming pattern
        tags = cert_detail.get("Certificate", {}).get("Tags", [])
        
        # Check for CloudFormation owner tag
        for tag in tags:
            if tag.get("Key") == "aws:cloudformation:stack-name":
                print(f"   ℹ️  Certificate is CloudFormation-managed")
                return False
        
        # If no CloudFormation tags, it's unmanaged
        return True
    except Exception:
        # If we can't determine, assume it's unmanaged
        return True


def _delete_acm_certificate(client: Any, cert_arn: str) -> None:
    """Delete an ACM certificate."""
    try:
        client.delete_certificate(CertificateArn=cert_arn)
    except Exception as e:
        print(f"   ⚠️  Could not delete certificate: {e}")


def _disconnect_cognito_domain(client: Any, domain_name: str) -> None:
    """Delete a Cognito custom domain so its certificate can be deleted."""
    try:
        print(f"      ⏳ Deleting Cognito domain: {domain_name}")
        
        # Get the domain description to find the user pool ID
        domain_desc = client.describe_user_pool_domain(Domain=domain_name)
        domain_info = domain_desc.get("DomainDescription", {})
        
        if not domain_info:
            print(f"      ℹ️  Domain not found")
            return
            
        user_pool_id = domain_info.get("UserPoolId")
        if not user_pool_id:
            print(f"      ⚠️  Could not find UserPoolId for domain")
            return
        
        # Delete the user pool domain (this frees up the certificate)
        client.delete_user_pool_domain(
            Domain=domain_name,
            UserPoolId=user_pool_id
        )
        print(f"      ✅ Cognito domain deleted")
        
        # Wait a moment for the deletion to propagate
        import time
        time.sleep(2)
        
    except Exception as e:
        print(f"      ⚠️  Could not delete Cognito domain: {e}")


def _cleanup_orphaned_route53_records(
    client: Any, domain_names: list[str]
) -> None:
    """Clean up orphaned Route53 validation records for deleted certificates."""
    try:
        # Look up hosted zones for these domains
        zones = _find_hosted_zones(client, domain_names)
        
        for zone_id, domain in zones:
            records = _list_hosted_zone_records(client, zone_id)
            
            # Find validation records for this domain
            for record in records:
                if record.get("Type") == "CNAME" and _is_validation_record(record):
                    # Check if this is a validation record for our domain
                    if _matches_domain(record.get("Name", ""), domain):
                        _delete_route53_record(client, zone_id, record)
                        print(f"   ✅ Deleted validation record: {record['Name']}")
    except Exception as e:
        print(f"   ⚠️  Could not clean Route53 records: {e}")


def _find_hosted_zones(client: Any, domain_names: list[str]) -> list[tuple[str, str]]:
    """Find hosted zone IDs for the given domain names."""
    zones = []
    try:
        paginator = client.get_paginator("list_hosted_zones")
        for page in paginator.paginate():
            for zone in page.get("HostedZones", []):
                zone_id = zone["Id"].split("/")[-1]
                zone_domain = zone["Name"].rstrip(".")
                
                # Check if any of our domains match this zone
                for domain in domain_names:
                    if domain.endswith(zone_domain):
                        zones.append((zone_id, zone_domain))
                        break
    except Exception as e:
        print(f"   ⚠️  Could not list hosted zones: {e}")
    
    return zones


def _list_hosted_zone_records(client: Any, hosted_zone_id: str) -> list[dict[str, Any]]:
    """List all records in a Route53 hosted zone."""
    records = []
    try:
        paginator = client.get_paginator("list_resource_record_sets")
        for page in paginator.paginate(HostedZoneId=hosted_zone_id):
            records.extend(page.get("ResourceRecordSets", []))
    except Exception as e:
        print(f"   ⚠️  Could not list hosted zone records: {e}")
    
    return records


def _is_validation_record(record: dict[str, Any]) -> bool:
    """Check if a record is likely an ACM validation record (CNAME with _acme or similar)."""
    name = record.get("Name", "").lower()
    return "_acme-challenge" in name or "_validation" in name


def _matches_domain(record_name: str, domain: str) -> bool:
    """Check if a Route53 record name corresponds to a domain."""
    record_name = record_name.rstrip(".").lower()
    domain = domain.lower()
    
    return record_name.endswith(domain) or domain.endswith(record_name.split(".")[0])


def _delete_route53_record(
    client: Any, hosted_zone_id: str, record: dict[str, Any]
) -> None:
    """Delete a Route53 record."""
    try:
        change_batch = {
            "Changes": [
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": {
                        "Name": record["Name"],
                        "Type": record["Type"],
                        "TTL": record.get("TTL"),
                        "ResourceRecords": record.get("ResourceRecords"),
                    },
                }
            ]
        }
        
        # Remove TTL if not present
        if "TTL" not in record:
            del change_batch["Changes"][0]["ResourceRecordSet"]["TTL"]
        
        client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch
        )
    except Exception as e:
        print(f"   ⚠️  Could not delete Route53 record {record['Name']}: {e}")
