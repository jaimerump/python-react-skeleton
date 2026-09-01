import js from '@eslint/js';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'playwright-report', 'test-results'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: { ...globals.browser, __TEST_AUTH_ENABLED__: 'readonly' },
    },
  },
  // React-specific rules apply to the app source only, not the Playwright e2e/ code.
  {
    files: ['src/**/*.{ts,tsx}'],
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },

  // --- Architecture boundary contract (the JS analog of import-linter) ---
  // shared/ is domain-agnostic: it must never depend on features or the app shell.
  {
    files: ['src/shared/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            { group: ['@/features/*', '@/app/*'], message: 'shared/ must not import from features/ or app/.' },
          ],
        },
      ],
    },
  },
  // A feature may import shared/ and its own slice (via relative paths), and may
  // depend on ANOTHER feature only through its public barrel (@/features/<name>),
  // never its internals (@/features/<name>/<file>). It must not import app/.
  {
    files: ['src/features/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            { group: ['@/app/*'], message: 'A feature must not import from the app/ shell.' },
            {
              group: ['@/features/*/*'],
              message: 'Import another feature only via its public barrel (@/features/<name>), never its internals.',
            },
          ],
        },
      ],
    },
  },
);
