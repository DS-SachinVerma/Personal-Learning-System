import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Resources from './components/Resources';
import Notes from './components/Notes';
import Tasks from './components/Tasks';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="top-nav">
          <nav className="top-nav-inner" aria-label="Main">
            <ul>
              <li>
                <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
                  Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink to="/resources" className={({ isActive }) => (isActive ? 'active' : undefined)}>
                  Resources
                </NavLink>
              </li>
              <li>
                <NavLink to="/notes" className={({ isActive }) => (isActive ? 'active' : undefined)}>
                  Notes
                </NavLink>
              </li>
              <li>
                <NavLink to="/tasks" className={({ isActive }) => (isActive ? 'active' : undefined)}>
                  Tasks
                </NavLink>
              </li>
            </ul>
          </nav>
        </header>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/tasks" element={<Tasks />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
