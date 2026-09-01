import {
  createContext,
  useContext,
  type HTMLAttributes,
  type LabelHTMLAttributes,
} from 'react';
import {
  Controller,
  FormProvider,
  useFormContext,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from 'react-hook-form';

import { cn } from '@/shared/lib/cn';

/**
 * Thin wrapper over react-hook-form (pair with a zod resolver via
 * `@hookform/resolvers/zod`) for validated forms. For trivial local state, use
 * `shared/hooks/useForm.ts` instead.
 */
export const Form = FormProvider;

const FieldNameContext = createContext<string>('');

export function FormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>(props: ControllerProps<TFieldValues, TName>) {
  return (
    <FieldNameContext.Provider value={props.name}>
      <Controller {...props} />
    </FieldNameContext.Provider>
  );
}

export function FormItem({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('space-y-2', className)} {...props} />;
}

export function FormLabel({ className, ...props }: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={cn('text-sm font-medium leading-none', className)} {...props} />;
}

/** Renders the active field's validation error from form state, if any. */
export function FormMessage({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  const name = useContext(FieldNameContext);
  const { formState } = useFormContext();
  const error = name ? formState.errors[name] : undefined;
  const message = error?.message ? String(error.message) : props.children;
  if (!message) return null;
  return (
    <p className={cn('text-sm font-medium text-destructive', className)} {...props}>
      {message}
    </p>
  );
}
