---
description: "Generate a complete Azure Cosmos DB content management system with deterministic, production-ready architecture."
---

# /cosmos.scaffold-cms

> Generate a complete Azure Cosmos DB content management system with deterministic, production-ready architecture.

## Intent

Scaffold a full CMS application that uses Azure Cosmos DB as its primary data store. The output must be structurally identical across runs given the same inputs.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{app_description}}` | What the application does | "A content management system API" |
| `{{language}}` | Target language/framework | "python", "dotnet", "java", "node" |
| `{{entities}}` | Core domain entities (pre-set) | "Articles, Categories, Tags, Authors, Comments" |
| `{{primary_queries}}` | **The 3-5 most frequent read queries** | "Get published articles by category (paginated); Get article by slug; Get comments for an article; Get articles by author; Search articles by keyword" |
| `{{scale}}` | Expected throughput | "100 RPS" or "10K RPS" |
| `{{auth_model}}` | Authentication approach | "Azure AD" or "Connection string" |

## Domain: Content Management System

### Entities

| Entity | Container | Description |
|--------|-----------|-------------|
| Article | articles | Content with draft/publish workflow |
| Category | categories | Hierarchical content categories |
| Tag | articles | Co-located with articles (type discriminator) |
| Author | authors | Content creator profiles |
| Comment | comments | Threaded comments on articles |

### Draft/Publish Workflow

```
draft → review → published → archived
  ↑       ↓
  └── rejected
```

- `Article.status` enforced in service layer. Invalid transitions → 409.
- Published articles get `publishedAt` timestamp set automatically.
- Only `published` articles returned by default on public list endpoints (filter via query param `?status=draft` for admin).

### Comment Threads

- Comments support one level of nesting via `parentCommentId` (nullable).
- Top-level comments have `parentCommentId: null`.
- Replies reference parent. No deeper nesting.

## Critical: Partition Key Determination

| Container | Partition Key | Justification |
|-----------|--------------|---------------|
| articles | `/categoryId` | >70% of reads are "articles by category"; point-reads use id+categoryId |
| categories | `/id` | Categories accessed by own ID |
| authors | `/id` | Authors accessed by own ID |
| comments | `/articleId` | Comments always queried per-article |

```
# PARTITION KEY: /categoryId
# JUSTIFICATION: Primary query is "published articles by category". Point-reads
# for article-by-slug require slug→categoryId index or cross-partition query.
# Cross-partition required for: full-text search across categories, articles by author.
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
GET    /api/articles?category={categoryId}&status=published&page=1  → 200 + paginated articles
GET    /api/articles/slug/{slug}                                     → 200 + article | 404
POST   /api/articles/{articleId}/publish                             → 200 + updated article
POST   /api/articles/{articleId}/archive                             → 200 + updated article
GET    /api/articles/{articleId}/comments                            → 200 + threaded comments
POST   /api/articles/{articleId}/comments                            → 201 + comment
GET    /api/authors/{authorId}/articles                              → 200 + articles by author
GET    /api/articles/search?q=keyword                                → 200 + matching articles
```

## Architecture Requirements

1. **Layering**: Handlers/Routes → Services → Repository → Cosmos SDK
2. **CosmosClient**: Single instance, singleton.
3. **Configuration**: Environment variables with typed config.
4. **Error handling**: Map Cosmos status codes to HTTP status codes
5. **Health check**: `/api/health`
6. **Slug uniqueness**: Enforce unique slugs via conditional upsert or check-then-create with etag.

## Data Modeling Constraints

- `Article`: `id`, `categoryId` (PK), `authorId`, `title`, `slug`, `body`, `status`, `tags` (array of strings), `publishedAt`, `createdAt`, `updatedAt`
- `Category`: `id`, `name`, `slug`, `parentCategoryId` (nullable), `createdAt`
- `Author`: `id`, `name`, `bio`, `avatarUrl`, `createdAt`
- `Comment`: `id`, `articleId` (PK), `authorName`, `body`, `parentCommentId` (nullable), `createdAt`

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
- ❌ Allowing published articles to transition back to draft without going through archive
- ❌ Deeply nested comment threads (max 1 level)

## Scale Considerations for `{{scale}}`

- If < 1000 RPS: Shared throughput, autoscale
- If 1000-10000 RPS: Dedicated throughput on articles container
- If > 10000 RPS: Change feed for search index, multi-region reads

---

## iteration-config.yaml (ALWAYS generate this file)

```yaml
version: 1
scaffold:
  prompt: cosmos.scaffold-cms
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
  - name: publish-workflow
    script: tests/publish-workflow.sh

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
├── models.py            # Article, Category, Author, Comment
├── repository.py        # ArticleRepository, CommentRepository, AuthorRepository
├── service.py           # ArticleService (publish workflow), CommentService
├── requirements.txt
├── .env.example
├── iteration-config.yaml
└── README.md
```

### SDK Method Reference (use ONLY these)
```python
from azure.cosmos.aio import CosmosClient

# Article search (CROSS-PARTITION)
# CROSS-PARTITION: full-text search must span all categories
query = "SELECT * FROM c WHERE CONTAINS(LOWER(c.title), @keyword) AND c.status = @status"
parameters = [{"name": "@keyword", "value": keyword.lower()}, {"name": "@status", "value": "published"}]
items = container.query_items(query=query, parameters=parameters, partition_key=None, max_item_count=20)
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
│   ├── Article.cs
│   ├── Category.cs
│   ├── Author.cs
│   └── Comment.cs
├── Repositories/
├── Services/
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
│   ├── model/Article.java
│   ├── model/Category.java
│   ├── model/Author.java
│   ├── model/Comment.java
│   ├── model/ArticleStatus.java
│   ├── repository/ArticleRepository.java
│   ├── service/ArticleService.java
│   └── controller/ArticleController.java
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

---

## Output Checklist

- [ ] All files from language-specific file structure
- [ ] Partition key justification comments
- [ ] iteration-config.yaml
- [ ] .env.example
- [ ] README.md
- [ ] Health check at `/api/health`
- [ ] Draft/publish workflow with state machine
- [ ] Threaded comments (1 level nesting)
- [ ] Article search (cross-partition with comment)
- [ ] Slug-based article lookup
- [ ] Proper client lifecycle
- [ ] Parameterized queries
- [ ] Error mapping
