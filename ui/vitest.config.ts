import { fileURLToPath, URL } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// https://vitest.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    // Tests exercise the test auth provider.
    __TEST_AUTH_ENABLED__: JSON.stringify(true),
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    // Isolated, heap-limited workers keep a memory-heavy suite from ballooning.
    pool: 'forks',
    exclude: ['**/node_modules/**', '**/e2e/**'],
  },
});
