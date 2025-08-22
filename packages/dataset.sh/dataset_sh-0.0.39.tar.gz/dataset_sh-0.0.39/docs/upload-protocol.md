# Dataset.sh Multipart Upload Protocol Documentation

## Overview

The Dataset.sh multipart upload protocol enables efficient, resumable uploads of large dataset files. The protocol supports chunked uploads with progress tracking, resumption of interrupted uploads, and automatic version management based on file checksums.

## Key Components

### 1. File Identification
- Files are uniquely identified by their SHA-256 checksum
- Version IDs are the file's checksum value
- Upload paths follow the pattern: `{namespace}/{dataset_name}:version={checksum}`

### 2. Upload Tokens
- JWT tokens are generated for secure upload operations
- Tokens are included in all upload-related requests

## Upload Protocol Flow

### Phase 1: Upload Negotiation

**Endpoint**: `POST /api/resource?action=upload`

**Request Parameters**:
```
- action: "upload"
- filename: "{namespace}/{dataset_name}"
- size: file size in bytes
- checksum: SHA-256 hash of the file
- tag: comma-separated list of tags (optional)
```

**Server Processing**:
1. Creates a `MultipartFileWriter` instance for the upload
2. Calculates optimal chunk size based on:
   - File size
   - `minimal_chunk_size` configuration (default: 5MB)
   - `max_chunk_count` configuration (default: 10,000)
   - Formula: `chunk_size = max(minimal_chunk_size, ceil(file_size / max_chunk_count))`
3. Checks for existing upload progress (resumable uploads)
4. Generates upload token for subsequent operations
5. Creates upload URLs for each part

**Response**:
```json
{
  "allowed": true,
  "action": "upload",
  "parts": [
    {
      "part_id": 0,
      "start": 0,
      "size": 5242880,
      "url": "https://server/api/dataset/{namespace}/{dataset}/upload?token=xxx&part_id=0...",
      "report_url": "https://server/api/dataset/{namespace}/{dataset}/upload-progress?token=xxx&part_id=0..."
    }
  ],
  "finished_parts": [0, 1, 2],
  "cancel_url": "https://server/api/dataset/{namespace}/{dataset}/upload-progress?action=abort...",
  "finish_url": "https://server/api/dataset/{namespace}/{dataset}/upload-progress?action=done..."
}
```

### Phase 2: Part Upload

For each part returned in the negotiation response:

**Endpoint**: `PUT /api/dataset/{namespace}/{dataset_name}/upload`

**Query Parameters**:
```
- token: JWT upload token
- part_id: Part number (0-indexed)
- checksum_value: File checksum
- file_size: Total file size
```

**Request Body**: Binary data for the specific chunk

**Server Processing**:
1. Verifies upload token
2. Creates/retrieves `MultipartFileWriter` instance
3. Writes chunk data to `part_file_{part_id}`
4. Marks part as complete in metadata

**Response**: 204 No Content on success

### Phase 3: Progress Reporting (Optional)

**Endpoint**: `POST /api/dataset/{namespace}/{dataset_name}/upload-progress`

**Query Parameters**:
```
- token: JWT upload token
- action: "progress-update"
- part_id: Part number
- checksum_value: File checksum
- file_size: Total file size
```

**Purpose**: Update upload progress metadata (currently a no-op in server implementation)

### Phase 4: Upload Completion or Cancellation

#### 4a. Complete Upload

**Endpoint**: `POST /api/dataset/{namespace}/{dataset_name}/upload-progress?action=done`

**Query Parameters**:
```
- token: JWT upload token
- action: "done"
- tag: Comma-separated tags (optional)
- checksum_value: File checksum
- file_size: Total file size
```

**Server Processing**:
1. Verifies all parts are uploaded
2. Assembles final file from parts
3. Imports file to local storage
4. Applies tags if specified
5. Removes temporary upload files

**Response**: 204 No Content on success

#### 4b. Cancel Upload

**Endpoint**: `POST /api/dataset/{namespace}/{dataset_name}/upload-progress?action=abort`

**Query Parameters**:
```
- token: JWT upload token
- action: "abort"
- checksum_value: File checksum
- file_size: Total file size
```

**Server Processing**:
1. Terminates upload writer
2. Cleans up temporary files

**Response**: 204 No Content

## Resumable Upload Support

The protocol supports resuming interrupted uploads:

1. **Upload State Persistence**: The server maintains upload state in `FilePartsInfo` objects
2. **Part Tracking**: Each uploaded part is marked in `.parts_status` file
3. **Resume Process**:
   - Client re-initiates upload negotiation with same checksum
   - Server returns list of already completed parts in `finished_parts`
   - Client skips uploading completed parts
   - Upload continues from the first incomplete part

## Storage Structure

### Temporary Upload Storage
```
{uploader_folder}/
├── {namespace}/
│   └── {dataset_name}/
│       └── dataset_file_{checksum}/
│           ├── .parts_info          # Upload metadata
│           ├── .parts_status        # Part completion status
│           ├── part_file_0          # Individual part files
│           ├── part_file_1
│           └── ...
```

### Final Storage
```
{data_folder}/
├── {namespace}/
│   └── {dataset_name}/
│       └── version/
│           └── {checksum}/
│               ├── file              # Final assembled dataset file
│               ├── meta.json         # Dataset metadata
│               └── .dataset.version.marker
```

## Client Implementation

The client (`FileServerClient`) handles the upload flow:

1. **Calculate file checksum** (SHA-256)
2. **Request upload permission** via negotiation endpoint
3. **Upload parts**:
   - Skip already uploaded parts (resumable support)
   - Read file chunks sequentially
   - Upload each chunk to its designated URL
   - Optionally report progress
4. **Finalize upload** via completion endpoint

### Error Handling

- Failed part uploads can be retried individually
- Entire upload can be resumed if interrupted
- Upload can be explicitly cancelled to clean up server resources

## Security Considerations

1. **Token-based Authorization**: All upload operations require valid JWT tokens
2. **Checksum Verification**: File integrity verified via SHA-256
3. **Path Traversal Protection**: `safe_join` used for all file operations
4. **Size Limits**: Configurable chunk sizes and part counts

## Configuration Parameters

Server administrators can configure:

- `minimal_chunk_size`: Minimum size for each upload chunk (default: 5MB)
- `max_chunk_count`: Maximum number of chunks allowed (default: 10,000)
- `allow_upload`: Global flag to enable/disable uploads
- `uploader_folder`: Temporary storage location for uploads
- `data_folder`: Final storage location for datasets

## Protocol Version Compatibility

The protocol includes version checking:
- Server version >= 0.0.37: Uses this multipart protocol
- Older versions: Fall back to legacy upload mechanism

The server includes its version in the `DATASET_SH_SERVER_VERSION` response header.