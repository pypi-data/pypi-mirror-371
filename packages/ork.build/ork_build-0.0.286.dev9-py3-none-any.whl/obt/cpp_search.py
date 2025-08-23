#!/usr/bin/env python3
"""
Generic C++ code search and database functionality
Base module that can be used across projects
"""

import sqlite3
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from tree_sitter import Language, Parser
import tree_sitter_cpp

# Initialize C++ parser
CPP_LANGUAGE = Language(tree_sitter_cpp.language(), "cpp")
parser = Parser()
parser.set_language(CPP_LANGUAGE)

class CppEntity:
    """Base class for C++ entities"""
    def __init__(self, name, namespace="", file="", line=0, decl_type="declaration"):
        self.name = name
        self.namespace = namespace
        self.file = file
        self.line = line
        self.decl_type = decl_type  # declaration, definition, forward_declaration
        self.is_template = False
        self.template_params = ""
        self.is_private_impl = False  # True if defined in .cpp file
        self.entity_type = "unknown"
        
    @property
    def full_name(self):
        if self.namespace:
            return f"{self.namespace}::{self.name}"
        return self.name

class ClassInfo(CppEntity):
    """Information about a C++ class or struct"""
    def __init__(self, name, namespace="", file="", line=0, decl_type="declaration"):
        super().__init__(name, namespace, file, line, decl_type)
        self.base_classes = []
        self.is_struct = False
        self.entity_type = "class"

class EnumInfo(CppEntity):
    """Information about a C++ enum"""
    def __init__(self, name, namespace="", file="", line=0, decl_type="declaration"):
        super().__init__(name, namespace, file, line, decl_type)
        self.is_enum_class = False
        self.underlying_type = ""
        self.enum_values = ""  # JSON string of enum values
        self.entity_type = "enum"

class FunctionInfo(CppEntity):
    """Information about a C++ function"""
    def __init__(self, name, namespace="", file="", line=0, decl_type="declaration"):
        super().__init__(name, namespace, file, line, decl_type)
        self.return_type = ""
        self.parameters = ""
        self.is_method = False
        self.is_virtual = False
        self.is_static = False
        self.is_const = False
        self.entity_type = "function"

class TypedefInfo(CppEntity):
    """Information about a C++ typedef or using alias"""
    def __init__(self, name, namespace="", file="", line=0, decl_type="declaration"):
        super().__init__(name, namespace, file, line, decl_type)
        self.target_type = ""
        self.is_using = False
        self.entity_type = "typedef"

