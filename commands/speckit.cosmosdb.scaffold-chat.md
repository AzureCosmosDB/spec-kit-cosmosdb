---
description: "Generate a complete Azure Cosmos DB real-time chat application with deterministic, production-ready architecture."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.scaffold-chat

> Generate a complete Azure Cosmos DB real-time chat application with deterministic, production-ready architecture.

## Intent

Scaffold a full real-time chat application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A real-time chat API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Conversations, Messages, Users" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get messages for a conversation (paginated, newest first); Get conversations for a user; Get user by ID; Get unread count per conversation for a user; Search messages by keyword in a conversation" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Real-Time Chat

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| User | users | User profile, display name, presence status |
| Conversation | conversations | Chat room or DM metadata, participant list |
| Message | messages | Individual chat messages |

### Key Patterns

- **Message history**: Messages partitioned by `conversationId`, queried newest-first with continuation token pagination.
- **Unread counts**: Each user's last-read timestamp per conversation stored in a `userConversations` container (partition key `/userId`). Unread count = messages after last-read timestamp.
- **User presence**: `lastSeenAt` timestamp on User document. Presence is "online" if within 5 minutes.
- **Message search**: SQL `CONTAINS()` or `LIKE` on message body within a conversation partition.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| users | `/id` | Users accessed by own ID |
| conversations | `/id` | Conversations accessed by own ID; participant lookup via userConversations |
| messages | `/conversationId` | >90% of queries are "get messages for conversation" |
| userConversations | `/userId` | "Get conversations for user" and "unread counts for user" |

```
# PARTITION KEY: /conversationId
# JUSTIFICATION: Messages are always queried within a conversation context.
# Cross-partition required for: global message search (not supported - search within conversation only).
```

## API Convention (MANDATORY - no deviation)

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
GET    /api/conversations/{conversationId}/messages?pageSize=50&continuationToken= → 200 + messages + continuation
POST   /api/conversations/{conversationId}/messages  → 201 + message
GET    /api/users/{userId}/conversations             → 200 + array of conversation summaries with unread counts
POST   /api/users/{userId}/conversations/{conversationId}/read  → 200 (mark as read, update lastReadAt)
GET    /api/conversations/{conversationId}/messages/search?q=keyword  → 200 + matching messages
PATCH  /api/users/{userId}/presence                  → 200 + updated presence
```

Rules:
- Resource names are **plural**
- All request/response bodies use **camelCase**
- Message list MUST support continuation-token pagination (not offset-based)
- Messages returned newest-first (`ORDER BY c.createdAt DESC`)

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Configuration**: Environment variables with typed config.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`
6. **Pagination**: Continuation-token based for message history. Max page size 100.

## Data Modeling Constraints

- `Message`: `id`, `conversationId` (PK), `senderId`, `body`, `createdAt`, `editedAt` (nullable), `deleted` (boolean, soft-delete)
- `Conversation`: `id`, `name` (nullable for DMs), `participantIds` (array), `createdAt`, `lastMessageAt`
- `User`: `id`, `displayName`, `email`, `lastSeenAt`, `createdAt`
- `UserConversation`: `id` (composite `userId_conversationId`), `userId` (PK), `conversationId`, `lastReadAt`, `joinedAt`

## Connection & Resilience

- Retry configuration: max 9 attempts, 30s max wait on 429s
- Connection mode: Direct for production, Gateway for emulator
- ⚠️ Linux emulator (vnext) uses HTTP not HTTPS - set `connection_verify=False` or `disable_ssl_verification=True` for local dev
- Client shutdown/cleanup on app termination

## Anti-Patterns (REJECT - never generate these)

- ❌ Hardcoded connection strings or keys
- ❌ Cross-partition queries without explicit comment
- ❌ Deprecated SDK methods
- ❌ Creating CosmosClient per-request
- ❌ Using offset-based pagination for message history (use continuation tokens)
- ❌ f-string interpolation in Cosmos SQL queries
- ❌ Loading entire message history without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Storing unread counts as a mutable counter (use timestamp comparison instead)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, single partition key
- If 1000-10000 RPS: Dedicated throughput on messages container
- If > 10000 RPS: Change feed for real-time notifications, multi-region

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: speckit.cosmosdb.scaffold-chat
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
  - name: message-pagination
    script: tests/message-pagination.sh

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
├── models.py            # User, Conversation, Message, UserConversation
├── repository.py        # MessageRepository, ConversationRepository, UserRepository
├── service.py           # ChatService, PresenceService
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Method Reference (use ONLY these)
```python
from azure.cosmos.aio import CosmosClient

# Continuation-token pagination
query = "SELECT * FROM c WHERE c.conversationId = @convId ORDER BY c.createdAt DESC"
parameters = [{"name": "@convId", "value": conv_id}]
items = container.query_items(query=query, parameters=parameters, partition_key=conv_id, max_item_count=page_size)
page = await items.by_page(continuation_token).next()
results = [item async for item in page]
new_token = items.continuation_token
```

### NEVER use these (deprecated/wrong in Python SDK)
- ❌ `client.read_account()` - does not exist; use `client.get_database_account()`
- ❌ `ConnectionMode.Direct`

---

## Language Appendix: .NET (C#)

**MUST use when `{{language}}` = dotnet**

### File Structure (MANDATORY)
```
{{app_name}}/
├── Program.cs
├── Models/
│   ├── User.cs
│   ├── Conversation.cs
│   ├── Message.cs
│   └── UserConversation.cs
├── Repositories/
├── Services/
├── Configuration/
│   └── CosmosSettings.cs
├── {{app_name}}.csproj
├── appsettings.json
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```csharp
// Continuation-token pagination
var query = new QueryDefinition("SELECT * FROM c WHERE c.conversationId = @convId ORDER BY c.createdAt DESC")
    .WithParameter("@convId", conversationId);
var options = new QueryRequestOptions { MaxItemCount = pageSize, PartitionKey = new PartitionKey(conversationId) };
var iterator = container.GetItemQueryIterator<Message>(query, continuationToken, options);
var page = await iterator.ReadNextAsync();
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
│   ├── model/Message.java
│   ├── model/Conversation.java
│   ├── model/User.java
│   ├── repository/MessageRepository.java
│   ├── service/ChatService.java
│   └── controller/ChatController.java
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
│   └── routes/
├── package.json
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Patterns
```javascript
// Continuation-token pagination
const { resources, continuationToken } = await container.items.query(
    { query: "SELECT * FROM c WHERE c.conversationId = @convId ORDER BY c.createdAt DESC",
      parameters: [{ name: "@convId", value: conversationId }] },
    { partitionKey: conversationId, maxItemCount: pageSize, continuationToken: token }
).fetchNext();
```

---

## Output Checklist

- [ ] All files from language-specific file structure
- [ ] Partition key justification comments
- [ ] iteration-config.yaml
- [ ] .env.example
- [ ] README.md
- [ ] Health check at `/api/health`
- [ ] Continuation-token pagination for messages
- [ ] Unread count via timestamp comparison
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping

## Telemetry

- **Always** set `user_agent_suffix` (Python/Java) or `ApplicationName` (.NET) to `"cosmos-intent-sdk"` on the `CosmosClient` for diagnostics and telemetry tracking.
