#!/usr/bin/env python3
"""
Migration script to convert unitNumber from String to Int in both accounts and profiles tables.

This script:
1. Scans the accounts table for records with unitNumber as string
2. Scans the profiles table for records with unitNumber as string
3. Converts string unit numbers to integers (if they're valid numbers)
4. Updates the records with the integer type in DynamoDB

Usage:
    # Dry run (default)
    uv run python scripts/migrate_unit_numbers.py --env dev

    # Actually apply changes
    uv run python scripts/migrate_unit_numbers.py --env dev --apply
"""

import argparse
import re
import sys
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate unitNumber from String to Int")
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Environment to migrate (default: dev)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply the changes (default is dry-run)",
    )
    return parser.parse_args()


def extract_numeric_unit_number(value: str) -> Optional[int]:
    """
    Extract numeric unit number from string.

    Examples:
        "123" -> 123
        "Pack 456" -> 456
        "Troop 789" -> 789
        "abc" -> None
    """
    # First try direct conversion
    try:
        return int(value)
    except ValueError:
        pass

    # Try to extract numbers from string like "Pack 123" or "Troop 456"
    numbers = re.findall(r"\d+", value)
    if numbers:
        return int(numbers[0])

    return None


def migrate_accounts_table(
    table_name: str, apply: bool, dynamodb_client: Any
) -> tuple[int, int, int]:
    """
    Migrate accounts table unitNumber fields.

    Returns:
        Tuple of (total_scanned, needs_migration, migrated)
    """
    print(f"\n{'='*80}")
    print(f"Scanning accounts table: {table_name}")
    print(f"{'='*80}\n")

    table = boto3.resource("dynamodb").Table(table_name)

    total_scanned = 0
    needs_migration = 0
    migrated = 0

    # Scan for all accounts
    scan_kwargs = {}

    while True:
        response = table.scan(**scan_kwargs)
        items = response.get("Items", [])
        total_scanned += len(items)

        for item in items:
            account_id = item.get("accountId", "UNKNOWN")
            unit_number = item.get("unitNumber")

            if unit_number is None:
                continue

            # Check if it's already a number (Decimal in DynamoDB)
            if isinstance(unit_number, (int, float)):
                continue

            # It's a string, try to convert
            if isinstance(unit_number, str):
                numeric_value = extract_numeric_unit_number(unit_number)

                if numeric_value is not None:
                    needs_migration += 1
                    print(f"Account {account_id}: '{unit_number}' -> {numeric_value}")

                    if apply:
                        try:
                            dynamodb_client.update_item(
                                TableName=table_name,
                                Key={"accountId": {"S": account_id}},
                                UpdateExpression="SET unitNumber = :num",
                                ExpressionAttributeValues={":num": {"N": str(numeric_value)}},
                            )
                            migrated += 1
                            print(f"  ✓ Migrated")
                        except ClientError as e:
                            print(f"  ✗ Error: {e}")
                    else:
                        print(f"  (dry-run, not applied)")
                else:
                    print(
                        f"Account {account_id}: Cannot convert '{unit_number}' to number - SKIPPED"
                    )

        # Check if there are more items to scan
        if "LastEvaluatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

    return total_scanned, needs_migration, migrated


def migrate_profiles_table(
    table_name: str, apply: bool, dynamodb_client: Any
) -> tuple[int, int, int]:
    """
    Migrate profiles table unitNumber fields.

    Returns:
        Tuple of (total_scanned, needs_migration, migrated)
    """
    print(f"\n{'='*80}")
    print(f"Scanning profiles table: {table_name}")
    print(f"{'='*80}\n")

    table = boto3.resource("dynamodb").Table(table_name)

    total_scanned = 0
    needs_migration = 0
    migrated = 0

    # Scan for all profiles
    scan_kwargs = {}

    while True:
        response = table.scan(**scan_kwargs)
        items = response.get("Items", [])
        total_scanned += len(items)

        for item in items:
            owner_account_id = item.get("ownerAccountId", "UNKNOWN")
            profile_id = item.get("profileId", "UNKNOWN")
            unit_number = item.get("unitNumber")

            if unit_number is None:
                continue

            # Check if it's already a number (Decimal in DynamoDB)
            if isinstance(unit_number, (int, float)):
                continue

            # It's a string, try to convert
            if isinstance(unit_number, str):
                numeric_value = extract_numeric_unit_number(unit_number)

                if numeric_value is not None:
                    needs_migration += 1
                    print(f"Profile {profile_id}: '{unit_number}' -> {numeric_value}")

                    if apply:
                        try:
                            dynamodb_client.update_item(
                                TableName=table_name,
                                Key={
                                    "ownerAccountId": {"S": owner_account_id},
                                    "profileId": {"S": profile_id},
                                },
                                UpdateExpression="SET unitNumber = :num",
                                ExpressionAttributeValues={":num": {"N": str(numeric_value)}},
                            )
                            migrated += 1
                            print(f"  ✓ Migrated")
                        except ClientError as e:
                            print(f"  ✗ Error: {e}")
                    else:
                        print(f"  (dry-run, not applied)")
                else:
                    print(
                        f"Profile {profile_id}: Cannot convert '{unit_number}' to number - SKIPPED"
                    )

        # Check if there are more items to scan
        if "LastEvaluatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

    return total_scanned, needs_migration, migrated


def main() -> None:
    """Main migration logic."""
    args = parse_args()

    # Table names
    accounts_table = f"kernelworx-accounts-ue1-{args.env}"
    profiles_table = f"kernelworx-profiles-v2-ue1-{args.env}"

    print(f"\nUnit Number Migration Script")
    print(f"Environment: {args.env}")
    print(f"Mode: {'APPLY CHANGES' if args.apply else 'DRY RUN (no changes)'}")

    dynamodb_client = boto3.client("dynamodb")

    # Migrate accounts
    try:
        accounts_total, accounts_need, accounts_migrated = migrate_accounts_table(
            accounts_table, args.apply, dynamodb_client
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"\n⚠️  Accounts table {accounts_table} not found - skipping")
            accounts_total = accounts_need = accounts_migrated = 0
        else:
            raise
    
    # Migrate profiles
    try:
        profiles_total, profiles_need, profiles_migrated = migrate_profiles_table(
            profiles_table, args.apply, dynamodb_client
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"\n⚠️  Profiles table {profiles_table} not found - skipping")
            profiles_total = profiles_need = profiles_migrated = 0
        else:
            raise
    # Summary
    print(f"\n{'='*80}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*80}\n")
    print(f"Accounts table ({accounts_table}):")
    print(f"  Total scanned: {accounts_total}")
    print(f"  Need migration: {accounts_need}")
    if args.apply:
        print(f"  Migrated: {accounts_migrated}")

    print(f"\nProfiles table ({profiles_table}):")
    print(f"  Total scanned: {profiles_total}")
    print(f"  Need migration: {profiles_need}")
    if args.apply:
        print(f"  Migrated: {profiles_migrated}")

    if not args.apply and (accounts_need > 0 or profiles_need > 0):
        print(f"\n⚠️  This was a DRY RUN. To apply changes, run with --apply flag")
        print(f"   Example: uv run python scripts/migrate_unit_numbers.py --env {args.env} --apply")
    elif args.apply:
        print(f"\n✓ Migration complete!")
    else:
        print(f"\n✓ No records need migration")


if __name__ == "__main__":
    main()
