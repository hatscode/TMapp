import logging
from typing import List, Optional
from datetime import datetime

from src.models.note import Note
from src.core.database import Database
from src.core.encryption import EncryptionService

logger = logging.getLogger(__name__)

class NoteController:
    """Controller for note operations."""
    
    def __init__(self, database: Database, encryption_service: EncryptionService):
        """Initialize note controller."""
        self.db = database
        self.encryption = encryption_service
        logger.info("NoteController initialized")
    
    def create_note(self, title: str = "Untitled", content: str = "", 
                   notebook_id: Optional[str] = None, tags: List[str] = None) -> Optional[Note]:
        """Create a new note."""
        try:
            note = Note(
                title=title or "Untitled",
                content=content,
                notebook_id=notebook_id,
                tags=tags or []
            )
            
            # Encrypt content
            if content:
                note.content_encrypted = self.encryption.encrypt(content)
                note.content = ""  # Clear plaintext
            
            note.update_metadata()
            
            if self.db.create_note(note):
                logger.info(f"Note created: {note.id}")
                return note
            return None
        
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return None
    
    def get_note(self, note_id: str, decrypt: bool = True) -> Optional[Note]:
        """Get note by ID."""
        try:
            note = self.db.get_note(note_id)
            if note and decrypt and note.is_encrypted:
                # Decrypt content
                if note.content_encrypted:
                    note.content = self.encryption.decrypt(note.content_encrypted)
            return note
        
        except Exception as e:
            logger.error(f"Failed to get note: {e}")
            return None
    
    def update_note(self, note: Note, encrypt: bool = True) -> bool:
        """Update existing note."""
        try:
            # Encrypt content if needed
            if encrypt and note.content and note.is_encrypted:
                note.content_encrypted = self.encryption.encrypt(note.content)
                note.content = ""  # Clear plaintext
            
            note.update_metadata()
            return self.db.update_note(note)
        
        except Exception as e:
            logger.error(f"Failed to update note: {e}")
            return False
    
    def delete_note(self, note_id: str, permanent: bool = False) -> bool:
        """Delete note."""
        return self.db.delete_note(note_id, permanent)
    
    def restore_note(self, note_id: str) -> bool:
        """Restore note from trash."""
        return self.db.restore_note(note_id)
    
    def get_all_notes(self, decrypt: bool = False) -> List[Note]:
        """Get all notes."""
        notes = self.db.get_all_notes()
        if decrypt:
            for note in notes:
                if note.is_encrypted and note.content_encrypted:
                    try:
                        note.content = self.encryption.decrypt(note.content_encrypted)
                    except Exception as e:
                        logger.error(f"Failed to decrypt note {note.id}: {e}")
        return notes
    
    def get_notes_by_notebook(self, notebook_id: str, decrypt: bool = False) -> List[Note]:
        """Get notes in a notebook."""
        notes = self.db.get_notes_by_notebook(notebook_id)
        if decrypt:
            for note in notes:
                if note.is_encrypted and note.content_encrypted:
                    try:
                        note.content = self.encryption.decrypt(note.content_encrypted)
                    except Exception as e:
                        logger.error(f"Failed to decrypt note {note.id}: {e}")
        return notes
    
    def get_favorite_notes(self) -> List[Note]:
        """Get favorite notes."""
        return self.db.get_favorite_notes()
    
    def get_deleted_notes(self) -> List[Note]:
        """Get deleted notes (trash)."""
        return self.db.get_deleted_notes()
    
    def toggle_favorite(self, note_id: str) -> bool:
        """Toggle note favorite status."""
        try:
            note = self.get_note(note_id, decrypt=False)
            if note:
                note.is_favorite = not note.is_favorite
                return self.db.update_note(note)
            return False
        except Exception as e:
            logger.error(f"Failed to toggle favorite: {e}")
            return False
    
    def search_notes(self, query: str) -> List[Note]:
        """Search notes."""
        return self.db.search_notes(query)