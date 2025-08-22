#!/usr/bin/env python3
"""
Example demonstrating how to use DatasetFileWriter with Typelang type annotations.
"""

from dataset_sh import DatasetFile
from typing import List, Optional

# Example 1: Basic Typelang usage
def create_dataset_with_typelang():
    """Create a dataset with Typelang type annotations."""
    
    # Define Typelang schema
    user_schema = """// use User

type User = {
  id: string
  name: string
  email: string
  age: int
  isActive: bool
  tags: string[]
}
"""
    
    # Sample data
    users_data = [
        {
            "id": "u001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 30,
            "isActive": True,
            "tags": ["developer", "team-lead"]
        },
        {
            "id": "u002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "age": 25,
            "isActive": True,
            "tags": ["designer", "frontend"]
        },
        {
            "id": "u003",
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "age": 35,
            "isActive": False,
            "tags": ["backend", "devops"]
        }
    ]
    
    # Create dataset file
    with DatasetFile.open("users_typelang.dataset", "w") as writer:
        writer.update_meta({
            "author": "Typelang Example",
            "authorEmail": "example@dataset.sh",
            "tags": ["typelang", "users"],
            "dataset_metadata": {
                "description": "User dataset with Typelang types",
                "version": "2.0.0"
            }
        })
        
        # Add collection with Typelang type annotation
        writer.add_collection("users", users_data, type_annotation=user_schema)
    
    print("Created users_typelang.dataset with Typelang type annotations")


# Example 2: Complex Typelang types
def create_ecommerce_dataset_typelang():
    """Create an e-commerce dataset with complex Typelang types."""
    
    # Define Product type
    product_schema = """// use Product

type Product = {
  id: string
  name: string
  description?: string
  price: float
  currency: "USD" | "EUR" | "GBP"
  inStock: bool
  categories: string[]
  metadata: Dict<string, any>
}
"""
    
    # Define Order type with nested types
    order_schema = """// use Order

type OrderItem = {
  productId: string
  quantity: int
  unitPrice: float
  discount?: float
}

type ShippingAddress = {
  street: string
  city: string
  state?: string
  country: string
  postalCode: string
}

type Order = {
  orderId: string
  customerId: string
  orderDate: string
  status: "pending" | "processing" | "shipped" | "delivered" | "cancelled"
  items: OrderItem[]
  shippingAddress: ShippingAddress
  totalAmount: float
  notes?: string
}
"""
    
    # Sample product data
    products_data = [
        {
            "id": "prod_001",
            "name": "Wireless Headphones",
            "description": "High-quality Bluetooth headphones",
            "price": 79.99,
            "currency": "USD",
            "inStock": True,
            "categories": ["Electronics", "Audio"],
            "metadata": {"brand": "TechSound", "warranty": "1 year"}
        },
        {
            "id": "prod_002",
            "name": "USB-C Cable",
            "price": 12.99,
            "currency": "USD",
            "inStock": True,
            "categories": ["Electronics", "Accessories"],
            "metadata": {"length": "2m", "color": "black"}
        }
    ]
    
    # Sample order data
    orders_data = [
        {
            "orderId": "ord_2024_001",
            "customerId": "cust_123",
            "orderDate": "2024-01-15T10:30:00Z",
            "status": "delivered",
            "items": [
                {
                    "productId": "prod_001",
                    "quantity": 1,
                    "unitPrice": 79.99,
                    "discount": 10.0
                },
                {
                    "productId": "prod_002",
                    "quantity": 2,
                    "unitPrice": 12.99
                }
            ],
            "shippingAddress": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
                "postalCode": "94105"
            },
            "totalAmount": 95.97,
            "notes": "Please leave at front door"
        }
    ]
    
    with DatasetFile.open("ecommerce_typelang.dataset", "w") as writer:
        writer.update_meta({
            "author": "E-commerce Team",
            "authorEmail": "data@ecommerce.com",
            "tags": ["ecommerce", "typelang", "complex-types"],
            "dataset_metadata": {
                "description": "E-commerce dataset with Typelang schemas",
                "created": "2024-01-15"
            }
        })
        
        # Add collections with their Typelang schemas
        writer.add_collection("products", products_data, type_annotation=product_schema)
        writer.add_collection("orders", orders_data, type_annotation=order_schema)
    
    print("Created ecommerce_typelang.dataset with complex Typelang types")


