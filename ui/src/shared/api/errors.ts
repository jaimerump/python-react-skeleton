/**
 * Stable, machine-readable error codes mirrored from the backend
 * (`app/api/schemas/base.py: ErrorCode`). Branch on these, not on messages.
 */
export type ApiErrorCode =
  | 'internal_error'
  | 'not_found'
  | 'conflict'
  | 'validation_error'
  | 'unauthorized'
  | 'forbidden'
  | (string & {}); // allow forward-compatible codes without losing autocomplete

/** Normalized API failure. The backend's varied error shapes flatten into this. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: ApiErrorCode,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Thrown when a request exceeds its timeout (distinct from a network abort). */
export class ApiTimeoutError extends Error {
  constructor(message = 'The request timed out.') {
    super(message);
    this.name = 'ApiTimeoutError';
  }
}

/** Extract a human-readable message from any thrown value, with a fallback. */
export function errorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
