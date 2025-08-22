#!/usr/bin/env python3
"""
Example demonstrating how to use DatasetFileWriter to create a dataset file.
"""

from dataset_sh import DatasetFile

# Example 1: Basic usage with context manager
def create_simple_dataset():
    """Create a simple dataset with one collection."""
    
    # Sample data
    users_data = [
        {"id": 1, "name": "Alice", "age": 30, "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "age": 25, "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "age": 35, "email": "charlie@example.com"},
        {"id": 4, "name": "Diana", "age": 28, "email": "diana@example.com"},
    ]
    
    # Create dataset file
    with DatasetFile.open("example_dataset.dataset", "w") as writer:
        # Add metadata
        writer.update_meta({
            "author": "Dataset Example",
            "authorEmail": "example@dataset.sh",
            "tags": ["example", "users"],
            "dataset_metadata": {
                "description": "Sample user dataset",
                "version": "1.0.0"
            }
        })
        
        # Add collection
        writer.add_collection("users", users_data)
    
    print(" Created example_dataset.dataset")


# Example 2: Dataset with type annotations
def create_typed_dataset():
    """Create a dataset with type annotations."""
    
    # Define type annotation using Typelang
    product_schema = """// use Product

type Product = {
  product_id: string
  name: string
  price: float
  in_stock: bool
  categories: string[]
}
"""
    
    # Sample product data
    products_data = [
        {
            "product_id": "P001",
            "name": "Laptop",
            "price": 999.99,
            "in_stock": True,
            "categories": ["Electronics", "Computers"]
        },
        {
            "product_id": "P002",
            "name": "Mouse",
            "price": 29.99,
            "in_stock": True,
            "categories": ["Electronics", "Accessories"]
        },
        {
            "product_id": "P003",
            "name": "Keyboard",
            "price": 79.99,
            "in_stock": False,
            "categories": ["Electronics", "Accessories"]
        },
        {
            "product_id": "P004",
            "name": "Monitor",
            "price": 299.99,
            "in_stock": True,
            "categories": ["Electronics", "Displays"]
        }
    ]
    
    with DatasetFile.open("products_dataset.dataset", "w") as writer:
        writer.update_meta({
            "author": "Product Catalog Team",
            "authorEmail": "catalog@example.com",
            "tags": ["products", "inventory", "typed"]
        })
        
        # Add collection with type annotation
        writer.add_collection(
            "products",
            products_data,
            type_annotation=product_schema
        )
    
    print(" Created products_dataset.dataset with type annotations")


# Example 3: Multiple collections with different type annotations
def create_multi_collection_dataset():
    """Create a dataset with multiple collections and type annotations."""
    
    # Define type annotations for each collection using Typelang
    order_schema = """// use Order

type Order = {
  order_id: string
  customer_id: int
  total: float
  status: "pending" | "shipped" | "completed" | "cancelled"
}
"""
    
    order_item_schema = """// use OrderItem

type OrderItem = {
  order_id: string
  product_id: string
  quantity: int
  price: float
}
"""
    
    customer_schema = """// use Customer

type Customer = {
  customer_id: int
  name: string
  email: string
  phone?: string
}
"""
    
    # Orders data
    orders_data = [
        {"order_id": "O001", "customer_id": 1, "total": 1299.98, "status": "completed"},
        {"order_id": "O002", "customer_id": 2, "total": 29.99, "status": "pending"},
        {"order_id": "O003", "customer_id": 1, "total": 379.98, "status": "shipped"},
    ]
    
    # Order items data
    order_items_data = [
        {"order_id": "O001", "product_id": "P001", "quantity": 1, "price": 999.99},
        {"order_id": "O001", "product_id": "P004", "quantity": 1, "price": 299.99},
        {"order_id": "O002", "product_id": "P002", "quantity": 1, "price": 29.99},
        {"order_id": "O003", "product_id": "P003", "quantity": 2, "price": 79.99},
        {"order_id": "O003", "product_id": "P002", "quantity": 1, "price": 29.99},
    ]
    
    # Customers data
    customers_data = [
        {"customer_id": 1, "name": "Alice Johnson", "email": "alice@example.com", "phone": None},
        {"customer_id": 2, "name": "Bob Smith", "email": "bob@example.com", "phone": "+1234567890"},
    ]
    
    with DatasetFile.open("ecommerce_dataset.dataset", "w") as writer:
        writer.update_meta({
            "author": "E-commerce Team",
            "authorEmail": "data@ecommerce.com",
            "tags": ["ecommerce", "orders", "multi-collection"],
            "dataset_metadata": {
                "description": "E-commerce dataset with orders, items, and customers",
                "created_date": "2024-01-15",
                "tables": "orders, order_items, customers"  # String instead of list
            }
        })
        
        # Add multiple collections with their type annotations
        writer.add_collection("orders", orders_data, type_annotation=order_schema)
        writer.add_collection("order_items", order_items_data, type_annotation=order_item_schema)
        writer.add_collection("customers", customers_data, type_annotation=customer_schema)
    
    print(" Created ecommerce_dataset.dataset with 3 collections")


# Example 4: Dataset with binary files
def create_dataset_with_binary():
    """Create a dataset with binary file attachments."""
    
    # Sample data
    documents_data = [
        {"doc_id": 1, "title": "Report Q1", "type": "pdf"},
        {"doc_id": 2, "title": "Presentation", "type": "pptx"},
        {"doc_id": 3, "title": "README", "type": "txt"},
    ]
    
    with DatasetFile.open("documents_dataset.dataset", "w") as writer:
        writer.update_meta({
            "author": "Document Manager",
            "authorEmail": "docs@example.com",
            "tags": ["documents", "binary"],
        })
        
        # Add collection
        writer.add_collection("documents", documents_data)
        
        # Add binary files (mock content for example)
        writer.add_binary_file("readme.txt", b"This is a sample README file.")
        writer.add_binary_file("config.json", b'{"setting": "value"}')
        writer.add_binary_file("sample.bin", bytes([0, 1, 2, 3, 4, 5]))
    
    print(" Created documents_dataset.dataset with binary files")


