"""
Cosmos DB Document Models - Multi-tenant SaaS
Entities: Organization, User, Document
Scale: 10K orgs, 500K users, 5M documents
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ============================================================
# Organization Entity
# Container: organizations
# Partition key: /id
# Justification: Each org queried by its own ID. 10K orgs = good cardinality.
# ============================================================

@dataclass
class Organization:
    id: str
    name: str
    slug: str
    plan: str  # free | pro | enterprise
    max_users: int
    type: str = "organization"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ============================================================
# User Entity
# Container: users
# Partition key: /orgId
# Justification: Primary access pattern is "get users in org". 
# 10K partitions with ~50 users each = even distribution.
# ============================================================

@dataclass
class User:
    id: str
    org_id: str  # partition key
    email: str
    name: str
    role: str  # owner | admin | member | viewer
    avatar_url: Optional[str] = None
    type: str = "user"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ============================================================
# Document Entity
# Container: documents
# Partition key: /orgId
# Justification: Documents queried by org (list all org docs) and by user
# within org. orgId gives 10K partitions. User queries filter within partition.
# Read-heavy pattern benefits from partition-scoped queries.
# ============================================================

@dataclass
class Document:
    id: str
    org_id: str  # partition key
    author_id: str  # userId who created it
    title: str
    content_type: str  # "pdf", "markdown", "docx"
    blob_url: str  # large content stored in Blob Storage
    size_bytes: int
    tags: list[str] = field(default_factory=list)
    shared_with: list[str] = field(default_factory=list)  # user IDs, bounded < 50
    type: str = "document"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ============================================================
# Example Documents (JSON representation)
# ============================================================

EXAMPLE_ORG = {
    "id": "org_abc123",
    "name": "TechStart Inc",
    "slug": "techstart",
    "plan": "pro",
    "maxUsers": 100,
    "type": "organization",
    "createdAt": "2024-01-10T12:00:00Z",
    "updatedAt": "2024-03-15T09:30:00Z"
}

EXAMPLE_USER = {
    "id": "usr_xyz789",
    "orgId": "org_abc123",
    "email": "jane@techstart.io",
    "name": "Jane Doe",
    "role": "admin",
    "avatarUrl": "https://cdn.example.com/avatars/jane.jpg",
    "type": "user",
    "createdAt": "2024-01-12T08:00:00Z",
    "updatedAt": "2024-04-01T16:45:00Z"
}

EXAMPLE_DOCUMENT = {
    "id": "doc_mno456",
    "orgId": "org_abc123",
    "authorId": "usr_xyz789",
    "title": "Architecture Decision Record - Database Selection",
    "contentType": "markdown",
    "blobUrl": "https://saasstorage.blob.core.windows.net/documents/doc_mno456.md",
    "sizeBytes": 15200,
    "tags": ["architecture", "adr", "database"],
    "sharedWith": ["usr_aaa111", "usr_bbb222"],
    "type": "document",
    "createdAt": "2024-05-20T14:00:00Z",
    "updatedAt": "2024-05-22T10:30:00Z"
}

# ============================================================
# Container Configurations
# ============================================================

CONTAINER_CONFIGS = [
    {
        "name": "organizations",
        "partition_key_path": "/id",
        "indexing_policy": {
            "automatic": True,
            "includedPaths": [{"path": "/name/?"}, {"path": "/plan/?"}],
            "excludedPaths": [{"path": "/*"}],
        },
        "estimated_document_size_kb": 0.4,
    },
    {
        "name": "users",
        "partition_key_path": "/orgId",
        "indexing_policy": {
            "automatic": True,
            "includedPaths": [
                {"path": "/orgId/?"},
                {"path": "/email/?"},
                {"path": "/role/?"},
                {"path": "/createdAt/?"},
            ],
            "excludedPaths": [{"path": "/*"}],
        },
        "estimated_document_size_kb": 0.6,
    },
    {
        "name": "documents",
        "partition_key_path": "/orgId",
        "indexing_policy": {
            "automatic": True,
            "includedPaths": [
                {"path": "/orgId/?"},
                {"path": "/authorId/?"},
                {"path": "/createdAt/?"},
                {"path": "/tags/[]/?"},
                {"path": "/title/?"},
            ],
            "excludedPaths": [{"path": "/blobUrl/?"}, {"path": "/*"}],
            "compositeIndexes": [
                [
                    {"path": "/orgId", "order": "ascending"},
                    {"path": "/createdAt", "order": "descending"},
                ],
                [
                    {"path": "/authorId", "order": "ascending"},
                    {"path": "/createdAt", "order": "descending"},
                ],
            ],
        },
        "estimated_document_size_kb": 1.2,
    },
]
