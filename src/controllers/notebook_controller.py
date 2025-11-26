# filepath: /home/wh1t3h4t/Desktop/TMapp/src/controllers/notebook_controller.py
import logging
from typing import List, Optional

from src.models.notebook import Notebook
from src.core.database import Database

logger = logging.getLogger(__name__)

class NotebookController:
    """Controller for notebook operations."""
    
    def __init__(self, database: Database):
        """Initialize notebook controller."""
        self.db = database
        logger.info("NotebookController initialized")
    
    def create_notebook(self, name: str, icon: str = "📓", 
                       color: str = "#4A9EFF", parent_id: Optional[str] = None) -> Optional[Notebook]:
        """Create a new notebook."""
        try:
            notebook = Notebook(
                name=name,
                icon=icon,
                color=color,
                parent_id=parent_id
            )
            
            if self.db.create_notebook(notebook):
                logger.info(f"Notebook created: {notebook.id}")
                return notebook
            return None
        
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            return None
    
    def get_notebook(self, notebook_id: str) -> Optional[Notebook]:
        """Get notebook by ID."""
        return self.db.get_notebook(notebook_id)
    
    def get_all_notebooks(self) -> List[Notebook]:
        """Get all notebooks."""
        return self.db.get_all_notebooks()
    
    def update_notebook(self, notebook: Notebook) -> bool:
        """Update existing notebook."""
        try:
            from datetime import datetime
            notebook.updated_at = datetime.now()
            return self.db.update_notebook(notebook)
        except Exception as e:
            logger.error(f"Failed to update notebook: {e}")
            return False
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete notebook."""
        return self.db.delete_notebook(notebook_id)
    
    def get_default_notebook(self) -> Optional[Notebook]:
        """Get default notebook."""
        notebooks = self.get_all_notebooks()
        for notebook in notebooks:
            if notebook.is_default:
                return notebook
        return notebooks[0] if notebooks else None