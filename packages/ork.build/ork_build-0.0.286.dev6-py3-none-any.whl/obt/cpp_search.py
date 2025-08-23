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
                
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entity_id INTEGER NOT NULL,
                    to_entity_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    relationship_data TEXT DEFAULT '',
                    FOREIGN KEY (from_entity_id) REFERENCES entities (id) ON DELETE CASCADE,
                    FOREIGN KEY (to_entity_id) REFERENCES entities (id) ON DELETE CASCADE
                );
                
                -- Indexes for fast searches
                CREATE INDEX IF NOT EXISTS idx_entities_name ON entities (name);
                CREATE INDEX IF NOT EXISTS idx_entities_type ON entities (entity_type);
                CREATE INDEX IF NOT EXISTS idx_entities_namespace ON entities (namespace);
                CREATE INDEX IF NOT EXISTS idx_entities_file ON entities (file_path);
                CREATE INDEX IF NOT EXISTS idx_files_path ON files (file_path);
                CREATE INDEX IF NOT EXISTS idx_members_entity ON members (entity_id);
                CREATE INDEX IF NOT EXISTS idx_members_type ON members (member_type);
                CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships (from_entity_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships (to_entity_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (relationship_type);
                
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
        if hasattr(entity, '_base_classes_detailed'):
            data_json['base_classes_detailed'] = entity._base_classes_detailed
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
                    # Update the entity_id for the member (since it was 0 during parsing)
                    member['entity_id'] = entity_id
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
                        member.get('data_json') if member.get('data_json') else None
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
            
    def add_relationship(self, from_entity_id: int, to_entity_id: int, 
                        relationship_type: str, relationship_data: str = '') -> int:
        """Add a relationship between entities"""
        with self.connect() as conn:
            cursor = conn.execute("""
                INSERT INTO relationships (
                    from_entity_id, to_entity_id, relationship_type, relationship_data
                ) VALUES (?, ?, ?, ?)
            """, (from_entity_id, to_entity_id, relationship_type, relationship_data))
            return cursor.lastrowid
    
    def get_relationships(self, entity_id: int, relationship_type: str = None, 
                         direction: str = 'from') -> List[Dict]:
        """Get relationships for an entity"""
        if direction == 'from':
            query = "SELECT * FROM relationships WHERE from_entity_id = ?"
        elif direction == 'to':
            query = "SELECT * FROM relationships WHERE to_entity_id = ?"
        else:  # both
            query = "SELECT * FROM relationships WHERE from_entity_id = ? OR to_entity_id = ?"
        
        params = [entity_id]
        if direction == 'both':
            params.append(entity_id)
        
        if relationship_type:
            query += " AND relationship_type = ?"
            params.append(relationship_type)
        
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def find_entity_by_name(self, name: str, namespace: str = '', entity_type: str = '') -> Optional[Dict]:
        """Find an entity by name and optional filters"""
        query = "SELECT * FROM entities WHERE name = ?"
        params = [name]
        
        if namespace:
            query += " AND namespace = ?"
            params.append(namespace)
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None

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
            
            # Extract base classes with detailed parsing
            if node.parent:
                for child in node.parent.children:
                    if child.type == 'base_class_clause':
                        parsed_bases = parse_base_classes(child, source_code)
                        # Store parsed base classes as structured data
                        for base in parsed_bases:
                            info.base_classes.append(f"{base['access']} {base['name']}")
                        # Also store detailed base class info in entity data
                        if parsed_bases:
                            info._base_classes_detailed = parsed_bases
            
            # Extract class members if it has a body
            class_members = []
            if has_body and node.parent:
                # Find the field_declaration_list
                for child in node.parent.children:
                    if child.type == 'field_declaration_list':
                        # Set default visibility based on struct vs class
                        default_visibility = "public" if info.is_struct else "private"
                        # Parse members, passing a temporary entity_id of 0 (will be updated)
                        class_members = parse_class_members_with_visibility(child, source_code, 0, default_visibility)
                        break
            
            if info.entity_type in entity_types:
                # Store members with the entity for later database insertion
                info._members = class_members
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
            
            # Extract base classes for template classes
            if node.parent:
                for child in node.parent.children:
                    if child.type == 'base_class_clause':
                        parsed_bases = parse_base_classes(child, source_code)
                        # Store parsed base classes as structured data
                        for base in parsed_bases:
                            info.base_classes.append(f"{base['access']} {base['name']}")
                        # Also store detailed base class info in entity data
                        if parsed_bases:
                            info._base_classes_detailed = parsed_bases
            
            # Extract class members if it has a body
            class_members = []
            if node.parent:  # class_specifier or struct_specifier
                for child in node.parent.children:
                    if child.type == 'field_declaration_list':
                        # Set default visibility based on struct vs class
                        default_visibility = "public" if info.is_struct else "private"
                        # Parse members, passing a temporary entity_id of 0 (will be updated)
                        class_members = parse_class_members_with_visibility(child, source_code, 0, default_visibility)
                        break
            
            if info.entity_type in entity_types:
                # Store members with the entity for later database insertion
                info._members = class_members
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

def parse_class_members_with_visibility(class_body_node, source_code, class_entity_id, default_visibility="private"):
    """Extract class/struct members with default visibility handling"""
    members = []
    current_visibility = default_visibility
    
    if not class_body_node:
        return members
        
    ordinal = 0
    # Traverse the field_declaration_list to track visibility and extract members
    for child in class_body_node.children:
        if child.type == 'access_specifier':
            # Update current visibility (private, protected, public)
            visibility_text = source_code[child.start_byte:child.end_byte].decode('utf-8')
            current_visibility = visibility_text.rstrip(':')
            
        elif child.type == 'field_declaration':
            # Could be a field or method declaration
            member_info = parse_field_declaration(child, source_code, current_visibility, class_entity_id)
            if member_info:
                member_info['ordinal'] = ordinal
                members.append(member_info)
                ordinal += 1
                
        elif child.type == 'declaration':
            # Constructor/destructor declarations
            member_info = parse_method_declaration(child, source_code, current_visibility, class_entity_id)
            if member_info:
                member_info['ordinal'] = ordinal
                members.append(member_info)
                ordinal += 1
                
        elif child.type == 'function_definition':
            # Inline method definitions
            member_info = parse_method_definition(child, source_code, current_visibility, class_entity_id)
            if member_info:
                member_info['ordinal'] = ordinal
                members.append(member_info)
                ordinal += 1
    
    return members

def parse_class_members(class_body_node, source_code, class_entity_id):
    """Extract class/struct members (fields and methods) with visibility"""
    members = []
    current_visibility = "private"  # Default for class, public for struct
    
    if not class_body_node:
        return members
        
    # Traverse the field_declaration_list to track visibility and extract members
    for child in class_body_node.children:
        if child.type == 'access_specifier':
            # Update current visibility (private, protected, public)
            visibility_text = source_code[child.start_byte:child.end_byte].decode('utf-8')
            current_visibility = visibility_text.rstrip(':')
            
        elif child.type == 'field_declaration':
            # Could be a field or method declaration
            member_info = parse_field_declaration(child, source_code, current_visibility, class_entity_id)
            if member_info:
                members.append(member_info)
                
        elif child.type == 'declaration':
            # Constructor/destructor declarations
            member_info = parse_method_declaration(child, source_code, current_visibility, class_entity_id)
            if member_info:
                members.append(member_info)
                
        elif child.type == 'function_definition':
            # Inline method definitions
            member_info = parse_method_definition(child, source_code, current_visibility, class_entity_id)
            if member_info:
                members.append(member_info)
    
    return members

def parse_field_declaration(field_node, source_code, visibility, class_entity_id):
    """Parse a field_declaration node - could be field or method"""
    # Check if this is a method (has function_declarator) or field (has field_identifier)
    has_function_declarator = any(child.type == 'function_declarator' for child in field_node.children)
    has_field_identifier = any(child.type == 'field_identifier' for child in field_node.children)
    
    if has_function_declarator:
        return parse_method_from_field_declaration(field_node, source_code, visibility, class_entity_id)
    elif has_field_identifier:
        return parse_field_from_field_declaration(field_node, source_code, visibility, class_entity_id)
    
    return None

def parse_field_from_field_declaration(field_node, source_code, visibility, class_entity_id):
    """Parse a field (member variable) from field_declaration"""
    member_info = {
        'entity_id': class_entity_id,
        'member_type': 'field',
        'name': '',
        'data_type': '',
        'visibility': visibility,
        'is_static': False,
        'ordinal': 0,
        'data_json': '{}'
    }
    
    # Parse components
    type_parts = []
    is_const = False
    
    for child in field_node.children:
        if child.type == 'field_identifier':
            member_info['name'] = source_code[child.start_byte:child.end_byte].decode('utf-8')
        elif child.type in ['primitive_type', 'qualified_identifier', 'type_identifier']:
            type_text = source_code[child.start_byte:child.end_byte].decode('utf-8')
            type_parts.append(type_text)
        elif child.type == 'storage_class_specifier':
            specifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            if specifier == 'static':
                member_info['is_static'] = True
        elif child.type == 'type_qualifier':
            qualifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            if qualifier == 'const':
                is_const = True
                type_parts.append(qualifier)
    
    # Build type string - avoid duplicate const
    member_info['data_type'] = ' '.join(type_parts)
    
    return member_info if member_info['name'] else None

def parse_method_from_field_declaration(field_node, source_code, visibility, class_entity_id):
    """Parse a method from field_declaration with function_declarator"""
    member_info = {
        'entity_id': class_entity_id,
        'member_type': 'method',
        'name': '',
        'data_type': '',  # Return type
        'visibility': visibility,
        'is_static': False,
        'ordinal': 0,
        'data_json': '{}'
    }
    
    # Parse components
    return_type_parts = []
    function_declarator_node = None
    
    for child in field_node.children:
        if child.type == 'function_declarator':
            function_declarator_node = child
        elif child.type in ['primitive_type', 'qualified_identifier', 'type_identifier']:
            return_type_parts.append(source_code[child.start_byte:child.end_byte].decode('utf-8'))
        elif child.type == 'storage_class_specifier':
            specifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            if specifier == 'static':
                member_info['is_static'] = True
        elif child.type == 'type_qualifier':
            qualifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            return_type_parts.append(qualifier)
    
    if function_declarator_node:
        # Extract method name and parameters
        method_info = parse_method_declarator(function_declarator_node, source_code)
        member_info['name'] = method_info.get('name', '')
        member_info['data_json'] = json.dumps({
            'parameters': method_info.get('parameters', []),
            'is_const': method_info.get('is_const', False),
            'is_virtual': method_info.get('is_virtual', False)
        })
    
    member_info['data_type'] = ' '.join(return_type_parts)
    
    return member_info if member_info['name'] else None

def parse_method_declaration(decl_node, source_code, visibility, class_entity_id):
    """Parse constructor/destructor from declaration node"""
    member_info = {
        'entity_id': class_entity_id,
        'member_type': 'method',
        'name': '',
        'data_type': '',  # Empty for constructors/destructors
        'visibility': visibility,
        'is_static': False,
        'ordinal': 0,
        'data_json': '{}'
    }
    
    # Find function_declarator
    function_declarator_node = None
    for child in decl_node.children:
        if child.type == 'function_declarator':
            function_declarator_node = child
            break
    
    if function_declarator_node:
        method_info = parse_method_declarator(function_declarator_node, source_code)
        member_info['name'] = method_info.get('name', '')
        member_info['data_json'] = json.dumps({
            'parameters': method_info.get('parameters', []),
            'is_constructor': '~' not in member_info['name'] and member_info['name'],
            'is_destructor': '~' in member_info['name']
        })
    
    return member_info if member_info['name'] else None

def parse_method_definition(func_def_node, source_code, visibility, class_entity_id):
    """Parse inline method definition"""
    # Similar to parse_method_from_field_declaration but for function_definition nodes
    member_info = {
        'entity_id': class_entity_id,
        'member_type': 'method',
        'name': '',
        'data_type': '',
        'visibility': visibility,
        'is_static': False,
        'ordinal': 0,
        'data_json': '{}'
    }
    
    return_type_parts = []
    function_declarator_node = None
    is_virtual = False
    
    for child in func_def_node.children:
        if child.type == 'function_declarator':
            function_declarator_node = child
        elif child.type in ['primitive_type', 'qualified_identifier', 'type_identifier']:
            return_type_parts.append(source_code[child.start_byte:child.end_byte].decode('utf-8'))
        elif child.type == 'storage_class_specifier':
            specifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            if specifier == 'virtual':
                is_virtual = True
    
    if function_declarator_node:
        method_info = parse_method_declarator(function_declarator_node, source_code)
        member_info['name'] = method_info.get('name', '')
        member_info['data_json'] = json.dumps({
            'parameters': method_info.get('parameters', []),
            'is_const': method_info.get('is_const', False),
            'is_virtual': is_virtual,
            'is_pure_virtual': '= 0' in source_code[func_def_node.start_byte:func_def_node.end_byte].decode('utf-8')
        })
    
    member_info['data_type'] = ' '.join(return_type_parts)
    
    return member_info if member_info['name'] else None

def parse_method_declarator(func_declarator_node, source_code):
    """Extract method name, parameters, and qualifiers from function_declarator"""
    method_info = {
        'name': '',
        'parameters': [],
        'is_const': False,
        'is_virtual': False
    }
    
    # Extract method name and parameters
    for child in func_declarator_node.children:
        if child.type in ['identifier', 'field_identifier']:
            method_info['name'] = source_code[child.start_byte:child.end_byte].decode('utf-8')
        elif child.type == 'destructor_name':
            method_info['name'] = source_code[child.start_byte:child.end_byte].decode('utf-8')
        elif child.type == 'parameter_list':
            method_info['parameters'] = parse_parameter_list(child, source_code)
        elif child.type == 'type_qualifier':
            qualifier = source_code[child.start_byte:child.end_byte].decode('utf-8')
            if qualifier == 'const':
                method_info['is_const'] = True
    
    return method_info

def parse_base_classes(base_class_clause_node, source_code):
    """Parse base class clause to extract individual base classes with access modifiers"""
    base_classes = []
    
    if not base_class_clause_node:
        return base_classes
    
    current_access = "private"  # Default for class inheritance
    current_virtual = False  # Track virtual inheritance
    
    for child in base_class_clause_node.children:
        if child.type == 'access_specifier':
            # New access specifier for the next base class
            current_access = source_code[child.start_byte:child.end_byte].decode('utf-8')
        elif child.type == 'virtual':
            # Virtual inheritance modifier
            current_virtual = True
        elif child.type in ['type_identifier', 'qualified_identifier', 'template_type']:
            # Base class name (including template types like TemplateBase<T>)
            class_name = source_code[child.start_byte:child.end_byte].decode('utf-8')
            base_classes.append({
                'name': class_name,
                'access': current_access,
                'is_virtual': current_virtual
            })
            # Reset for next base class
            current_access = "private"
            current_virtual = False
        elif child.type == ':':
            # Start of base class clause, skip
            continue
        elif child.type == ',':
            # Separator between base classes, skip  
            continue
    
    return base_classes

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