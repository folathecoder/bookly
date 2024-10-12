from pydantic import BaseModel
from typing import  Optional

class BookModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    published_date: str

class BookResponseModel(BookModel):
    id: int

class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    published_date: Optional[str] = None