class CppDatabase:
    """SQLite database for C++ code entities"""
    
    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self._ensure_parent_dir()
        
    def _ensure_parent_dir(self):
        """Ensure parent directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def connect(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def initialize(self, project_name: str = ""):
        """Initialize database schema"""
        with self.connect() as conn:
            conn.executescript("""
                -- Main entities table
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    namespace TEXT DEFAULT '',
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    decl_type TEXT DEFAULT 'declaration',
                    is_template BOOLEAN DEFAULT FALSE,
                    is_private_impl BOOLEAN DEFAULT FALSE,
                    data_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- File tracking for incremental updates
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    last_modified REAL NOT NULL,
                    file_hash TEXT NOT NULL,
                    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Entity members (class/struct fields, enum values, function params)
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id INTEGER NOT NULL,
                    member_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data_type TEXT DEFAULT '',
                    visibility TEXT DEFAULT '',
                    is_static BOOLEAN DEFAULT FALSE,
                    ordinal INTEGER DEFAULT 0,
                    data_json TEXT,
                    FOREIGN KEY (entity_id) REFERENCES entities (id) ON DELETE CASCADE
                );
                
                -- Indexes for fast searches
                CREATE INDEX IF NOT EXISTS idx_entities_name ON entities (name);
                CREATE INDEX IF NOT EXISTS idx_entities_type ON entities (entity_type);
                CREATE INDEX IF NOT EXISTS idx_entities_namespace ON entities (namespace);
                CREATE INDEX IF NOT EXISTS idx_entities_file ON entities (file_path);
                CREATE INDEX IF NOT EXISTS idx_files_path ON files (file_path);
                CREATE INDEX IF NOT EXISTS idx_members_entity ON members (entity_id);
                CREATE INDEX IF NOT EXISTS idx_members_type ON members (member_type);
                
                -- Version info
                CREATE TABLE IF NOT EXISTS db_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                
                INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('version', '1.0');
            """)
            if project_name:
                conn.execute(
                    "INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('project', ?)", 
                    (project_name,)
                )
    
    def file_hash(self, filepath: Path) -> str:
        """Calculate hash of file contents"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
            
    def is_file_modified(self, filepath: Path) -> bool:
        """Check if file has been modified since last parse"""
        if not filepath.exists():
            return False
            
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT last_modified, file_hash FROM files WHERE file_path = ?", 
                (str(filepath),)
            )
            row = cursor.fetchone()
            
            if not row:
                return True
                
            stat = filepath.stat()
            current_mtime = stat.st_mtime
            current_hash = self.file_hash(filepath)
            
            return (current_mtime != row['last_modified'] or 
                   current_hash != row['file_hash'])
    
    def update_file_record(self, filepath: Path):
        """Update file modification tracking"""
        if not filepath.exists():
            return
            
        stat = filepath.stat()
        file_hash = self.file_hash(filepath)
        
        with self.connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO files (file_path, last_modified, file_hash, parsed_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (str(filepath), stat.st_mtime, file_hash))
            
    def add_entity(self, entity, members: List[Dict] = None) -> int:
        """Add entity to database"""
        # Prepare entity data
        data_json = {}
        if hasattr(entity, 'base_classes') and entity.base_classes:
            data_json['base_classes'] = entity.base_classes
        if hasattr(entity, 'underlying_type') and entity.underlying_type:
            data_json['underlying_type'] = entity.underlying_type
        if hasattr(entity, 'is_enum_class'):
            data_json['is_enum_class'] = entity.is_enum_class
        if hasattr(entity, 'template_params') and entity.template_params:
            data_json['template_params'] = entity.template_params
        if hasattr(entity, 'return_type') and entity.return_type:
            data_json['return_type'] = entity.return_type
        if hasattr(entity, 'parameters') and entity.parameters:
            data_json['parameters'] = entity.parameters
            
        with self.connect() as conn:
            cursor = conn.execute("""
                INSERT INTO entities (
                    name, entity_type, namespace, file_path, line_number, 
                    decl_type, is_template, is_private_impl, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.name,
                entity.entity_type,
                entity.namespace or '',
                entity.file,
                entity.line,
                entity.decl_type,
                getattr(entity, 'is_template', False),
                getattr(entity, 'is_private_impl', False),
                json.dumps(data_json) if data_json else None
            ))
            
            entity_id = cursor.lastrowid
            
            # Add members if provided
            if members:
                for member in members:
                    conn.execute("""
                        INSERT INTO members (
                            entity_id, member_type, name, data_type, 
                            visibility, is_static, ordinal, data_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entity_id,
                        member.get('member_type', ''),
                        member.get('name', ''),
                        member.get('data_type', ''),
                        member.get('visibility', ''),
                        member.get('is_static', False),
                        member.get('ordinal', 0),
                        json.dumps(member.get('data', {})) if member.get('data') else None
                    ))
                    
            return entity_id
            
    def clear_file_entities(self, filepath: Path):
        """Remove all entities from a specific file"""
        with self.connect() as conn:
            conn.execute("DELETE FROM entities WHERE file_path = ?", (str(filepath),))
            
    def search_entities(self, 
                       pattern: str = None,
                       entity_types: List[str] = None,
                       namespace: str = None,
                       decl_type: str = None,
                       file_pattern: str = None) -> List[Dict]:
        """Search entities in database"""
        query = "SELECT * FROM entities WHERE 1=1"
        params = []
        
        if pattern:
            query += " AND name LIKE ?"
            params.append(f"%{pattern}%")
            
        if entity_types:
            placeholders = ','.join('?' * len(entity_types))
            query += f" AND entity_type IN ({placeholders})"
            params.extend(entity_types)
            
        if namespace:
            query += " AND namespace LIKE ?"
            params.append(f"%{namespace}%")
            
        if decl_type:
            query += " AND decl_type = ?"
            params.append(decl_type)
            
        if file_pattern:
            query += " AND file_path LIKE ?"
            params.append(f"%{file_pattern}%")
            
        query += " ORDER BY file_path, line_number"
        
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_entity_members(self, entity_id: int, member_type: str = None) -> List[Dict]:
        """Get members of an entity"""
        query = "SELECT * FROM members WHERE entity_id = ?"
        params = [entity_id]
        
        if member_type:
            query += " AND member_type = ?"
            params.append(member_type)
            
        query += " ORDER BY ordinal, name"
        
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.connect() as conn:
            stats = {}
            
            # Entity counts by type
            cursor = conn.execute("""
                SELECT entity_type, COUNT(*) as count 
                FROM entities 
                GROUP BY entity_type 
                ORDER BY count DESC
            """)
            stats['entities_by_type'] = dict(cursor.fetchall())
            
            # Total entities
            cursor = conn.execute("SELECT COUNT(*) as count FROM entities")
            stats['total_entities'] = cursor.fetchone()['count']
            
            # Files tracked
            cursor = conn.execute("SELECT COUNT(*) as count FROM files")
            stats['files_tracked'] = cursor.fetchone()['count']
            
            # Database size
            stats['db_size'] = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return stats
            
    def exists(self) -> bool:
        """Check if database exists"""
        return self.db_path.exists()

