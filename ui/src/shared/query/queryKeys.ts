/**
 * Central hierarchical query-key factory. Kept in one place (not split per slice)
 * so cross-feature, prefix-based invalidation works: invalidating a parent key
 * matches all children.
 *
 * Convention: shape keys as `domain → entity → action(params)` and put any
 * params object LAST in the tuple so different filters cache independently, e.g.
 *   list: (brandId: string, params?: Filters) =>
 *     ['things', brandId, 'list', params] as const
 */
export const queryKeys = {
  health: {
    all: ['health'] as const,
    ready: () => ['health', 'ready'] as const,
  },
} as const;
