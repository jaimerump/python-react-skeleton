import { Toaster as SonnerToaster } from 'sonner';

import { useTheme } from '@/shared/theme/ThemeProvider';

/**
 * Single toast surface, mounted once in the provider tree. Everywhere else,
 * `import { toast } from 'sonner'` and call `toast.success/error`.
 */
export function Toaster() {
  const { theme } = useTheme();
  return <SonnerToaster theme={theme} position="bottom-right" richColors closeButton />;
}
