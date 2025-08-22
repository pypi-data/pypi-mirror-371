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
            # Replica set connection string optimized for fast failover (w=1)
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{os.environ["MONGODB_HOST"]}/'
                f'?replicaSet={os.environ["MONGODB_REPLICA_SET"]}'
                f'&authSource={os.environ["MONGODB_AUTH_DB"]}'
                f'&readPreference=primaryPreferred'  # Use secondary when primary down
                f'&w=1'  # Write to primary only (matches cluster default)
                f'&wtimeout=5000'  # 5 second write timeout (matches cluster config)
                f'&serverSelectionTimeoutMS=15000'  # 15 seconds (3x election timeout)
                f'&connectTimeoutMS=10000'  # 10 seconds for individual connections
                f'&socketTimeoutMS=30000'  # 30 seconds for operations
                f'&heartbeatFrequencyMS=2000'  # 2 seconds (matches replica set settings)
                f'&localThresholdMS=15'  # Use nearby secondaries (15ms threshold)
                f'&retryWrites=true'  # Automatically retry writes on failover
                f'&retryReads=true'  # Automatically retry reads on failover
                f'&maxStalenessSeconds=90'  # Allow 90 seconds of staleness for reads
                f'&maxPoolSize=50'  # Connection pool size
                f'&minPoolSize=5'  # Minimum connections ready
                f'&maxIdleTimeMS=300000'  # 5 minutes max idle connection time
            )
        self._client = None  # Client will be created on first access

    @property
    def client(self) -> MongoClient:
        """
        Lazily initialize the MongoClient for this process.
        """
        if self._client is None:
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