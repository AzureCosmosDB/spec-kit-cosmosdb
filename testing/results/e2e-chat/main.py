"""Chat API - FastAPI + Azure Cosmos DB"""
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, Header
from pydantic import BaseModel, Field
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions

ENDPOINT = "http://localhost:8081"
KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DATABASE_NAME = "chat_db"

client: Optional[CosmosClient] = None
db = None
users_container = None
conversations_container = None
messages_container = None
user_conversations_container = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, users_container, conversations_container, messages_container, user_conversations_container
    client = CosmosClient(ENDPOINT, credential=KEY)
    db = await client.create_database_if_not_exists(DATABASE_NAME)
    users_container = await db.create_container_if_not_exists(id="users", partition_key={"paths": ["/id"], "kind": "Hash"})
    conversations_container = await db.create_container_if_not_exists(id="conversations", partition_key={"paths": ["/id"], "kind": "Hash"})
    messages_container = await db.create_container_if_not_exists(id="messages", partition_key={"paths": ["/conversationId"], "kind": "Hash"})
    user_conversations_container = await db.create_container_if_not_exists(id="userConversations", partition_key={"paths": ["/userId"], "kind": "Hash"})
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)


class UserCreate(BaseModel):
    displayName: str
    email: str

class ConversationCreate(BaseModel):
    name: Optional[str] = None
    participantIds: list[str]

class MessageCreate(BaseModel):
    senderId: str
    body: str


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/users", status_code=201)
async def create_user(user: UserCreate):
    doc = {
        "id": str(uuid.uuid4()),
        "displayName": user.displayName,
        "email": user.email,
        "lastSeenAt": datetime.now(timezone.utc).isoformat(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = await users_container.create_item(body=doc)
    return result


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    try:
        return await users_container.read_item(item=user_id, partition_key=user_id)
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/api/conversations", status_code=201)
async def create_conversation(conv: ConversationCreate):
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": conv_id,
        "name": conv.name,
        "participantIds": conv.participantIds,
        "createdAt": now,
        "lastMessageAt": now,
    }
    result = await conversations_container.create_item(body=doc)
    # Create userConversation entries
    for uid in conv.participantIds:
        uc_doc = {
            "id": f"{uid}_{conv_id}",
            "userId": uid,
            "conversationId": conv_id,
            "lastReadAt": now,
            "joinedAt": now,
        }
        await user_conversations_container.create_item(body=uc_doc)
    return result


@app.post("/api/conversations/{conversation_id}/messages", status_code=201)
async def send_message(conversation_id: str, msg: MessageCreate):
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "conversationId": conversation_id,
        "senderId": msg.senderId,
        "body": msg.body,
        "createdAt": now,
        "editedAt": None,
        "deleted": False,
    }
    result = await messages_container.create_item(body=doc)
    # Update lastMessageAt
    try:
        conv = await conversations_container.read_item(item=conversation_id, partition_key=conversation_id)
        conv["lastMessageAt"] = now
        await conversations_container.replace_item(item=conversation_id, body=conv)
    except Exception:
        pass
    return result


@app.get("/api/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, pageSize: int = Query(default=50, le=100), continuationToken: Optional[str] = Query(default=None)):
    query = "SELECT * FROM c WHERE c.conversationId = @convId ORDER BY c.createdAt DESC"
    parameters = [{"name": "@convId", "value": conversation_id}]
    items = messages_container.query_items(
        query=query, parameters=parameters,
        partition_key=conversation_id, max_item_count=pageSize
    )
    results = []
    async for item in items:
        results.append(item)
        if len(results) >= pageSize:
            break
    return {"messages": results, "continuationToken": None}


@app.get("/api/users/{user_id}/conversations")
async def get_user_conversations(user_id: str):
    query = "SELECT * FROM c WHERE c.userId = @userId"
    parameters = [{"name": "@userId", "value": user_id}]
    items = user_conversations_container.query_items(query=query, parameters=parameters, partition_key=user_id)
    user_convs = [item async for item in items]
    
    results = []
    for uc in user_convs:
        # Count unread messages
        count_query = "SELECT VALUE COUNT(1) FROM c WHERE c.conversationId = @convId AND c.createdAt > @lastRead"
        count_params = [
            {"name": "@convId", "value": uc["conversationId"]},
            {"name": "@lastRead", "value": uc["lastReadAt"]},
        ]
        count_items = messages_container.query_items(
            query=count_query, parameters=count_params,
            partition_key=uc["conversationId"]
        )
        unread = 0
        async for c in count_items:
            unread = c
        results.append({
            "conversationId": uc["conversationId"],
            "lastReadAt": uc["lastReadAt"],
            "unreadCount": unread,
        })
    return results


@app.post("/api/users/{user_id}/conversations/{conversation_id}/read")
async def mark_read(user_id: str, conversation_id: str):
    doc_id = f"{user_id}_{conversation_id}"
    try:
        item = await user_conversations_container.read_item(item=doc_id, partition_key=user_id)
        item["lastReadAt"] = datetime.now(timezone.utc).isoformat()
        await user_conversations_container.replace_item(item=doc_id, body=item)
        return {"status": "ok"}
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
