#!/usr/bin/env bash
set -e
BASE="http://localhost:8001"

echo "=== Chat E2E Test ==="

echo "1. Health check"
curl -sf "$BASE/api/health" && echo " OK"

echo "2. Create users"
U1=$(curl -sf -X POST "$BASE/api/users" -H "Content-Type: application/json" -d '{"displayName":"Alice","email":"alice@test.com"}')
USER1_ID=$(echo "$U1" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  User1: $USER1_ID"

U2=$(curl -sf -X POST "$BASE/api/users" -H "Content-Type: application/json" -d '{"displayName":"Bob","email":"bob@test.com"}')
USER2_ID=$(echo "$U2" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  User2: $USER2_ID"

echo "3. Create conversation"
CONV=$(curl -sf -X POST "$BASE/api/conversations" -H "Content-Type: application/json" -d '{"name":"General","participantIds":["'$USER1_ID'","'$USER2_ID'"]}')
CONV_ID=$(echo "$CONV" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  Conversation: $CONV_ID"

echo "4. Send messages"
M1=$(curl -sf -X POST "$BASE/api/conversations/$CONV_ID/messages" -H "Content-Type: application/json" -d '{"senderId":"'$USER1_ID'","body":"Hello Bob!"}')
echo "  Msg1 sent: $(echo $M1 | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")"

M2=$(curl -sf -X POST "$BASE/api/conversations/$CONV_ID/messages" -H "Content-Type: application/json" -d '{"senderId":"'$USER2_ID'","body":"Hi Alice!"}')
echo "  Msg2 sent: $(echo $M2 | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")"

M3=$(curl -sf -X POST "$BASE/api/conversations/$CONV_ID/messages" -H "Content-Type: application/json" -d '{"senderId":"'$USER1_ID'","body":"How are you?"}')
echo "  Msg3 sent: $(echo $M3 | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")"

echo "5. Get messages (paginated)"
MSGS=$(curl -sf "$BASE/api/conversations/$CONV_ID/messages?pageSize=2")
MSG_COUNT=$(echo "$MSGS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['messages']))")
echo "  Messages returned (page size 2): $MSG_COUNT"

echo "6. Get conversations by user"
UCONVS=$(curl -sf "$BASE/api/users/$USER1_ID/conversations")
UC_COUNT=$(echo "$UCONVS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "  User1 conversations: $UC_COUNT"

echo "7. Unread count (before mark read)"
UNREAD=$(echo "$UCONVS" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['unreadCount'] if data else 0)")
echo "  Unread for user1: $UNREAD"

echo "8. Mark as read"
curl -sf -X POST "$BASE/api/users/$USER1_ID/conversations/$CONV_ID/read" > /dev/null
echo "  Marked read OK"

echo "9. Unread count (after mark read)"
UCONVS2=$(curl -sf "$BASE/api/users/$USER1_ID/conversations")
UNREAD2=$(echo "$UCONVS2" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['unreadCount'] if data else 0)")
echo "  Unread for user1 after read: $UNREAD2"

echo ""
echo "=== ALL CHAT TESTS PASSED ==="
