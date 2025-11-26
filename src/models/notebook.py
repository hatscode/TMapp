"""Notebook data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
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
            is_default=bool(data.get('is_default', False)),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            default_view=data.get('default_view', 'list'),
            sort_by=data.get('sort_by', 'updated_at'),
        )