# Example 5: Advanced types with inline types and unions
def create_advanced_types_dataset():
    """Create a dataset demonstrating advanced type features."""
    
    # Complex type with inline types and unions using Typelang
    event_schema = """// use Event

type UserInfo = {
  user_id: string
  session_id: string
  ip_address?: string
}

type MetadataItem = {
  key: string
  value: string
}

type Event = {
  event_id: string
  timestamp: int
  event_type: "click" | "view" | "purchase" | "signup"
  user_info: UserInfo
  payload: string | int | Dict<string, string>
  metadata: MetadataItem[]
}
"""
    
    # Sample event data
    events_data = [
        {
            "event_id": "evt_001",
            "timestamp": 1704067200,
            "event_type": "signup",
            "user_info": {
                "user_id": "user_123",
                "session_id": "sess_abc",
                "ip_address": "192.168.1.1"
            },
            "payload": "New user registration",
            "metadata": [
                {"key": "source", "value": "organic"},
                {"key": "campaign", "value": "spring2024"}
            ]
        },
        {
            "event_id": "evt_002",
            "timestamp": 1704067300,
            "event_type": "click",
            "user_info": {
                "user_id": "user_456",
                "session_id": "sess_def",
                "ip_address": None
            },
            "payload": {"button": "checkout", "page": "cart"},
            "metadata": []
        },
        {
            "event_id": "evt_003",
            "timestamp": 1704067400,
            "event_type": "purchase",
            "user_info": {
                "user_id": "user_123",
                "session_id": "sess_ghi",
                "ip_address": "192.168.1.2"
            },
            "payload": 4599,  # Purchase amount in cents
            "metadata": [
                {"key": "payment_method", "value": "credit_card"}
            ]
        }
    ]
    
    with DatasetFile.open("advanced_types_dataset.dataset", "w") as writer:
        writer.update_meta({
            "author": "Analytics Team",
            "authorEmail": "analytics@example.com",
            "tags": ["events", "analytics", "advanced-types"],
            "dataset_metadata": {
                "description": "Event stream with complex type structures"
            }
        })
        
        writer.add_collection("events", events_data, type_annotation=event_schema)
    
    print(" Created advanced_types_dataset.dataset with complex types")


# Example 6: Using progress bar with large datasets
def create_large_dataset_with_progress():
    """Create a large dataset with progress tracking."""
    from tqdm import tqdm
    
    # Generate large dataset
    large_data = []
    for i in range(10000):
        large_data.append({
            "id": i,
            "value": i * 2.5,
            "category": f"cat_{i % 10}",
            "is_active": i % 2 == 0,
            "metadata": {
                "created": f"2024-01-{(i % 30) + 1:02d}",
                "source": "generated"
            }
        })
    
    with DatasetFile.open("large_dataset.dataset", "w") as writer:
        writer.update_meta({
            "author": "Data Generator",
            "authorEmail": "generator@example.com",
            "tags": ["large", "generated"],
            "dataset_metadata": {
                "record_count": len(large_data),
                "generation_method": "synthetic"
            }
        })
        
        # Add collection with progress bar
        writer.add_collection(
            "records",
            large_data,
            tqdm=tqdm  # Pass tqdm for progress tracking
        )
    
    print(" Created large_dataset.dataset with 10,000 records")


# Example 7: Reading and verifying created dataset
def verify_dataset(filename):
    """Read and verify a created dataset."""
    import os
    from dataset_sh import open_dataset_file
    
    print(f"\nVerifying {filename}:")
    
    if not os.path.exists(filename):
        print(f"  File {filename} not found, skipping verification")
        return
    
    with open_dataset_file(filename) as reader:
        # Print metadata
        meta = reader.meta
        print(f"  Author: {meta.author}")
        print(f"  Tags: {meta.tags}")
        print(f"  Collections: {reader.collections()}")
        
        # Sample data from first collection
        if reader.collections():
            first_collection = reader.collections()[0]
            collection = reader.collection(first_collection)
            
            # Get type annotation if exists
            type_info = collection.type_annotation_typelang()
            if type_info:
                print(f"  Type annotation exists: Yes (Typelang)")
                # Validate the schema
                if collection.validate_typelang():
                    print(f"  Schema is valid: Yes")
            
            # Show first 3 records
            print(f"  First 3 records from '{first_collection}':")
            for i, record in enumerate(collection.top(3)):
                print(f"    {i+1}: {record}")


if __name__ == "__main__":
    print("Dataset File Writer Examples")
    print("=" * 40)
    
    # Run examples
    print("\n1. Simple dataset:")
    create_simple_dataset()
    
    print("\n2. Typed dataset:")
    create_typed_dataset()
    
    print("\n3. Multi-collection dataset:")
    create_multi_collection_dataset()
    
    print("\n4. Dataset with binary files:")
    create_dataset_with_binary()
    
    print("\n5. Advanced types dataset:")
    create_advanced_types_dataset()
    
    print("\n6. Large dataset with progress:")
    create_large_dataset_with_progress()
    
    # Verify created datasets
    print("\n" + "=" * 40)
    print("Verification:")
    verify_dataset("example_dataset.dataset")
    verify_dataset("products_dataset.dataset")
    verify_dataset("ecommerce_dataset.dataset")
    verify_dataset("advanced_types_dataset.dataset")