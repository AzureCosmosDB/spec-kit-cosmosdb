"""
Cosmos DB Document Models for Multi-tenant SaaS Application
Entities: Organization, User, Document
Scale: 10K orgs, 500K users, 5M documents
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


# --- Organization Model ---

@dataclass
class Organization:
    """
    Partition key: `/id` (orgId)
    Justification: Organizations are accessed by their own ID. High cardinality (10K).
    Each org is a natural partition boundary for org-level queries.
    """
    id: str
    name: str
    plan: str  # "free", "pro", "enterprise"
    type: str = "organization"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# --- User Model ---

@dataclass
class User:
    """
    Partition key: `/orgId`
    Justification: Users belong to one org. Most queries fetch users within an org.
    High cardinality (10K orgs), even distribution (~50 users per org).
    """
    id: str
    org_id: str  # partition key
    email: str
    display_name: str
    role: str  # "admin", "member", "viewer"
    type: str = "user"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# --- Document Model ---

@dataclass
class Document:
    """
    Partition key: `/userId`
    Justification: Documents are read-heavy, queried by user (primary access pattern).
    500K users gives high cardinality and even distribution (~10 docs per user).
    For org-level queries, use a separate container or change feed + materialized view.
    """
    id: str
    user_id: str  # partition key
    org_id: str  # denormalized for org-level queries via secondary index
    title: str
    content_ref: str  # reference to Azure Blob Storage for large content
    size_bytes: int
    tags: list[str] = field(default_factory=list)  # bounded, < 50 tags
    type: str = "document"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# --- Example Documents ---

EXAMPLE_ORGANIZATION = {
    "id": "org-001",
    "name": "Acme Corp",
    "plan": "enterprise",
    "type": "organization",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-06-01T14:22:00Z"
}

EXAMPLE_USER = {
    "id": "user-12345",
    "orgId": "org-001",
    "email": "alice@acme.com",
    "displayName": "Alice Smith",
    "role": "admin",
    "type": "user",
    "createdAt": "2024-02-01T09:00:00Z",
    "updatedAt": "2024-05-20T11:15:00Z"
}

EXAMPLE_DOCUMENT = {
    "id": "doc-99001",
    "userId": "user-12345",
    "orgId": "org-001",
    "title": "Q2 Report",
    "contentRef": "https://storage.blob.core.windows.net/docs/doc-99001.pdf",
    "sizeBytes": 245000,
    "tags": ["report", "q2", "finance"],
    "type": "document",
    "createdAt": "2024-06-10T08:00:00Z",
    "updatedAt": "2024-06-10T08:00:00Z"
}


# --- Container Configuration ---

CONTAINERS = {
    "organizations": {
        "partition_key": "/id",
        "indexing_policy": {
            "includedPaths": [{"path": "/name/?"}],
            "excludedPaths": [{"path": "/*"}],
        },
        "estimated_doc_size_kb": 0.5,
    },
    "users": {
        "partition_key": "/orgId",
        "indexing_policy": {
            "includedPaths": [
                {"path": "/orgId/?"},
                {"path": "/email/?"},
                {"path": "/role/?"},
            ],
            "excludedPaths": [{"path": "/*"}],
        },
        "estimated_doc_size_kb": 0.8,
    },
    "documents": {
        "partition_key": "/userId",
        "indexing_policy": {
            "includedPaths": [
                {"path": "/userId/?"},
                {"path": "/orgId/?"},
                {"path": "/createdAt/?"},
                {"path": "/tags/[]/?"},
            ],
            "excludedPaths": [{"path": "/*"}],
            "compositeIndexes": [
                [
                    {"path": "/userId", "order": "ascending"},
                    {"path": "/createdAt", "order": "descending"},
                ]
            ],
        },
        "estimated_doc_size_kb": 1.0,
    },
}
