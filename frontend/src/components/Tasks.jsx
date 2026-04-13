import { useEffect, useState } from 'react';
import axios from 'axios';

const emptyDraft = () => ({
  task: '',
  status: 'pending',
  priority: 'medium',
  deadline: '',
});

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [draft, setDraft] = useState(emptyDraft);
  const [selectedId, setSelectedId] = useState(null);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  const [leftWidth, setLeftWidth] = useState(320);
  const [rightWidth, setRightWidth] = useState(320);

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [tasks, filters]);

  const fetchTasks = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/tasks');
      setTasks(res.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const applyFilters = () => {
    let filtered = tasks;
    if (filters.status) {
      filtered = filtered.filter((t) => t.status === filters.status);
    }
    if (filters.priority) {
      filtered = filtered.filter((t) => t.priority === filters.priority);
    }
    setFilteredTasks(filtered);
  };

  const beginNew = () => {
    setSelectedId(null);
    setDraft(emptyDraft());
  };

  const selectTask = (task) => {
    setSelectedId(task.id);
    setDraft({ ...task });
  };

  const toPayload = () => ({
    task: draft.task,
    status: draft.status,
    priority: draft.priority,
    deadline: draft.deadline,
  });

  const saveTask = async () => {
    try {
      const payload = toPayload();
      if (selectedId) {
        await axios.put(`http://127.0.0.1:8000/tasks/${selectedId}`, payload);
      } else {
        await axios.post('http://127.0.0.1:8000/tasks', payload);
      }
      const res = await axios.get('http://127.0.0.1:8000/tasks');
      setTasks(res.data);
      if (selectedId) {
        const updated = res.data.find((t) => t.id === selectedId);
        if (updated) setDraft({ ...updated });
      } else {
        beginNew();
      }
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  const deleteTask = async (id) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await axios.delete(`http://127.0.0.1:8000/tasks/${id}`);
      if (selectedId === id) beginNew();
      fetchTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleResizeStart = (e, direction) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = direction === 'left' ? leftWidth : rightWidth;
    const handleMouseMove = (e) => {
      const deltaX = direction === 'left' ? (e.clientX - startX) : (startX - e.clientX);
      const newWidth = startWidth + deltaX;
      const clampedWidth = Math.max(220, Math.min(600, newWidth));
      if (direction === 'left') setLeftWidth(clampedWidth);
      else setRightWidth(clampedWidth);
    };
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const toggleStatus = async (task, e) => {
    e.stopPropagation();
    const newStatus = task.status === 'pending' ? 'completed' : 'pending';
    try {
      await axios.put(`http://127.0.0.1:8000/tasks/${task.id}`, {
        ...task,
        status: newStatus,
      });
      fetchTasks();
      if (selectedId === task.id) {
        setDraft((d) => ({ ...d, status: newStatus }));
      }
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  return (
    <main className="page-workspace" aria-label="Tasks">
      <div className="workspace-shell">
        <div className="workspace-three-col">
          <aside className="workspace-sidebar" style={{ width: leftWidth }} aria-label="Task options">
            <div className="workspace-sidebar-head">
              <h2 className="workspace-sidebar-title">{selectedId ? 'Details' : 'New task'}</h2>
              <button type="button" className="sidebar-new-btn" onClick={beginNew}>
                + New
              </button>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select
                value={draft.priority}
                onChange={(e) => setDraft({ ...draft, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="form-group">
              <label>Deadline (optional)</label>
              <input
                type="date"
                value={draft.deadline}
                onChange={(e) => setDraft({ ...draft, deadline: e.target.value })}
              />
            </div>
            {selectedId && (
              <div className="form-group">
                <label>Status</label>
                <select
                  value={draft.status}
                  onChange={(e) => setDraft({ ...draft, status: e.target.value })}
                >
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            )}
            <div className="form-actions">
              <button type="button" onClick={saveTask}>
                {selectedId ? '💾 Save' : '➕ Add'}
              </button>
              {selectedId && (
                <button type="button" className="btn-secondary" onClick={beginNew}>
                  New task
                </button>
              )}
            </div>
            <div className="resize-handle" onMouseDown={(e) => handleResizeStart(e, 'left')}></div>
          </aside>

          <section className="workspace-editor-column" aria-label="Task description">
            <div className="preview-panel preview-panel--fill">
              <textarea
                className="markdown-textarea"
                placeholder="What you need to learn or do (multiple lines ok)"
                value={draft.task}
                onChange={(e) => setDraft({ ...draft, task: e.target.value })}
              />
            </div>
          </section>

          <aside className="workspace-list-column" style={{ width: rightWidth }} aria-label="All tasks">
            <div className="filters">
              <div className="filter-group">
                <label>Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div className="filter-group">
                <label>Priority</label>
                <select
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                >
                  <option value="">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
            <div className="workspace-list-scroll workspace-list-scroll--plain">
              {filteredTasks.length === 0 ? (
                <p className="item-list-empty">No tasks match.</p>
              ) : (
                <ul className="item-list-plain">
                  {filteredTasks.map((task) => (
                    <li
                      key={task.id}
                      className={selectedId === task.id ? 'is-selected' : ''}
                    >
                      <input
                        type="checkbox"
                        className="item-list-plain-check"
                        checked={task.status === 'completed'}
                        onChange={(e) => toggleStatus(task, e)}
                        aria-label={task.status === 'completed' ? 'Mark pending' : 'Mark done'}
                      />
                      <button
                        type="button"
                        className="item-list-plain-btn"
                        onClick={() => selectTask(task)}
                      >
                        <span
                          className={`item-list-plain-title${
                            task.status === 'completed' ? ' is-done' : ''
                          }`}
                        >
                          {task.task?.trim() || 'Untitled'}
                        </span>
                        <span className="item-list-plain-meta">
                          <span>{task.id}</span>
                          <span className={`priority-badge priority-${task.priority}`}>
                            {task.priority}
                          </span>
                          {task.deadline && (
                            <span>{new Date(task.deadline).toLocaleDateString()}</span>
                          )}
                        </span>
                      </button>
                      <button
                        type="button"
                        className="item-list-plain-delete"
                        aria-label="Delete task"
                        onClick={() => deleteTask(task.id)}
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="resize-handle" onMouseDown={(e) => handleResizeStart(e, 'right')}></div>
          </aside>
        </div>
      </div>
    </main>
  );
}

export default Tasks;
