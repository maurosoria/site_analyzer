import argparse
import json
from typing import Optional
from interfaces.base import BaseInterface
from core.config import Config
from core.analyzer import SiteAnalyzer
from storage.factory import StorageFactory
from enumeration.factory import EnumeratorFactory
from models.scan_result import ScanResults

class CLIInterface(BaseInterface):
    """Command line interface"""
    
    def run(self, args: Optional[list] = None):
        """Run CLI analysis"""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        config = self._create_config_from_args(parsed_args)
        
        analyzer = SiteAnalyzer(config)
        
        storage = StorageFactory.create(config)
        analyzer.set_storage(storage)
        
        enumerators = EnumeratorFactory.create_enumerators(config)
        for enumerator in enumerators:
            analyzer.add_enumerator(enumerator)
        
        if parsed_args.command == 'analyze':
            results = analyzer.analyze(parsed_args.target)
            self.display_results(results)
            
        elif parsed_args.command == 'list':
            scans = analyzer.list_scans(parsed_args.limit)
            self._display_scan_list(scans)
            
        elif parsed_args.command == 'show':
            results = analyzer.get_scan_result(parsed_args.scan_id)
            if results:
                self.display_results(results)
            else:
                print(f"Scan {parsed_args.scan_id} not found")
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(description='Site Analyzer - Web reconnaissance tool')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        analyze_parser = subparsers.add_parser('analyze', help='Analyze a target')
        analyze_parser.add_argument('-u', '--target', required=True, help='Target URL or domain')
        analyze_parser.add_argument('--storage-type', choices=['file', 'mongodb', 'sql'], 
                                  default='file', help='Storage backend type')
        analyze_parser.add_argument('--storage-config', help='Storage configuration (JSON)')
        analyze_parser.add_argument('--enumerators', nargs='+', 
                                  choices=['web_scanner', 'dns_enumeration', 'security_trails'],
                                  default=['web_scanner', 'dns_enumeration'],
                                  help='Enabled enumerators')
        analyze_parser.add_argument('--security-trails-key', help='SecurityTrails API key')
        analyze_parser.add_argument('--output-format', choices=['json', 'table'], 
                                  default='table', help='Output format')
        analyze_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        
        list_parser = subparsers.add_parser('list', help='List previous scans')
        list_parser.add_argument('--limit', type=int, default=10, help='Number of scans to show')
        list_parser.add_argument('--storage-type', choices=['file', 'mongodb', 'sql'], 
                                default='file', help='Storage backend type')
        list_parser.add_argument('--storage-config', help='Storage configuration (JSON)')
        
        show_parser = subparsers.add_parser('show', help='Show specific scan results')
        show_parser.add_argument('scan_id', help='Scan ID to show')
        show_parser.add_argument('--storage-type', choices=['file', 'mongodb', 'sql'], 
                                default='file', help='Storage backend type')
        show_parser.add_argument('--storage-config', help='Storage configuration (JSON)')
        show_parser.add_argument('--output-format', choices=['json', 'table'], 
                                default='table', help='Output format')
        
        return parser
    
    def _create_config_from_args(self, args) -> Config:
        """Create config from parsed arguments"""
        storage_config = {}
        if hasattr(args, 'storage_config') and args.storage_config:
            storage_config = json.loads(args.storage_config)
        
        config = Config(
            target=getattr(args, 'target', None),
            storage_type=args.storage_type,
            storage_config=storage_config,
            security_trails_api_key=getattr(args, 'security_trails_key', None),
            enabled_enumerators=getattr(args, 'enumerators', ['web_scanner', 'dns_enumeration']),
            log_level='DEBUG' if getattr(args, 'debug', False) else 'INFO'
        )
        
        return config
    
    def display_results(self, results: ScanResults):
        """Display scan results"""
        print(f"\n=== Scan Results for {results.target} ===")
        print(f"Scan ID: {results.scan_id}")
        print(f"Status: {results.status.value}")
        print(f"Start Time: {results.start_time}")
        print(f"End Time: {results.end_time}")
        
        if results.emails:
            print(f"\nEmails Found ({len(results.emails)}):")
            for email in sorted(results.emails):
                print(f"  - {email}")
        
        if results.subdomains:
            print(f"\nSubdomains Found ({len(results.subdomains)}):")
            for subdomain in sorted(results.subdomains):
                print(f"  - {subdomain}")
        
        if results.urls:
            print(f"\nURLs Found ({len(results.urls)}):")
            for url in sorted(list(results.urls)[:10]):  # Limit to first 10
                print(f"  - {url}")
            if len(results.urls) > 10:
                print(f"  ... and {len(results.urls) - 10} more")
        
        if results.endpoints:
            print(f"\nEndpoints Found ({len(results.endpoints)}):")
            for endpoint in sorted(results.endpoints):
                print(f"  - {endpoint}")
        
        if results.ip_addresses:
            print(f"\nIP Addresses ({len(results.ip_addresses)}):")
            for ip in sorted(results.ip_addresses):
                print(f"  - {ip}")
        
        if results.virtual_hosts:
            print(f"\nVirtual Hosts ({len(results.virtual_hosts)}):")
            for vhost in sorted(results.virtual_hosts):
                print(f"  - {vhost}")
        
        print(f"\nEnumeration Results: {len(results.enumeration_results)} strategies executed")
        for enum_result in results.enumeration_results:
            print(f"  - {enum_result.enumerator_name}: {len(enum_result.errors)} errors")
    
    def _display_scan_list(self, scans: list):
        """Display list of scans"""
        print("\n=== Recent Scans ===")
        if not scans:
            print("No scans found")
            return
            
        print(f"{'Scan ID':<36} {'Target':<30} {'Status':<12} {'Start Time'}")
        print("-" * 90)
        
        for scan in scans:
            print(f"{scan['scan_id']:<36} {scan['target']:<30} {scan['status']:<12} {scan['start_time']}")
