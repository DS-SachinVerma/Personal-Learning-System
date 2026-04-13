import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({ resources: 0, notes: 0, tasks: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const resourcesRes = await axios.get('http://127.0.0.1:8000/resources');
        const notesRes = await axios.get('http://127.0.0.1:8000/notes');
        const tasksRes = await axios.get('http://127.0.0.1:8000/tasks');
        setStats({
          resources: resourcesRes.data.length,
          notes: notesRes.data.length,
          tasks: tasksRes.data.length,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        setError('Unable to fetch dashboard data. Make sure the backend server is running and refresh the page.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <main className="page-dashboard">
      <div className="dashboard-summary">
        <Link to="/resources" className="dashboard-summary-card">
          <div className="dashboard-summary-icon">📚</div>
          <div>
            <div className="dashboard-summary-label">Resources</div>
            <div className="dashboard-summary-value">{loading ? 'Loading…' : stats.resources}</div>
          </div>
        </Link>
        <Link to="/notes" className="dashboard-summary-card">
          <div className="dashboard-summary-icon">📝</div>
          <div>
            <div className="dashboard-summary-label">Notes</div>
            <div className="dashboard-summary-value">{loading ? 'Loading…' : stats.notes}</div>
          </div>
        </Link>
        <Link to="/tasks" className="dashboard-summary-card">
          <div className="dashboard-summary-icon">✅</div>
          <div>
            <div className="dashboard-summary-label">Tasks</div>
            <div className="dashboard-summary-value">{loading ? 'Loading…' : stats.tasks}</div>
          </div>
        </Link>
      </div>

      <div className="dashboard-cards">
        <Link to="/resources" className="box-card">
          <div>
            <div className="box-card-icon">📚</div>
            <div className="box-card-title">Resources</div>
            <div className="box-card-copy">Browse saved courses, papers, videos, and learning links in one place.</div>
          </div>
          <div className="box-card-footer">{loading ? 'Loading…' : `${stats.resources} saved`}</div>
        </Link>

        <Link to="/notes" className="box-card">
          <div>
            <div className="box-card-icon">📝</div>
            <div className="box-card-title">Notes</div>
            <div className="box-card-copy">Open your markdown notes workspace and keep long form learning content organized.</div>
          </div>
          <div className="box-card-footer">{loading ? 'Loading…' : `${stats.notes} notes`}</div>
        </Link>

        <Link to="/tasks" className="box-card">
          <div>
            <div className="box-card-icon">✅</div>
            <div className="box-card-title">Tasks</div>
            <div className="box-card-copy">View and manage actions, milestones, and study reminders for every learning goal.</div>
          </div>
          <div className="box-card-footer">{loading ? 'Loading…' : `${stats.tasks} tasks`}</div>
        </Link>
      </div>

      {error && <div className="error-box">{error}</div>}
    </main>
  );
}

export default Dashboard;