from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Post:
    id: int
    page_url: str
    image_url: Optional[str] = None
    sample_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    rating: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    source: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_ext: Optional[str] = None

@dataclass
class Tag:
    name: str
    count: int
