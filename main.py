#!/usr/bin/env python3
"""
Site Analyzer - Refactored version with multiple interfaces and storage backends
"""

import sys
import os
from core.config import Config
from interfaces.cli import CLIInterface
from interfaces.grpc_server import GRPCInterface
from interfaces.rest_api import RestAPI

def main():
    """Main entry point for refactored site analyzer"""
    
    if len(sys.argv) < 2:
        print("Usage: python main_refactored.py <interface> [options]")
        print("Interfaces: cli, grpc, rest")
        print("\nExamples:")
        print("  python main_refactored.py cli analyze -u example.com")
        print("  python main_refactored.py grpc")
        print("  python main_refactored.py rest")
        sys.exit(1)
    
    interface_type = sys.argv[1]
    remaining_args = sys.argv[2:]
    
    config = Config.from_env()
    
    try:
        if interface_type == 'cli':
            interface = CLIInterface(config)
            interface.run(remaining_args)
            
        elif interface_type == 'grpc':
            interface = GRPCInterface(config)
            interface.run()
            
        elif interface_type == 'rest':
            interface = RestAPI(config)
            interface.run()
            
        else:
            print(f"Unknown interface type: {interface_type}")
            print("Available interfaces: cli, grpc, rest")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