def extract_namespace(node, source_code):
    """Extract namespace context for a node"""
    namespaces = []
    current = node.parent
    
    while current:
        if current.type == 'namespace_definition':
            # Find the namespace name
            for child in current.children:
                if child.type == 'namespace_identifier':
                    ns_name = source_code[child.start_byte:child.end_byte].decode('utf-8')
                    namespaces.insert(0, ns_name)
                    break
        current = current.parent
    
    return "::".join(namespaces)

def parse_cpp_file(filepath: Path, entity_types: set = None) -> List[CppEntity]:
    """Parse a C++ file and extract entity information"""
    if entity_types is None:
        entity_types = {'class', 'struct', 'enum', 'function', 'typedef', 'alias'}
    
    try:
        with open(filepath, 'rb') as f:
            source_code = f.read()
    except Exception as e:
        return []
    
    tree = parser.parse(source_code)
    entities = []
    
    # Parse classes and structs
    if 'class' in entity_types or 'struct' in entity_types:
        entities.extend(parse_classes_and_structs(tree, source_code, filepath, entity_types))
    
    # Parse enums
    if 'enum' in entity_types:
        entities.extend(parse_enums(tree, source_code, filepath))
    
    # Parse functions
    if 'function' in entity_types:
        entities.extend(parse_functions(tree, source_code, filepath))
    
    # Parse typedefs and aliases
    if 'typedef' in entity_types or 'alias' in entity_types:
        entities.extend(parse_typedefs_and_aliases(tree, source_code, filepath, entity_types))
    
    return entities

