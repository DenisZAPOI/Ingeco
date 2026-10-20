import { useCallback, useState } from 'react';

import { errorMessage } from '../lib/errorMessage';
import { fieldErrors, type FieldErrors } from '../lib/fieldErrors';

/** Sending a form: submitting state, general message and messages per field. */
export function useSubmit<Data, Result>(send: (data: Data) => Promise<Result>) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<FieldErrors>({});

  const submit = useCallback(
    async (data: Data): Promise<Result | null> => {
      setSubmitting(true);
      setError(null);
      setErrors({});
      try {
        return await send(data);
      } catch (caught) {
        setError(errorMessage(caught));
        setErrors(fieldErrors(caught));
        return null;
      } finally {
        setSubmitting(false);
      }
    },
    [send],
  );

  return { submit, submitting, error, errors };
}
