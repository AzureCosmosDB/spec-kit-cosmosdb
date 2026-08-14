#!/bin/bash
# E2E test script
BASE="http://localhost:8000"
RESULTS=""
PASS=0
FAIL=0

check() {
    local name="$1" expected_code="$2" actual_code="$3" body="$4"
    if [ "$actual_code" = "$expected_code" ]; then
        RESULTS+="| $name | PASS | $actual_code |\n"
        ((PASS++))
    else
        RESULTS+="| $name | FAIL | Expected $expected_code, got $actual_code. Body: $body |\n"
        ((FAIL++))
    fi
}

# Health
resp=$(curl -s -w "\n%{http_code}" $BASE/api/health)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | head -1)
check "GET /api/health" "200" "$code" "$body"

# Create customer
CUST='{"id":"cust-001","name":"Alice","email":"alice@test.com"}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$CUST" $BASE/api/customers)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/customers" "201" "$code" "$body"

# Get customer
resp=$(curl -s -w "\n%{http_code}" $BASE/api/customers/cust-001)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/customers/{id}" "200" "$code" "$body"

# Create products
PROD1='{"id":"prod-001","categoryId":"electronics","name":"Laptop","price":999.99,"stockCount":50}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD1" $BASE/api/products)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/products (Laptop)" "201" "$code" "$body"

PROD2='{"id":"prod-002","categoryId":"electronics","name":"Phone","price":699.99,"stockCount":100}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD2" $BASE/api/products)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/products (Phone)" "201" "$code" "$body"

PROD3='{"id":"prod-003","categoryId":"books","name":"Cosmos Guide","price":29.99,"stockCount":200}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD3" $BASE/api/products)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/products (Book)" "201" "$code" "$body"

# Get products by category
resp=$(curl -s -w "\n%{http_code}" $BASE/api/products/category/electronics)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/products/category/electronics" "200" "$code" "$body"

resp=$(curl -s -w "\n%{http_code}" $BASE/api/products/category/books)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/products/category/books" "200" "$code" "$body"

# Create order
ORDER='{"customerId":"cust-001","items":[{"productId":"prod-001","productName":"Laptop","quantity":1,"unitPrice":999.99},{"productId":"prod-002","productName":"Phone","quantity":2,"unitPrice":699.99}]}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$ORDER" $BASE/api/orders)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders" "201" "$code" "$body"
ORDER_ID=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Get order history by customer
resp=$(curl -s -w "\n%{http_code}" $BASE/api/customers/cust-001/orders)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/customers/{id}/orders" "200" "$code" "$body"

# Get order by ID
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders/$ORDER_ID?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/orders/{id}?customerId" "200" "$code" "$body"

# Get order items
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders/$ORDER_ID/items?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/orders/{id}/items" "200" "$code" "$body"

# Transition: placed -> paid
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/pay?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders/{id}/pay (placed→paid)" "200" "$code" "$body"

# Transition: paid -> shipped
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/ship?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders/{id}/ship (paid→shipped)" "200" "$code" "$body"

# Invalid transition: shipped -> paid (should 409)
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/pay?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders/{id}/pay (shipped→paid, invalid=409)" "409" "$code" "$body"

# List orders by status
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders?status=shipped")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "GET /api/orders?status=shipped" "200" "$code" "$body"

# Create second order and cancel it (test restock)
ORDER2='{"customerId":"cust-001","items":[{"productId":"prod-003","productName":"Cosmos Guide","quantity":3,"unitPrice":29.99}]}'
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$ORDER2" $BASE/api/orders)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders (2nd order)" "201" "$code" "$body"
ORDER2_ID=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Cancel it
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER2_ID/cancel?customerId=cust-001")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders/{id}/cancel (placed→cancelled)" "200" "$code" "$body"

# Summary
echo ""
echo "# E2E Test Results"
echo ""
echo "| Endpoint | Result | Details |"
echo "|----------|--------|---------|"
echo -e "$RESULTS"
echo ""
echo "**Total: $PASS passed, $FAIL failed**"