# Parsing functions implementations
def parse_classes_and_structs(tree, source_code, filepath, entity_types):
    """Parse classes and structs from the syntax tree"""
    entities = []
    
    # Query for class and struct declarations
    class_query = CPP_LANGUAGE.query("""
        [
            (class_specifier
              name: (type_identifier) @class_name) @class
            (struct_specifier
              name: (type_identifier) @struct_name) @struct
        ]
    """)
    
    # Query for template classes and structs
    template_query = CPP_LANGUAGE.query("""
        (template_declaration
          [
            (class_specifier
              name: (type_identifier) @template_class_name) @template_class
            (struct_specifier
              name: (type_identifier) @template_struct_name) @template_struct
          ])
    """)
    
    # Process regular classes and structs
    for node, capture_name in class_query.captures(tree.root_node):
        if capture_name in ['class_name', 'struct_name']:
            entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
            line_num = source_code[:node.start_byte].count(b'\n') + 1
            namespace = extract_namespace(node, source_code)
            
            # Determine if it's a definition or just declaration
            has_body = False
            if node.parent and node.parent.type in ['class_specifier', 'struct_specifier']:
                for sibling in node.parent.children:
                    if sibling.type == 'field_declaration_list':
                        has_body = True
                        break
            
            decl_type = "definition" if has_body else "declaration"
            
            info = ClassInfo(
                name=entity_name,
                namespace=namespace,
                file=str(filepath),
                line=line_num,
                decl_type=decl_type
            )
            
            info.is_struct = (capture_name == 'struct_name' or 
                            (node.parent and node.parent.type == 'struct_specifier'))
            info.entity_type = "struct" if info.is_struct else "class"
            
            # Check if it's a private implementation
            if str(filepath).endswith(('.cpp', '.cc', '.cxx')) and has_body:
                info.is_private_impl = True
            
            # Extract base classes
            if node.parent:
                for child in node.parent.children:
                    if child.type == 'base_class_clause':
                        base_text = source_code[child.start_byte:child.end_byte].decode('utf-8')
                        info.base_classes.append(base_text.replace(':', '').strip())
            
            if info.entity_type in entity_types:
                entities.append(info)
    
    # Process template classes and structs
    for node, capture_name in template_query.captures(tree.root_node):
        if capture_name in ['template_class_name', 'template_struct_name']:
            entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
            line_num = source_code[:node.start_byte].count(b'\n') + 1
            namespace = extract_namespace(node, source_code)
            
            info = ClassInfo(
                name=entity_name,
                namespace=namespace,
                file=str(filepath),
                line=line_num,
                decl_type="definition"
            )
            info.is_template = True
            info.is_struct = (capture_name == 'template_struct_name' or 
                            (node.parent and node.parent.type == 'struct_specifier'))
            info.entity_type = "struct" if info.is_struct else "class"
            
            # Check if it's a private implementation
            if str(filepath).endswith(('.cpp', '.cc', '.cxx')):
                info.is_private_impl = True
            
            # Get template parameters
            template_node = node.parent.parent  # Go up to template_declaration
            for child in template_node.children:
                if child.type == 'template_parameter_list':
                    info.template_params = source_code[child.start_byte:child.end_byte].decode('utf-8')
                    break
            
            if info.entity_type in entity_types:
                entities.append(info)
    
    return entities

def parse_enums(tree, source_code, filepath):
    """Parse enums from the syntax tree"""
    entities = []
    
    # Query for enum declarations
    enum_query = CPP_LANGUAGE.query("""
        [
            (enum_specifier
              name: (type_identifier) @enum_name) @enum
        ]
    """)
    
    for node, capture_name in enum_query.captures(tree.root_node):
        if capture_name == 'enum_name':
            entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
            line_num = source_code[:node.start_byte].count(b'\n') + 1
            namespace = extract_namespace(node, source_code)
            
            info = EnumInfo(
                name=entity_name,
                namespace=namespace,
                file=str(filepath),
                line=line_num,
                decl_type="definition"
            )
            
            # Get the enum specifier node (parent of enum_name)
            enum_node = node.parent
            if enum_node:
                # Extract underlying type by parsing the children
                found_colon = False
                for child in enum_node.children:
                    if child.type == ':':
                        found_colon = True
                    elif found_colon and child.type in ['type_identifier', 'primitive_type', 'qualified_identifier']:
                        info.underlying_type = source_code[child.start_byte:child.end_byte].decode('utf-8').strip()
                        break
                
                # Check if it's enum class by looking at the full enum declaration
                enum_text = source_code[enum_node.start_byte:enum_node.end_byte].decode('utf-8')
                if 'enum class' in enum_text or 'enum struct' in enum_text:
                    info.is_enum_class = True
                
                # Extract enum values
                enum_values = parse_enum_values(enum_node, source_code)
                info.enum_values = json.dumps(enum_values)
            
            # Check if it's a private implementation
            if str(filepath).endswith(('.cpp', '.cc', '.cxx')):
                info.is_private_impl = True
            
            entities.append(info)
    
    return entities

