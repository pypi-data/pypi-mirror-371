#!/usr/bin/env python3
"""
Standalone C++ entity search tool using tree-sitter
Works on any directory without requiring project structure
"""

import os
import sys
import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Set, Optional

# Add obt to path if needed
import sys
from pathlib import Path
obt_dir = Path(__file__).parent / "obt"
if obt_dir.exists():
    sys.path.insert(0, str(obt_dir.parent))

from obt.deco import Deco
from obt.cpp_formatter import CppFormatter
from ork.cppsearch import parse_cpp_file
from ork.cppdb import CppDatabase

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
    if not entities:
        print("// No matching entities found")
        return
        
    deco = Deco()
    
    # Group by file
    by_file = defaultdict(list)
    for entity in entities:
        by_file[entity.file].append(entity)
    
    print("/////////////////////////////////////////////////////////////")
    print(f"// Found {len(entities)} entities in {args.directory}")
    print("/////////")
    
    # Define column widths
    LINE_LENGTH = 128
    line_col_width = 8
    type_col_width = 10
    kind_col_width = 12
    namespace_col_width = 20
    identifier_col_width = LINE_LENGTH - (line_col_width + type_col_width + kind_col_width + namespace_col_width)
    
    # Legend configs
    legend_configs = [
        (line_col_width, 'center'),
        (type_col_width, 'center'),
        (kind_col_width, 'center'),
        (namespace_col_width, 'center'),
        (None, 'left')
    ]
    legend_texts = ["LINE", "TYPE", "KIND", "NAMESPACE", "IDENTIFIER"]
    formatted_legend = deco.formatColumns(legend_configs, legend_texts)
    
    def print_header():
        print()
        print(deco.bg('grey4') + deco.fg('white') + formatted_legend.ljust(LINE_LENGTH) + deco.reset())
    
    file_count = 0
    global_line_count = 0
    
    for filepath in sorted(by_file.keys()):
        file_entities = by_file[filepath]
        
        # Print header between files if needed
        if file_count > 0 and global_line_count >= 80:
            print_header()
            global_line_count = 0
        
        # Print filename header
        print()
        display_path = str(filepath).replace(str(args.directory) + "/", "")
        filename_padded = display_path.center(LINE_LENGTH)
        print(deco.bg('grey1') + deco.fg('pink') + filename_padded + deco.reset())
        
        file_count += 1
        file_line_count = 0
        
        for entity in sorted(file_entities, key=lambda x: x.line):
            # Build display strings
            match_type = entity.match_type if hasattr(entity, 'match_type') else 'DEF'
            kind = entity.entity_type
            namespace_text = entity.namespace if entity.namespace else "-"
            
            # Truncate namespace if too long
            if len(namespace_text) > namespace_col_width - 2:
                namespace_text = namespace_text[:namespace_col_width-5] + "..."
            
            # Build identifier
            if entity.entity_type == "function":
                formatter = CppFormatter(deco=None)
                formatter.set_namespace_context(entity.namespace if hasattr(entity, 'namespace') else "")
                identifier = formatter.format_function_signature(entity)
            else:
                identifier = entity.name
            
            # Format columns
            line_str = str(entity.line).center(line_col_width)
            type_str = match_type.center(type_col_width)
            kind_str = kind.center(kind_col_width)
            namespace_str = namespace_text.center(namespace_col_width)
            
            # Handle function signatures with multiple lines
            if entity.entity_type == "function" and hasattr(identifier, 'parts'):
                # Similar formatting as main script but simplified
                print(f"{deco.yellow(str(entity.line).rjust(6))} {deco.green(match_type.ljust(8))} "
                      f"{deco.cyan(kind.ljust(10))} {deco.brightgreen(namespace_text.ljust(20))} "
                      f"{identifier.plain_text()}")
            else:
                # Simple entities
                print(f"{deco.yellow(str(entity.line).rjust(6))} {deco.green(match_type.ljust(8))} "
                      f"{deco.cyan(kind.ljust(10))} {deco.brightgreen(namespace_text.ljust(20))} "
                      f"{deco.white(identifier)}")
            
            file_line_count += 1
            global_line_count += 1
            
            # Print header every 80 lines within file
            if file_line_count > 0 and file_line_count % 80 == 0:
                print_header()
                global_line_count = 0

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
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
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