import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from ..storage.file_storage import FileStorage
from ..storage.mongodb_storage import MongoDBStorage
from ..storage.sql_storage import SQLStorage
from ..storage.factory import StorageFactory
from ..models.scan_result import ScanResult

class TestFileStorage:
    """Test file-based storage implementation"""
    
    def test_file_storage_initialization(self):
        """Test FileStorage initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileStorage({'output_dir': temp_dir})
            assert storage.output_dir == temp_dir
    
    def test_store_result(self):
        """Test storing scan result to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileStorage({'output_dir': temp_dir})
            
            result = ScanResult(
                scan_id="test-123",
                target="example.com",
                success=True,
                data={'emails': ['test@example.com']},
                errors=[]
            )
            
            storage.store(result)
            
            expected_file = os.path.join(temp_dir, "test-123.json")
            assert os.path.exists(expected_file)
    
    def test_retrieve_result(self):
        """Test retrieving scan result from file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileStorage({'output_dir': temp_dir})
            
            original_result = ScanResult(
                scan_id="test-456",
                target="example.com",
                success=True,
                data={'urls': ['https://example.com']},
                errors=[]
            )
            storage.store(original_result)
            
            retrieved_result = storage.retrieve("test-456")
            
            assert retrieved_result is not None
            assert retrieved_result.scan_id == "test-456"
            assert retrieved_result.target == "example.com"

class TestMongoDBStorage:
    """Test MongoDB storage implementation"""
    
    @patch('pymongo.MongoClient')
    def test_mongodb_initialization(self, mock_client):
        """Test MongoDB storage initialization"""
        mock_db = Mock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        config = {
            'host': 'localhost',
            'port': 27017,
            'database': 'test_db',
            'collection': 'scan_results'
        }
        
        storage = MongoDBStorage(config)
        assert storage.collection_name == 'scan_results'
    
    @patch('pymongo.MongoClient')
    def test_store_result_mongodb(self, mock_client):
        """Test storing result in MongoDB"""
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db
        
        storage = MongoDBStorage({
            'host': 'localhost',
            'database': 'test_db',
            'collection': 'scan_results'
        })
        
        result = ScanResult(
            scan_id="mongo-test",
            target="example.com",
            success=True,
            data={'keywords': ['api', 'token']},
            errors=[]
        )
        
        storage.store(result)
        mock_collection.insert_one.assert_called_once()
    
    @patch('pymongo.MongoClient')
    def test_retrieve_result_mongodb(self, mock_client):
        """Test retrieving result from MongoDB"""
        mock_collection = Mock()
        mock_collection.find_one.return_value = {
            'scan_id': 'mongo-retrieve',
            'target': 'example.com',
            'success': True,
            'data': {'endpoints': ['/api/users']},
            'errors': []
        }
        
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db
        
        storage = MongoDBStorage({
            'host': 'localhost',
            'database': 'test_db',
            'collection': 'scan_results'
        })
        
        result = storage.retrieve('mongo-retrieve')
        assert result.scan_id == 'mongo-retrieve'
        assert result.target == 'example.com'

class TestSQLStorage:
    """Test SQL storage implementation"""
    
    @patch('sqlalchemy.create_engine')
    def test_sql_storage_initialization(self, mock_create_engine):
        """Test SQL storage initialization"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        storage = SQLStorage({'connection_string': 'sqlite:///test.db'})
        assert storage.engine == mock_engine
    
    @patch('sqlalchemy.create_engine')
    def test_store_result_sql(self, mock_create_engine):
        """Test storing result in SQL database"""
        mock_engine = Mock()
        mock_session = Mock()
        mock_create_engine.return_value = mock_engine
        
        with patch('sqlalchemy.orm.sessionmaker') as mock_sessionmaker:
            mock_sessionmaker.return_value.return_value = mock_session
            
            storage = SQLStorage({'connection_string': 'sqlite:///test.db'})
            
            result = ScanResult(
                scan_id="sql-test",
                target="example.com",
                success=True,
                data={'js_paths': ['/js/app.js']},
                errors=[]
            )
            
            storage.store(result)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

class TestStorageFactory:
    """Test storage factory"""
    
    def test_create_file_storage(self):
        """Test creating file storage via factory"""
        config = {'type': 'file', 'output_dir': '/tmp/test'}
        storage = StorageFactory.create_storage(config)
        assert isinstance(storage, FileStorage)
    
    def test_create_mongodb_storage(self):
        """Test creating MongoDB storage via factory"""
        config = {
            'type': 'mongodb',
            'host': 'localhost',
            'database': 'test_db',
            'collection': 'results'
        }
        with patch('pymongo.MongoClient'):
            storage = StorageFactory.create_storage(config)
            assert isinstance(storage, MongoDBStorage)
    
    def test_create_sql_storage(self):
        """Test creating SQL storage via factory"""
        config = {
            'type': 'sql',
            'connection_string': 'sqlite:///test.db'
        }
        with patch('sqlalchemy.create_engine'):
            storage = StorageFactory.create_storage(config)
            assert isinstance(storage, SQLStorage)
    
    def test_invalid_storage_type(self):
        """Test handling invalid storage type"""
        config = {'type': 'invalid'}
        with pytest.raises(ValueError):
            StorageFactory.create_storage(config)

class TestStorageIntegration:
    """Integration tests for storage systems"""
    
    def test_storage_workflow(self):
        """Test complete storage workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileStorage({'output_dir': temp_dir})
            
            result = ScanResult(
                scan_id="integration-test",
                target="example.com",
                success=True,
                data={
                    'emails': ['test@example.com'],
                    'urls': ['https://example.com'],
                    'keywords': ['api', 'token']
                },
                errors=[]
            )
            
            storage.store(result)
            retrieved = storage.retrieve("integration-test")
            
            assert retrieved.scan_id == result.scan_id
            assert retrieved.target == result.target
            assert retrieved.data['emails'] == result.data['emails']
            assert retrieved.success == result.success
