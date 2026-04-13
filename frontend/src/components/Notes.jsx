import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import MarkdownPreview from './MarkdownPreview';

const emptyDraft = () => ({ title: '', content: '', tags: '', linked_resource_id: '' });

function Notes() {
  const previewRef = useRef(null);
  const [notes, setNotes] = useState([]);
  const [filteredNotes, setFilteredNotes] = useState([]);
  const [draft, setDraft] = useState(emptyDraft);
  const [selectedId, setSelectedId] = useState(null);
  const [filters, setFilters] = useState({ tags: '' });
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
    fetchNotes();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [notes, filters]);

  const fetchNotes = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/notes');
      setNotes(res.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const applyFilters = () => {
    let filtered = notes;
    if (filters.tags) {
      const filterText = filters.tags.toLowerCase();
      filtered = filtered.filter((n) => {
        const noteTags = n.tags || '';
        return noteTags.toLowerCase().includes(filterText);
      });
    }
    setFilteredNotes(filtered);
  };

  const beginNew = () => {
    setSelectedId(null);
    setDraft(emptyDraft());
    setViewMode('edit');
  };

  const selectNote = (note) => {
    setSelectedId(note.id);
    setDraft({ ...note });
    setViewMode('edit');
  };

  const toPayload = () => ({
    title: draft.title,
    content: draft.content,
    tags: draft.tags,
    linked_resource_id: draft.linked_resource_id,
  });

  const saveNote = async () => {
    try {
      const payload = toPayload();
      if (selectedId) {
        await axios.put(`http://127.0.0.1:8000/notes/${selectedId}`, payload);
      } else {
        await axios.post('http://127.0.0.1:8000/notes', payload);
      }
      const res = await axios.get('http://127.0.0.1:8000/notes');
      setNotes(res.data);
      if (selectedId) {
        const updated = res.data.find((n) => n.id === selectedId);
        if (updated) setDraft({ ...updated });
      } else {
        beginNew();
      }
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  const deleteNote = async (id) => {
    if (!window.confirm('Delete this note?')) return;
    try {
      await axios.delete(`http://127.0.0.1:8000/notes/${id}`);
      if (selectedId === id) beginNew();
      fetchNotes();
    } catch (error) {
      console.error('Error deleting note:', error);
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
    <main className="page-workspace" aria-label="Notes">
      <div className="workspace-shell">
        <div className="workspace-three-col">
          <aside className="workspace-sidebar" style={{ width: leftWidth }} aria-label="Note details">
            <div className="workspace-sidebar-head">
              <h2 className="workspace-sidebar-title">{selectedId ? 'Details' : 'New note'}</h2>
              <button type="button" className="sidebar-new-btn" onClick={beginNew}>
                + New
              </button>
            </div>
            {viewMode === 'preview' ? (
              <div className="toc">
                <h3>Table of Contents</h3>
                <ul>
                  {getTOC(draft.content).map((item, index) => (
                    <li key={index} style={{ marginLeft: `${(item.level - 1) * 20}px` }}>
                      <button type="button" className="toc-link" onClick={(e) => scrollToHeading(e, item.id)}>{item.text}</button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="notes-details">
                <div className="form-group">
                  <label>Title</label>
                  <input
                    type="text"
                    placeholder="Note title"
                    value={draft.title}
                    onChange={(e) => setDraft({ ...draft, title: e.target.value })}
                  />
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
                <div className="form-group">
                  <label>Linked Resource ID (optional)</label>
                  <input
                    type="number"
                    placeholder="ID of related resource"
                    value={draft.linked_resource_id}
                    onChange={(e) => setDraft({ ...draft, linked_resource_id: e.target.value })}
                  />
                  <p className="markdown-hint" style={{ marginTop: '0.5rem' }}>
                    Enter the numeric resource ID shown in the Resources list to link this note to a resource.
                  </p>
                </div>
                <p className="markdown-hint">
                  Tip: Use <code># Heading</code> for headings. Body is edited in the center.
                </p>
                <div className="form-actions">
                  <button type="button" onClick={saveNote}>
                    {selectedId ? '💾 Save' : '📝 Create'}
                  </button>
                </div>
              </div>
            )}
            <div className="resize-handle" onMouseDown={(e) => handleResizeStart(e, 'left')}></div>
          </aside>

          <section className="workspace-editor-column" aria-label="Markdown editor">
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
                  placeholder="Write your notes in Markdown..."
                  value={draft.content}
                  onChange={(e) => setDraft({ ...draft, content: e.target.value })}
                />
              ) : (
                <MarkdownPreview ref={previewRef} content={draft.content} />
              )}
            </div>
          </section>

          <aside className="workspace-list-column" style={{ width: rightWidth }} aria-label="All notes">
            <div className="filters">
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
              {filteredNotes.length === 0 ? (
                <p className="item-list-empty">No notes match.</p>
              ) : (
                <ul className="item-list-plain">
                  {filteredNotes.map((note) => (
                    <li
                      key={note.id}
                      className={selectedId === note.id ? 'is-selected' : ''}
                    >
                      <button
                        type="button"
                        className="item-list-plain-btn"
                        onClick={() => selectNote(note)}
                      >
                        <span className="item-list-plain-title">{note.title?.trim() || 'Untitled'}</span>
                        {note.tags && (
                          <span className="item-list-plain-meta">{note.tags}</span>
                        )}
                      </button>
                      <button
                        type="button"
                        className="item-list-plain-delete"
                        aria-label="Delete note"
                        onClick={() => deleteNote(note.id)}
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

export default Notes;
