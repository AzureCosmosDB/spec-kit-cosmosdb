---
description: "Generate a complete Azure Cosmos DB workflow/task management application with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-workflow

> Generate a complete Azure Cosmos DB workflow/task management application with deterministic, production-ready architecture.

## Intent

Scaffold a full workflow and task management application (like Jira) that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A workflow/task management API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Projects, Tasks, Assignees, Comments, StatusHistory" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get tasks for a project; Get tasks assigned to a user; Get task by ID within project; Get comments for a task; Get status history for a task" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Workflow/Task Management

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Project | projects | Project metadata, members, settings |
| Task | tasks | Work items with status, priority, assignee |
| Comment | tasks | Co-located with task (type discriminator) |
| StatusHistory | tasks | Co-located with task (type discriminator) — audit log of status changes |
| Assignee | assignees | User profiles for assignment (lightweight) |

### Status Transitions (state machine)

```
backlog → todo → in_progress → in_review → done
                      ↓
                   blocked
```

- Invalid transitions return 409.
- Every transition creates a `StatusHistory` document (audit log) co-located with the task.
- `StatusHistory` records: `fromStatus`, `toStatus`, `changedBy`, `changedAt`, `reason` (optional).

### Tasks by Assignee (cross-concern)

- Primary access is tasks-by-project (single partition).
- Tasks-by-assignee requires either:
  - A denormalized `assigneeTasks` container (partition key `/assigneeId`) updated via change feed, OR
  - Cross-partition query with explicit comment.
- Scaffold MUST implement the denormalized approach for `{{scale}}` > 1000 RPS.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| projects | `/id` | Projects accessed by own ID |
| tasks | `/projectId` | >70% of queries are "tasks for project"; comments and status history co-located |
| assignees | `/id` | Assignees accessed by own ID |
| assigneeTasks | `/assigneeId` | Denormalized view: "tasks assigned to user" (change-feed populated) |

```
# PARTITION KEY: /projectId
# JUSTIFICATION: Tasks, comments, and status history are always queried within project context.
# Tasks-by-assignee served via denormalized assigneeTasks container.
```

## API Convention (MANDATORY — no deviation)

```
GET    /api/{resource}           → 200 + array
POST   /api/{resource}           → 201 + created object + Location header
GET    /api/{resource}/{id}      → 200 + object | 404
PATCH  /api/{resource}/{id}      → 200 + updated object | 404
DELETE /api/{resource}/{id}      → 204 | 404
GET    /api/health               → 200 + {"status": "healthy"}
```

### Domain-Specific Endpoints

```
GET    /api/projects/{projectId}/tasks?status=&priority=&page=    → 200 + filtered tasks
GET    /api/projects/{projectId}/tasks/{taskId}                    → 200 + task
PATCH  /api/projects/{projectId}/tasks/{taskId}                    → 200 + updated task
POST   /api/projects/{projectId}/tasks/{taskId}/transition         → 200 + task (body: { "status": "in_progress" })
GET    /api/projects/{projectId}/tasks/{taskId}/comments           → 200 + comments
POST   /api/projects/{projectId}/tasks/{taskId}/comments           → 201 + comment
GET    /api/projects/{projectId}/tasks/{taskId}/history            → 200 + status history
GET    /api/assignees/{assigneeId}/tasks                           → 200 + tasks assigned to user
GET    /api/projects/{projectId}/activity?from=&to=                → 200 + recent activity log
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Status machine**: Service layer validates transitions, rejects invalid ones with 409.
4. **Audit log**: Every status change creates a StatusHistory document.
5. **Error handling**: Map Cosmos status codes to HTTP status codes
6. **Health check**: `/api/health`

## Data Modeling Constraints

- `Task`: `id`, `projectId` (PK), `type: "task"`, `title`, `description`, `status`, `priority` (low/medium/high/critical), `assigneeId`, `labels` (array), `createdBy`, `createdAt`, `updatedAt`
- `Comment`: `id`, `projectId` (PK), `type: "comment"`, `taskId`, `authorId`, `body`, `createdAt`, `editedAt`
- `StatusHistory`: `id`, `projectId` (PK), `type: "statusHistory"`, `taskId`, `fromStatus`, `toStatus`, `changedBy`, `changedAt`, `reason`
- `Project`: `id`, `name`, `description`, `memberIds` (array), `createdAt`, `updatedAt`
- `Assignee`: `id`, `name`, `email`, `avatarUrl`
- `AssigneeTask`: `id`, `assigneeId` (PK), `taskId`, `projectId`, `title`, `status`, `priority`, `updatedAt`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS — set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination

## Anti-Patterns (REJECT — never generate these)

- ❌ Hardcoded connection strings or keys
- ❌ Cross-partition queries without explicit comment
- ❌ Deprecated SDK methods
- ❌ Creating CosmosClient per-request
- ❌ f-string interpolation in Cosmos SQL queries
- ❌ Loading unbounded result sets without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Allowing invalid status transitions
- ❌ Status changes without creating StatusHistory audit record
- ❌ Querying tasks-by-assignee via cross-partition scan at scale (use denormalized container)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, cross-partition for tasks-by-assignee acceptable
- If 1000-10000 RPS: Dedicated throughput on tasks, denormalized assigneeTasks via change feed
- If > 10000 RPS: Multi-region, change feed for denormalization, hierarchical partition key

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-workflow
  language: "{{language}}"
  generated_at: "{{ISO_8601_TIMESTAMP}}"

validation:
  - name: app-starts
    command: "{{start_command}}"
    expect: "listening on"
    timeout: 15s
  - name: health-check
    command: "curl -sf http://localhost:8000/api/health"
    expect: '{"status":"healthy"}'
  - name: crud-cycle
    script: tests/smoke.sh
  - name: status-transition
    script: tests/status-transition.sh

iteration:
  max_rounds: 3
  on_failure: fix-and-retry
  on_success: commit
```

