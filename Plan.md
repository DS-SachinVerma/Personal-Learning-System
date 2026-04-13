Read [](file:///d%3A/WebSite)

Analyzing your answers...

Created memory file [](file:///c%3A/Users/Admin/AppData/Roaming/Code/User/workspaceStorage/fad590e4859df33e9503997da5356088/GitHub.copilot-chat/memory-tool/memories/MzEwZTZjZTUtODIyOC00ZWQ3LThmMjItYTc2OTM1Mzk0MjRj/plan.md)

## Plan: Learning Management System

Build a web-based learning tracker combining resource management, note-taking, task planning, and a public blog, using FastAPI for backend, React for frontend, and SQLite for database. Focus on core features for daily use: resource tracking, notes, tasks, search/tagging, and daily logs. Include public blog in MVP for portfolio benefits. Deploy to Render (backend), Vercel (frontend), Supabase (DB upgrade later).

**Steps**

### Phase 1: Project Setup and Backend Foundations (Week 1)
1. Set up project structure: Create directories for backend (FastAPI), frontend (React), and shared configs.
2. Initialize FastAPI backend: Set up virtual environment, install dependencies (FastAPI, SQLAlchemy, SQLite), create basic app structure with routers for resources, notes, tasks.
3. Design and create database models: Define tables for Resources (id, title, type, link, status, tags, notes, created_at), Notes (id, title, content, tags, linked_resource_id), Tasks (id, task, status, priority, deadline).
4. Implement Resources CRUD API: POST /resources, GET /resources, PUT /resources/{id}, DELETE /resources/{id}. Include filtering by type, status, tags.
5. Add basic authentication if needed (optional for MVP, but consider for public blog).

### Phase 2: Notes System and Search (Week 2)
6. Implement Notes CRUD API: POST /notes, GET /notes, PUT /notes/{id}, DELETE /notes/{id}. Support Markdown content.
7. Add search functionality: Implement keyword search across resources and notes, filter by tags, status.
8. Integrate tagging system: Ensure tags are stored as JSON or comma-separated, searchable.
9. Create basic React frontend: Set up React app, install axios for API calls, create components for Resources list, Notes editor (with Markdown support).

### Phase 3: Tasks, Dashboard, and UI Polish (Week 3)
10. Implement Tasks CRUD API: POST /tasks, GET /tasks, PUT /tasks/{id}, DELETE /tasks/{id}. Include priority and deadline handling.
11. Build Dashboard page: Show today's tasks, recent notes, learning progress (e.g., completed resources count).
12. Create Resources Page: List resources with filters (type, status, tags), status update functionality.
13. Create Notes Page: Markdown editor for creating/editing notes, search interface.
14. Create Roadmap Page: Tasks list with status updates, priority sorting.
15. Add Daily/Weekly Logs: Extend notes or tasks to include time tracking and daily summaries.

### Phase 4: Public Blog and Deployment (Week 4)
16. Implement Public Blog: Add API endpoints to publish notes as blog posts, create public view pages in React.
17. Polish UI: Apply preferred design from design.md (assuming added), ensure responsive, simple styling.
18. Set up deployment: Configure FastAPI for Render, React for Vercel, migrate DB to Supabase if needed.
19. Add basic tests: Unit tests for API endpoints, integration tests for CRUD operations.
20. Final verification: Test full flow, deploy, and ensure usability.

**Relevant files**
- `backend/app/main.py` — FastAPI app entry, routers setup
- `backend/app/models.py` — SQLAlchemy models for Resources, Notes, Tasks
- `backend/app/routers/resources.py` — Resources API endpoints
- `backend/app/routers/notes.py` — Notes API endpoints
- `backend/app/routers/tasks.py` — Tasks API endpoints
- `frontend/src/App.js` — Main React app, routing
- `frontend/src/components/Dashboard.js` — Dashboard component
- `frontend/src/components/Resources.js` — Resources list and filters
- `frontend/src/components/Notes.js` — Notes editor and list
- `frontend/src/components/Tasks.js` — Tasks management
- design.md — Reference for UI design preferences

**Verification**
1. Run backend tests: Use pytest to verify CRUD operations for resources, notes, tasks.
2. Test API endpoints: Use Postman or curl to check GET/POST/PUT/DELETE for each resource.
3. Frontend integration: Ensure React components fetch and display data correctly, test search and filters.
4. End-to-end: Manually create a resource, add notes, mark tasks, verify dashboard updates.
5. Deployment check: Deploy to staging, test public blog access, ensure no errors.
6. Usability: Use the app daily for a week, track learning, ensure it reduces clutter.

**Decisions**
- Tech stack: Option 1 (FastAPI + React + SQLite) as preferred.
- Database: Start with SQLite for simplicity, upgrade to Supabase later.
- Deployment: Render for backend, Vercel for frontend, Supabase for DB.
- Scope: Include public blog in MVP as requested. Exclude advanced features like AI integration for now.
- UI: Keep simple, reference design.md for preferences.

**Further Considerations**
1. Authentication: For public blog, consider adding user auth (e.g., JWT) to protect private notes. Recommendation: Add basic auth in Phase 1 if blog is public.