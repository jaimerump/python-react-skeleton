/**
 * Placeholder login screen. `ProtectedRoute` redirects here when logged out.
 * Wire this to the real auth vendor (§8) once one is chosen.
 */
export function LoginPage() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 p-8 text-center">
      <h1 className="text-xl font-semibold">Sign in</h1>
      <p className="text-sm text-muted-foreground">Authentication is not configured yet.</p>
    </div>
  );
}
