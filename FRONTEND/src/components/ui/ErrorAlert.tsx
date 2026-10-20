type ErrorAlertProps = {
  message: string;
  onRetry: () => void;
};

/** Failure of a call, with the button that makes it again. */
export function ErrorAlert({ message, onRetry }: ErrorAlertProps) {
  return (
    <div role="alert" className="alert alert-error">
      <p>{message}</p>
      <button type="button" className="button" onClick={onRetry}>
        Réessayer
      </button>
    </div>
  );
}
