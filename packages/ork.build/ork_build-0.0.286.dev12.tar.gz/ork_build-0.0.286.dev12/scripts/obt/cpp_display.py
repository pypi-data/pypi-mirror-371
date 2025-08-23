"""
C++ Entity Display Module
Provides formatted, colorized display of C++ entities from search results
"""

from collections import defaultdict
from typing import List, Optional
from pathlib import Path
from obt.deco import Deco
from obt.cpp_formatter import CppFormatter

class CppEntityDisplay:
    """Handles display of C++ entities with formatting and colors"""
    
    def __init__(self, line_length: int = 148):  # Was 128, now +20 (10 for namespace, 10 for identifier)
        self.LINE_LENGTH = line_length
        self.deco = Deco()
        
        # Define column widths
        self.line_col_width = 8   # Line number
        self.type_col_width = 10  # Match type
        self.kind_col_width = 12  # Entity kind
        self.namespace_col_width = 30  # Namespace (was 20, now +10)
        self.identifier_col_width = self.LINE_LENGTH - (
            self.line_col_width + self.type_col_width + 
            self.kind_col_width + self.namespace_col_width
        )  # Identifier gets the rest (now has 10 more chars)
        
        # Legend configs for formatColumns
        self.legend_configs = [
            (self.line_col_width, 'center'),
            (self.type_col_width, 'center'),
            (self.kind_col_width, 'center'),
            (self.namespace_col_width, 'center'),
            (None, 'left')
        ]
        self.legend_texts = ["LINE", "TYPE", "KIND", "NAMESPACE", "IDENTIFIER"]
        self.formatted_legend = self.deco.formatColumns(self.legend_configs, self.legend_texts)
    
    def print_header(self):
        """Print column header with grey background"""
        print()
        print(self.deco.bg('grey4') + self.deco.fg('white') + 
              self.formatted_legend.ljust(self.LINE_LENGTH) + self.deco.reset())
    
    def get_match_type(self, entity) -> str:
        """Determine the match type for an entity"""
        # Handle private implementation flag
        if hasattr(entity, 'is_private_impl') and entity.is_private_impl:
            return 'PIMPL'
            
        if hasattr(entity, 'decl_type'):
            if entity.decl_type == 'definition':
                return 'DEF'
            elif entity.decl_type == 'forward_declaration':
                return 'FWD'
            else:
                return 'DECL'
        return 'DEF'
    
    def get_kind_color(self, kind: str):
        """Get color function for entity kind"""
        kind_colors = {
            'class': self.deco.cyan,
            'struct': self.deco.cyan,
            'function': self.deco.cyan,
            'enum': self.deco.magenta,
            'typedef': self.deco.yellow,
            'alias': self.deco.yellow,
            'namespace': self.deco.blue,
            'variable': self.deco.green,
            'union': self.deco.orange,
        }
        return kind_colors.get(kind, self.deco.white)
    
    def get_identifier_color(self, entity_type: str):
        """Get color function for identifier based on entity type"""
        identifier_colors = {
            'class': self.deco.white,
            'struct': self.deco.white,
            'function': self.deco.white,  # Functions use formatter colors
            'enum': self.deco.white,
            'typedef': self.deco.cyan,
            'alias': self.deco.cyan,
            'namespace': self.deco.white,
            'variable': self.deco.white,
            'union': self.deco.white,
        }
        return identifier_colors.get(entity_type, self.deco.white)
    
    def display_entities(self, entities: List, root_path: Optional[Path] = None, 
                        sepfiles: bool = False):
        """Display entities with full formatting"""
        if not entities:
            print("// No matching entities found")
            return
        
        # Group by file
        by_file = defaultdict(list)
        for entity in entities:
            by_file[str(entity.file)].append(entity)
        
        print("/////////////////////////////////////////////////////////////")
        print(f"// Found {len(entities)} entities")
        print("/////////")
        
        file_count = 0
        global_line_count = 0
        
        for filepath in sorted(by_file.keys()):
            file_entities = by_file[filepath]
            
            # Print header between files if needed
            if file_count > 0 and global_line_count >= 80:
                self.print_header()
                global_line_count = 0
            
            # Add separator between files if requested
            if sepfiles and file_count > 0:
                print()
            
            # Print filename header (pink on grey1 background, centered)
            print()
            display_path = filepath
            if root_path:
                display_path = str(filepath).replace(str(root_path) + "/", "")
            filename_padded = display_path.center(self.LINE_LENGTH)
            print(self.deco.bg('grey1') + self.deco.fg('pink') + 
                  filename_padded + self.deco.reset())
            
            file_count += 1
            file_line_count = 0
            
            for entity in sorted(file_entities, key=lambda x: x.line):
                # Build display components
                match_type = self.get_match_type(entity)
                kind = entity.entity_type
                namespace_text = entity.namespace if entity.namespace else "-"
                
                # Truncate namespace if too long
                if len(namespace_text) > self.namespace_col_width - 2:
                    keep_start = 8
                    keep_end = self.namespace_col_width - 4 - keep_start
                    namespace_text = namespace_text[:keep_start] + "..." + namespace_text[-keep_end:]
                
                # Build identifier
                if entity.entity_type == "function":
                    formatter = CppFormatter(deco=None)
                    formatter.set_namespace_context(entity.namespace if hasattr(entity, 'namespace') else "")
                    identifier = formatter.format_function_signature(entity)
                else:
                    identifier = entity.name
                    if hasattr(entity, 'is_template') and entity.is_template:
                        identifier = f"template{entity.template_params} {identifier}"
                
                # Format columns
                line_str = str(entity.line).center(self.line_col_width)
                type_str = match_type.center(self.type_col_width)
                kind_str = kind.center(self.kind_col_width)
                namespace_str = namespace_text.center(self.namespace_col_width)
                
                # Get colors
                kind_color = self.get_kind_color(kind)
                identifier_color = self.get_identifier_color(entity.entity_type)
                
                # Handle function signatures with multiple lines
                if entity.entity_type == "function" and hasattr(identifier, 'parts'):
                    self._display_multiline_function(
                        entity, identifier, line_str, type_str, kind_str, 
                        namespace_str, kind_color, file_line_count, global_line_count
                    )
                    # Count lines
                    num_lines = len([1 for text, _ in identifier.parts if '\n' in text]) + 1
                    file_line_count += num_lines
                    global_line_count += num_lines
                else:
                    # Simple entities
                    padded_identifier = identifier
                    if isinstance(identifier, str):
                        padded_identifier = identifier.ljust(self.identifier_col_width) if len(identifier) < self.identifier_col_width else identifier
                    else:
                        padded_identifier = identifier.plain_text().ljust(self.identifier_col_width)
                    identifier_rendered = self.deco.bg('grey2') + identifier_color(padded_identifier) + self.deco.reset()
                    
                    colored_columns = [
                        self.deco.bg('black') + self.deco.yellow(line_str) + self.deco.reset(),
                        self.deco.bg('grey2') + self.deco.green(type_str) + self.deco.reset(),
                        self.deco.bg('grey4') + kind_color(kind_str) + self.deco.reset(),
                        self.deco.bg('grey2') + self.deco.brightgreen(namespace_str) + self.deco.reset(),
                        identifier_rendered
                    ]
                    
                    # Print header every 80 lines within a file
                    if file_line_count > 0 and file_line_count % 80 == 0:
                        self.print_header()
                        global_line_count = 0
                    
                    print(''.join(colored_columns))
                    file_line_count += 1
                    global_line_count += 1
    
    def _display_multiline_function(self, entity, identifier, line_str, type_str, 
                                   kind_str, namespace_str, kind_color, 
                                   file_line_count, global_line_count):
        """Display a function with multiline parameters"""
        # Split identifier into lines
        identifier_lines = []
        current_line_parts = []
        
        for text, tag in identifier.parts:
            if '\n' in text:
                parts = text.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        identifier_lines.append(current_line_parts)
                        current_line_parts = []
                    if part:
                        current_line_parts.append((part, tag))
            else:
                current_line_parts.append((text, tag))
        
        if current_line_parts:
            identifier_lines.append(current_line_parts)
        
        # Render first line
        first_line_parts = []
        first_line_parts.append(self.deco.bg('grey2'))
        first_line_text = []
        for text, tag in identifier_lines[0] if identifier_lines else []:
            first_line_text.append(text)
            if tag == 'return_type':
                first_line_parts.append(self.deco.fg('magenta') + text)
            elif tag == 'param_type':
                first_line_parts.append(self.deco.fg('yellow') + text)
            elif tag == 'param_name':
                first_line_parts.append(self.deco.fg('orange') + text)
            elif tag == 'function_name':
                first_line_parts.append(self.deco.fg('white') + text)
            else:
                first_line_parts.append(self.deco.fg('white') + text)
        
        # Pad to full column width
        first_line_len = len(''.join(first_line_text))
        if first_line_len < self.identifier_col_width:
            first_line_parts.append(' ' * (self.identifier_col_width - first_line_len))
        first_line_parts.append(self.deco.reset())
        identifier_rendered = ''.join(first_line_parts)
        
        # Print the first line
        colored_columns = [
            self.deco.bg('black') + self.deco.yellow(line_str) + self.deco.reset(),
            self.deco.bg('grey2') + self.deco.green(type_str) + self.deco.reset(),
            self.deco.bg('grey4') + kind_color(kind_str) + self.deco.reset(),
            self.deco.bg('grey2') + self.deco.brightgreen(namespace_str) + self.deco.reset(),
            identifier_rendered
        ]
        
        # Print header every 80 lines
        if file_line_count > 0 and file_line_count % 80 == 0:
            self.print_header()
        
        print(''.join(colored_columns))
        
        # Print continuation lines
        for line_parts in identifier_lines[1:]:
            continuation_parts = []
            continuation_parts.append(self.deco.bg('grey2'))
            continuation_text = []
            for text, tag in line_parts:
                continuation_text.append(text)
                if tag == 'param_type':
                    continuation_parts.append(self.deco.fg('yellow') + text)
                elif tag == 'param_name':
                    continuation_parts.append(self.deco.fg('orange') + text)
                else:
                    continuation_parts.append(self.deco.fg('white') + text)
            
            # Pad to full column width
            continuation_len = len(''.join(continuation_text))
            if continuation_len < self.identifier_col_width:
                continuation_parts.append(' ' * (self.identifier_col_width - continuation_len))
            continuation_parts.append(self.deco.reset())
            
            continuation_columns = [
                self.deco.bg('black') + " " * self.line_col_width + self.deco.reset(),
                self.deco.bg('grey2') + " " * self.type_col_width + self.deco.reset(),
                self.deco.bg('grey4') + " " * self.kind_col_width + self.deco.reset(),
                self.deco.bg('grey2') + " " * self.namespace_col_width + self.deco.reset(),
                ''.join(continuation_parts)
            ]
            print(''.join(continuation_columns))