import { createContext, useContext, type ReactNode } from 'react';

/**
 * Feature-flag seam (⇄ swappable: LaunchDarkly, etc.). This is a no-op default:
 * every flag is off. Swap the provider body for a real client and keep `useFlag`
 * as the stable call site. Sits outermost in the provider tree.
 */
type Flags = Record<string, boolean>;

const FlagContext = createContext<Flags>({});

export function FeatureFlagProvider({
  children,
  flags = {},
}: {
  children: ReactNode;
  flags?: Flags;
}) {
  return <FlagContext.Provider value={flags}>{children}</FlagContext.Provider>;
}

export function useFlag(key: string, defaultValue = false): boolean {
  const flags = useContext(FlagContext);
  return flags[key] ?? defaultValue;
}
