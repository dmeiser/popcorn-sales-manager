/**
 * Global setup/teardown for integration tests.
 * 
 * This file runs ONCE before all tests start and the returned function runs ONCE after all tests complete.
 * It's used to clean up test accounts that are created by the Cognito post-auth trigger.
 */

import { DynamoDBClient, ScanCommand, DeleteItemCommand } from '@aws-sdk/client-dynamodb';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load .env from project root
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const dynamoClient = new DynamoDBClient({ region: 'us-east-1' });
const tableName = process.env.TABLE_NAME || 'kernelworx-app-dev';

/**
 * Global setup - runs before all tests.
 * Returns a teardown function that runs after all tests.
 */
export default async function globalSetup(): Promise<() => Promise<void>> {
  console.log('\n🚀 Global integration test setup starting...');
  console.log(`   Table: ${tableName}`);
  
  // Check initial table state
  const scanCommand = new ScanCommand({
    TableName: tableName,
    Select: 'COUNT',
  });
  const result = await dynamoClient.send(scanCommand);
  console.log(`   Initial record count: ${result.Count}`);
  console.log('✅ Global setup complete.\n');
  
  // Return teardown function
  return async function teardown(): Promise<void> {
    console.log('\n🧹 Global integration test teardown starting...');
    
    // Scan and delete ALL remaining records
    let totalDeleted = 0;
    let hasMoreItems = true;
    let lastEvaluatedKey: Record<string, any> | undefined;
    
    while (hasMoreItems) {
      const result = await dynamoClient.send(new ScanCommand({
        TableName: tableName,
        ProjectionExpression: 'PK, SK',
        ExclusiveStartKey: lastEvaluatedKey,
      }));
      
      if (result.Items && result.Items.length > 0) {
        for (const item of result.Items) {
          const pk = item.PK?.S;
          const sk = item.SK?.S;
          
          if (pk && sk) {
            await dynamoClient.send(new DeleteItemCommand({
              TableName: tableName,
              Key: {
                PK: { S: pk },
                SK: { S: sk },
              },
            }));
            totalDeleted++;
          }
        }
      }
      
      lastEvaluatedKey = result.LastEvaluatedKey;
      hasMoreItems = !!lastEvaluatedKey;
    }
    
    console.log(`   Deleted ${totalDeleted} records.`);
    
    // Verify table is empty
    const verifyResult = await dynamoClient.send(new ScanCommand({
      TableName: tableName,
      Select: 'COUNT',
    }));
    
    if (verifyResult.Count === 0) {
      console.log('✅ Table is now empty. Global teardown complete.\n');
    } else {
      console.log(`⚠️  Warning: ${verifyResult.Count} records remain in table.\n`);
    }
  };
}
