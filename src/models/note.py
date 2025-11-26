# filepath: /home/wh1t3h4t/Desktop/TMapp/src/models/notebook.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

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

"""Note data model."""
@dataclass
class Note:
    """Note data model."""
    
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
    
    def is_deleted(self) -> bool:
        """Check if note is in trash."""
        return self.deleted_at is not None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_encrypted': self.content_encrypted,
            'notebook_id': self.notebook_id,
            'tags': ','.join(self.tags) if self.tags else '',
            'is_favorite': self.is_favorite,
            'is_encrypted': self.is_encrypted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'has_images': self.has_images,
            'has_checkboxes': self.has_checkboxes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """Create from dictionary."""
        tags = data.get('tags', '')
        return cls(
            id=data['id'],
            title=data.get('title', ''),
            content=data.get('content', ''),
            content_encrypted=data.get('content_encrypted', b''),
            notebook_id=data.get('notebook_id'),
            tags=tags.split(',') if tags else [],
            is_favorite=bool(data.get('is_favorite', False)),
            is_encrypted=bool(data.get('is_encrypted', True)),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            deleted_at=datetime.fromisoformat(data['deleted_at']) if data.get('deleted_at') else None,
            word_count=data.get('word_count', 0),
            char_count=data.get('char_count', 0),
            has_images=bool(data.get('has_images', False)),
            has_checkboxes=bool(data.get('has_checkboxes', False)),
        )