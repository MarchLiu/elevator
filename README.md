# Elevator System

A web-based elevator system built with FastAPI, PostgreSQL, and Vue.js.

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (for database migrations)

### Frontend
- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia (State Management)

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
- Create a database named 'elevator'
- Update the database connection string in your environment variables

4. Run the backend server:
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

## Development

- Backend API will be available at: http://localhost:8000
- Frontend development server will be available at: http://localhost:5173
- API documentation will be available at: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/elevator
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```


