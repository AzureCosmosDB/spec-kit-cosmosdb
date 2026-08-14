"""Live test against Cosmos DB emulator."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from azure.cosmos import CosmosClient, PartitionKey
from repository import Product, ProductRepository

ENDPOINT = "http://localhost:8081"
KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DB_NAME = "test-repo"
CONTAINER_NAME = "products"

results = []

def record(name, passed, error=None):
    status = "PASS" if passed else "FAIL"
    msg = f"[{status}] {name}"
    if error:
        msg += f" — {error}"
    print(msg)
    results.append((name, passed, error))

def main():
    # Setup
    client = CosmosClient(ENDPOINT, KEY)
    try:
        client.delete_database(DB_NAME)
    except:
        pass
    db = client.create_database(DB_NAME)
    container = db.create_container(CONTAINER_NAME, partition_key=PartitionKey(path="/categoryId"))
    repo = ProductRepository(container)

    # a. Create 3 products in 2 categories
    products = [
        Product("p1", "electronics", "Laptop", 999.99, 10, "A laptop", "2024-01-01T00:00:00Z"),
        Product("p2", "electronics", "Mouse", 29.99, 100, "A mouse", "2024-01-02T00:00:00Z"),
        Product("p3", "books", "Python Guide", 49.99, 50, "A book", "2024-01-03T00:00:00Z"),
    ]
    for p in products:
        try:
            repo.create(p)
            record(f"Create {p.productId}", True)
        except Exception as e:
            record(f"Create {p.productId}", False, str(e))

    # b. Read by ID
    try:
        result = repo.read("p1", "electronics")
        passed = result is not None and result.name == "Laptop"
        record("Read by ID", passed, None if passed else f"Got: {result}")
    except Exception as e:
        record("Read by ID", False, str(e))

    # c. List by category
    try:
        items = repo.list_by_category("electronics")
        passed = len(items) == 2
        record("List by category", passed, None if passed else f"Got {len(items)} items")
    except Exception as e:
        record("List by category", False, str(e))

    # d. Update stock
    try:
        updated = repo.update_stock("p1", "electronics", 5)
        passed = updated.stock == 5
        record("Update stock", passed, None if passed else f"Stock={updated.stock}")
    except Exception as e:
        record("Update stock", False, str(e))

    # e. Delete
    try:
        deleted = repo.delete("p2", "electronics")
        record("Delete", deleted, None if deleted else "delete returned False")
    except Exception as e:
        record("Delete", False, str(e))

    # Verify delete
    try:
        result = repo.read("p2", "electronics")
        record("Verify delete", result is None, None if result is None else "Still exists")
    except Exception as e:
        record("Verify delete", False, str(e))

    # Search by name
    try:
        items = repo.search_by_name("Laptop")
        passed = len(items) == 1 and items[0].productId == "p1"
        record("Search by name", passed, None if passed else f"Got {len(items)} items")
    except Exception as e:
        record("Search by name", False, str(e))

    # Summary
    print(f"\n{'='*40}")
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    print(f"Results: {passed}/{total} passed")

    # Cleanup
    try:
        client.delete_database(DB_NAME)
    except:
        pass

if __name__ == "__main__":
    main()
