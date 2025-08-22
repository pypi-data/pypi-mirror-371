# DatasetFile Internal Structure

## Overview

DatasetFile is a ZIP-based archive format for storing structured datasets with collections, metadata, and binary files. The file uses ZIP compression (default: ZIP_DEFLATED with compression level 9) to efficiently store data.

## Internal Directory Structure

```
dataset.zip/
├── meta.json                     # Metadata file (required)
├── coll/                         # Collections folder
│   ├── <collection_name>/        # Individual collection folder
│   │   ├── data.jsonl           # Collection data in JSONL format
│   │   └── type.tl              # Optional type annotations in Typelang format
│   └── ...
└── bin/                          # Binary files folder
    ├── <file1>                   # Binary file 1
    ├── <file2>                   # Binary file 2
    └── ...
```

## Component Details

### 1. Metadata File (`meta.json`)

Located at the root of the ZIP archive. Contains dataset-level metadata stored as a JSON object.

**Structure (DatasetFileMeta):**
```json
{
  "author": "string (optional)",
  "authorEmail": "string (optional)",
  "description": "string (optional)",
  "tags": ["array", "of", "strings"] (optional),
  "collections": [
    {
      "name": "collection_name",
      "data_format": "jsonl"
    }
  ],
  "dataset_metadata": {
    "key": "value pairs (optional)"
  }
}
```

### 2. Collections (`coll/`)

Each collection is stored in its own subdirectory under `coll/`.

#### Collection Structure
- **Path**: `coll/<collection_name>/`
- **Data File**: `coll/<collection_name>/data.jsonl`
  - Format: JSONL (JSON Lines) - one JSON object per line
  - Each line represents a single data item
  - Empty lines are ignored during reading

- **Type File**: `coll/<collection_name>/type.tl` (optional)
  - Contains type annotation information for the collection in Typelang format
  - Must start with a special comment: `// use TypeName` where TypeName is the main type
  - Typelang is a TypeScript-flavored schema definition language

### 3. Binary Files (`bin/`)

Binary files are stored flat in the `bin/` directory.

- **Path**: `bin/<filename>`
- **Content**: Raw binary data
- **Access**: Via `binary_files()`, `open_binary_file()` methods

## File Operations

### Writing a DatasetFile

1. **Create Writer**: Initialize `DatasetFileWriter` with file path
2. **Update Metadata**: Set author, email, tags, etc.
3. **Add Collections**: Use `add_collection()` with:
   - Collection name
   - List of data items (dict/list)
   - Optional type annotations (Typelang string or UserDefinedType)
4. **Add Binary Files**: Use `add_binary_file()` with filename and bytes
5. **Close**: Writes metadata and closes ZIP file

### Reading a DatasetFile

1. **Open Reader**: Initialize `DatasetFileReader` with file path
2. **Access Metadata**: Via `meta` attribute
3. **List Collections**: Use `collections()` method
4. **Read Collection**: Use `collection()` or `coll()` methods
   - Returns `CollectionReader` object
   - Supports iteration, sampling, type annotations
5. **Access Binary Files**: Use `binary_files()` and `open_binary_file()`

## Key Classes

### DatasetFile
- Factory class with static `open()` method
- Returns appropriate reader/writer based on mode

### DatasetFileWriter
- Context manager support
- Methods: `update_meta()`, `add_collection()`, `add_binary_file()`
- Auto-writes metadata on close

### DatasetFileReader
- Context manager support
- Methods: `collections()`, `collection()`, `binary_files()`, `open_binary_file()`
- Provides dict-like access via `__getitem__`

### CollectionReader
- Iterates over collection data
- Methods: `type_annotation()`, `type_annotation_typelang()`, `validate_typelang()`, `top()`, `random_sample()`, `to_list()`
- Lazy loading for memory efficiency
- Supports both legacy JSON and new Typelang type formats

## Internal Path Constants

Defined in `DatasetFileInternalPath`:
- `BINARY_FOLDER = 'bin'`
- `COLLECTION_FOLDER = 'coll'`
- `META_FILE_NAME = 'meta.json'`
- `DATA_FILE = 'data.jsonl'`
- `TYPE_FILE = 'type.tl'`

## Usage Examples

### Basic Usage

```python
# Writing
with DatasetFile.open('dataset.zip', 'w') as writer:
    writer.update_meta({'author': 'John Doe'})
    writer.add_collection('train', data_list)
    writer.add_binary_file('model.pkl', model_bytes)

# Reading
with DatasetFile.open('dataset.zip', 'r') as reader:
    print(reader.meta.author)
    for item in reader.collection('train'):
        process(item)
```

### Using Typelang Type Annotations

```python
# Define Typelang schema
user_schema = """// use User

type User = {
  id: string
  name: string
  email?: string
  age: int
  isActive: bool
}
"""

# Writing with Typelang
with DatasetFile.open('dataset.zip', 'w') as writer:
    writer.update_meta({'author': 'John Doe'})
    writer.add_collection('users', user_data, type_annotation=user_schema)

# Reading and validating Typelang
with DatasetFile.open('dataset.zip', 'r') as reader:
    users_coll = reader.collection('users')
    
    # Get Typelang schema
    schema = users_coll.type_annotation_typelang()
    if schema:
        print("Schema found:", schema[:50])
    
    # Validate schema format
    if users_coll.validate_typelang():
        print("Schema is valid")
```