/// <reference types="vitest" />
import { defineConfig } from 'vite';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load .env from project root
dotenv.config({ path: path.resolve(__dirname, '../.env') });

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['../tests/integration/**/*.test.ts'],
    testTimeout: 30000, // 30 seconds for API calls
    hookTimeout: 30000,
    setupFiles: ['../tests/integration/setup.ts'],
  },
});
