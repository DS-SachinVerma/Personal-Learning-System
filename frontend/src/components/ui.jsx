import { Link } from 'react-router-dom';

export function Loading({ what = 'Loading…' }) {
  return <p className="muted pad">{what}</p>;
}

export function Empty({ children }) {
  return <p className="muted pad">{children}</p>;
}

export function Badge({ kind, children }) {
  return <span className={`badge badge--${kind || 'default'}`}>{children}</span>;
}

const MATURITY = { experimental: 'exp', emerging: 'new', proven: 'ok', legacy: 'old' };

export function MaturityBadge({ value }) {
  if (!value) return null;
  return <span className={`badge badge--maturity maturity--${value}`}>{value}</span>;
}

export function SourceBadge({ value }) {
  if (!value) return null;
  return <span className={`badge badge--source source--${value}`}>{value}</span>;
}

export function TypeBadge({ value }) {
  if (!value) return null;
  return <span className="badge badge--type">{value}</span>;
}

export function Tags({ value }) {
  if (!value) return null;
  const list = value.split(',').map((t) => t.trim()).filter(Boolean);
  if (!list.length) return null;
  return (
    <span className="tags">
      {list.map((t) => (
        <span className="tag" key={t}>#{t}</span>
      ))}
    </span>
  );
}

export function TechChip({ tech }) {
  return (
    <Link className="chip chip--tech" to={`/techniques/${tech.id}`}>
      {tech.name}
      {tech.maturity ? <span className="chip-sub">{tech.maturity}</span> : null}
    </Link>
  );
}

export function TaskChip({ task }) {
  return (
    <Link className="chip chip--task" to={`/tasks/${task.slug || task.id}`}>
      {task.name}
    </Link>
  );
}

export function ResourceChip({ resource }) {
  return (
    <Link className="chip chip--res" to={`/resources/${resource.id}`}>
      {resource.title}
    </Link>
  );
}

export function fmtDate(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return iso;
  }
}
