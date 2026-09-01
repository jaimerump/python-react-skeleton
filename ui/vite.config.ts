import { fileURLToPath, URL } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isProd = mode === 'production';

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    define: {
      // Build-time flag: enables the test auth provider. False in prod so the
      // real branch is the only one that survives dead-code elimination.
      __TEST_AUTH_ENABLED__: JSON.stringify(env.VITE_TEST_AUTH === 'true' && !isProd),
    },
    server: {
      port: 5173,
      proxy: {
        // The backend serves routes at root (/health, /ready); the frontend
        // fetch wrapper uses an /api base, so strip the prefix when proxying.
        '/api': {
          target: env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    esbuild: {
      drop: isProd ? ['console', 'debugger'] : [],
    },
    build: {
      rollupOptions: {
        output: {
          // Manual vendor chunk splitting to control bundle size.
          manualChunks: {
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            'vendor-tanstack': ['@tanstack/react-query'],
            'vendor-ui': ['@radix-ui/react-tooltip', 'sonner', 'lucide-react'],
          },
        },
      },
    },
  };
});
