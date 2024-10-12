from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from starlette import status
from fastapi.responses import JSONResponse

app = FastAPI(title="Books API", description="A simple API for managing books")

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    publisher: str = Field(..., min_length=1, max_length=100)
    page_count: int = Field(..., gt=0)
    language: str = Field(..., min_length=2, max_length=50)
    published_date: str

    @validator('published_date')
    def validate_published_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, min_length=1, max_length=100)
    page_count: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, min_length=2, max_length=50)
    published_date: Optional[str] = None

    @validator('published_date')
    def validate_published_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

class Book(BookBase):
    id: int

class BookRepository:
    def __init__(self):
        self.books = [
            {
                "id": 1,
                "title": "Think Python",
                "author": "Allen B. Downey",
                "publisher": "O'Reilly Media",
                "published_date": "2021-01-01",
                "page_count": 1234,
                "language": "English",
            },
            # ... (other books)
        ]

    def get_all(self) -> List[Book]:
        return [Book(**book) for book in self.books]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        book = next((book for book in self.books if book["id"] == book_id), None)
        return Book(**book) if book else None

    def create(self, book: BookCreate) -> Book:
        book_id = max(b["id"] for b in self.books) + 1 if self.books else 1
        new_book = {"id": book_id, **book.dict()}
        self.books.append(new_book)
        return Book(**new_book)

    def update(self, book_id: int, book_update: BookUpdate) -> Optional[Book]:
        for book in self.books:
            if book["id"] == book_id:
                book.update({k: v for k, v in book_update.dict().items() if v is not None})
                return Book(**book)
        return None

    def delete(self, book_id: int) -> bool:
        initial_length = len(self.books)
        self.books = [book for book in self.books if book["id"] != book_id]
        return len(self.books) < initial_length

book_repo = BookRepository()

def get_book_repo() -> BookRepository:
    return book_repo

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/books", response_model=List[Book], status_code=status.HTTP_200_OK)
async def read_all_books(repo: BookRepository = Depends(get_book_repo)):
    books = repo.get_all()
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    return books

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, repo: BookRepository = Depends(get_book_repo)):
    if any(existing_book.title == book.title for existing_book in repo.get_all()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already exists")
    return repo.create(book)

@app.get("/books/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, repo: BookRepository = Depends(get_book_repo)):
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")
    return book

@app.patch("/books/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book_update: BookUpdate, repo: BookRepository = Depends(get_book_repo)):
    updated_book = repo.update(book_id, book_update)
    if not updated_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")
    return updated_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, repo: BookRepository = Depends(get_book_repo)):
    if not repo.delete(book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")
    return None