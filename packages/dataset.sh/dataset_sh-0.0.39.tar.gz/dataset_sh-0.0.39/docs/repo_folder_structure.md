# Dataset.sh Repository Folder Structure

## Overview

Dataset.sh uses a hierarchical folder structure for local dataset storage and organization. The system manages datasets through namespaces, datasets, and versions, with support for tags and metadata.

## Local Storage Structure

The default local storage location is `~/dataset_sh/storage/` (configurable via `STORAGE_BASE` constant).

### Directory Hierarchy

```
~/dataset_sh/storage/
├── <namespace>/
│   ├── .dataset.namespace.marker      # Namespace marker file
│   └── <dataset_name>/
│       ├── .dataset.marker            # Dataset marker file
│       ├── readme.md                  # Dataset README
│       ├── tag                        # Tag mappings (JSON)
│       └── version/
│           └── <version_id>/
│               ├── .dataset.version.marker    # Version marker file
│               ├── file                       # Actual dataset file (ZIP)
│               ├── meta.json                  # Dataset metadata
│               ├── data_sample_<collection>.jsonl    # Sample data
│               └── type_annotation_<collection>.json # Type annotations
```

## Core Components

### 1. LocalStorage
- **Location**: Base storage directory (default: `~/dataset_sh/storage/`)
- **Purpose**: Root container for all local datasets
- **Methods**:
  - `namespaces()`: List all namespaces
  - `namespace(name)`: Access specific namespace
  - `datasets()`: List all datasets across namespaces
  - `dataset(name)`: Access dataset by "namespace/dataset" format

### 2. LocalNamespace
- **Location**: `<storage>/<namespace>/`
- **Marker**: `.dataset.namespace.marker`
- **Purpose**: Groups datasets under a namespace (typically username/organization)
- **Methods**:
  - `datasets()`: List datasets in namespace
  - `dataset(name)`: Access specific dataset

### 3. LocalDataset
- **Location**: `<storage>/<namespace>/<dataset_name>/`
- **Marker**: `.dataset.marker`
- **Purpose**: Container for all versions of a dataset
- **Structure**:
  - `readme.md`: Dataset documentation
  - `tag`: JSON file mapping tag names to version IDs
  - `version/`: Directory containing all versions
- **Methods**:
  - `versions()`: List all versions
  - `version(id)`: Access specific version
  - `tag(name)`: Get version by tag
  - `latest()`: Get latest tagged version
  - `import_file()`: Import new dataset file as version
  - `import_data()`: Create version from data

### 4. LocalDatasetVersion
- **Location**: `<storage>/<namespace>/<dataset>/<version>/<version_id>/`
- **Marker**: `.dataset.version.marker`
- **Purpose**: Specific version of a dataset
- **Files**:
  - `file`: The actual dataset ZIP file
  - `meta.json`: Extracted metadata
  - `data_sample_<collection>.jsonl`: Sample data for quick preview
  - `type_annotation_<collection>.json`: Type information
- **Methods**:
  - `open()`: Open dataset file for reading
  - `meta()`: Get metadata
  - `sample()`: Get sample data
  - `upload_to()`: Upload to remote repository

## Remote Storage Components

### 1. Remote
- **Purpose**: Connection to remote dataset.sh server
- **Configuration**: Host URL and optional access key
- **Methods**:
  - `namespace(name)`: Access remote namespace
  - `dataset(name)`: Access remote dataset
  - `test_connection()`: Verify server connection

### 2. RemoteNamespace
- **Purpose**: Remote namespace representation
- **Methods**:
  - `dataset(name)`: Access remote dataset

### 3. RemoteDataset
- **Purpose**: Remote dataset representation
- **Methods**:
  - `versions()`: List available versions
  - `tags()`: List available tags
  - `upload_from_file()`: Upload new version
  - `update_readme()`: Update dataset documentation

### 4. RemoteDatasetVersion
- **Purpose**: Specific remote version
- **Methods**:
  - `download_to_file()`: Download to local file
  - `download_to()`: Download to local dataset
  - `download()`: Download to default location

