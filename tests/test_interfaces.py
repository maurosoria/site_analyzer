import pytest
from unittest.mock import Mock, patch, AsyncMock
from interfaces.cli import CLIInterface
from interfaces.rest_api import RestAPI
from interfaces.grpc_server import GRPCInterface

class TestCLIInterface:
    """Test CLI interface"""
    
    def test_cli_initialization(self, config):
        """Test CLI interface initialization"""
        cli = CLIInterface(config)
        assert cli.config == config
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args, config):
        """Test CLI argument parsing"""
        mock_args = Mock()
        mock_args.target = 'example.com'
        mock_args.enumerators = ['web_scanner', 'dns_enumeration']
        mock_args.storage = 'file'
        mock_args.output_dir = '/tmp/results'
        mock_parse_args.return_value = mock_args
        
        cli = CLIInterface(config)
        args = cli._parse_arguments()
        
        assert args.target == 'example.com'
        assert 'web_scanner' in args.enumerators
    
    @patch('..core.analyzer.SiteAnalyzer')
    def test_run_analysis(self, mock_analyzer_class, config):
        """Test running analysis via CLI"""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = Mock(success=True)
        mock_analyzer_class.return_value = mock_analyzer
        
        cli = CLIInterface(config)
        
        with patch.object(cli, '_parse_arguments') as mock_parse:
            mock_args = Mock()
            mock_args.target = 'example.com'
            mock_args.enumerators = ['web_scanner']
            mock_args.storage = 'file'
            mock_args.output_dir = '/tmp'
            mock_parse.return_value = mock_args
            
            cli.run()
            mock_analyzer.analyze.assert_called_once()

class TestRestAPIInterface:
    """Test REST API interface"""
    
    def test_api_initialization(self, config):
        """Test REST API initialization"""
        api = RestAPI(config)
        assert api.config == config
        assert api.app is not None
    
    @patch('..core.analyzer.SiteAnalyzer')
    def test_analyze_endpoint(self, mock_analyzer_class, config):
        """Test /analyze endpoint"""
        mock_analyzer = Mock()
        mock_result = Mock()
        mock_result.to_dict.return_value = {'success': True, 'target': 'example.com'}
        mock_analyzer.analyze.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer
        
        api = RestAPI(config)
        
        with api.app.test_client() as client:
            response = client.post('/analyze', json={
                'target': 'example.com',
                'enumerators': ['web_scanner'],
                'storage_config': {'type': 'file', 'output_dir': '/tmp'}
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_analyze_endpoint_missing_target(self, config):
        """Test /analyze endpoint with missing target"""
        api = RestAPI(config)
        
        with api.app.test_client() as client:
            response = client.post('/analyze', json={
                'enumerators': ['web_scanner']
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_health_endpoint(self, config):
        """Test /health endpoint"""
        api = RestAPI(config)
        
        with api.app.test_client() as client:
            response = client.get('/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'

class TestGRPCInterface:
    """Test gRPC interface"""
    
    def test_grpc_initialization(self, config):
        """Test gRPC interface initialization"""
        grpc_interface = GRPCInterface(config)
        assert grpc_interface.config == config
    
    @patch('..core.analyzer.SiteAnalyzer')
    @pytest.mark.asyncio
    async def test_analyze_grpc(self, mock_analyzer_class, config):
        """Test gRPC Analyze method"""
        mock_analyzer = Mock()
        mock_result = Mock()
        mock_result.to_dict.return_value = {
            'success': True,
            'target': 'example.com',
            'data': {'emails': ['test@example.com']}
        }
        mock_analyzer.analyze.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer
        
        grpc_interface = GRPCInterface(config)
        
        mock_request = Mock()
        mock_request.target = 'example.com'
        mock_request.enumerators = ['web_scanner']
        mock_request.storage_config = '{"type": "file"}'
        
        mock_context = Mock()
        
        response = await grpc_interface.Analyze(mock_request, mock_context)
        
        assert response.success is True
        assert response.target == 'example.com'
    
    @patch('grpc.aio.server')
    @pytest.mark.asyncio
    async def test_serve_grpc(self, mock_server, config):
        """Test gRPC server startup"""
        mock_server_instance = AsyncMock()
        mock_server.return_value = mock_server_instance
        
        grpc_interface = GRPCInterface(config)
        
        with patch.object(grpc_interface, 'serve') as mock_serve:
            mock_serve.return_value = None
            grpc_interface.serve()
            mock_serve.assert_called_once()

class TestInterfaceIntegration:
    """Integration tests for interfaces"""
    
    @patch('..core.analyzer.SiteAnalyzer')
    def test_multiple_interfaces_same_config(self, mock_analyzer_class, config):
        """Test that multiple interfaces can use the same config"""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = Mock(success=True)
        mock_analyzer_class.return_value = mock_analyzer
        
        cli = CLIInterface(config)
        api = RestAPI(config)
        grpc_interface = GRPCInterface(config)
        
        assert cli.config == config
        assert api.config == config
        assert grpc_interface.config == config
    
    def test_interface_error_handling(self, config):
        """Test error handling across interfaces"""
        with patch('..core.analyzer.SiteAnalyzer', side_effect=Exception("Test error")):
            api = RestAPI(config)
            
            with api.app.test_client() as client:
                response = client.post('/analyze', json={
                    'target': 'example.com',
                    'enumerators': ['web_scanner'],
                    'storage_config': {'type': 'file'}
                })
                
                assert response.status_code == 500
                data = response.get_json()
                assert 'error' in data
