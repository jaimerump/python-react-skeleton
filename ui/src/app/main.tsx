import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { initErrorReporting, logger } from '@/shared/lib/logger';
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary';
import '@/shared/styles/index.css';

import { App } from './App';

// Bootstrap outside React: monitoring + global listeners.
initErrorReporting();

window.addEventListener('error', (event) => {
  // Recover from stale chunk references after a deploy by reloading once.
  if (/Loading chunk .* failed|dynamically imported module/i.test(event.message)) {
    window.location.reload();
    return;
  }
  logger.error('window.error', event.error ?? event.message);
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('unhandledrejection', event.reason);
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
