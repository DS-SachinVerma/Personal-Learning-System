import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { getResources } from '../api';
import { Loading, Empty, SourceBadge, TypeBadge, fmtDate } from './ui';

const TYPES = ['', 'paper', 'repo', 'blog', 'model', 'dataset', 'docs', 'video'];

export default function ResourceList({ mode = 'all' }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [type, setType] = useState('');

  useEffect(() => {
    setLoading(true);
    // Reading list = curated study-only sources, so we pull reviewed ones and
    // keep the ones with no task insights (below).
    const params =
      mode === 'intake' ? { status: 'intake' } :
      mode === 'reading' ? { status: 'reviewed' } : {};
    getResources(params).then(setItems).finally(() => setLoading(false));
  }, [mode]);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return items.filter((r) => {
      // study pile: reviewed sources with no *actionable* insight (study-only or untied)
      if (mode === 'reading' && r.insights?.some((i) => i.kind === 'use')) return false;
      if (type && r.type !== type) return false;
      if (needle && !(`${r.title} ${r.summary || ''} ${r.tags || ''} ${r.author || ''}`.toLowerCase().includes(needle))) return false;
      return true;
    });
  }, [items, q, type, mode]);

  if (loading) return <Loading what="Loading sources…" />;

  const intake = mode === 'intake';
  const reading = mode === 'reading';
  const heading = intake ? 'Intake queue' : reading ? 'Reading list' : 'Sources';
  const lead = intake
    ? 'Freshly collected — waiting to be summarized and filed into tasks.'
    : reading
    ? 'Study-worthy sources — background and theory, not tied to a specific job.'
    : 'Papers, repos, models, datasets and blogs behind our techniques.';

  return (
    <div className="wrap">
      <h1 className="page-title">{heading}</h1>
      <p className="muted lead">{lead}</p>

      <div className="toolbar">
        <input className="search" placeholder="Search sources…" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="select" value={type} onChange={(e) => setType(e.target.value)}>
          {TYPES.map((t) => <option key={t} value={t}>{t ? t : 'All types'}</option>)}
        </select>
      </div>

      {filtered.length === 0 ? (
        <Empty>{intake ? 'Intake is clear. 🎉' : 'No sources match.'}</Empty>
      ) : (
        <ul className="res-list">
          {filtered.map((r) => (
            <li key={r.id}>
              <Link to={`/resources/${r.id}`} className="res-row">
                <div className="res-row-main">
                  <span className="res-title">{r.title}</span>
                  <span className="res-meta">
                    <TypeBadge value={r.type} />
                    <SourceBadge value={r.source} />
                    {r.author ? <span className="muted small">{r.author}</span> : null}
                    {typeof r.stars === 'number' ? <span className="muted small">★ {r.stars.toLocaleString()}</span> : null}
                  </span>
                  {reading && r.insights?.some((i) => i.kind === 'study' && i.task) ? (
                    <span className="res-tasks">
                      <span className="muted small">read for:</span>
                      {r.insights.filter((i) => i.kind === 'study' && i.task).map((i) => (
                        <span key={i.id} className="mini-chip">{i.task.name}</span>
                      ))}
                    </span>
                  ) : null}
                </div>
                <div className="res-row-side">
                  {r.status === 'intake' ? <span className="badge badge--intake">intake</span> : null}
                  {r.insights?.length ? <span className="muted small">{r.insights.length} insights</span> : null}
                  <span className="muted small">{fmtDate(r.created_at)}</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
