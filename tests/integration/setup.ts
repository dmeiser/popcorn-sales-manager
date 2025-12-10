/**
 * Setup file for integration tests.
 * Loads environment variables and validates required config.
 */

// Validate required environment variables
const requiredEnvVars = [
  'TEST_USER_POOL_ID',
  'TEST_USER_POOL_CLIENT_ID',
  'TEST_APPSYNC_ENDPOINT',
  'TEST_OWNER_EMAIL',
  'TEST_OWNER_PASSWORD',
  'TEST_CONTRIBUTOR_EMAIL',
  'TEST_CONTRIBUTOR_PASSWORD',
  'TEST_READONLY_EMAIL',
  'TEST_READONLY_PASSWORD',
];

const missing = requiredEnvVars.filter((varName) => !process.env[varName]);

if (missing.length > 0) {
  console.error('❌ Missing required environment variables:');
  missing.forEach((varName) => console.error(`   - ${varName}`));
  console.error('\nPlease check your .env file at the project root.');
  process.exit(1);
}

console.log('✅ Integration test environment configured');
console.log(`   AppSync: ${process.env.TEST_APPSYNC_ENDPOINT}`);
console.log(`   User Pool: ${process.env.TEST_USER_POOL_ID}`);
