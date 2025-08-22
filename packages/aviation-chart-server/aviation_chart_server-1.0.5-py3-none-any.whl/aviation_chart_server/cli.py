#!/usr/bin/env python3
"""
Command-line interface for the Aviation Chart Server package.
"""

import sys
import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Aviation Chart Server - Serve FAA aviation charts as tile pyramids",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aviation-chart-server                          # Start server on default port 8187
  aviation-chart-server --port 3000             # Start server on port 3000  
  aviation-chart-server --host 0.0.0.0 --port 8080  # Start server accessible from network
  aviation-chart-server --test-date 12-26-2024  # Test mode for specific date
  aviation-chart-server --zoom 10               # Use zoom level 10 for tile generation
  aviation-chart-server --chart-type sectional helicopter  # Process only specific chart types
  aviation-chart-server --test-date 12-26-2024 --zoom 9 --chart-type ifr-enroute-high  # Combined options
        """
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8187,
        help='Port to run the server on (default: 8187)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind the server to (default: localhost, use 0.0.0.0 for network access)'
    )
    parser.add_argument(
        '--test-date',
        type=str,
        help='Run in test mode for a specific date (format: MM-DD-YYYY)'
    )
    parser.add_argument(
        '--zoom',
        type=int,
        default=8,
        help='Zoom level for tile generation (default: 8)'
    )
    parser.add_argument(
        '--chart-type',
        nargs='*',
        choices=['helicopter', 'ifr-enroute-high', 'ifr-enroute-low', 'sectional', 'terminal-area'],
        help='Chart types to process. Available: helicopter, ifr-enroute-high, ifr-enroute-low, sectional, terminal-area. If not specified, all types are processed.'
    )
    
    args = parser.parse_args()
    
    # Prepare sys.argv for chart_server.py
    sys.argv = ['chart_server.py']
    
    # Add host and port arguments
    sys.argv.extend(['--host', args.host])
    sys.argv.extend(['--port', str(args.port)])
    
    if args.test_date:
        sys.argv.extend(['--test-date', args.test_date])
    
    # Add zoom level if different from default
    if args.zoom != 8:
        sys.argv.extend(['--zoom', str(args.zoom)])
    
    # Add chart types if specified
    if args.chart_type:
        sys.argv.append('--chart-type')
        sys.argv.extend(args.chart_type)
    
    # Call the server main function
    from . import chart_server
    chart_server.main()


if __name__ == '__main__':
    main()
