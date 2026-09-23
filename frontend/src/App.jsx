import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Browse from './components/Browse';
import TaskDetail from './components/TaskDetail';
import Techniques from './components/Techniques';
import TechniqueDetail from './components/TechniqueDetail';
import ResourceList from './components/ResourceList';
import ResourceDetail from './components/ResourceDetail';
import './App.css';

const navClass = ({ isActive }) => (isActive ? 'active' : undefined);

function App() {
  return (
    <Router>
      <header className="top-nav">
        <nav className="top-nav-inner" aria-label="Main">
          <span className="brand">◆ Technique Library</span>
          <ul>
            <li><NavLink to="/" end className={navClass}>Dashboard</NavLink></li>
            <li><NavLink to="/browse" className={navClass}>Browse Tasks</NavLink></li>
            <li><NavLink to="/techniques" className={navClass}>Techniques</NavLink></li>
            <li><NavLink to="/resources" className={navClass}>Sources</NavLink></li>
            <li><NavLink to="/reading" className={navClass}>Reading</NavLink></li>
            <li><NavLink to="/intake" className={navClass}>Intake</NavLink></li>
          </ul>
        </nav>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/browse" element={<Browse />} />
          <Route path="/tasks/:slug" element={<TaskDetail />} />
          <Route path="/techniques" element={<Techniques />} />
          <Route path="/techniques/:id" element={<TechniqueDetail />} />
          <Route path="/resources" element={<ResourceList mode="all" />} />
          <Route path="/reading" element={<ResourceList mode="reading" />} />
          <Route path="/intake" element={<ResourceList mode="intake" />} />
          <Route path="/resources/:id" element={<ResourceDetail />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
