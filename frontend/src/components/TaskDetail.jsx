import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTask } from '../api';
import MarkdownPreview from './MarkdownPreview';
import { Loading, Empty, TechChip, Tags, fmtDate } from './ui';

export default function TaskDetail() {
  const { slug } = useParams();
  const [task, setTask] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setTask(null);
    setErr(false);
    getTask(slug).then(setTask).catch(() => setErr(true));
  }, [slug]);

  if (err) return <Empty>Task not found. <Link to="/browse">Back to browse</Link></Empty>;
  if (!task) return <Loading what="Loading task…" />;

  const useInsights = task.insights.filter((i) => i.kind !== 'study');
  const studyInsights = task.insights.filter((i) => i.kind === 'study');

  return (
    <div className="wrap">
      <Link to="/browse" className="back">← Browse</Link>
      <div className="detail-head">
        <span className="eyebrow">{task.domain}</span>
        <h1 className="page-title">{task.name}</h1>
        {task.one_liner ? <p className="lead">{task.one_liner}</p> : null}
        <Tags value={task.tags} />
      </div>

      {task.overview ? (
        <section className="card">
          <MarkdownPreview content={task.overview} />
        </section>
      ) : null}

      <section className="section">
        <h2>Candidate techniques</h2>
        {task.techniques.length === 0 ? (
          <Empty>No techniques linked yet.</Empty>
        ) : (
          <div className="chip-row">
            {task.techniques.map((t) => <TechChip key={t.id} tech={t} />)}
          </div>
        )}
      </section>

      <InsightSection
        title="What our sources say"
        empty="No actionable insights collected for this task yet."
        insights={useInsights}
      />

      {studyInsights.length > 0 ? (
        <InsightSection title="Further reading" insights={studyInsights} study />
      ) : null}

      {task.experiments.length > 0 ? (
        <section className="section">
          <h2>Benchmarks</h2>
          <ul className="exp-list">
            {task.experiments.map((e) => (
              <li key={e.id} className="card">
                <div className="exp-head">
                  <strong>{e.title}</strong>
                  <span className="muted small">
                    {e.dataset ? `${e.dataset} · ` : ''}{e.metric} · {fmtDate(e.created_at)}
                  </span>
                </div>
                {e.results ? <MarkdownPreview content={e.results} /> : null}
                {e.code_link ? <a href={e.code_link} target="_blank" rel="noreferrer">Code ↗</a> : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

function InsightList({ insights, study }) {
  return (
    <ul className="insight-list">
      {insights.map((i) => (
        <li key={i.id} className={study ? 'insight insight--study' : 'insight'}>
          {i.title ? <h3 className="insight-title">{i.title}</h3> : null}
          {i.detail ? <MarkdownPreview content={i.detail} /> : null}
          <div className="insight-foot">
            {i.resource ? (
              <Link to={`/resources/${i.resource.id}`} className="src-link">
                <span className={`badge badge--source source--${i.resource.source}`}>
                  {i.resource.source}
                </span>
                {i.resource.title}
              </Link>
            ) : null}
            {i.technique ? (
              <Link to={`/techniques/${i.technique.id}`} className="via">via {i.technique.name}</Link>
            ) : null}
          </div>
        </li>
      ))}
    </ul>
  );
}

function InsightSection({ title, insights, empty, study }) {
  // The study lane is collapsed by default so the actionable shelf reads first.
  if (study) {
    return (
      <section className="section">
        <details className="study-lane">
          <summary className="study-summary">
            {title}<span className="lane-tag">study</span>
            <span className="muted small"> · {insights.length}</span>
          </summary>
          <div className="study-body">
            <InsightList insights={insights} study />
          </div>
        </details>
      </section>
    );
  }
  return (
    <section className="section">
      <h2>{title}</h2>
      {insights.length === 0
        ? (empty ? <Empty>{empty}</Empty> : null)
        : <InsightList insights={insights} />}
    </section>
  );
}
