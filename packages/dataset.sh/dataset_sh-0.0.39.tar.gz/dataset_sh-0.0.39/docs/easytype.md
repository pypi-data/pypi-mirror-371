# EasyType - Design Documentation

## Overview

EasyType is a Python library for building and manipulating type definitions programmatically. It provides a fluent API for creating complex type structures that can be serialized to dictionaries, making it useful for code generation, API documentation, and type system modeling.

## Architecture

### Core Components

The library is built around a hierarchical type system with the following main components:

```
easytype/
├── __init__.py        # Public API (exports TypeBuilder)
├── core.py            # Core type system implementation
├── common.py          # Utility functions (currently placeholder)
└── utils.py           # Additional utilities (currently empty)
```

## Type System Design

### Type Hierarchy

EasyType implements a comprehensive type system with six main type categories:

#### 1. **PrimitiveType**
Represents basic scalar types:
- `int` - Integer values
- `float` - Floating-point numbers
- `str` - String values
- `bool` - Boolean values
- `list` - Generic list container
- `dict` - Generic dictionary/map
- `any` - Any type (equivalent to TypeScript's `any` or Python's `typing.Any`)

#### 2. **TypeReference**
A string-based reference to another type, enabling:
- Recursive type definitions
- Forward references
- Decoupled type dependencies

Example: `'Example'` can reference a type named "Example"

#### 3. **UserDefinedType**
Custom types with named fields:
- Has a unique name identifier
- Contains a list of `FieldDefinition` objects
- Supports optional comments for documentation
- Can include references to other UserDefinedTypes

```python
TypeBuilder.create('Person',
    name=str,
    age=int,
    address='Address'  # TypeReference
)
```

#### 4. **InlineType**
Anonymous structured types defined inline:
- Similar to UserDefinedType but without a name
- Useful for nested structures that don't need reusability

```python
dict(
    street=str,
    city=str,
    zip_code=int
)
```

#### 5. **ParameterizedType**
Generic types with type parameters:
- `list[T]` - Typed lists
- `dict[K, V]` - Typed dictionaries
- `tuple[T1, T2, ...]` - Fixed-length tuples
- `optional[T]` - Optional values (nullable)
- `union[T1, T2, ...]` - Union types

#### 6. **EnumType**
Enumeration types with string choices:
- List of allowed string values
- Optional name for referencing
- Supports documentation comments

```python
['apple', 'orange', 'banana']
```

### Type Resolution

The `resolve_type()` function is the core type resolution mechanism that converts various Python representations into EasyType objects:

1. **Already Resolved**: If the input is already a resolved type, returns it unchanged
2. **String Input**: Converts to `TypeReference`
3. **Dictionary Input**: Converts to `InlineType`
4. **List of Strings**: Converts to `EnumType`
5. **Python Types**: Analyzes using `typing` module introspection
   - Checks for generic origin (List, Dict, Union, etc.)
   - Extracts type arguments
   - Handles special cases (Optional as Union with None)

### Field Definitions

Each field in a structured type consists of:
- `fieldKey`: The field name/identifier
- `fieldType`: A resolved type (any of the six type categories)
- `comment`: Optional documentation string

## API Design

### Primary Interface: TypeBuilder

The `TypeBuilder` class provides the main API for creating types:

```python
class TypeBuilder:
    @staticmethod
    def create(_name: str, **kwargs) -> UserDefinedType
    
    @staticmethod
    def create_from_dict(_name: str, kwargs: dict) -> UserDefinedType
```

Both methods create `UserDefinedType` instances with fields derived from the keyword arguments.

### Fluent Interface

All type classes support method chaining through fluent interfaces:

```python
type_def = TypeBuilder.create('MyType', field=int)
    .with_comment('This is my type')
    .reference(another_type)
```

### Serialization

All types implement `to_dict()` for serialization:

```python
{
    'type': 'TypeName',  # Discriminator field
    'name': '...',       # For named types
    'fields': [...],     # For structured types
    'params': [...],     # For parameterized types
    'choices': [...],    # For enum types
    'comment': '...'     # Optional documentation
}
```

### Deserialization

The `parse_from_dict()` function reconstructs type objects from their dictionary representation, enabling:
- Type persistence
- Network transmission
- Configuration-based type definitions

## Design Patterns

### 1. **Discriminated Union Pattern**
All serialized types include a `type` field as a discriminator, enabling safe deserialization and type checking.

### 2. **Builder Pattern**
`TypeBuilder` implements the builder pattern for constructing complex type hierarchies with a clean API.

### 3. **Fluent Interface**
Methods like `with_comment()` return `self`, enabling method chaining for more readable code.

### 4. **Recursive Type Support**
Types can reference themselves or other types through `TypeReference`, enabling complex recursive structures like trees or linked lists.

### 5. **Immutable-Style Updates**
While not strictly immutable, the API encourages creating new instances rather than modifying existing ones.

## Use Cases

### 1. **Code Generation**
Generate TypeScript, GraphQL, or other schema definitions from Python type definitions.

### 2. **API Documentation**
Define API request/response schemas programmatically.

### 3. **Type Validation**
Build runtime type validators from type definitions.

### 4. **Schema Migration**
Version and migrate type schemas over time.

### 5. **Cross-Language Type Sharing**
Share type definitions between Python and other languages through JSON serialization.

## Example: Kitchen Sink

The `examples/kitchen_sink.py` demonstrates all type features:

```python
from easytype import TypeBuilder
import typing

# User-defined type
at = TypeBuilder.create('AnotherType', some_value=int)

# Complex type with all features
t = TypeBuilder.create('Example',
    # Recursive reference
    recursive_value='Example',
    
    # Primitives
    int_value=int,
    str_value=str,
    
    # Inline type
    inline_value=dict(x=int, y=str),
    
    # Enum
    enum_value=['apple', 'orange'],
    
    # User-defined reference
    another_type_value=at,
    
    # Parameterized types
    list_of_int=list[int],
    optional_str=typing.Optional[str],
    dict_of_bool=dict[str, bool],
    union_type=typing.Union[int, str]
)
```

## Testing Strategy

The test suite (`tests/test_core.py`) covers:

1. **Type Resolution**: Tests for all input types and their correct resolution
2. **Serialization/Deserialization**: Round-trip testing for all type categories
3. **Edge Cases**: Handling of unsupported types, None values, empty collections
4. **Fluent Interface**: Comment and reference chaining
5. **Complex Types**: Nested and recursive type definitions

## Future Considerations

### Potential Enhancements

1. **Validation**: Add runtime validation of values against type definitions
2. **Code Generation**: Built-in generators for TypeScript, JSON Schema, etc.
3. **Type Inference**: Automatically infer types from sample data
4. **Schema Evolution**: Tools for migrating between type versions
5. **Performance**: Optimize for large type hierarchies

### Extension Points

1. **Custom Type Classes**: Allow users to define new type categories
2. **Plugins**: Support for type transformers and validators
3. **Metadata**: Additional fields for constraints, defaults, etc.

## Dependencies

The library has zero runtime dependencies, relying only on Python's standard library:
- `typing` module for type introspection
- `dataclasses` for clean class definitions
- Standard collections (`list`, `dict`)

Development dependencies include:
- `pytest` for testing
- `mypy` for type checking
- `hatchling` for building

## License

MIT License - See LICENSE file for details