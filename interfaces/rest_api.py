from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from typing import Dict, Any
from .base import BaseInterface
from ..core.config import Config
from ..core.analyzer import SiteAnalyzer
from ..storage.factory import StorageFactory
from ..enumeration.factory import EnumeratorFactory
from ..models.scan_result import ScanResults

class RestAPI(BaseInterface):
    """Flask REST API interface with Swagger documentation"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.app = Flask(__name__)
        
        self.api = Api(
            self.app,
            version='1.0.0',
            title='Site Analyzer REST API',
            description='Comprehensive website analysis and enumeration API',
            doc='/docs/',
            prefix='/api/v1'
        )
        
        self.analyzer = SiteAnalyzer(config)
        
        storage = StorageFactory.create(config)
        self.analyzer.set_storage(storage)
        
        enumerators = EnumeratorFactory.create_enumerators(config)
        for enumerator in enumerators:
            self.analyzer.add_enumerator(enumerator)
        
        self._setup_models()
        self._setup_namespaces()
    
    def _setup_models(self):
        """Setup API models for Swagger documentation"""
        
        self.analyze_request = self.api.model('AnalyzeRequest', {
            'target': fields.String(required=True, description='Target URL to analyze', example='https://example.com'),
            'enumerators': fields.List(fields.String, description='Specific enumerators to use', example=['web_scanner', 'dns_enumeration'])
        })
        
        self.health_response = self.api.model('HealthResponse', {
            'status': fields.String(description='Service health status', example='healthy'),
            'service': fields.String(description='Service name', example='site_analyzer')
        })
        
        self.error_response = self.api.model('ErrorResponse', {
            'error': fields.String(description='Error message', example='Missing target parameter')
        })
        
        self.scan_result = self.api.model('ScanResult', {
            'scan_id': fields.String(description='Unique scan identifier'),
            'target': fields.String(description='Target URL'),
            'status': fields.String(description='Scan status', enum=['pending', 'running', 'completed', 'failed']),
            'start_time': fields.String(description='Scan start time (ISO format)'),
            'end_time': fields.String(description='Scan end time (ISO format)'),
            'emails': fields.List(fields.String, description='Discovered email addresses'),
            'urls': fields.List(fields.String, description='Discovered URLs'),
            'endpoints': fields.List(fields.String, description='Discovered API endpoints'),
            'keywords': fields.List(fields.String, description='Extracted keywords'),
            'subdomains': fields.List(fields.String, description='Discovered subdomains'),
            'ip_addresses': fields.List(fields.String, description='Discovered IP addresses'),
            'virtual_hosts': fields.List(fields.String, description='Discovered virtual hosts'),
            'enumeration_results': fields.List(fields.Raw, description='Detailed enumeration results')
        })
        
        self.enumerator_info = self.api.model('EnumeratorInfo', {
            'name': fields.String(description='Enumerator name'),
            'description': fields.String(description='Enumerator description'),
            'enabled': fields.Boolean(description='Whether enumerator is enabled')
        })
        
        self.storage_type_info = self.api.model('StorageTypeInfo', {
            'name': fields.String(description='Storage type name'),
            'description': fields.String(description='Storage type description'),
            'supported': fields.Boolean(description='Whether storage type is supported')
        })
    
    def _setup_namespaces(self):
        """Setup API namespaces and routes with Swagger documentation"""
        
        health_ns = Namespace('health', description='Health check operations')
        
        @health_ns.route('')
        class Health(Resource):
            @health_ns.doc('health_check')
            @health_ns.marshal_with(self.health_response)
            def get(self):
                """Health check endpoint"""
                return {'status': 'healthy', 'service': 'site_analyzer'}
        
        analysis_ns = Namespace('analysis', description='Website analysis operations')
        
        @analysis_ns.route('')
        class Analyze(Resource):
            @analysis_ns.doc('analyze_target')
            @analysis_ns.expect(self.analyze_request)
            @analysis_ns.marshal_with(self.scan_result, code=200)
            @analysis_ns.marshal_with(self.error_response, code=400)
            @analysis_ns.marshal_with(self.error_response, code=500)
            def post(self):
                """Analyze a target URL"""
                try:
                    data = request.get_json()
                    if not data or 'target' not in data:
                        return {'error': 'Missing target parameter'}, 400
                    
                    target = data['target']
                    results = self.analyzer.analyze(target)
                    
                    response = self._convert_results_to_dict(results)
                    return response
                    
                except Exception as e:
                    return {'error': str(e)}, 500
        
        scans_ns = Namespace('scans', description='Scan management operations')
        
        @scans_ns.route('')
        class ScansList(Resource):
            @scans_ns.doc('list_scans')
            @scans_ns.param('limit', 'Maximum number of scans to return', type=int, default=100)
            def get(self):
                """List recent scans"""
                try:
                    limit = request.args.get('limit', 100, type=int)
                    scans = self.analyzer.list_scans(limit)
                    return {'scans': scans}
                    
                except Exception as e:
                    return {'error': str(e)}, 500
        
        @scans_ns.route('/<string:scan_id>')
        class ScanDetail(Resource):
            @scans_ns.doc('get_scan')
            @scans_ns.marshal_with(self.scan_result, code=200)
            @scans_ns.marshal_with(self.error_response, code=404)
            @scans_ns.marshal_with(self.error_response, code=500)
            def get(self, scan_id):
                """Get specific scan result"""
                try:
                    results = self.analyzer.get_scan_result(scan_id)
                    if not results:
                        return {'error': 'Scan not found'}, 404
                    
                    response = self._convert_results_to_dict(results)
                    return response
                    
                except Exception as e:
                    return {'error': str(e)}, 500
            
            @scans_ns.doc('delete_scan')
            @scans_ns.marshal_with(self.error_response, code=404)
            @scans_ns.marshal_with(self.error_response, code=500)
            def delete(self, scan_id):
                """Delete scan result"""
                try:
                    success = self.analyzer.storage.delete(scan_id)
                    if success:
                        return {'message': 'Scan deleted successfully'}
                    else:
                        return {'error': 'Scan not found'}, 404
                        
                except Exception as e:
                    return {'error': str(e)}, 500
        
        config_ns = Namespace('config', description='Configuration and capabilities')
        
        @config_ns.route('/enumerators')
        class EnumeratorsList(Resource):
            @config_ns.doc('list_enumerators')
            @config_ns.marshal_list_with(self.enumerator_info)
            def get(self):
                """List available enumerators"""
                try:
                    enumerators = EnumeratorFactory.get_available_types()
                    return enumerators
                    
                except Exception as e:
                    return {'error': str(e)}, 500
        
        @config_ns.route('/storage-types')
        class StorageTypesList(Resource):
            @config_ns.doc('list_storage_types')
            @config_ns.marshal_list_with(self.storage_type_info)
            def get(self):
                """List available storage types"""
                try:
                    storage_types = StorageFactory.get_available_types()
                    return storage_types
                    
                except Exception as e:
                    return {'error': str(e)}, 500
        
        self.api.add_namespace(health_ns, path='/health')
        self.api.add_namespace(analysis_ns, path='/analyze')
        self.api.add_namespace(scans_ns, path='/scans')
        self.api.add_namespace(config_ns, path='/config')
    
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
