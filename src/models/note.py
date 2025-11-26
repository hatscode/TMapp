"""Note model with encryption support."""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

@dataclass
class Notebook:
    """Notebook data model."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    icon: str = "📓"
    color: str = "#4A9EFF"
    description: str = ""
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # View preferences
    default_view: str = "list"  # list or grid
    sort_by: str = "updated_at"  # updated_at, created_at, title
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'description': self.description,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'default_view': self.default_view,
            'sort_by': self.sort_by,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Notebook':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data.get('name', ''),
            icon=data.get('icon', '📓'),
            color=data.get('color', '#4A9EFF'),
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            sort_order=data.get('sort_order', 0),
            is_default=data.get('is_default', False),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            default_view=data.get('default_view', 'list'),
            sort_by=data.get('sort_by', 'updated_at'),
        )

"""Note model with encryption support."""
@dataclass
class Note:
    """Note model with encryption support."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: str = ""
    content_encrypted: bytes = b""
    notebook_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    is_encrypted: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None
    
    # Metadata
    word_count: int = 0
    char_count: int = 0
    has_images: bool = False
    has_checkboxes: bool = False
    
    def update_metadata(self):
        """Update note metadata based on content."""
        if self.content:
            self.word_count = len(self.content.split())
            self.char_count = len(self.content)
            self.has_images = '![' in self.content
            self.has_checkboxes = '- [ ]' in self.content or '- [x]' in self.content
        self.updated_at = datetime.now()
    
    def set_content(self, content: str):
        """Set note content (plain text)."""
        self.content = content
        self.word_count = len(content.split()) if content else 0
        self.char_count = len(content)
        self.has_checkboxes = '- [ ]' in content or '- [x]' in content or '- [X]' in content
        self.updated_at = datetime.now()
        logger.debug(f"Content updated for note {self.id}: {self.word_count} words")
    
    def get_plain_text(self) -> str:
        """Get plain text content."""
        return self.content or ""
    
    def set_encrypted_content(self, encrypted_data: bytes):
        """Set encrypted content."""
        self.content_encrypted = encrypted_data
        self.is_encrypted = True
        self.content = None  # Clear plain text when encrypted
        logger.debug(f"Encrypted content set for note {self.id}")
    
    def get_encrypted_content(self) -> Optional[bytes]:
        """Get encrypted content."""
        return self.content_encrypted
    
    def add_tag(self, tag: str):
        """Add a tag."""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ",".join(current_tags)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag."""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ",".join(current_tags)
            self.updated_at = datetime.now()
    
    def get_tags_list(self) -> list:
        """Get tags as list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
    
    def set_tags(self, tags: list):
        """Set tags from list."""
        self.tags = ",".join(tags)
        self.updated_at = datetime.now()
    
    def toggle_favorite(self):
        """Toggle favorite status."""
        self.is_favorite = not self.is_favorite
        self.updated_at = datetime.now()
    
    def soft_delete(self):
        """Soft delete (move to trash)."""
        self.deleted_at = datetime.now()
        self.updated_at = datetime.now()
    
    def restore(self):
        """Restore from trash."""
        self.deleted_at = None
        self.updated_at = datetime.now()
    
    def is_deleted(self) -> bool:
        """Check if note is deleted."""
        return self.deleted_at is not None
    
    def get_preview(self, length: int = 100) -> str:
        """Get content preview."""
        text = self.get_plain_text()
        if len(text) <= length:
            return text
        return text[:length] + "..."
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_encrypted': self.content_encrypted,
            'notebook_id': self.notebook_id,
            'tags': self.tags,
            'is_favorite': self.is_favorite,
            'is_encrypted': self.is_encrypted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'has_images': self.has_images,
            'has_checkboxes': self.has_checkboxes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """Create note from dictionary."""
        # Parse datetime strings
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = datetime.now()
        
        updated_at = None
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                updated_at = datetime.now()
        
        deleted_at = None
        if data.get('deleted_at'):
            try:
                deleted_at = datetime.fromisoformat(data['deleted_at'])
            except (ValueError, TypeError):
                pass
        
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            content_encrypted=data.get('content_encrypted'),
            notebook_id=data.get('notebook_id'),
            tags=data.get('tags', ''),
            is_favorite=bool(data.get('is_favorite', False)),
            is_encrypted=bool(data.get('is_encrypted', True)),
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at,
            word_count=data.get('word_count', 0),
            char_count=data.get('char_count', 0),
            has_images=bool(data.get('has_images', False)),
            has_checkboxes=bool(data.get('has_checkboxes', False)),
        )
    
    def __repr__(self):
        """String representation."""
        return f"Note(id={self.id}, title='{self.title}', words={self.word_count})"
    
    def __str__(self):
        """User-friendly string."""
        return self.title or "Untitled Note"