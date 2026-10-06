import type { ReactNode } from 'react';

type RequestStateProps = {
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  children: ReactNode;
};

/** Loading state, error state with a retry button, or the content. */
export function RequestState({ loading, error, onRetry, children }: RequestStateProps) {
  if (loading) {
    return <p role="status">Chargement…</p>;
  }
  if (error) {
    return (
      <div role="alert" className="request-error">
        <p>{error}</p>
        <button type="button" className="button" onClick={onRetry}>
          Réessayer
        </button>
      </div>
    );
  }
  return children;
}
