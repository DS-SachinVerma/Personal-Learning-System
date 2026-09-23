import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTechnique } from '../api';
import MarkdownPreview from './MarkdownPreview';
import { Loading, Empty, MaturityBadge, TaskChip, Tags, fmtDate } from './ui';

export default function TechniqueDetail() {
  const { id } = useParams();
  const [tech, setTech] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setTech(null);
    setErr(false);
    getTechnique(id).then(setTech).catch(() => setErr(true));
  }, [id]);

  if (err) return <Empty>Technique not found. <Link to="/techniques">Back</Link></Empty>;
  if (!tech) return <Loading what="Loading technique…" />;

  return (
    <div className="wrap">
      <Link to="/techniques" className="back">← Techniques</Link>
      <div className="detail-head">
        <div className="title-row">
          <h1 className="page-title">{tech.name}</h1>
          <MaturityBadge value={tech.maturity} />
        </div>
        <Tags value={tech.tags} />
        <p className="muted small">Last reviewed {fmtDate(tech.last_reviewed_at)}</p>
      </div>

      {tech.summary ? (
        <section className="card"><MarkdownPreview content={tech.summary} /></section>
      ) : null}

      <section className="section">
        <h2>Used for</h2>
        {tech.tasks.length === 0 ? (
          <Empty>Not linked to any task yet.</Empty>
        ) : (
          <div className="chip-row">
            {tech.tasks.map((t) => <TaskChip key={t.id} task={t} />)}
          </div>
        )}
      </section>

      <section className="section">
        <h2>Notes from sources</h2>
        {tech.insights.length === 0 ? (
          <Empty>No source insights reference this technique yet.</Empty>
        ) : (
          <ul className="insight-list">
            {tech.insights.map((i) => (
              <li key={i.id} className="insight">
                {i.title ? <h3 className="insight-title">{i.title}</h3> : null}
                {i.detail ? <MarkdownPreview content={i.detail} /> : null}
                <div className="insight-foot">
                  {i.resource ? (
                    <Link to={`/resources/${i.resource.id}`} className="src-link">
                      <span className={`badge badge--source source--${i.resource.source}`}>{i.resource.source}</span>
                      {i.resource.title}
                    </Link>
                  ) : null}
                  {i.task ? <Link to={`/tasks/${i.task.slug || i.task.id}`} className="via">for {i.task.name}</Link> : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
