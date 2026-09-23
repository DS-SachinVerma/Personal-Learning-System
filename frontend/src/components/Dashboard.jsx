import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDomains, getTasks, getTechniques, getResources, getDigest } from '../api';
import { Loading, Empty, fmtDate } from './ui';

const KIND_ICON = { added: '＋', updated: '✎', version: '⟳', insight: '◆', linked: '🔗' };

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [domains, setDomains] = useState([]);
  const [digest, setDigest] = useState([]);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDomains(), getTasks(), getTechniques(), getResources()])
      .then(([dom, tasks, techs, res]) => {
        setDomains(dom);
        setStats({
          tasks: tasks.length,
          techniques: techs.length,
          resources: res.length,
          intake: res.filter((r) => r.status === 'intake').length,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    getDigest({ days }).then(setDigest);
  }, [days]);

  if (loading) return <Loading what="Loading dashboard…" />;

  return (
    <div className="wrap">
      <h1 className="page-title">Dashboard</h1>
      <p className="muted lead">Your reference shelf — open the task that landed on your desk.</p>

      <div className="stat-row">
        <Link to="/browse" className="stat">
          <span className="stat-num">{stats.tasks}</span>
          <span className="stat-label">Tasks</span>
        </Link>
        <Link to="/techniques" className="stat">
          <span className="stat-num">{stats.techniques}</span>
          <span className="stat-label">Techniques</span>
        </Link>
        <Link to="/resources" className="stat">
          <span className="stat-num">{stats.resources}</span>
          <span className="stat-label">Sources</span>
        </Link>
        <Link to="/intake" className="stat stat--accent">
          <span className="stat-num">{stats.intake}</span>
          <span className="stat-label">In intake</span>
        </Link>
      </div>

      <div className="two-col">
        <section className="card">
          <div className="card-head">
            <h2>Recent activity</h2>
            <div className="seg">
              {[1, 7, 30].map((d) => (
                <button
                  key={d}
                  className={days === d ? 'seg-btn active' : 'seg-btn'}
                  onClick={() => setDays(d)}
                >
                  {d === 1 ? 'Today' : `${d}d`}
                </button>
              ))}
            </div>
          </div>
          {digest.length === 0 ? (
            <Empty>Nothing in this window yet. New sources land here as we add them.</Empty>
          ) : (
            <ul className="feed">
              {digest.map((e) => (
                <li key={e.id} className="feed-item">
                  <span className={`feed-icon kind--${e.kind}`}>{KIND_ICON[e.kind] || '•'}</span>
                  <div className="feed-body">
                    <span className="feed-name">{e.entity_name}</span>
                    {e.note ? <span className="feed-note">{e.note}</span> : null}
                    <span className="feed-date">{fmtDate(e.created_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <div className="card-head"><h2>Domains</h2></div>
          <ul className="domain-list">
            {domains.map((d) => (
              <li key={d.domain}>
                <Link to={`/browse?domain=${encodeURIComponent(d.domain)}`} className="domain-row">
                  <span>{d.domain}</span>
                  <span className="count">{d.task_count}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
