import { ApiError, ApiTimeoutError, type ApiErrorCode } from './errors';

/**
 * Tier 1 of the API layer: the single fetch wrapper every domain module goes
 * through. Centralizes base URL, auth token, CSRF echo, timeout, 401 handling,
 * and error normalization so no feature re-implements them.
 */

// In dev VITE_API_URL is empty → base is '/api', which the Vite proxy forwards
// to the backend (stripping the prefix). In prod, point VITE_API_URL at the origin.
const API_URL = (import.meta.env.VITE_API_URL ?? '') + '/api';

const DEFAULT_TIMEOUT_MS = 30_000;
const CSRF_COOKIE = 'csrftoken'; // matches app/api/middleware/csrf.py
const CSRF_HEADER = 'X-CSRF-Token';

/** Event the auth layer listens for to trigger auto-logout. */
export const SESSION_EXPIRED_EVENT = 'app:session-expired';

/**
 * The non-React bridge: AuthProvider registers a token provider so this module
 * (which is not a hook) can read a fresh access token and refresh on 401.
 */
export interface TokenProvider {
  getToken: () => string | null;
  refreshToken: () => Promise<string | null>;
}

let tokenProvider: TokenProvider | null = null;

export function registerTokenProvider(provider: TokenProvider | null): void {
  tokenProvider = provider;
}

export interface FetchOptions extends Omit<RequestInit, 'body'> {
  body?: BodyInit | null;
  /** Per-request timeout override (ms). */
  timeoutMs?: number;
  /** Internal: prevents infinite 401-refresh recursion. */
  _retried?: boolean;
}

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE']);

function readCookie(name: string): string | undefined {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1];
}

function buildHeaders(method: string, token: string | null, provided?: HeadersInit): Headers {
  const headers = new Headers(provided);
  if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  // Double-submit CSRF: echo the cookie on state-changing requests (§5).
  if (!SAFE_METHODS.has(method.toUpperCase())) {
    const csrf = readCookie(CSRF_COOKIE);
    if (csrf) headers.set(CSRF_HEADER, csrf);
  }
  return headers;
}

/** Flatten the backend's varied error shapes into one message + optional code. */
async function normalizeError(response: Response): Promise<ApiError> {
  let message = response.statusText || 'Request failed';
  let code: ApiErrorCode | undefined;

  try {
    const data = await response.json();
    const detail = data?.detail;
    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail)) {
      // FastAPI 422 validation shape: [{ loc, msg, type }, ...]
      code = 'validation_error';
      message = detail.map((d: { msg?: string }) => d?.msg).filter(Boolean).join(', ') || message;
    } else if (detail && typeof detail === 'object') {
      // Typed shape: { message, error_code }
      message = detail.message ?? message;
      code = detail.error_code ?? code;
    }
  } catch {
    // Non-JSON body — keep the statusText fallback.
  }

  return new ApiError(response.status, message, code);
}

async function rawFetch(path: string, options: FetchOptions, token: string | null): Promise<Response> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, method = 'GET', ...rest } = options;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(`${API_URL}${path}`, {
      ...rest,
      method,
      headers: buildHeaders(method, token, headers),
      credentials: 'include',
      signal: options.signal ?? controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError' && !options.signal) {
      throw new ApiTimeoutError();
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

/** Core typed request. Returns `undefined` for 204. */
export async function fetchApi<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const token = tokenProvider?.getToken() ?? null;
  let response = await rawFetch(path, options, token);

  // 401: refresh the token once and retry; if still 401, signal session expiry.
  if (response.status === 401 && !options._retried && tokenProvider) {
    const fresh = await tokenProvider.refreshToken();
    if (fresh) {
      response = await rawFetch(path, { ...options, _retried: true }, fresh);
    }
    if (response.status === 401) {
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    }
  }

  if (!response.ok) throw await normalizeError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Blob variant for downloads. */
export async function fetchBlob(path: string, options: FetchOptions = {}): Promise<Blob> {
  const token = tokenProvider?.getToken() ?? null;
  const response = await rawFetch(path, options, token);
  if (!response.ok) throw await normalizeError(response);
  return response.blob();
}
