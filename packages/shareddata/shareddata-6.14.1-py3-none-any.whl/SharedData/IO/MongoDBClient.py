import os
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection

class MongoDBClient:
    """
    MongoDB client handler for safe usage in forking environments.
    Lazily initializes a client to avoid fork-safety warnings.
    Optimized for replica set failover scenarios.
    """

    def __init__(self, user: str = 'SharedData') -> None:
        """
        Initialize MongoDB client handler.
        
        Args:
            user (str): The database user namespace. Defaults to 'SharedData'.
        """
        self._user = user
        if not 'MONGODB_REPLICA_SET' in os.environ:
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{os.environ["MONGODB_HOST"]}:'
                f'{os.environ["MONGODB_PORT"]}/'
            )
        else:
            # Replica set connection string optimized for failover scenarios
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{os.environ["MONGODB_HOST"]}/'
                f'?replicaSet={os.environ["MONGODB_REPLICA_SET"]}'
                f'&authSource={os.environ["MONGODB_AUTH_DB"]}'
                f'&readPreference=primaryPreferred'  # Use secondary when primary down
                f'&w=1'  # Explicit write concern 1 for maximum availability
                f'&serverSelectionTimeoutMS=5000'  # Fast failover detection (reduced from 15s)
                f'&connectTimeoutMS=5000'  # Fast connection timeout for down nodes
                f'&socketTimeoutMS=10000'  # Reduced socket timeout
                f'&heartbeatFrequencyMS=2000'  # More frequent health checks
                f'&retryWrites=true'  # Automatically retry writes on failover
                f'&retryReads=true'  # Automatically retry reads on failover
                f'&maxPoolSize=50'  # Reasonable connection pool size
                f'&minPoolSize=5'  # Keep minimum connections ready
            )
        self._client = None  # Client will be created on first access

    @property
    def client(self) -> MongoClient:
        """
        Lazily initialize the MongoClient for this process.
        Includes health check and automatic reconnection for failover scenarios.
        """
        if self._client is None:
            self._client = MongoClient(self.mongodb_conn_str)
        
        # Test connection health and recreate if needed
        try:
            # Quick ping to test if connection is alive
            self._client.admin.command('ping')
        except Exception:
            # Connection is dead, recreate it
            if self._client:
                self._client.close()
            self._client = MongoClient(self.mongodb_conn_str)
        
        return self._client

    @client.setter
    def client(self, value: MongoClient) -> None:
        """
        Manually set the MongoDB client.
        """
        self._client = value

    def __getitem__(self, collection_name: str) -> Collection:
        """
        Allow dictionary-like access to collections in the user's database.
        
        Args:
            collection_name (str): The name of the collection to access.
        
        Returns:
            Collection: The requested MongoDB collection.
        """
        return self.client[self._user][collection_name]
    
    def execute_with_retry(self, operation, max_retries: int = 3, delay: float = 0.5):
        """
        Execute a MongoDB operation with automatic retry on connection failures.
        
        Args:
            operation: A callable that performs the MongoDB operation
            max_retries (int): Maximum number of retry attempts
            delay (float): Delay between retries in seconds
            
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        import time
        
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except (pymongo.errors.ServerSelectionTimeoutError, 
                    pymongo.errors.NetworkTimeout,
                    pymongo.errors.AutoReconnect) as e:
                last_exception = e
                if attempt < max_retries:
                    # Force client recreation on connection errors
                    if self._client:
                        self._client.close()
                        self._client = None
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise
            except Exception as e:
                # Don't retry on non-connection errors
                raise
        
        raise last_exception
        
    @staticmethod
    def ensure_index(coll, index_fields, **kwargs):
        """
        Ensure a specific index exists on the collection.
        
        Parameters:
            coll (pymongo.collection.Collection): The MongoDB collection.
            index_fields (list of tuples): Index fields and order, e.g., [('status', ASCENDING)].
            kwargs: Any additional options for create_index (e.g., name, unique).
        """
        existing_indexes = coll.index_information()

        # Normalize input index spec for comparison
        target_index = pymongo.helpers._index_list(index_fields)

        for index_name, index_data in existing_indexes.items():
            if pymongo.helpers._index_list(index_data['key']) == target_index:
                return  # Index already exists

        coll.create_index(index_fields, **kwargs)