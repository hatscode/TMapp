"""SQLite database manager."""
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from src.models.note import Note
from src.models.notebook import Notebook

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: Path):
        """Initialize database."""
        self.db_path = db_path
        self._ensure_database()
        logger.info(f"Database initialized: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _ensure_database(self):
        """Create database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Notebooks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notebooks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    icon TEXT DEFAULT '📓',
                    color TEXT DEFAULT '#4A9EFF',
                    description TEXT,
                    parent_id TEXT,
                    sort_order INTEGER DEFAULT 0,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    default_view TEXT DEFAULT 'list',
                    sort_by TEXT DEFAULT 'updated_at'
                )
            """)
            
            # Notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    content_encrypted BLOB,
                    notebook_id TEXT,
                    tags TEXT,
                    is_favorite BOOLEAN DEFAULT 0,
                    is_encrypted BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    deleted_at TEXT,
                    word_count INTEGER DEFAULT 0,
                    char_count INTEGER DEFAULT 0,
                    has_images BOOLEAN DEFAULT 0,
                    has_checkboxes BOOLEAN DEFAULT 0,
                    FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
                )
            """)
            
            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_notebook ON notes(notebook_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_deleted ON notes(deleted_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_favorite ON notes(is_favorite)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes(tags)")
            
            # Create default notebook if none exists
            cursor.execute("SELECT COUNT(*) FROM notebooks")
            if cursor.fetchone()[0] == 0:
                default_notebook = Notebook(
                    id=str(uuid4()),
                    name="My Notes",
                    icon="📓",
                    color="#4A9EFF",
                    is_default=True,
                )
                self._insert_notebook(cursor, default_notebook)
                logger.info("Created default notebook")
            
            conn.commit()
    
    def _insert_notebook(self, cursor, notebook: Notebook):
        """Insert notebook."""
        data = notebook.to_dict()
        cursor.execute("""
            INSERT INTO notebooks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(data.values()))
    
    def create_notebook(self, notebook: Notebook) -> bool:
        """Create notebook."""
        try:
            with self.get_connection() as conn:
                self._insert_notebook(conn.cursor(), notebook)
            logger.info(f"Notebook created: {notebook.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            return False
    
    def get_notebook(self, notebook_id: str) -> Optional[Notebook]:
        """Get notebook by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notebooks WHERE id = ?", (notebook_id,))
                row = cursor.fetchone()
                if row:
                    return Notebook.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Failed to get notebook: {e}")
            return None
    
    def get_default_notebook(self) -> Optional[Notebook]:
        """Get default notebook."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notebooks WHERE is_default = 1 LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return Notebook.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Failed to get default notebook: {e}")
            return None
    
    def get_all_notebooks(self) -> List[Notebook]:
        """Get all notebooks."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notebooks ORDER BY sort_order, name")
                rows = cursor.fetchall()
                return [Notebook.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get notebooks: {e}")
            return []
    
    def update_notebook(self, notebook: Notebook) -> bool:
        """Update notebook."""
        try:
            notebook.updated_at = datetime.now()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                data = notebook.to_dict()
                cursor.execute("""
                    UPDATE notebooks SET
                        name=?, icon=?, color=?, description=?, parent_id=?,
                        sort_order=?, is_default=?, updated_at=?,
                        default_view=?, sort_by=?
                    WHERE id=?
                """, (
                    data['name'], data['icon'], data['color'], data['description'],
                    data['parent_id'], data['sort_order'], data['is_default'],
                    data['updated_at'], data['default_view'], data['sort_by'],
                    data['id']
                ))
            logger.info(f"Notebook updated: {notebook.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update notebook: {e}")
            return False
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete notebook."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
            logger.info(f"Notebook deleted: {notebook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete notebook: {e}")
            return False
    
    def create_note(self, note: Note) -> bool:
        """Create note."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                data = note.to_dict()
                cursor.execute("""
                    INSERT INTO notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))
            logger.info(f"Note created: {note.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return False
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get note by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()
                if row:
                    return Note.from_dict(dict(row))
            return None
        except Exception as e:
            logger.error(f"Failed to get note: {e}")
            return None
    
    def get_all_notes(self, include_deleted: bool = False) -> List[Note]:
        """Get all notes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if include_deleted:
                    cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
                else:
                    cursor.execute("SELECT * FROM notes WHERE deleted_at IS NULL ORDER BY updated_at DESC")
                rows = cursor.fetchall()
                return [Note.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return []
    
    def get_notes_by_notebook(self, notebook_id: str, include_deleted: bool = False) -> List[Note]:
        """Get notes by notebook."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if include_deleted:
                    cursor.execute(
                        "SELECT * FROM notes WHERE notebook_id = ? ORDER BY updated_at DESC",
                        (notebook_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM notes WHERE notebook_id = ? AND deleted_at IS NULL ORDER BY updated_at DESC",
                        (notebook_id,)
                    )
                rows = cursor.fetchall()
                return [Note.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return []
    
    def get_favorite_notes(self) -> List[Note]:
        """Get favorite notes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM notes WHERE is_favorite = 1 AND deleted_at IS NULL ORDER BY updated_at DESC"
                )
                rows = cursor.fetchall()
                return [Note.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get favorites: {e}")
            return []
    
    def get_deleted_notes(self) -> List[Note]:
        """Get deleted notes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC")
                rows = cursor.fetchall()
                return [Note.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get deleted notes: {e}")
            return []
    
    def update_note(self, note: Note) -> bool:
        """Update note."""
        try:
            note.updated_at = datetime.now()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                data = note.to_dict()
                cursor.execute("""
                    UPDATE notes SET
                        title=?, content=?, content_encrypted=?, notebook_id=?,
                        tags=?, is_favorite=?, is_encrypted=?, updated_at=?,
                        deleted_at=?, word_count=?, char_count=?,
                        has_images=?, has_checkboxes=?
                    WHERE id=?
                """, (
                    data['title'], data['content'], data['content_encrypted'],
                    data['notebook_id'], data['tags'], data['is_favorite'],
                    data['is_encrypted'], data['updated_at'], data['deleted_at'],
                    data['word_count'], data['char_count'], data['has_images'],
                    data['has_checkboxes'], data['id']
                ))
            logger.info(f"Note updated: {note.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update note: {e}")
            return False
    
    def delete_note(self, note_id: str, permanent: bool = False) -> bool:
        """Delete note."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if permanent:
                    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                    logger.info(f"Note permanently deleted: {note_id}")
                else:
                    cursor.execute(
                        "UPDATE notes SET deleted_at = ? WHERE id = ?",
                        (datetime.now().isoformat(), note_id)
                    )
                    logger.info(f"Note moved to trash: {note_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete note: {e}")
            return False
    
    def restore_note(self, note_id: str) -> bool:
        """Restore note from trash."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET deleted_at = NULL WHERE id = ?", (note_id,))
            logger.info(f"Note restored: {note_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore note: {e}")
            return False
    
    def search_notes(self, query: str) -> List[Note]:
        """Search notes by title, content, or tags."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_pattern = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM notes
                    WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)
                    AND deleted_at IS NULL
                    ORDER BY updated_at DESC
                """, (search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                return [Note.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to search notes: {e}")
            return []