def parse_enum_values(enum_node, source_code):
    """Extract enum values from an enum_specifier node"""
    enum_values = []
    
    # Find the enumerator_list
    enumerator_list_query = CPP_LANGUAGE.query("""
        (enumerator_list) @enum_list
    """)
    
    for list_node, capture_name in enumerator_list_query.captures(enum_node):
        if capture_name == 'enum_list':
            # Find all enumerators in this list
            enumerator_query = CPP_LANGUAGE.query("""
                (enumerator) @enumerator
            """)
            
            for enum_node, enum_capture in enumerator_query.captures(list_node):
                if enum_capture == 'enumerator':
                    enum_info = {'name': '', 'value': ''}
                    
                    # Parse enumerator - could be just name or name = value
                    enum_text = source_code[enum_node.start_byte:enum_node.end_byte].decode('utf-8').strip()
                    
                    if '=' in enum_text:
                        # Has explicit value
                        parts = enum_text.split('=', 1)
                        enum_info['name'] = parts[0].strip()
                        enum_info['value'] = parts[1].strip()
                    else:
                        # Just name, no explicit value
                        enum_info['name'] = enum_text
                        enum_info['value'] = ''
                    
                    enum_values.append(enum_info)
    
    return enum_values

def parse_parameter_list(param_list_node, source_code):
    """Extract parameter information from parameter_list node"""
    parameters = []
    
    if not param_list_node:
        return parameters
        
    # Query for both regular and optional parameter declarations
    param_query = CPP_LANGUAGE.query("""
        [
            (parameter_declaration) @param
            (optional_parameter_declaration) @param
        ]
    """)
    
    for node, capture_name in param_query.captures(param_list_node):
        if capture_name == 'param':
            param_info = {'name': '', 'type': '', 'default': ''}
            
            # Parse the parameter text manually for now
            param_text = source_code[node.start_byte:node.end_byte].decode('utf-8').strip()
            
            # Basic parsing - look for type and name
            # This is a simple approach that handles most common cases
            parts = param_text.split('=')
            if len(parts) > 1:
                param_info['default'] = parts[1].strip()
                param_decl = parts[0].strip()
            else:
                param_decl = param_text.strip()
            
            # Extract type and name from declaration part
            tokens = param_decl.split()
            if len(tokens) >= 2:
                # Last token is usually the parameter name (if present)
                last_token = tokens[-1].rstrip('*&')
                if last_token.isidentifier():
                    param_info['name'] = last_token
                    param_info['type'] = ' '.join(tokens[:-1])
                else:
                    # No parameter name, just type
                    param_info['type'] = param_decl
            elif len(tokens) == 1:
                # Only type, no name
                param_info['type'] = tokens[0]
            
            parameters.append(param_info)
    
    return parameters