---

## Language Appendix: Python

**MUST use when `{{language}}` = python**

### Versions & Dependencies (requirements.txt)
```
azure-cosmos>=4.9.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
```

### File Structure (MANDATORY)
```
{{app_name}}/
├── main.py
├── config.py
├── models.py            # Project, Task, Comment, StatusHistory, Assignee, AssigneeTask
├── repository.py        # TaskRepository, ProjectRepository, AssigneeTaskRepository
├── service.py           # TaskService (status machine + audit), ProjectService
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### Status Machine Pattern
```python
VALID_TRANSITIONS = {
    "backlog": ["todo"],
    "todo": ["in_progress"],
    "in_progress": ["in_review", "blocked"],
    "blocked": ["in_progress"],
    "in_review": ["done", "in_progress"],
    "done": [],
}

def validate_transition(current: str, target: str) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])
```

### NEVER use these
- ❌ `client.read_account()` — does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct`

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── Project.cs, Task.cs, Comment.cs, StatusHistory.cs, Assignee.cs
├── Repositories/
├── Services/
│   ├── TaskService.cs
│   └── ChangeFeedProcessor.cs (stub for assigneeTask sync)
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

---

## Language Appendix: Java

**MUST use when `{{language}}` = java**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/main/java/com/example/{{app_name}}/
│   ├── Application.java
│   ├── config/CosmosConfig.java
│   ├── model/Project.java, Task.java, Comment.java, StatusHistory.java, TaskStatus.java
│   ├── repository/
│   ├── service/TaskService.java
│   └── controller/TaskController.java, ProjectController.java
├── src/main/resources/application.yml
├── pom.xml
├── iteration-config.yaml
└── README.md
```

---

## Language Appendix: Node.js

**MUST use when `{{language}}` = node**

### File Structure (MANDATORY)
```
{{app_name}}/
├── src/
│   ├── index.js
│   ├── config.js
│   ├── models/
│   ├── repositories/
│   ├── services/
│   │   ├── taskService.js
│   │   └── changeFeedProcessor.js (stub)
│   └── routes/
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

---

## Output Checklist

- [ ] All files from language-specific file structure
- [ ] Partition key justification comments
- [ ] iteration-config.yaml
- [ ] .env.example
- [ ] README.md
- [ ] Health check at `/api/health`
- [ ] Status transition state machine with validation
- [ ] StatusHistory audit log on every transition
- [ ] Tasks-by-assignee via denormalized container (or cross-partition with comment)
- [ ] Comment CRUD on tasks
- [ ] Activity log endpoint
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"cosmos-intent-sdk"` on the `CosmosClient` for diagnostics and telemetry tracking.
