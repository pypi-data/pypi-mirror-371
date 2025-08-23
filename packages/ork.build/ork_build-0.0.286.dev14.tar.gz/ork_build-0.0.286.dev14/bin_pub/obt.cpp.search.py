#!/usr/bin/env python3
"""
Standalone C++ entity search tool using tree-sitter
Works on any directory without requiring project structure
Only uses obt modules - no orkid dependencies
"""

import os
import sys
import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import List

from obt.cpp_search import parse_cpp_file, CppDatabase
from obt.cpp_display import CppEntityDisplay

def search_directory(directory: Path, args) -> List:
    """Search a directory for C++ entities"""
    all_entities = []
    
    # Entity types to search for
    entity_types = set()
    if args.types:
        for t in args.types:
            if t == 'all':
                entity_types = {'class', 'struct', 'function', 'typedef', 'alias', 
                               'enum', 'namespace', 'variable', 'union'}
                break
            entity_types.add(t)
    else:
        entity_types = {'class', 'struct', 'function'}
    
    # C++ file extensions
    cpp_extensions = {'.cpp', '.hpp', '.h', '.cc', '.cxx', '.inl', '.c', '.C'}
    
    # Walk directory
    for ext in cpp_extensions:
        for filepath in directory.rglob(f'*{ext}'):
            # Skip build directories
            if any(skip in str(filepath) for skip in ['/build/', '/.build/', '/obj/', '/.git/', '/node_modules/']):
                continue
                
            try:
                entities = parse_cpp_file(filepath, entity_types)
                all_entities.extend(entities)
            except Exception as e:
                if args.verbose:
                    print(f"// Error parsing {filepath}: {e}", file=sys.stderr)
    
    return all_entities

def filter_entities(entities: List, args) -> List:
    """Filter entities based on search criteria"""
    filtered = entities
    
    # Filter by name pattern
    if args.name:
        import re
        pattern = re.compile(args.name, re.IGNORECASE if args.ignore_case else 0)
        filtered = [e for e in filtered if pattern.search(e.name)]
    
    # Filter by namespace
    if args.namespace:
        filtered = [e for e in filtered if args.namespace in e.namespace]
    
    # Filter by file pattern
    if args.file_pattern:
        import re
        pattern = re.compile(args.file_pattern)
        filtered = [e for e in filtered if pattern.search(str(e.file))]
    
    return filtered

def display_entities(entities: List, args):
    """Display entities in formatted output"""
    display = CppEntityDisplay()
    display.display_entities(entities, root_path=args.directory, sepfiles=getattr(args, 'sepfiles', False))

def main():
    parser = argparse.ArgumentParser(
        description='Standalone C++ entity search - works on any directory'
    )
    
    # Directory argument
    parser.add_argument('directory', type=Path,
                       help='Directory to search')
    
    # Entity type filters
    parser.add_argument('-t', '--types', nargs='+',
                       choices=['class', 'struct', 'function', 'typedef', 'alias', 
                               'enum', 'namespace', 'variable', 'union', 'all'],
                       help='Entity types to search for (default: class, struct, function)')
    
    # Search filters
    parser.add_argument('-n', '--name', 
                       help='Filter by name (regex pattern)')
    parser.add_argument('--namespace',
                       help='Filter by namespace')
    parser.add_argument('-f', '--file-pattern',
                       help='Filter by file path pattern (regex)')
    parser.add_argument('-i', '--ignore-case', action='store_true',
                       help='Case-insensitive name search')
    
    # Output options
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--sepfiles', action='store_true',
                       help='Add blank line separator between files')
    
    args = parser.parse_args()
    
    # Validate directory
    if not args.directory.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        sys.exit(1)
    
    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)
    
    # Search directory
    entities = search_directory(args.directory, args)
    
    # Filter results
    filtered = filter_entities(entities, args)
    
    # Output results
    if args.json:
        output = []
        for entity in filtered:
            output.append({
                'name': entity.name,
                'namespace': entity.namespace,
                'file': str(entity.file),
                'line': entity.line,
                'type': entity.entity_type,
            })
        print(json.dumps(output, indent=2))
    else:
        display_entities(filtered, args)

if __name__ == "__main__":
    main()