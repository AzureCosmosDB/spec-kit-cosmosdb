---
description: "Generate a complete Azure Cosmos DB social feed/timeline application with deterministic, production-ready architecture."
---

# /cosmos.scaffold-social

> Generate a complete Azure Cosmos DB social feed/timeline application with deterministic, production-ready architecture.

## Intent

Scaffold a full social feed application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A social feed/timeline API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Users, Posts, Likes, Follows, Comments" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get feed for a user (timeline); Get posts by a user; Get comments for a post; Get followers/following for a user; Get like count for a post" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Social Feed/Timeline

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| User | users | User profiles |
| Post | posts | User-created content |
| Like | posts | Co-located with post (type discriminator) |
| Follow | follows | Follower/following relationships |
| Comment | posts | Co-located with post (type discriminator) |
| FeedItem | feeds | Denormalized timeline entries (fan-out on write) |

### Fan-Out on Write Pattern

When a user creates a post:
1. Write the post to `posts` container (partition key `/authorId`).
2. Query `follows` container for all followers of the author.
3. For each follower, write a `FeedItem` to the `feeds` container (partition key `/userId`).
4. Fan-out SHOULD be async (change feed processor or background task). Stub the handler in code.

### Activity Notifications

- When a post receives a like or comment, create a notification document in a `notifications` container (partition key `/recipientUserId`).
- Notifications have `read` boolean flag.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| users | `/id` | Users accessed by own ID |
| posts | `/authorId` | "Get posts by user" is primary; comments/likes co-located via type discriminator |
| follows | `/followerId` | "Get who I follow" is the primary read (for fan-out source) |
| feeds | `/userId` | "Get my feed" is the #1 query — each user's timeline is a single partition |
| notifications | `/recipientUserId` | Notifications always queried per-user |

```
# PARTITION KEY: /userId
# JUSTIFICATION: Feed is always read per-user. Fan-out on write ensures each user's
# feed is a single-partition read. Trade-off: write amplification on post creation.
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
GET    /api/users/{userId}/feed?pageSize=20&continuationToken=  → 200 + feed items
GET    /api/users/{userId}/posts                                 → 200 + user's posts
POST   /api/posts                                                → 201 + post (triggers fan-out)
POST   /api/posts/{postId}/like                                  → 201 + like
DELETE /api/posts/{postId}/like                                  → 204 (unlike)
GET    /api/posts/{postId}/comments                              → 200 + comments
POST   /api/posts/{postId}/comments                              → 201 + comment
POST   /api/users/{userId}/follow/{targetUserId}                 → 201 + follow
DELETE /api/users/{userId}/follow/{targetUserId}                 → 204 (unfollow)
GET    /api/users/{userId}/followers                             → 200 + follower list
GET    /api/users/{userId}/following                             → 200 + following list
GET    /api/users/{userId}/notifications                         → 200 + notifications
POST   /api/users/{userId}/notifications/read                    → 200 (mark all read)
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Fan-out**: Stub change feed processor or background task for timeline fan-out.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`

## Data Modeling Constraints

- `Post`: `id`, `authorId` (PK), `type: "post"`, `body`, `mediaUrl` (nullable), `likeCount` (denormalized), `commentCount` (denormalized), `createdAt`
- `Like`: `id`, `authorId` (PK = post's authorId), `type: "like"`, `postId`, `userId`, `createdAt`
- `Comment`: `id`, `authorId` (PK = post's authorId), `type: "comment"`, `postId`, `userId`, `body`, `createdAt`
- `Follow`: `id`, `followerId` (PK), `followeeId`, `createdAt`
- `FeedItem`: `id`, `userId` (PK), `postId`, `authorId`, `authorName`, `bodyPreview`, `createdAt`
- `User`: `id`, `displayName`, `bio`, `avatarUrl`, `followerCount`, `followingCount`, `createdAt`

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
- ❌ Loading unbounded feed without pagination
- ❌ Missing client.close() / dispose on shutdown
- ❌ Fan-out on read (querying all followed users' posts at read time) — use fan-out on write
- ❌ Synchronous fan-out in the post-creation request path (must be async)
- ❌ Maintaining like/comment counts via cross-partition aggregation queries (use denormalized counters)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, synchronous fan-out acceptable for small follower counts
- If 1000-10000 RPS: Dedicated throughput on feeds and posts, async fan-out mandatory
- If > 10000 RPS: Multi-region, change feed for fan-out, celebrity fan-out capping

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: cosmos.scaffold-social
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
  - name: feed-query
    script: tests/feed-query.sh

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
├── models.py            # User, Post, Like, Comment, Follow, FeedItem
├── repository.py        # PostRepository, FeedRepository, FollowRepository, NotificationRepository
├── service.py           # PostService (with fan-out stub), FeedService, FollowService
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
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
│   ├── User.cs, Post.cs, Like.cs, Comment.cs, Follow.cs, FeedItem.cs
├── Repositories/
├── Services/
│   ├── PostService.cs
│   ├── FeedService.cs
│   └── FanOutProcessor.cs
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
│   ├── model/Post.java, User.java, Follow.java, FeedItem.java
│   ├── repository/
│   ├── service/PostService.java, FeedService.java
│   └── controller/
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
│   │   └── fanOutService.js
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
- [ ] Fan-out on write stub (change feed or background task)
- [ ] Denormalized counters for likes/comments
- [ ] Feed pagination with continuation tokens
- [ ] Follow/unfollow with follower count updates
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping
