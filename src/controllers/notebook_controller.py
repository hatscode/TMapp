"""Notebook controller for business logic."""
import logging
from typing import List, Optional
from uuid import uuid4

from src.models.notebook import Notebook
from src.core.database import Database

logger = logging.getLogger(__name__)


class NotebookController:
    """Controller for notebook operations."""
    
    def __init__(self, database: Database):
        """Initialize notebook controller."""
        self.db = database
        logger.info("NotebookController initialized")
    
    def create_notebook(self, name: str, icon: str = "📓", color: str = "#4A9EFF",
                       description: str = "", parent_id: Optional[str] = None) -> Optional[Notebook]:
        """Create a new notebook."""
        try:
            notebook = Notebook(
                id=str(uuid4()),
                name=name,
                icon=icon,
                color=color,
                description=description,
                parent_id=parent_id
            )
            
            if self.db.create_notebook(notebook):
                logger.info(f"Notebook created: {notebook.name}")
                return notebook
            return None
        
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            return None
    
    def get_notebook(self, notebook_id: str) -> Optional[Notebook]:
        """Get notebook by ID."""
        return self.db.get_notebook(notebook_id)
    
    def get_default_notebook(self) -> Optional[Notebook]:
        """Get the default notebook."""
        return self.db.get_default_notebook()
    
    def get_all_notebooks(self) -> List[Notebook]:
        """Get all notebooks."""
        return self.db.get_all_notebooks()
    
    def update_notebook(self, notebook: Notebook) -> bool:
        """Update notebook."""
        return self.db.update_notebook(notebook)
    
    def delete_notebook(self, notebook_id: str, move_notes_to: Optional[str] = None) -> bool:
        """Delete notebook and optionally move notes."""
        try:
            # If moving notes, update them first
            if move_notes_to:
                notes = self.db.get_notes_by_notebook(notebook_id)
                for note in notes:
                    note.notebook_id = move_notes_to
                    self.db.update_note(note)
            
            return self.db.delete_notebook(notebook_id)
        
        except Exception as e:
            logger.error(f"Failed to delete notebook: {e}")
            return False
    
    def rename_notebook(self, notebook_id: str, new_name: str) -> bool:
        """Rename a notebook."""
        try:
            notebook = self.get_notebook(notebook_id)
            if notebook:
                notebook.name = new_name
                return self.update_notebook(notebook)
            return False
        except Exception as e:
            logger.error(f"Failed to rename notebook: {e}")
            return False
    
    def set_default_notebook(self, notebook_id: str) -> bool:
        """Set a notebook as default."""
        try:
            # Clear existing default
            notebooks = self.get_all_notebooks()
            for nb in notebooks:
                if nb.is_default:
                    nb.is_default = False
                    self.update_notebook(nb)
            
            # Set new default
            notebook = self.get_notebook(notebook_id)
            if notebook:
                notebook.is_default = True
                return self.update_notebook(notebook)
            return False
        
        except Exception as e:
            logger.error(f"Failed to set default notebook: {e}")
            return False