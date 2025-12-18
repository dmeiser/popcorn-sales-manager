#!/usr/bin/env python3
"""
Validate and fix shares in the DynamoDB shares table.

This script:
1. Scans all shares in the shares table
2. Identifies shares with missing ownerAccountId or profileId
3. Attempts to backfill ownerAccountId from the profiles table
4. Deletes shares that cannot be fixed

Usage:
    python scripts/validate_and_fix_shares.py --env dev [--fix]
"""

import argparse
import sys
import boto3
from typing import Dict, List, Any


def scan_shares(table_name: str) -> List[Dict[str, Any]]:
    """Scan all shares from the shares table."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print(f"Scanning shares table: {table_name}")
    shares = []
    
    response = table.scan()
    shares.extend(response.get('Items', []))
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        shares.extend(response.get('Items', []))
    
    print(f"Found {len(shares)} total shares")
    return shares


def get_profile_owner(profiles_table_name: str, profile_id: str) -> str | None:
    """Query profiles table GSI to find ownerAccountId for a profileId."""
    dynamodb = boto3.client('dynamodb')
    
    try:
        response = dynamodb.query(
            TableName=profiles_table_name,
            IndexName='profileId-index',
            KeyConditionExpression='profileId = :profileId',
            ExpressionAttributeValues={
                ':profileId': {'S': profile_id}
            },
            Limit=1
        )
        
        items = response.get('Items', [])
        if items and 'ownerAccountId' in items[0]:
            return items[0]['ownerAccountId']['S']
    except Exception as e:
        print(f"  Error querying profiles table: {e}")
    
    return None


def validate_and_fix_shares(
    shares_table_name: str,
    profiles_table_name: str,
    shares: List[Dict[str, Any]],
    fix: bool = False
) -> None:
    """Validate shares and optionally fix them."""
    
    invalid_shares = []
    fixable_shares = []
    
    for share in shares:
        profile_id = share.get('profileId')
        target_account_id = share.get('targetAccountId')
        owner_account_id = share.get('ownerAccountId')
        
        # Check for missing required fields
        if not profile_id or not target_account_id:
            print(f"❌ Share missing required keys: {share}")
            invalid_shares.append(share)
            continue
        
        # Check for missing ownerAccountId
        if not owner_account_id:
            print(f"⚠️  Share missing ownerAccountId: profileId={profile_id}, targetAccountId={target_account_id}")
            
            # Try to backfill from profiles table
            owner = get_profile_owner(profiles_table_name, profile_id)
            if owner:
                print(f"  ✓ Found ownerAccountId from profiles table: {owner}")
                fixable_shares.append({
                    'share': share,
                    'ownerAccountId': owner
                })
            else:
                print(f"  ✗ Could not find ownerAccountId - profile may not exist")
                invalid_shares.append(share)
    
    print("\n" + "="*80)
    print(f"Validation complete:")
    print(f"  Total shares: {len(shares)}")
    print(f"  Valid shares: {len(shares) - len(invalid_shares) - len(fixable_shares)}")
    print(f"  Fixable shares (missing ownerAccountId): {len(fixable_shares)}")
    print(f"  Invalid shares (cannot fix): {len(invalid_shares)}")
    print("="*80 + "\n")
    
    if not fix:
        print("Run with --fix to apply fixes")
        return
    
    # Fix shares
    dynamodb = boto3.resource('dynamodb')
    shares_table = dynamodb.Table(shares_table_name)
    
    if fixable_shares:
        print(f"\nFixing {len(fixable_shares)} shares...")
        for item in fixable_shares:
            share = item['share']
            owner_account_id = item['ownerAccountId']
            
            try:
                shares_table.update_item(
                    Key={
                        'profileId': share['profileId'],
                        'targetAccountId': share['targetAccountId']
                    },
                    UpdateExpression='SET ownerAccountId = :owner',
                    ExpressionAttributeValues={
                        ':owner': owner_account_id
                    }
                )
                print(f"  ✓ Fixed share: profileId={share['profileId']}, targetAccountId={share['targetAccountId']}")
            except Exception as e:
                print(f"  ✗ Error fixing share: {e}")
    
    # Delete invalid shares
    if invalid_shares:
        print(f"\nDeleting {len(invalid_shares)} invalid shares...")
        for share in invalid_shares:
            if not share.get('profileId') or not share.get('targetAccountId'):
                print(f"  ⚠️  Cannot delete share with missing keys: {share}")
                continue
            
            try:
                shares_table.delete_item(
                    Key={
                        'profileId': share['profileId'],
                        'targetAccountId': share['targetAccountId']
                    }
                )
                print(f"  ✓ Deleted invalid share: profileId={share['profileId']}, targetAccountId={share['targetAccountId']}")
            except Exception as e:
                print(f"  ✗ Error deleting share: {e}")
    
    print("\n✅ Done!")


def main():
    parser = argparse.ArgumentParser(description='Validate and fix shares in DynamoDB')
    parser.add_argument('--env', required=True, choices=['dev', 'prod'], help='Environment')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: dry-run)')
    args = parser.parse_args()
    
    # Table names
    shares_table = f"kernelworx-shares-ue1-{args.env}"
    profiles_table = f"kernelworx-profiles-ue1-{args.env}"
    
    print(f"Environment: {args.env}")
    print(f"Shares table: {shares_table}")
    print(f"Profiles table: {profiles_table}")
    print(f"Mode: {'FIX' if args.fix else 'DRY-RUN'}")
    print()
    
    if args.fix:
        confirm = input("⚠️  This will modify the database. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Scan and validate shares
    shares = scan_shares(shares_table)
    validate_and_fix_shares(shares_table, profiles_table, shares, fix=args.fix)


if __name__ == '__main__':
    main()
