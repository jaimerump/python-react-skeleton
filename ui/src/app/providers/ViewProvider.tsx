import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

/**
 * App-state context example (§6): a view mode that isn't server data. Persists to
 * localStorage. A real app might force a default from the user's role; kept simple
 * here as the pattern to copy for selected-entity / view-mode contexts.
 */
export type View = 'default' | 'admin';

interface ViewContextType {
  currentView: View;
  setView: (view: View) => void;
}

const ViewContext = createContext<ViewContextType | undefined>(undefined);

const STORAGE_KEY = 'app:view';

export function ViewProvider({ children }: { children: ReactNode }) {
  const [currentView, setCurrentView] = useState<View>(
    () => (localStorage.getItem(STORAGE_KEY) as View) || 'default',
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, currentView);
  }, [currentView]);

  const value = useMemo<ViewContextType>(
    () => ({ currentView, setView: setCurrentView }),
    [currentView],
  );

  return <ViewContext.Provider value={value}>{children}</ViewContext.Provider>;
}

export function useView(): ViewContextType {
  const ctx = useContext(ViewContext);
  if (!ctx) throw new Error('useView must be used within a ViewProvider');
  return ctx;
}
