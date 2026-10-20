import type { ReactNode } from 'react';

import { ErrorAlert } from './ErrorAlert';
import { LoadingMessage } from './LoadingMessage';

type RequestStateProps = {
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  children: ReactNode;
};

/** Loading state, error state with a retry button, or the content. */
export function RequestState({ loading, error, onRetry, children }: RequestStateProps) {
  if (loading) {
    return <LoadingMessage />;
  }
  if (error) {
    return <ErrorAlert message={error} onRetry={onRetry} />;
  }
  return children;
}
