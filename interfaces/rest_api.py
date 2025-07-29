from flask import Flask, request, jsonify
from typing import Dict, Any
from .base import BaseInterface
from ..core.config import Config
from ..core.analyzer import SiteAnalyzer
from ..storage.factory import StorageFactory
from ..enumeration.factory import EnumeratorFactory
from ..models.scan_result import ScanResults

class RestAPI(BaseInterface):
    """Flask REST API interface"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.app = Flask(__name__)
        self.analyzer = SiteAnalyzer(config)
        
        storage = StorageFactory.create(config)
        self.analyzer.set_storage(storage)
        
        enumerators = EnumeratorFactory.create_enumerators(config)
        for enumerator in enumerators:
            self.analyzer.add_enumerator(enumerator)
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'service': 'site_analyzer'})
        
        @self.app.route('/analyze', methods=['POST'])
        def analyze():
            """REST endpoint for analysis"""
            try:
                data = request.get_json()
                if not data or 'target' not in data:
                    return jsonify({'error': 'Missing target parameter'}), 400
                
                target = data['target']
                results = self.analyzer.analyze(target)
                
                response = self._convert_results_to_dict(results)
                return jsonify(response)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/scans', methods=['GET'])
        def list_scans():
            """List recent scans"""
            try:
                limit = request.args.get('limit', 100, type=int)
                scans = self.analyzer.list_scans(limit)
                return jsonify({'scans': scans})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/scans/<scan_id>', methods=['GET'])
        def get_scan(scan_id):
            """Get specific scan result"""
            try:
                results = self.analyzer.get_scan_result(scan_id)
                if not results:
                    return jsonify({'error': 'Scan not found'}), 404
                
                response = self._convert_results_to_dict(results)
                return jsonify(response)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/scans/<scan_id>', methods=['DELETE'])
        def delete_scan(scan_id):
            """Delete scan result"""
            try:
                success = self.analyzer.storage.delete(scan_id)
                if success:
                    return jsonify({'message': 'Scan deleted successfully'})
                else:
                    return jsonify({'error': 'Scan not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/enumerators', methods=['GET'])
        def list_enumerators():
            """List available enumerators"""
            try:
                enumerators = EnumeratorFactory.get_available_types()
                return jsonify({'enumerators': enumerators})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/storage/types', methods=['GET'])
        def list_storage_types():
            """List available storage types"""
            try:
                storage_types = StorageFactory.get_available_types()
                return jsonify({'storage_types': storage_types})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _convert_results_to_dict(self, results: ScanResults) -> Dict[str, Any]:
        """Convert ScanResults to dictionary for JSON response"""
        return {
            'scan_id': results.scan_id,
            'target': results.target,
            'status': results.status.value,
            'start_time': results.start_time.isoformat(),
            'end_time': results.end_time.isoformat() if results.end_time else None,
            'emails': list(results.emails),
            'urls': list(results.urls),
            'endpoints': list(results.endpoints),
            'keywords': list(results.keywords),
            'sourcemap_matches': list(results.sourcemap_matches),
            'js_paths': list(results.js_paths),
            'subdomains': list(results.subdomains),
            'dns_records': results.dns_records,
            'historical_dns': results.historical_dns,
            'whois_data': results.whois_data,
            'domain_info': results.domain_info,
            'ip_addresses': list(results.ip_addresses),
            'virtual_hosts': list(results.virtual_hosts),
            'detected_services': results.detected_services,
            'enumeration_results': [
                {
                    'enumerator_name': er.enumerator_name,
                    'target': er.target,
                    'timestamp': er.timestamp.isoformat(),
                    'data_summary': {
                        'keys': list(er.data.keys()),
                        'total_items': sum(len(v) if isinstance(v, (list, set, dict)) else 1 for v in er.data.values())
                    },
                    'errors': er.errors
                }
                for er in results.enumeration_results
            ]
        }
    
    def run(self, *args, **kwargs):
        """Start Flask server"""
        host = kwargs.get('host', '0.0.0.0')
        port = kwargs.get('port', self.config.rest_port)
        debug = kwargs.get('debug', False)
        
        print(f"Starting REST API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def display_results(self, results: ScanResults):
        """Display results (not used in REST interface)"""
        pass
