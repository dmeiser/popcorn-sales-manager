#!/usr/bin/env python3
"""
One-time migration: Ensure all shares have required ownerAccountId field.

This script scans the shares table and backfills ownerAccountId for any shares
that are missing it by querying the profiles table.
"""

import boto3
import sys

def main():
    env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    
    shares_table_name = f'kernelworx-shares-ue1-{env}'
    profiles_table_name = f'kernelworx-profiles-ue1-{env}'
    
    print(f"Migrating shares in {shares_table_name}")
    
    dynamodb = boto3.resource('dynamodb')
    dynamodb_client = boto3.client('dynamodb')
    
    shares_table = dynamodb.Table(shares_table_name)
    
    # Scan all shares
    response = shares_table.scan()
    shares = response.get('Items', [])
    
    while 'LastEvaluatedKey' in response:
        response = shares_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        shares.extend(response.get('Items', []))
    
    print(f"Found {len(shares)} shares")
    
    fixed_count = 0
    deleted_count = 0
    
    for share in shares:
        profile_id = share.get('profileId')
        target_account_id = share.get('targetAccountId')
        owner_account_id = share.get('ownerAccountId')
        
        # Skip if missing primary keys
        if not profile_id or not target_account_id:
            print(f"  WARNING: Share missing primary keys, deleting: {share}")
            # Can't delete without keys
            continue
        
        # Check if ownerAccountId is missing
        if not owner_account_id:
            print(f"  Backfilling ownerAccountId for profileId={profile_id}")
            
            # Query profiles table to get ownerAccountId
            try:
                prof_response = dynamodb_client.query(
                    TableName=profiles_table_name,
                    IndexName='profileId-index',
                    KeyConditionExpression='profileId = :pid',
                    ExpressionAttributeValues={':pid': {'S': profile_id}},
                    Limit=1
                )
                
                if prof_response['Items']:
                    owner_id = prof_response['Items'][0]['ownerAccountId']['S']
                    
                    # Update the share
                    shares_table.update_item(
                        Key={'profileId': profile_id, 'targetAccountId': target_account_id},
                        UpdateExpression='SET ownerAccountId = :owner',
                        ExpressionAttributeValues={':owner': owner_id}
                    )
                    print(f"    ✓ Set ownerAccountId={owner_id}")
                    fixed_count += 1
                else:
                    print(f"    ✗ Profile not found, deleting share")
                    shares_table.delete_item(Key={'profileId': profile_id, 'targetAccountId': target_account_id})
                    deleted_count += 1
                    
            except Exception as e:
                print(f"    ERROR: {e}")
    
    print(f"\n✅ Migration complete: {fixed_count} fixed, {deleted_count} deleted")

if __name__ == '__main__':
    main()
