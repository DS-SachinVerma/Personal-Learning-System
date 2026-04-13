import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import MarkdownPreview from './MarkdownPreview';

const emptyDraft = () => ({
  title: '',
  type: '',
  link: '',
  status: 'to_learn',
  tags: '',
  notes: '',
});

function Resources() {
  const previewRef = useRef(null);
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [draft, setDraft] = useState(emptyDraft);
  const [selectedId, setSelectedId] = useState(null);
  const [filters, setFilters] = useState({ type: '', status: '', tags: '' });
  const [viewMode, setViewMode] = useState('edit');
  const [leftWidth, setLeftWidth] = useState(320);
  const [rightWidth, setRightWidth] = useState(320);

  const getTOC = (content) => {
    const lines = content.split('\n');
    const toc = [];
    lines.forEach(line => {
      const match = line.match(/^(#{1,6})\s+(.+)/);
      if (match) {
        const level = match[1].length;
        const text = match[2];
        const id = text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
        toc.push({ level, text, id });
      }
    });
    return toc;
  };

  const Heading = ({ level, children }) => {
    const id = children.toString().toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
    const Tag = `h${level}`;
    return React.createElement(Tag, { id }, children);
  };

  const scrollToHeading = (event, id) => {
    event.preventDefault();
    if (!previewRef.current) return;
    const headings = previewRef.current.querySelectorAll('[id]');
    const heading = Array.from(headings).find((el) => el.id === id);
    if (heading) {
      heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [resources, filters]);

  const fetchResources = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/resources');
      setResources(res.data);
    } catch (error) {
      console.error('Error fetching resources:', error);
    }
  };

  const applyFilters = () => {
    let filtered = resources;
    if (filters.type) {
      filtered = filtered.filter((r) => r.type === filters.type);
    }
    if (filters.status) {
      filtered = filtered.filter((r) => r.status === filters.status);
    }
    if (filters.tags) {
      filtered = filtered.filter((r) =>
        r.tags.toLowerCase().includes(filters.tags.toLowerCase())
      );
    }
    setFilteredResources(filtered);
  };

  const beginNew = () => {
    setSelectedId(null);
    setDraft(emptyDraft());
    setViewMode('edit');
  };

  const selectResource = (resource) => {
    setSelectedId(resource.id);
    setDraft({ ...resource });
    setViewMode('edit');
  };

  const toPayload = () => ({
    title: draft.title,
    type: draft.type,
    link: draft.link,
    status: draft.status,
    tags: draft.tags,
    notes: draft.notes,
  });

  const saveResource = async () => {
    try {
      const payload = toPayload();
      if (selectedId) {
        await axios.put(`http://127.0.0.1:8000/resources/${selectedId}`, payload);
      } else {
        await axios.post('http://127.0.0.1:8000/resources', payload);
      }
      const res = await axios.get('http://127.0.0.1:8000/resources');
      setResources(res.data);
      if (selectedId) {
        const updated = res.data.find((r) => r.id === selectedId);
        if (updated) setDraft({ ...updated });
      } else {
        beginNew();
      }
    } catch (error) {
      console.error('Error saving resource:', error);
    }
  };

  const deleteResource = async (id) => {
    if (!window.confirm('Delete this resource?')) return;
    try {
      await axios.delete(`http://127.0.0.1:8000/resources/${id}`);
      if (selectedId === id) beginNew();
      fetchResources();
    } catch (error) {
      console.error('Error deleting resource:', error);
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

  return (
    <main className="page-workspace" aria-label="Resources">
      <div className="workspace-shell">
        <div className="workspace-three-col">
          <aside className="workspace-sidebar" style={{ width: leftWidth }} aria-label="Resource fields">
            <div className="workspace-sidebar-head">
              <h2 className="workspace-sidebar-title">
                {selectedId ? `Details · #${selectedId}` : 'New resource'}
              </h2>
              <button type="button" className="sidebar-new-btn" onClick={beginNew}>
                + New
              </button>
            </div>
            {viewMode === 'preview' ? (
              <div className="toc">
                <h3>Table of Contents</h3>
                <ul>
                  {getTOC(draft.notes).map((item, index) => (
                    <li key={index} style={{ marginLeft: `${(item.level - 1) * 20}px` }}>
                      <button type="button" className="toc-link" onClick={(e) => scrollToHeading(e, item.id)}>{item.text}</button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <>
                <div className="form-group">
                  <label>Title</label>
                  <input
                    type="text"
                    placeholder="Resource title"
                    value={draft.title}
                    onChange={(e) => setDraft({ ...draft, title: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Type</label>
                  <select
                    value={draft.type}
                    onChange={(e) => setDraft({ ...draft, type: e.target.value })}
                  >
                    <option value="">Select Type</option>
                    <option value="paper">Paper</option>
                    <option value="video">Video</option>
                    <option value="blog">Blog</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Link</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={draft.link}
                    onChange={(e) => setDraft({ ...draft, link: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={draft.status}
                    onChange={(e) => setDraft({ ...draft, status: e.target.value })}
                  >
                    <option value="to_learn">To Learn</option>
                    <option value="learning">Learning</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Tags</label>
                  <input
                    type="text"
                    placeholder="Comma-separated tags"
                    value={draft.tags}
                    onChange={(e) => setDraft({ ...draft, tags: e.target.value })}
                  />
                </div>
                <div className="form-actions">
                  <button type="button" onClick={saveResource}>
                    {selectedId ? '💾 Save' : '➕ Add'}
                  </button>
                </div>
              </>
            )}
            <div className="resize-handle" onMouseDown={(e) => handleResizeStart(e, 'left')}></div>
          </aside>

          <section className="workspace-editor-column" aria-label="Notes for this resource">
            <div className="preview-panel preview-panel--fill">
              <div className="editor-header editor-header--tabs-only">
                <div className="editor-tabs">
                  <button
                    type="button"
                    className={viewMode === 'edit' ? 'active' : 'btn-secondary'}
                    onClick={() => setViewMode('edit')}
                  >
                    ✏️ Edit
                  </button>
                  <button
                    type="button"
                    className={viewMode === 'preview' ? 'active' : 'btn-secondary'}
                    onClick={() => setViewMode('preview')}
                  >
                    👁️ Preview
                  </button>
                </div>
              </div>
              {viewMode === 'edit' ? (
                <textarea
                  className="markdown-textarea"
                  placeholder="Notes — key points, understanding, or follow-ups for this resource"
                  value={draft.notes}
                  onChange={(e) => setDraft({ ...draft, notes: e.target.value })}
                />
              ) : (
                <MarkdownPreview ref={previewRef} content={draft.notes} />
              )}
            </div>
          </section>

          <aside className="workspace-list-column" style={{ width: rightWidth }} aria-label="All resources">
            <div className="filters">
              <div className="filter-group">
                <label>Type</label>
                <select
                  value={filters.type}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                >
                  <option value="">All Types</option>
                  <option value="paper">Paper</option>
                  <option value="video">Video</option>
                  <option value="blog">Blog</option>
                </select>
              </div>
              <div className="filter-group">
                <label>Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <option value="">All Statuses</option>
                  <option value="to_learn">To Learn</option>
                  <option value="learning">Learning</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div className="filter-group">
                <label>Tags</label>
                <input
                  type="text"
                  placeholder="Filter by tags"
                  value={filters.tags}
                  onChange={(e) => setFilters({ ...filters, tags: e.target.value })}
                />
              </div>
            </div>
            <div className="workspace-list-scroll workspace-list-scroll--plain">
              {filteredResources.length === 0 ? (
                <p className="item-list-empty">No resources match.</p>
              ) : (
                <ul className="item-list-plain">
                  {filteredResources.map((resource) => (
                    <li
                      key={resource.id}
                      className={selectedId === resource.id ? 'is-selected' : ''}
                    >
                      <button
                        type="button"
                        className="item-list-plain-btn"
                        onClick={() => selectResource(resource)}
                      >
                        <span className="item-list-plain-title">
                          {resource.title?.trim() || 'Untitled'}
                        </span>
                        <span className="item-list-plain-meta">{resource.id}</span>
                        <span className="item-list-plain-badges">
                          {resource.type && (
                            <span className="type-badge type-badge--tiny">{resource.type}</span>
                          )}
                          <span
                            className={`status-badge status-${resource.status} status-badge--tiny`}
                          >
                            {resource.status.replace('_', ' ')}
                          </span>
                        </span>
                      </button>
                      <button
                        type="button"
                        className="item-list-plain-delete"
                        aria-label="Delete resource"
                        onClick={() => deleteResource(resource.id)}
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

export default Resources;
