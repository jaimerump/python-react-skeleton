import { Link, Outlet } from 'react-router-dom';

import { useTheme } from '@/shared/theme/ThemeProvider';
import { Button } from '@/shared/ui/button';

/** The app shell: a thin header + the routed content. No business logic. */
export function AppLayout() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <Link to="/" className="font-semibold">
          app
        </Link>
        <Button variant="ghost" size="sm" onClick={toggleTheme}>
          {theme === 'dark' ? 'Light' : 'Dark'}
        </Button>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
