from typing import List
from fastapi import HTTPException, APIRouter
from starlette import status
from src.books.book_data import books
from src.books.schemas import BookModel, BookUpdateModel, BookResponseModel
from src.books.helpers import generate_id

book_router = APIRouter()

@book_router.get("/", response_model=List[BookResponseModel], status_code=status.HTTP_200_OK)
async def read_all_books():
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Books not found")
    else:
        return books

@book_router.post("/", response_model=BookResponseModel, status_code=status.HTTP_201_CREATED)
async def create_book(body: BookModel):
    if any(book["title"] == body.title for book in books):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already exist")

    book_id: int = generate_id()
    new_book = {"id": book_id, **body.model_dump()}
    books.append(new_book)
    return new_book

@book_router.get("/{book_id}", response_model=BookResponseModel, status_code=status.HTTP_200_OK)
async def get_book(book_id: int):
    book = next((book for book in books if book["id"] == book_id), None)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")
    return book

@book_router.patch("/{book_id}", response_model=BookResponseModel, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, body: BookUpdateModel):

    for book in books:
        if book["id"] == book_id:
            for key, value in body.model_dump(exclude_unset=True).items():
                book[key] = value
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return None

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id: '{book_id}' not found")