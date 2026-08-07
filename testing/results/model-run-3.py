"""
Cosmos DB Document Models for Multi-tenant SaaS Application
Scale: 10K organizations, 500K users, 5M documents

Design decisions:
- Users partitioned by orgId (primary query pattern: list users in org)
- Documents partitioned by userId (primary query pattern: list docs by user)
- Org-level document queries handled via change feed materialized view
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrgPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# -------------------------------------------------------
# Organization
# Container: organizations | Partition key: /id
# Rationale: Orgs are looked up by ID. 10K distinct values = high cardinality.
# Estimated doc size: ~0.5 KB
# -------------------------------------------------------

@dataclass
class Organization:
    id: str
    name: str
    plan: OrgPlan
    owner_user_id: str
    type: str = "organization"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# -------------------------------------------------------
# User
# Container: users | Partition key: /orgId
# Rationale: Most frequent query is "list users in org".
# 10K orgs => 10K partitions, ~50 users/partition. Even write distribution.
# Estimated doc size: ~0.7 KB
# -------------------------------------------------------

@dataclass
class User:
    id: str
    org_id: str  # partition key
    email: str
    display_name: str
    role: UserRole
    type: str = "user"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# -------------------------------------------------------
# Document
# Container: documents | Partition key: /userId
# Rationale: Primary access = "get documents for a user". 500K users = excellent
# cardinality and write distribution (~10 docs/partition).
# For org-level queries: denormalize orgId and use composite index,
# or maintain a materialized view partitioned by orgId.
# Estimated doc size: ~1.0 KB (content stored externally)
# -------------------------------------------------------

@dataclass
class Document:
    id: str
    user_id: str  # partition key
    org_id: str  # denormalized for cross-reference
    title: str
    blob_reference: str  # Azure Blob Storage URL
    mime_type: str
    size_bytes: int
    tags: list[str] = field(default_factory=list)  # bounded, max 30
    type: str = "document"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# -------------------------------------------------------
# Example JSON Documents
# -------------------------------------------------------

EXAMPLE_ORGANIZATION = {
    "id": "org-0001",
    "name": "Contoso Ltd",
    "plan": "enterprise",
    "ownerUserId": "user-1001",
    "type": "organization",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-06-15T12:00:00Z"
}

EXAMPLE_USER = {
    "id": "user-1001",
    "orgId": "org-0001",
    "email": "bob@contoso.com",
    "displayName": "Bob Johnson",
    "role": "owner",
    "type": "user",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-05-10T08:30:00Z"
}

EXAMPLE_DOCUMENT = {
    "id": "doc-500001",
    "userId": "user-1001",
    "orgId": "org-0001",
    "title": "Product Requirements Document",
    "blobReference": "https://myaccount.blob.core.windows.net/documents/doc-500001.pdf",
    "mimeType": "application/pdf",
    "sizeBytes": 524288,
    "tags": ["product", "requirements", "2024"],
    "type": "document",
    "createdAt": "2024-03-01T10:00:00Z",
    "updatedAt": "2024-03-05T16:45:00Z"
}

# -------------------------------------------------------
# Container Configurations
# -------------------------------------------------------

CONTAINER_CONFIGS = {
    "organizations": {
        "partition_key": "/id",
        "default_ttl": None,
        "indexing_policy": {
            "includedPaths": [{"path": "/name/?"}],
            "excludedPaths": [{"path": "/*"}],
        },
    },
    "users": {
        "partition_key": "/orgId",
        "default_ttl": None,
        "indexing_policy": {
            "includedPaths": [
                {"path": "/orgId/?"},
                {"path": "/email/?"},
                {"path": "/role/?"},
            ],
            "excludedPaths": [{"path": "/*"}],
            "compositeIndexes": [
                [
                    {"path": "/orgId", "order": "ascending"},
                    {"path": "/createdAt", "order": "descending"},
                ]
            ],
        },
    },
    "documents": {
        "partition_key": "/userId",
        "default_ttl": None,
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
    },
}
