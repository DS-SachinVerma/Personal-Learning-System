import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { getTechniques } from '../api';
import { Loading, Empty, MaturityBadge, Tags } from './ui';

const MATURITIES = ['', 'experimental', 'emerging', 'proven', 'legacy'];

export default function Techniques() {
  const [techs, setTechs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [maturity, setMaturity] = useState('');

  useEffect(() => {
    getTechniques().then(setTechs).finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return techs.filter((t) => {
      if (maturity && t.maturity !== maturity) return false;
      if (needle && !(`${t.name} ${t.summary || ''} ${t.tags || ''}`.toLowerCase().includes(needle))) return false;
      return true;
    });
  }, [techs, q, maturity]);

  if (loading) return <Loading what="Loading techniques…" />;

  return (
    <div className="wrap">
      <h1 className="page-title">Techniques</h1>
      <div className="toolbar">
        <input className="search" placeholder="Search techniques…" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="select" value={maturity} onChange={(e) => setMaturity(e.target.value)}>
          {MATURITIES.map((m) => <option key={m} value={m}>{m ? m : 'All maturity'}</option>)}
        </select>
      </div>

      {filtered.length === 0 ? (
        <Empty>No techniques yet — they get added as sources are curated.</Empty>
      ) : (
        <div className="tech-grid">
          {filtered.map((t) => (
            <Link key={t.id} to={`/techniques/${t.id}`} className="tech-card">
              <div className="tech-card-head">
                <span className="tech-card-name">{t.name}</span>
                <MaturityBadge value={t.maturity} />
              </div>
              <div className="tech-card-tasks">
                {t.tasks.slice(0, 4).map((tk) => <span key={tk.id} className="mini-chip">{tk.name}</span>)}
                {t.tasks.length > 4 ? <span className="mini-chip">+{t.tasks.length - 4}</span> : null}
              </div>
              <Tags value={t.tags} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
