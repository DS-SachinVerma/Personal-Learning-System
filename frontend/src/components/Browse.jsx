import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getTasks } from '../api';
import { Loading, Empty } from './ui';

export default function Browse() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [params, setParams] = useSearchParams();
  const domainFilter = params.get('domain') || '';

  useEffect(() => {
    getTasks().then(setTasks).finally(() => setLoading(false));
  }, []);

  const grouped = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const byDomain = {};
    for (const t of tasks) {
      if (domainFilter && t.domain !== domainFilter) continue;
      if (needle && !(`${t.name} ${t.one_liner || ''}`.toLowerCase().includes(needle))) continue;
      (byDomain[t.domain || 'Uncategorized'] ||= []).push(t);
    }
    return Object.entries(byDomain).sort(([a], [b]) => a.localeCompare(b));
  }, [tasks, q, domainFilter]);

  if (loading) return <Loading what="Loading tasks…" />;

  return (
    <div className="wrap">
      <h1 className="page-title">Browse tasks</h1>
      <div className="toolbar">
        <input
          className="search"
          placeholder="Search tasks…  (e.g. forecasting, RAG, anomaly)"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        {domainFilter ? (
          <button className="pill pill--clear" onClick={() => setParams({})}>
            {domainFilter} ✕
          </button>
        ) : null}
      </div>

      {grouped.length === 0 ? (
        <Empty>No tasks match.</Empty>
      ) : (
        grouped.map(([domain, items]) => (
          <section key={domain} className="domain-block">
            <h2 className="domain-title">
              {domain} <span className="muted small">· {items.length}</span>
            </h2>
            <div className="task-grid">
              {items.map((t) => (
                <Link key={t.id} to={`/tasks/${t.slug || t.id}`} className="task-card">
                  <span className="task-card-name">{t.name}</span>
                  <span className="task-card-line">{t.one_liner}</span>
                  <span className="task-card-counts">
                    {t.technique_count} techniques · {t.resource_count} sources
                    {t.experiment_count ? ` · ${t.experiment_count} benchmarks` : ''}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  );
}
