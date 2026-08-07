#!/bin/bash
# E2E test script with unique IDs
BASE="http://localhost:8000"
RESULTS=""
PASS=0
FAIL=0
TS=$(date +%s)

check() {
    local name="$1" expected_code="$2" actual_code="$3" body="$4"
    if [ "$actual_code" = "$expected_code" ]; then
        RESULTS+="| $name | ✅ PASS | $actual_code |\n"
        ((PASS++))
    else
        RESULTS+="| $name | ❌ FAIL | Expected $expected_code, got $actual_code |\n"
        ((FAIL++))
    fi
}

# Health
resp=$(curl -s -w "\n%{http_code}" $BASE/api/health)
code=$(echo "$resp" | tail -1)
check "GET /api/health" "200" "$code"

# Create customer
CUST="{\"id\":\"cust-$TS\",\"name\":\"Alice\",\"email\":\"alice@test.com\"}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$CUST" $BASE/api/customers)
code=$(echo "$resp" | tail -1)
check "POST /api/customers" "201" "$code"

# Get customer
resp=$(curl -s -w "\n%{http_code}" $BASE/api/customers/cust-$TS)
code=$(echo "$resp" | tail -1)
check "GET /api/customers/{id}" "200" "$code"

# Create products
PROD1="{\"id\":\"prod-$TS-1\",\"categoryId\":\"electronics\",\"name\":\"Laptop\",\"price\":999.99,\"stockCount\":50}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD1" $BASE/api/products)
code=$(echo "$resp" | tail -1)
check "POST /api/products (Laptop)" "201" "$code"

PROD2="{\"id\":\"prod-$TS-2\",\"categoryId\":\"electronics\",\"name\":\"Phone\",\"price\":699.99,\"stockCount\":100}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD2" $BASE/api/products)
code=$(echo "$resp" | tail -1)
check "POST /api/products (Phone)" "201" "$code"

PROD3="{\"id\":\"prod-$TS-3\",\"categoryId\":\"books\",\"name\":\"Cosmos Guide\",\"price\":29.99,\"stockCount\":200}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$PROD3" $BASE/api/products)
code=$(echo "$resp" | tail -1)
check "POST /api/products (Book)" "201" "$code"

# Get products by category
resp=$(curl -s -w "\n%{http_code}" $BASE/api/products/category/electronics)
code=$(echo "$resp" | tail -1)
check "GET /api/products/category/electronics" "200" "$code"

resp=$(curl -s -w "\n%{http_code}" $BASE/api/products/category/books)
code=$(echo "$resp" | tail -1)
check "GET /api/products/category/books" "200" "$code"

# Create order
ORDER="{\"customerId\":\"cust-$TS\",\"items\":[{\"productId\":\"prod-$TS-1\",\"productName\":\"Laptop\",\"quantity\":1,\"unitPrice\":999.99},{\"productId\":\"prod-$TS-2\",\"productName\":\"Phone\",\"quantity\":2,\"unitPrice\":699.99}]}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$ORDER" $BASE/api/orders)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders" "201" "$code"
ORDER_ID=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Get order history by customer
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/customers/cust-$TS/orders")
code=$(echo "$resp" | tail -1)
check "GET /api/customers/{id}/orders (order history)" "200" "$code"

# Get order by ID
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders/$ORDER_ID?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "GET /api/orders/{id}?customerId" "200" "$code"

# Get order items
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders/$ORDER_ID/items?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "GET /api/orders/{id}/items" "200" "$code"

# Transition: placed -> paid
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/pay?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "POST /orders/{id}/pay (placed→paid)" "200" "$code"

# Transition: paid -> shipped
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/ship?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "POST /orders/{id}/ship (paid→shipped)" "200" "$code"

# Invalid transition: shipped -> paid (should 409)
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER_ID/pay?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "POST /orders/{id}/pay (shipped→paid INVALID=409)" "409" "$code"

# List orders by status
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/orders?status=shipped")
code=$(echo "$resp" | tail -1)
check "GET /api/orders?status=shipped" "200" "$code"

# Create second order and cancel it
ORDER2="{\"customerId\":\"cust-$TS\",\"items\":[{\"productId\":\"prod-$TS-3\",\"productName\":\"Cosmos Guide\",\"quantity\":3,\"unitPrice\":29.99}]}"
resp=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$ORDER2" $BASE/api/orders)
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
check "POST /api/orders (2nd order)" "201" "$code"
ORDER2_ID=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

# Cancel it
resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/orders/$ORDER2_ID/cancel?customerId=cust-$TS")
code=$(echo "$resp" | tail -1)
check "POST /orders/{id}/cancel (placed→cancelled)" "200" "$code"

# Verify stock was restored after cancel (product should have 200 again)
resp=$(curl -s -w "\n%{http_code}" "$BASE/api/products/category/books")
code=$(echo "$resp" | tail -1)
body=$(echo "$resp" | sed '$d')
STOCK=$(echo "$body" | python3 -c "
import sys,json
products = json.load(sys.stdin)
for p in products:
    if p['id'] == 'prod-$TS-3':
        print(p['stockCount'])
        break
" 2>/dev/null)
if [ "$STOCK" = "200" ]; then
    RESULTS+="| Stock restored after cancel | ✅ PASS | stockCount=200 |\n"
    ((PASS++))
else
    RESULTS+="| Stock restored after cancel | ❌ FAIL | stockCount=$STOCK (expected 200) |\n"
    ((FAIL++))
fi

# Summary
echo ""
echo "# E2E Test Results — E-commerce Scaffold"
echo ""
echo "| Endpoint | Result | Details |"
echo "|----------|--------|---------|"
echo -e "$RESULTS"
echo ""
echo "**Total: $PASS passed, $FAIL failed out of $((PASS+FAIL)) tests**"
