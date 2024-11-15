#!/usr/bin/env python3
"""Base module.
Defines a reusable `Base` class for managing and persisting objects.
Provides functionality for:
- Object initialization with unique identifiers.
- JSON serialization and deserialization.
- File-based persistence for saving and loading objects.
- CRUD operations and querying.

Dependencies:
- `json` for JSON serialization/deserialization.
- `uuid` for generating unique identifiers.
- `os.path` for file operations.
- `datetime` for handling timestamps.
- `typing` for type hints.
"""

import json
import uuid
from os import path
from datetime import datetime
from typing import TypeVar, List, Iterable


# Define constants for timestamp formatting and in-memory data storage
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"  # ISO-like timestamp format
DATA = {}  # Global in-memory storage for objects of different classes


class Base():
    """Base class for creating and managing objects.
    Provides unique ID generation, timestamp tracking, and file-based storage.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """Initialize a Base instance with optional arguments.
        
        Attributes:
        - `id` (str): Unique identifier for the object (default: new UUID).
        - `created_at` (datetime): Timestamp when the object was created.
        - `updated_at` (datetime): Timestamp when the object was last updated.
        
        If `id`, `created_at`, or `updated_at` are provided in `kwargs`, they are
        used; otherwise, defaults are generated.
        """
        s_class = str(self.__class__.__name__)
        if DATA.get(s_class) is None:
            DATA[s_class] = {}  # Initialize storage for the class type

        # Initialize attributes with defaults or provided values
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.created_at = datetime.strptime(kwargs.get('created_at', datetime.utcnow().strftime(TIMESTAMP_FORMAT)),
                                            TIMESTAMP_FORMAT)
        self.updated_at = datetime.strptime(kwargs.get('updated_at', datetime.utcnow().strftime(TIMESTAMP_FORMAT)),
                                            TIMESTAMP_FORMAT)

    def __eq__(self, other: TypeVar('Base')) -> bool:
        """Compare two Base objects for equality based on their IDs."""
        if type(self) != type(other):
            return False
        return self.id == other.id

    def to_json(self, for_serialization: bool = False) -> dict:
        """Convert the object to a JSON-serializable dictionary.
        
        If `for_serialization` is True, private attributes are included.
        Timestamps are converted to strings in the defined format.
        """
        result = {}
        for key, value in self.__dict__.items():
            if not for_serialization and key.startswith('_'):
                continue
            if isinstance(value, datetime):
                result[key] = value.strftime(TIMESTAMP_FORMAT)
            else:
                result[key] = value
        return result

    @classmethod
    def load_from_file(cls):
        """Load all objects of the class type from a JSON file."""
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        DATA[s_class] = {}
        if not path.exists(file_path):  # Return if no file exists
            return

        with open(file_path, 'r') as f:
            objs_json = json.load(f)
            for obj_id, obj_json in objs_json.items():
                DATA[s_class][obj_id] = cls(**obj_json)

    @classmethod
    def save_to_file(cls):
        """Save all objects of the class type to a JSON file."""
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        objs_json = {obj_id: obj.to_json(True) for obj_id, obj in DATA[s_class].items()}

        with open(file_path, 'w') as f:
            json.dump(objs_json, f)

    def save(self):
        """Save the current object to the in-memory storage and persist to file."""
        s_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()  # Update the `updated_at` timestamp
        DATA[s_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self):
        """Remove the object from in-memory storage and persist changes."""
        s_class = self.__class__.__name__
        if self.id in DATA[s_class]:
            del DATA[s_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def count(cls) -> int:
        """Return the count of all objects of the class type."""
        return len(DATA[cls.__name__])

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]:
        """Return all objects of the class type."""
        return cls.search()

    @classmethod
    def get(cls, id: str) -> TypeVar('Base'):
        """Retrieve a single object by its ID."""
        return DATA[cls.__name__].get(id)

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]:
        """Search for objects matching specified attributes.

        Args:
        - `attributes` (dict): Key-value pairs to match object attributes.
        
        Returns:
        - A list of matching objects.
        """
        s_class = cls.__name__

        def _search(obj):
            if not attributes:  # Return all objects if no attributes specified
                return True
            return all(getattr(obj, k, None) == v for k, v in attributes.items())

        return list(filter(_search, DATA[s_class].values()))

