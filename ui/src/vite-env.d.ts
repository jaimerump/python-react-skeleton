/// <reference types="vite/client" />

// Build-time flag defined in vite.config.ts / vitest.config.ts. Gates the test
// auth provider so the unused branch is dead-code-eliminated in prod.
declare const __TEST_AUTH_ENABLED__: boolean;

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_PROXY_TARGET?: string;
  readonly VITE_TEST_AUTH?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