def parse_functions(tree, source_code, filepath):
    """Parse functions from the syntax tree with return types and parameters"""
    entities = []
    
    # Query for function declarations and definitions
    function_query = CPP_LANGUAGE.query("""
        [
            (declaration
              (function_declarator
                (identifier) @func_name
                (parameter_list) @param_list)) @func_decl
            (function_definition
              (function_declarator
                (identifier) @func_name
                (parameter_list) @param_list)) @func_def
        ]
    """)
    
    for node, capture_name in function_query.captures(tree.root_node):
        if capture_name == 'func_name':
            entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
            line_num = source_code[:node.start_byte].count(b'\n') + 1
            namespace = extract_namespace(node, source_code)
            
            # Find parameter list for this function
            param_list_node = None
            func_declarator = node.parent  # function_declarator node
            for child in func_declarator.children:
                if child.type == 'parameter_list':
                    param_list_node = child
                    break
            
            # Find return type by looking at the parent declaration/definition
            return_type = ""
            parent = func_declarator.parent  # declaration or function_definition
            if parent:
                # Look for type specifier in the declaration
                for child in parent.children:
                    if child.type in ['type_identifier', 'primitive_type', 'qualified_identifier']:
                        return_type = source_code[child.start_byte:child.end_byte].decode('utf-8').strip()
                        break
                    elif child.type == 'sized_type_specifier':
                        # Handle cases like "unsigned int", "long long"
                        return_type = source_code[child.start_byte:child.end_byte].decode('utf-8').strip()
                        break
            
            # Determine if it's a declaration or definition
            decl_type = "definition" if parent and parent.type == 'function_definition' else "declaration"
            
            # Parse parameters using our new function
            parameters = parse_parameter_list(param_list_node, source_code)
            
            info = FunctionInfo(
                name=entity_name,
                namespace=namespace,
                file=str(filepath),
                line=line_num,
                decl_type=decl_type
            )
            
            # POPULATE THE MISSING FIELDS - This is the key enhancement!
            info.return_type = return_type
            info.parameters = json.dumps(parameters)  # Store as JSON string
            
            # Check if it's a private implementation (static function in .cpp file)
            if str(filepath).endswith(('.cpp', '.cc', '.cxx')) and decl_type == "definition":
                func_parent = node.parent
                while func_parent and func_parent.type != 'function_definition':
                    func_parent = func_parent.parent
                
                if func_parent:
                    func_text = source_code[func_parent.start_byte:func_parent.end_byte].decode('utf-8')
                    if func_text.strip().startswith('static '):
                        info.is_private_impl = True
            
            entities.append(info)
    
    return entities

def parse_typedefs_and_aliases(tree, source_code, filepath, entity_types):
    """Parse typedefs and using aliases from the syntax tree"""
    entities = []
    
    # Query for typedef declarations
    typedef_query = CPP_LANGUAGE.query("""
        (type_definition
          (type_identifier) @typedef_name) @typedef
    """)
    
    # Query for using alias declarations
    alias_query = CPP_LANGUAGE.query("""
        (alias_declaration
          name: (type_identifier) @alias_name) @alias
    """)
    
    # Process typedefs
    if 'typedef' in entity_types:
        for node, capture_name in typedef_query.captures(tree.root_node):
            if capture_name == 'typedef_name':
                entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
                line_num = source_code[:node.start_byte].count(b'\n') + 1
                namespace = extract_namespace(node, source_code)
                
                info = TypedefInfo(
                    name=entity_name,
                    namespace=namespace,
                    file=str(filepath),
                    line=line_num,
                    decl_type="declaration"
                )
                info.is_using = False
                
                # Check if it's a private implementation
                if str(filepath).endswith(('.cpp', '.cc', '.cxx')):
                    info.is_private_impl = True
                
                entities.append(info)
    
    # Process using aliases
    if 'alias' in entity_types:
        for node, capture_name in alias_query.captures(tree.root_node):
            if capture_name == 'alias_name':
                entity_name = source_code[node.start_byte:node.end_byte].decode('utf-8')
                line_num = source_code[:node.start_byte].count(b'\n') + 1
                namespace = extract_namespace(node, source_code)
                
                info = TypedefInfo(
                    name=entity_name,
                    namespace=namespace,
                    file=str(filepath),
                    line=line_num,
                    decl_type="declaration"
                )
                info.is_using = True
                
                # Check if it's a private implementation
                if str(filepath).endswith(('.cpp', '.cc', '.cxx')):
                    info.is_private_impl = True
                
                entities.append(info)
    
    return entities