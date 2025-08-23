#!/usr/bin/env python3
"""
Generic C++ database builder
Handles building and updating C++ search databases for any project
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Callable
from obt.cpp_search import CppDatabase, parse_cpp_file

class CppDatabaseBuilder:
    """Generic database builder for C++ codebases"""
    
    def __init__(self, 
                 db_path: Path, 
                 project_name: str = "",
                 get_paths_func: Callable = None):
        """
        Initialize database builder
        
        Args:
            db_path: Path to database file
            project_name: Name of project for metadata
            get_paths_func: Function to get search paths for the project
        """
        self.db_path = Path(db_path)
        self.project_name = project_name
        self.get_paths_func = get_paths_func
        self.db = CppDatabase(self.db_path)
        
    def build_database(self, 
                      modules: List[str] = None, 
                      directories: List[str] = None,
                      paths: List[str] = None,
                      rebuild: bool = False) -> Dict:
        """Build or rebuild the database"""
        
        if rebuild and self.db.exists():
            print(f"Removing existing database: {self.db_path}")
            self.db_path.unlink()
            
        print(f"{'Building' if rebuild else 'Creating'} database: {self.db_path}")
        self.db.initialize(self.project_name)
        
        # Get paths to scan
        search_paths = self._get_search_paths(modules, directories, paths)
        return self._scan_and_store(search_paths, update_mode=False)
        
    def update_database(self,
                       modules: List[str] = None,
                       directories: List[str] = None, 
                       paths: List[str] = None) -> Dict:
        """Update database with only changed files"""
        
        if not self.db.exists():
            print(f"Database does not exist: {self.db_path}")
            return self.build_database(modules, directories, paths, rebuild=True)
            
        print(f"Updating database: {self.db_path}")
        
        # Get paths to scan
        search_paths = self._get_search_paths(modules, directories, paths)
        return self._scan_and_store(search_paths, update_mode=True)
        
    def _get_search_paths(self, 
                         modules: List[str] = None,
                         directories: List[str] = None,
                         paths: List[str] = None) -> List[Path]:
        """Get search paths using project-specific function or defaults"""
        
        search_paths = []
        
        # Use project-specific path function if provided
        if self.get_paths_func:
            search_paths = self.get_paths_func(
                specific_dirs=directories,
                module_names=modules
            )
        
        # Add additional paths
        if paths:
            search_paths.extend([Path(p) for p in paths])
            
        # Fallback: current directory if no paths found
        if not search_paths:
            search_paths = [Path.cwd()]
            
        return search_paths
        
    def _scan_and_store(self, search_paths: List[Path], update_mode: bool = False) -> Dict:
        """Scan paths and store entities in database"""
        
        total_files = 0
        updated_files = 0 
        total_entities = 0
        
        cpp_extensions = {'.cpp', '.hpp', '.h', '.cc', '.cxx', '.inl'}
        
        if os.environ.get("DEBUG"):
            print(f"Scanning paths:")
            for path in search_paths:
                print(f"  {path}")
            
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for ext in cpp_extensions:
                for filepath in search_path.rglob(f'*{ext}'):
                    # Skip generated/build directories
                    if any(skip in str(filepath) for skip in ['/build/', '/.build/', '/obj/']):
                        continue
                    
                    total_files += 1
                    
                    # Check if file needs updating
                    if update_mode and not self.db.is_file_modified(filepath):
                        continue
                        
                    updated_files += 1
                    if os.environ.get("DEBUG"):
                        print(f"Parsing: {filepath}")
                    
                    try:
                        # Clear existing entities for this file
                        self.db.clear_file_entities(filepath)
                        
                        # Parse and add entities
                        entities = parse_cpp_file(filepath)  # Uses default entity types
                        for entity in entities:
                            self.db.add_entity(entity)
                            total_entities += 1
                            
                        # Update file tracking
                        self.db.update_file_record(filepath)
                        
                    except Exception as e:
                        if os.environ.get("DEBUG"):
                            print(f"Error parsing {filepath}: {e}")
                        continue
                        
        print(f"Processed {updated_files}/{total_files} files, stored {total_entities} entities")
        return {
            'total_files': total_files,
            'updated_files': updated_files,
            'total_entities': total_entities
        }
        
    def get_database(self) -> CppDatabase:
        """Get the database instance"""
        return self.db
        
    def get_stats(self) -> Optional[Dict]:
        """Get database statistics"""
        if not self.db.exists():
            return None
        return self.db.get_stats()
        
    def exists(self) -> bool:
        """Check if database exists"""
        return self.db.exists()