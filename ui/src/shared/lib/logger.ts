/**
 * Thin logging seam. Today it wraps `console`; swap the body for a real reporter
 * (Sentry, etc.) without touching call sites. Bootstrap init lives in main.tsx.
 */
export const logger = {
  debug: (...args: unknown[]) => console.debug(...args),
  info: (...args: unknown[]) => console.info(...args),
  warn: (...args: unknown[]) => console.warn(...args),
  error: (...args: unknown[]) => console.error(...args),
};

/** Called once from main.tsx. No-op until a monitoring vendor is wired in. */
export function initErrorReporting(): void {
  // TODO: initialize Sentry / FullStory here (§10 seam). No-op for now.
}
