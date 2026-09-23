import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getResource } from '../api';
import MarkdownPreview from './MarkdownPreview';
import { Loading, Empty, SourceBadge, TypeBadge, Tags, fmtDate } from './ui';

export default function ResourceDetail() {
  const { id } = useParams();
  const [r, setR] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setR(null);
    setErr(false);
    getResource(id).then(setR).catch(() => setErr(true));
  }, [id]);

  if (err) return <Empty>Source not found. <Link to="/resources">Back</Link></Empty>;
  if (!r) return <Loading what="Loading source…" />;

  return (
    <div className="wrap">
      <Link to="/resources" className="back">← Sources</Link>
      <div className="detail-head">
        <h1 className="page-title">{r.title}</h1>
        <div className="res-meta">
          <TypeBadge value={r.type} />
          <SourceBadge value={r.source} />
          {r.status === 'intake' ? <span className="badge badge--intake">intake</span> : null}
          {r.author ? <span className="muted small">{r.author}</span> : null}
          {typeof r.stars === 'number' ? <span className="muted small">★ {r.stars.toLocaleString()}</span> : null}
        </div>
        {r.link ? <a className="ext" href={r.link} target="_blank" rel="noreferrer">Open source ↗</a> : null}
        <Tags value={r.tags} />
      </div>

      {r.summary ? (
        <section className="card"><MarkdownPreview content={r.summary} /></section>
      ) : null}

      <section className="section">
        <h2>What we take from it</h2>
        {r.insights.length === 0 ? (
          <Empty>Not yet curated into any task.</Empty>
        ) : (
          <ul className="insight-list">
            {r.insights.map((i) => (
              <li key={i.id} className="insight">
                <div className="insight-for">
                  {i.task ? <Link to={`/tasks/${i.task.slug || i.task.id}`} className="chip chip--task">{i.task.name}</Link> : null}
                  {i.technique ? <Link to={`/techniques/${i.technique.id}`} className="chip chip--tech">{i.technique.name}</Link> : null}
                </div>
                {i.title ? <h3 className="insight-title">{i.title}</h3> : null}
                {i.detail ? <MarkdownPreview content={i.detail} /> : null}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section">
        <h2>Version history</h2>
        {r.versions.length === 0 ? (
          <Empty>No tracked updates yet.</Empty>
        ) : (
          <ol className="timeline">
            {r.versions.map((v) => (
              <li key={v.id} className="tl-item">
                <div className="tl-dot" />
                <div className="tl-body">
                  <div className="tl-head">
                    <strong>{v.version_label || 'update'}</strong>
                    <span className="muted small">{fmtDate(v.changed_on)}</span>
                  </div>
                  {v.what_changed ? <p className="tl-what">{v.what_changed}</p> : null}
                  {v.why_it_matters ? <p className="tl-why"><span className="why-label">Why it matters:</span> {v.why_it_matters}</p> : null}
                  {v.link ? <a href={v.link} target="_blank" rel="noreferrer" className="small">Details ↗</a> : null}
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
