import type { ComponentType, ReactNode } from 'react';

type EmptyStateProps = {
  Icon: ComponentType<{ className?: string }>;
  message: string;
  /** At most one action: the next step (« Réserver un trajet »). */
  children?: ReactNode;
};

/** An empty list: a drawing, a sentence that says so, and what to do next.
 *  The icon decorates, the sentence says it. */
export function EmptyState({ Icon, message, children }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <span className="icon-chip">
        <Icon />
      </span>
      <p>{message}</p>
      {children}
    </div>
  );
}
