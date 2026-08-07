# Workflow Manager API

Azure Cosmos DB-powered task/workflow management system built with FastAPI.

## Architecture

- **Language**: Python / FastAPI
- **Database**: Azure Cosmos DB
- **Scale**: 100 projects, 1K users, 50K tasks

## Containers & Partition Keys

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| projects | `/id` | Projects accessed by own ID |
| tasks | `/projectId` | >70% queries: tasks within project context |
| assignees | `/id` | Assignees accessed by own ID |
| assigneeTasks | `/assigneeId` | Denormalized view for tasks-by-assignee |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Cosmos DB credentials
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/projects/{id}/tasks` - Tasks by project (filterable)
- `GET /api/projects/{id}/tasks/{taskId}` - Get task
- `PATCH /api/projects/{id}/tasks/{taskId}` - Update task
- `POST /api/projects/{id}/tasks/{taskId}/transition` - Status transition
- `GET /api/projects/{id}/tasks/{taskId}/comments` - Task comments
- `POST /api/projects/{id}/tasks/{taskId}/comments` - Add comment
- `GET /api/projects/{id}/tasks/{taskId}/history` - Status history
- `GET /api/assignees/{id}/tasks` - Tasks by assignee
- `GET /api/projects/{id}/activity` - Activity log
