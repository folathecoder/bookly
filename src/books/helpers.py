from src.books.book_data import books

def generate_id():
    return 1 if len(books) == 0 else books[-1]["id"] + 1