### 5. RemoteDatasetVersionTag
- **Purpose**: Tagged remote version
- **Methods**: Similar to RemoteDatasetVersion

## File Formats

### Marker Files

Marker files indicate valid dataset components and follow a simple format:

#### File Names
- `.dataset.namespace.marker` - Marks a valid namespace
- `.dataset.marker` - Marks a valid dataset  
- `.dataset.version.marker` - Marks a valid version

#### File Format
```
1
```
- Plain text file containing only "1"
- Created automatically during initialization
- Used for existence checking (`exists()` method checks for marker presence)
- Parent markers created recursively when creating child components

### Tag File

The tag file stores mappings between tag names and version IDs.

#### Location
`<namespace>/<dataset>/tag`

#### Format
```json
{
  "tags": {
    "latest": "sha256_abc123def456...",
    "stable": "sha256_789ghi012jkl...",
    "v1.0": "sha256_abc123def456...",
    "dev": "sha256_mno345pqr678..."
  }
}
```

#### Details
- JSON format with a single `tags` object
- Keys are tag names (strings)
- Values are version IDs (checksums)
- Common tags: "latest", "stable", "dev", version numbers
- Empty initially: `{"tags": {}}`
- Updated via `set_tag()` and `remove_tag()` methods

### Meta File

Extracted metadata from the dataset file.

#### Location
`<namespace>/<dataset>/version/<version_id>/meta.json`

#### Format
```json
{
  "author": "John Doe",
  "authorEmail": "john@example.com",
  "description": "Dataset description",
  "tags": ["machine-learning", "nlp"],
  "collections": [
    {
      "name": "main",
      "data_format": "jsonl"
    }
  ],
  "dataset_metadata": {
    "key": "value"
  }
}
```

### Sample Files

#### Location
`<namespace>/<dataset>/version/<version_id>/data_sample_<collection>.jsonl`

#### Format
- JSONL format (one JSON object per line)
- Limited to ~10KB or 30 lines
- Example:
```jsonl
{"id": 1, "text": "Sample data 1"}
{"id": 2, "text": "Sample data 2"}
```

### Type Annotation Files

#### Location
`<namespace>/<dataset>/version/<version_id>/type_annotation_<collection>.json`

#### Format
- JSON representation of the collection's type structure
- Used for code generation and validation

## Version IDs

Version IDs are checksums of the dataset file:
- Ensures content integrity
- Prevents duplicate versions
- Used as directory names under `version/`

## File Operations Flow

### Import/Create Version
1. Calculate file checksum → version ID
2. Create version directory
3. Copy/move dataset file
4. Extract metadata and samples
5. Update tags (if specified)

### Download from Remote
1. Download to temporary file
2. Import as new version
3. Verify checksum matches
4. Apply tags

### Upload to Remote
1. Read local version file
2. Upload via multipart or FileServerClient
3. Apply tags on remote

## Configuration Files

### Global Configuration
- `~/.dataset_sh_config.json`: Client configuration
- `~/.dataset_sh_author.json`: Default author information

### Environment Variables
- `DSH_DEFAULT_HOST`: Default remote server (default: https://base.dataset.sh)
- `DSH_DAEMON_PID_FILE`: Daemon process ID file location

## Constants

Key constants from `constants.py`:
- `STORAGE_BASE`: Local storage root directory
- `DEFAULT_COLLECTION_NAME`: "main" (default collection name)
- `SAMPLE_CHAR_COUNT`: 10,000 (max characters in samples)

## Usage Examples

### Access Local Dataset
```python
from dataset_sh.clients.obj import LocalStorage

storage = LocalStorage()
dataset = storage.dataset("username/dataset_name")
latest_version = dataset.latest()
with latest_version.open() as reader:
    # Read dataset
    pass
```

### Import New Version
```python
dataset = storage.dataset("username/dataset_name")
dataset.import_file("path/to/dataset.zip", tags=["v1.0", "latest"])
```

### Download from Remote
```python
from dataset_sh.clients.obj import remote

rem = remote()
remote_dataset = rem.dataset("username/dataset_name")
remote_dataset.latest().download()
```