# Example 3: Generic types in Typelang
def create_generic_types_dataset():
    """Create a dataset demonstrating generic types in Typelang."""
    
    # Define generic Response type
    response_schema = """// use ApiResponse

type ApiResponse<T> = {
  success: bool
  data?: T
  error?: string
  timestamp: string
}

type UserData = {
  userId: string
  username: string
  email: string
}

type ApiResponse = ApiResponse<UserData>
"""
    
    # Sample API response data
    responses_data = [
        {
            "success": True,
            "data": {
                "userId": "u123",
                "username": "alice",
                "email": "alice@example.com"
            },
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "success": False,
            "error": "User not found",
            "timestamp": "2024-01-15T10:01:00Z"
        },
        {
            "success": True,
            "data": {
                "userId": "u456",
                "username": "bob",
                "email": "bob@example.com"
            },
            "timestamp": "2024-01-15T10:02:00Z"
        }
    ]
    
    with DatasetFile.open("api_responses_typelang.dataset", "w") as writer:
        writer.update_meta({
            "author": "API Team",
            "authorEmail": "api@example.com",
            "tags": ["api", "typelang", "generics"],
            "dataset_metadata": {
                "description": "API responses with generic Typelang types"
            }
        })
        
        writer.add_collection("responses", responses_data, type_annotation=response_schema)
    
    print("Created api_responses_typelang.dataset with generic types")


# Example 4: Reading and validating Typelang datasets
def read_and_validate_typelang_dataset(filename):
    """Read a dataset and validate its Typelang type annotations."""
    import os
    from dataset_sh import open_dataset_file
    
    print(f"\nReading {filename}:")
    
    if not os.path.exists(filename):
        print(f"  File not found, skipping")
        return
    
    with open_dataset_file(filename) as reader:
        # Print metadata
        print(f"  Author: {reader.meta.author}")
        print(f"  Collections: {reader.collections()}")
        
        # Check each collection's type annotation
        for coll_name in reader.collections():
            collection = reader.collection(coll_name)
            
            # Get Typelang schema
            typelang_schema = collection.type_annotation_typelang()
            if typelang_schema:
                print(f"\n  Collection '{coll_name}' Typelang schema:")
                # Print first few lines of schema
                lines = typelang_schema.strip().split('\n')[:5]
                for line in lines:
                    print(f"    {line}")
                if len(typelang_schema.strip().split('\n')) > 5:
                    print("    ...")
                
                # Validate schema format
                is_valid = collection.validate_typelang()
                print(f"    Schema valid: {is_valid}")
            else:
                print(f"  Collection '{coll_name}': No Typelang schema")
            
            # Show sample data
            print(f"  First 2 records:")
            for i, record in enumerate(collection.top(2)):
                print(f"    {i+1}: {record}")


# Example 5: Compile Typelang to TypeScript (if typelang is installed)
def compile_typelang_example():
    """Example of compiling Typelang to TypeScript using the typelang package."""
    try:
        from typelang import Compiler
        
        schema = """// use Product

type Product = {
  id: string
  name: string
  price: float
  inStock: bool
  categories: string[]
}

type Order = {
  orderId: string
  products: Product[]
  totalAmount: float
  status: "pending" | "shipped" | "delivered"
}
"""
        
        compiler = Compiler()
        
        # Compile to TypeScript
        typescript = compiler.compile(schema, target="typescript")
        if typescript:
            print("\nCompiled to TypeScript:")
            print(typescript)
        
        # Compile to Python Pydantic
        pydantic = compiler.compile(schema, target="python-pydantic")
        if pydantic:
            print("\nCompiled to Python Pydantic:")
            print(pydantic[:300] + "..." if len(pydantic) > 300 else pydantic)
        
    except ImportError:
        print("\nTypelang package not installed. Install with: pip install typelang")
    except Exception as e:
        print(f"\nError compiling Typelang: {e}")


if __name__ == "__main__":
    print("Dataset File with Typelang Examples")
    print("=" * 50)
    
    # Create datasets
    print("\n1. Basic Typelang dataset:")
    create_dataset_with_typelang()
    
    print("\n2. E-commerce dataset with complex types:")
    create_ecommerce_dataset_typelang()
    
    print("\n3. Generic types dataset:")
    create_generic_types_dataset()
    
    # Read and validate
    print("\n" + "=" * 50)
    print("Validation:")
    read_and_validate_typelang_dataset("users_typelang.dataset")
    read_and_validate_typelang_dataset("ecommerce_typelang.dataset")
    read_and_validate_typelang_dataset("api_responses_typelang.dataset")
    
    # Compile example
    print("\n" + "=" * 50)
    print("Typelang Compilation Example:")
    compile_typelang_example()