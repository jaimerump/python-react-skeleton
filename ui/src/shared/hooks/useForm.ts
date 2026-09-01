import { useCallback, useMemo, useState } from 'react';

/**
 * Lightweight form state for simple cases (no schema validation). For validated
 * forms, prefer react-hook-form + zod via `shared/ui/form.tsx`.
 */
export function useForm<T extends Record<string, unknown>>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});

  const setField = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
  }, [initialValues]);

  const isDirty = useMemo(
    () => (Object.keys(initialValues) as (keyof T)[]).some((k) => values[k] !== initialValues[k]),
    [values, initialValues],
  );

  return { values, setField, setValues, errors, setErrors, resetForm, isDirty };
}
