# Personal Learning System

A full-stack learning management system built with React (frontend) and FastAPI (backend).

## Features

- **Dashboard**: Overview of resources, notes, and tasks
- **Resources**: Manage learning materials (papers, videos, blogs)
- **Notes**: Markdown-based note taking with preview
- **Tasks**: Task management with priorities and deadlines

## Tech Stack

- **Frontend**: React, Vite, React Router, Axios
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Styling**: Custom CSS with dark theme

## Local Development

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DS-SachinVerma/Personal-Learning-System.git
   cd Personal-Learning-System
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate

   pip install -r requirements.txt
   python run.py
   ```
   Backend will run on http://127.0.0.1:8000

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will run on http://localhost:5176

## Deployment

### Frontend Deployment (Vercel - Recommended)

1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Set the root directory to `frontend`
3. Deploy automatically on push

### Backend Deployment (Railway - Recommended)

1. Connect your GitHub repo to [Railway](https://railway.app)
2. Set the root directory to `backend`
3. Add environment variables if needed
4. Deploy automatically on push

## API Endpoints

- `GET /resources` - Get all resources
- `POST /resources` - Create a resource
- `PUT /resources/{id}` - Update a resource
- `DELETE /resources/{id}` - Delete a resource
- `GET /notes` - Get all notes
- `POST /notes` - Create a note
- `PUT /notes/{id}` - Update a note
- `DELETE /notes/{id}` - Delete a note
- `GET /tasks` - Get all tasks
- `POST /tasks` - Create a task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Push to your fork
6. Create a pull request

## License

MIT License</content>
<parameter name="filePath">d:\WebSite\README.md