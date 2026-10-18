import { Icon } from "./Icon";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return <div className="async-state" role="status"><span className="spinner" />{label}</div>;
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="async-state async-state--error" role="alert">
      <Icon name="warning" />
      <p>{message}</p>
      {onRetry ? <button className="button button--outline button--small" onClick={onRetry}>Try again</button> : null}
    </div>
  );
}

export function EmptyState({ title, message, action }: { title: string; message: string; action?: React.ReactNode }) {
  return (
    <div className="empty-state">
      <span className="empty-state__icon"><Icon name="leaf" /></span>
      <h2>{title}</h2>
      <p>{message}</p>
      {action}
    </div>
  );
}
