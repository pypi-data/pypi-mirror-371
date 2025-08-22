import json
import os
import tempfile
import zipfile
from typing import Optional, List, Union
import re

from .core import CollectionConfig, DatasetFileMeta
from .models import DatasetFileInternalPath
from .utils.misc import id_function
from .utils.sample import reservoir_sampling


class DatasetFile:

    def __init__(self):
        raise ValueError('Please use DatasetFile.open(filename, mode)')

    @staticmethod
    def open(fp: str, mode: str = 'r'):
        """
        Open a dataset file
        :param fp: path to the file
        :param mode: r for read and w for write.
        :return:
        """
        if mode == 'r':
            return DatasetFileReader(fp)
        elif mode == 'w':
            return DatasetFileWriter(fp)
        else:
            raise ValueError('mode must be one of "r" or "w"')

    @staticmethod
    def binary_file_path(fn: str):
        return os.path.join(DatasetFileInternalPath.BINARY_FOLDER, fn)


class DatasetFileWriter:
    def __init__(self, file_path: str, compression=zipfile.ZIP_DEFLATED, compresslevel=9, zip_args=None):
        """
        Write to a dataset file, this object can also be used as a context manager.

        This object need to be closed.

        :param file_path: location of the dataset file to write.
        :param compression: compress mode for zip file.
        :param compresslevel: note that the default compression algorithm ZIP_LZMA do not use this value.

        """
        if zip_args is None:
            zip_args = {}
        self.zip_file = zipfile.ZipFile(
            file_path, 'w', compression=compression, compresslevel=compresslevel,
            **zip_args
        )
        self.meta = DatasetFileMeta()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        close the writer.
        :return:
        """
        with self.zip_file.open(DatasetFileInternalPath.META_FILE_NAME, 'w') as out:
            out.write(self.meta.model_dump_json().encode('utf-8'))
        self.zip_file.close()

    def update_meta(self, meta):
        author = meta.get('author', None)
        if author is not None:
            self.meta.author = author

        author_email = meta.get('authorEmail', None)
        if author_email is not None:
            self.meta.authorEmail = author_email

        tags = meta.get('tags', None)
        if tags is not None:
            self.meta.tags = tags

        dataset_metadata = meta.get('dataset_metadata', None)
        if dataset_metadata is not None:
            self.meta.dataset_metadata = dataset_metadata

    def add_collection(
            self,
            collection_name: str,
            data: List[Union[dict, list]],
            type_annotation: Optional[str] = None,
            tqdm=id_function,
    ):
        """
        add a data collection to this dataset.
        :param collection_name: name of the collection to add.
        :param data: list of json compatible objects .
        :param type_annotation: type annotation of the data - Typelang string.
        :param tqdm: Optional tqdm progress bar.
        :return:
        """
        for coll in self.meta.collections:
            if coll.name == collection_name:
                raise ValueError(f'collection {collection_name} already exists')

        new_coll = CollectionConfig(
            name=collection_name,
        )

        self.meta.collections.append(new_coll)

        target_fp = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            collection_name,
            DatasetFileInternalPath.DATA_FILE
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            fn = os.path.join(temp_dir, 'temp-dataset.jsonl')
            with open(fn, 'w') as out:
                for item in tqdm(data):
                    out.write(json.dumps(item))
                    out.write("\n")
            self.zip_file.write(fn, arcname=target_fp)
        #
        # with self.zip_file.open(target_fp, 'w') as out:
        #     for item in tqdm(data):
        #         out.write(json.dumps(item).encode('utf-8'))
        #         out.write("\n".encode('utf-8'))

        if type_annotation is not None:
            type_file = os.path.join(
                DatasetFileInternalPath.COLLECTION_FOLDER,
                collection_name,
                DatasetFileInternalPath.TYPE_FILE
            )

            with self.zip_file.open(type_file, 'w') as out:
                # Validate the Typelang schema
                self._validate_typelang(type_annotation)
                out.write(type_annotation.encode('utf-8'))

    def _validate_typelang(self, content: str) -> None:
        """Validate that Typelang content starts with // use comment and is valid Typelang.
        
        Raises:
            ValueError: With specific error message for each validation failure
        """
        # Check if content is empty
        if not content or not content.strip():
            raise ValueError(
                "Typelang schema is empty. Schema must start with '// use TypeName' comment "
                "followed by type definitions."
            )
        
        lines = content.strip().split('\n')
        if not lines:
            raise ValueError(
                "Typelang schema is empty. Schema must start with '// use TypeName' comment."
            )
        
        first_line = lines[0].strip()
        
        # Check for required // use comment
        if not first_line.startswith('//'):
            raise ValueError(
                f"Typelang schema must start with '// use TypeName' comment on the first line. "
                f"Found: '{first_line[:50]}{'...' if len(first_line) > 50 else ''}'"
            )
        
        if not re.match(r'^//\s+use\s+\w+', first_line):
            raise ValueError(
                f"Invalid format for first line comment. Expected '// use TypeName', "
                f"but found: '{first_line}'. Make sure there's a space after '//' and 'use', "
                f"followed by a valid type name."
            )
        
        # Extract the type name from the comment
        match = re.match(r'^//\s+use\s+(\w+)', first_line)
        if not match:
            raise ValueError(
                f"Could not extract type name from comment. Expected format: '// use TypeName', "
                f"found: '{first_line}'"
            )
        
        type_name = match.group(1)
        
        # Validate the Typelang syntax using the compiler
        try:
            from typelang import Compiler
        except ImportError:
            # If typelang is not installed, warn but allow (for environments without typelang)
            import warnings
            warnings.warn(
                "Typelang package is not installed. Skipping syntax validation. "
                "Install with: pip install typelang"
            )
            return
        
        try:
            compiler = Compiler()
            result = compiler.compile(content, target="jsonschema")  # Use jsonschema to validate
            
            if result is None:
                # Check for compilation errors
                errors = compiler.get_errors()
                if errors:
                    error_msg = "Typelang compilation failed with the following errors:\n"
                    for i, error in enumerate(errors, 1):
                        error_msg += f"  {i}. {error}\n"
                    error_msg += "\nPlease fix the syntax errors in your Typelang schema."
                    raise ValueError(error_msg)
                else:
                    raise ValueError(
                        "Typelang compilation failed but no specific errors were reported. "
                        "Please check your schema syntax."
                    )
            
            # Verify the specified type exists in the schema
            # The type_name from the comment should be defined in the schema
            if f"type {type_name}" not in content and f"interface {type_name}" not in content:
                # Try to find what types ARE defined to give a helpful error
                defined_types = []
                for line in content.split('\n'):
                    type_match = re.match(r'^\s*(type|interface)\s+(\w+)', line)
                    if type_match:
                        defined_types.append(type_match.group(2))
                
                if defined_types:
                    raise ValueError(
                        f"Type '{type_name}' specified in '// use {type_name}' is not defined in the schema.\n"
                        f"Found the following type definitions: {', '.join(defined_types)}\n"
                        f"Please either define 'type {type_name}' or change the '// use' comment to match an existing type."
                    )
                else:
                    raise ValueError(
                        f"Type '{type_name}' specified in '// use {type_name}' is not defined in the schema.\n"
                        f"No type definitions found. Please add 'type {type_name} = {{ ... }}' to define the type."
                    )
            
        except ValueError:
            # Re-raise ValueError as-is (these are our validation errors)
            raise
        except Exception as e:
            # Catch any other unexpected errors and provide context
            raise ValueError(
                f"Unexpected error while validating Typelang schema: {str(e)}\n"
                f"This might be a bug. Please check your schema or report this issue."
            )
    
    def add_binary_file(self, fn: str, content: bytes):
        """
        Add a binary file to the dataset
        :param fn: name of the binary file.
        :param content: content in bytes.
        :return:
        """
        binary_file_path = DatasetFile.binary_file_path(fn)
        with self.zip_file.open(binary_file_path, 'w') as out:
            out.write(content)


class DatasetFileReader:
    def __init__(self, file_path):
        """
        Read a dataset, this object can be used as a context manager.

        This object must be closed.

        :param file_path:
        """
        self.zip_file = zipfile.ZipFile(file_path, 'r')

        with self.zip_file.open(DatasetFileInternalPath.META_FILE_NAME, 'r') as fd:
            self.meta = DatasetFileMeta(**json.load(fd))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.zip_file.close()

    def binary_files(self):
        """
        Open a binary file for read.
        :return: a file descriptor for the binary file to read.
        """
        prefix = DatasetFileInternalPath.BINARY_FOLDER + '/'
        for name in self.zip_file.namelist():
            if name.startswith(prefix):
                yield name[len(prefix):]

    def open_binary_file(self, filename):
        """
        Open a binary file for read.
        :param filename: name of the binary file.
        :return: a file descriptor for the binary file to read.
        """
        return self.zip_file.open(
            DatasetFile.binary_file_path(filename),
            'r'
        )

    def collection(self, collection_name):
        """
        Open a collection.
        :param collection_name: name of a collection
        :return: a CollectionReader object for the given collection name.
        """
        cfg = [c for c in self.meta.collections if c.name == collection_name]
        if len(cfg) == 0:
            raise ValueError(f"Collection {collection_name} do not exist")
        else:
            cfg = cfg[0]
        return CollectionReader(self.zip_file, collection_name, cfg)

    def coll(self, collection_name):
        return self.collection(collection_name)

    def collections(self):
        """
        List all collection names
        :return: list of collection names.
        """
        return [c.name for c in self.meta.collections]

    def __getitem__(self, item):
        return self.collection(item)


class CollectionReader(object):
    def __init__(self, zip_file, collection_name, config: CollectionConfig):
        """
        Collection Reader
        :param zip_file:
        :param collection_name:
        :param config:
        """
        self.zip_file = zip_file
        self.collection_name = collection_name
        self.config = config

    def type_annotation(self) -> Optional[str]:
        """Get type annotation - returns Typelang string."""
        ta_content = self.type_annotation_raw()
        if ta_content is None:
            return None
        return ta_content

    def type_annotation_dict(self) -> Optional[dict]:
        """Get type annotation as dict (for backward compatibility)."""
        ta_content = self.type_annotation_raw()
        if ta_content is None:
            return None
        
        # Try to parse as JSON
        try:
            return json.loads(ta_content)
        except json.JSONDecodeError:
            # It's Typelang format, return None for dict representation
            return None
    
    def type_annotation_raw(self) -> Optional[str]:
        """Get raw type annotation content."""
        entry = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            self.collection_name,
            DatasetFileInternalPath.TYPE_FILE
        )
        if entry in self.zip_file.namelist():
            with self.zip_file.open(entry, 'r') as fd:
                return fd.read().decode('utf-8')
        return None
    
    def type_annotation_typelang(self) -> Optional[str]:
        """Get type annotation as Typelang string."""
        ta_content = self.type_annotation_raw()
        if ta_content and ta_content.strip().startswith('// use'):
            return ta_content
        return None
    
    def validate_typelang(self) -> bool:
        """Validate that the type.tl file has proper format."""
        tl_content = self.type_annotation_typelang()
        if not tl_content:
            return True  # No type annotation is valid
        
        lines = tl_content.strip().split('\n')
        if not lines:
            return False
        
        # Check first line for // use comment
        first_line = lines[0].strip()
        return bool(re.match(r'^//\s+use\s+\w+', first_line))

    def top(self, n=10):
        ret = []
        for i, row in enumerate(self):
            if i >= n:
                break
            ret.append(row)
        return ret

    def random_sample(self, n=10):
        return reservoir_sampling(self, n)

    def __iter__(self):
        """
        Iterate through the collection.
        :return:
        """
        entry = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            self.collection_name,
            DatasetFileInternalPath.DATA_FILE
        )
        with self.zip_file.open(entry, 'r') as fd:
            for line in fd:
                line = line.strip()
                if len(line) > 0:
                    item = json.loads(line)
                    yield item

    def to_list(self):
        """
        Read the collection as list instead of iterator
        :return:
        """
        return list(self)


# Standard IO operations


def open_dataset_file(fp: str) -> 'DatasetFileReader':
    """
    Read a dataset file
    :param fp: path to the file
    :return:
    """
    return DatasetFileReader(fp)


def create(fp: str, compression=zipfile.ZIP_DEFLATED, compresslevel=9) -> 'DatasetFileWriter':
    """
    Create a dataset file to write
    :param fp: path to the file
    :param compression: compress mode for zip file.
    :param compresslevel: note that the default compression algorithm ZIP_LZMA do not use this value.
    :return:
    """
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return DatasetFileWriter(fp, compression=compression, compresslevel=compresslevel)
