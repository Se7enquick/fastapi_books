from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from starlette.responses import JSONResponse


app = FastAPI()


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str
    description: Optional[str] = Field(None, title='description of the book',
                                       max_length=100, min_length=1)


BOOKS = []


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request,
                                            exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Hey, why do u want {exception.books_to_return} books?"}
    )


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=3)
    author: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(title='Description of book',
                                       max_length=100,
                                       min_length=10)
    rating: int = Field(gt=-1, lt=6)

    class Config:
        schema_extra = {
            'example': {
                'id': "8f8979d4-f889-4b86-9ff0-9dc762bd0906",
                'title': 'Example Title',
                'author': "Example Author",
                'description': 'Description',
                'rating': 3
            }
        }


@app.post('/books/login/')
async def book_login(book_id: int, username: Optional[str] = Header(None), password: Optional[str] = Header(None)):
    if username == 'FastAPIUser' and password == 'test1234!':
        return BOOKS[book_id]
    return 'Invalid user'


@app.get('/header')
async def read_header(random_header: Optional[str] = Header(None)):
    return {"Random-Header": random_header}


@app.get('/')
async def read_all_books(how_many: Optional[int] = None):

    if how_many and how_many < 0:
        raise NegativeNumberException(books_to_return=how_many)

    if len(BOOKS) < 1:
        create_books_no_api()

    if how_many and len(BOOKS) >= how_many > 0:
        i = 1
        new_books = []
        while i <= how_many:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books
    return BOOKS


@app.get('/book/{book_id}')
async def read_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_cannot_be_found_exception()


@app.get('/book/rating/{book_id}', response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_cannot_be_found_exception()


@app.put('/{book_id}')
async def update_book(book_id: UUID, book: Book):
    counter = 0

    for book in BOOKS:
        counter += 1
        if book.id == book_id:
            BOOKS[counter - 1] = book
            return BOOKS[counter - 1]
    raise raise_item_cannot_be_found_exception()


@app.delete('/{book_id}')
async def delete_book(book_id: UUID):
    counter = 0
    for book in BOOKS:
        counter += 1
        if book.id == book_id:
            del BOOKS[counter - 1]
            return f'ID: {book_id} was deleted'
    raise raise_item_cannot_be_found_exception()


@app.post('/', status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


def create_books_no_api():
    book1 = Book(id='3f8979d4-f889-4b86-9ff0-9dc762bd0906',
                 title='Title 1',
                 author='Author 1',
                 description='Description 1',
                 rating=4)

    book2 = Book(id='6f8979d4-f889-4b86-9ff0-9dc762bd0906',
                 title='Title 2',
                 author='Author 2',
                 description='Description 2',
                 rating=4)

    book3 = Book(id='5f8979d4-f889-4b86-9ff0-9dc762bd0906',
                 title='Title 3',
                 author='Author 3',
                 description='Description 3',
                 rating=4)

    book4 = Book(id='2f8979d4-f889-4b86-9ff0-9dc762bd0906',
                 title='Title 4',
                 author='Author 4',
                 description='Description 4',
                 rating=4)

    BOOKS.append(book1)
    BOOKS.append(book2)
    BOOKS.append(book3)
    BOOKS.append(book4)


def raise_item_cannot_be_found_exception():
    return HTTPException(status_code=404,
                         detail='Book not found',
                         headers={'X-Header_Error':
                                      'Nothing to be seen in UUID'})
