import pytest
import uuid
from bson import ObjectId
from datetime import datetime
from backend.database import collections
from backend.models.books import (
    read_book_field,
    read_book_by_bookId,
    read_book_by_identifier,
    read_book_title,
    read_book_author,
    read_book_page_count,
    read_book_genre,
    read_book_tags,
    read_book_publication_date,
    read_book_isbn,
    read_book_isbn13,
    read_book_cover_image,
    read_book_language,
    read_book_publisher,
    read_book_summary,
    read_book_genre_tags,
    create_book,
    update_book_details,
    add_book_author,
    add_book_tag,
    remove_book_author,
    remove_book_tag,
    delete_book,
)

books_collection = collections["Books"]


def test_read_book_field_valid():
    book_id = "67c2bf84443c76002b50a956"
    field = "title"
    assert (
        read_book_field(book_id, field)
        == "Harry Potter and the Half-Blood Prince (Harry Potter  #6)"
    )


def test_read_book_field_invalid():
    book_id = "67c2bf84443c76002b50a956"
    field = "invalid_field"
    assert read_book_field(book_id, field) == "Field not found"


def test_read_book_field_invalid_id():
    book_id = "invalid_id"
    field = "title"
    assert read_book_field(book_id, field) == "Invalid book ID format"


def test_read_book_field_book_not_found():
    book_id = "000000000000000000000000"
    field = "title"
    assert read_book_field(book_id, field) == "Book not found."


def test_read_book_by_bookId_valid():
    book_id = "67c2bf84443c76002b50a956"
    assert (
        read_book_by_bookId(book_id)["title"]
        == "Harry Potter and the Half-Blood Prince (Harry Potter  #6)"
    )


def test_read_book_by_bookId_book_not_found():
    book_id = "000000000000000000000000"
    assert read_book_by_bookId(book_id) == "Book not found."


def test_read_book_by_bookId_invalid_id_format():
    book_id = "temporary_id"
    assert "Invalid book ID format" in read_book_by_bookId(book_id)


def test_read_book_by_identifier():
    identifier = "isbn"
    value = "452284244"
    print(read_book_by_identifier(value, identifier))

    assert read_book_by_identifier(value, identifier) != "Book not found."


def test_read_book_by_identifier_invalid():
    value = "invalid_value"
    identifier = "title"
    assert read_book_by_identifier(value, identifier) == "Book not found."


def test_read_book_by_identifier_invalid_identifier():
    value = "Harry Potter and the Half-Blood Prince (Harry Potter  #6)"
    identifier = "invalid_identifier"
    assert (
        read_book_by_identifier(value, identifier)
        == "Error: Invalid identifier. Use 'title', 'isbn', or 'isbn13'."
    )


def test_read_book_title():
    id = "67c2bf84443c76002b50a956"
    assert (
        read_book_title(id)
        == "Harry Potter and the Half-Blood Prince (Harry Potter  #6)"
    )


def test_read_book_author():
    id = "67c2bf84443c76002b50a956"
    assert read_book_author(id) == ["J.K. Rowling", "Mary GrandPrÃ©"]


def test_read_book_page_count():
    id = "67c2bf84443c76002b50a956"
    assert read_book_page_count(id) == 652


def test_read_book_genre():
    id = "67c2bf84443c76002b50a956"
    assert read_book_genre(id) == "Juvenile Fiction"


def test_read_book_tags():
    id = "67c2bf85443c76002b50a95b"
    assert read_book_tags(id) == [
        "Harry Potter",
        "Wizards in literature",
        "Magic in literature",
        "Characters",
        "English Fantasy fiction",
        "Children's stories, English",
    ]


def test_read_book_publication_date():
    id = "67c2bf84443c76002b50a956"
    assert read_book_publication_date(id) == datetime(2006, 9, 16, 0, 0)
    # 2006-09-16T00:00:00.000+00:00


def test_read_book_isbn():
    id = "67c2bf84443c76002b50a956"
    assert read_book_isbn(id) == "439785960"


def test_read_book_isbn13():
    id = "67c2bf84443c76002b50a956"
    assert read_book_isbn13(id) == "9780439785969"


def test_read_book_cover_image():
    id = "67c2bf84443c76002b50a956"
    assert (
        read_book_cover_image(id)
        == "https://covers.openlibrary.org/b/id/14656839-M.jpg"
    )


def test_read_book_language():
    id = "67c2bf84443c76002b50a956"
    assert read_book_language(id) == "eng"


def test_read_book_publisher():
    id = "67c2bf84443c76002b50a956"
    assert read_book_publisher(id) == "Scholastic Inc."


def test_read_book_summary():
    id = "67c2bf84443c76002b50a956"
    assert (
        read_book_summary(id)
        == "The war against Voldemort is not going well; even the Muggles have been affected. Dumbledore is absent from Hogwarts for long stretches of time, and the Order of the Phoenix has already suffered losses.\n\nAnd yet . . . as with all wars, life goes on. Sixth-year students learn to Apparate. Teenagers flirt and fight and fall in love. Harry receives some extraordinary help in Potions from the mysterious Half-Blood Prince. And with Dumbledore's guidance, he seeks out the full, complex story of the boy who became Lord Voldemort -- and thus finds what may be his only vulnerability."
    )


def test_genre_tags():
    id = "67c2bf85443c76002b50a959"
    assert read_book_genre_tags(id) == [
        "children's",
        "action & adventure",
        "fiction",
        "speculative fiction",
        "children's fantasy",
        "fantasy",
        "children's fiction",
        "science fiction",
    ]


def test_create_update_and_delete_book():
    """Helper function to create a test book and return its ID."""
    # create the book
    title = "Test Book"
    author = "Test Author"
    page_count = 100
    genre = "Test Genre"
    tags = "test"
    publication_date = "2025-01-01"
    isbn = "111111111"
    isbn13 = "1111111111111"
    cover_image = "http://example.com/test.jpg"
    language = "eng"
    publisher = "Test Publisher"
    summary = "This is a test book."
    genre_tags = ["Fiction", "Adventure"]

    book_id = create_book(
        title,
        author,
        page_count,
        genre,
        tags,
        publication_date,
        isbn,
        isbn13,
        cover_image,
        language,
        publisher,
        summary,
        genre_tags,
    )
    assert book_id != "Schema Validation Error: "
    assert book_id != "Error: ISBN or ISBN-13 must be unique!"

    # update the book
    result = update_book_details(book_id, title="Updated Test Book")
    assert result == "Book updated successfully."

    # delete the book
    result = delete_book(book_id)
    assert books_collection.find_one({"_id": ObjectId(book_id)}) is None
    assert result == "Book and related records deleted successfully."


def test_update_book_details_book_dne():
    book_id = "000000000000000000000000"
    title = "Updated Test Book"
    result = update_book_details(book_id, title=title)
    assert result == "Error: Book not found."


def test_update_book_details_invalid_id_format():
    book_id = "temporary_id"
    title = "Updated Test Book"
    result = update_book_details(book_id, title=title)
    assert result == "Error: Invalid ObjectId format."


# Also implicitly tests create_book and remove_book
def test_add_and_remove_book_author():
    # create the book
    title = "Test Book"
    author = ["Test Author"]
    page_count = 100
    genre = "Test Genre"
    tags = ["test", "book"]
    publication_date = "2025-01-01"
    isbn = "2222222222"
    isbn13 = "222222222222"
    cover_image = "http://example.com/test.jpg"
    language = "eng"
    publisher = "Test Publisher"
    summary = "This is a test book."
    genre_tags = ["Fiction", "Adventure"]

    book_id = create_book(
        title,
        author,
        page_count,
        genre,
        tags,
        publication_date,
        isbn,
        isbn13,
        cover_image,
        language,
        publisher,
        summary,
        genre_tags,
    )
    assert book_id != "Schema Validation Error: "
    assert book_id != "Error: ISBN or ISBN-13 must be unique!"

    # add an author
    result = add_book_author(book_id, "New Author")
    assert result == "Author added successfully."

    # remove the author
    result = remove_book_author(book_id, "New Author")
    assert result == "Author removed successfully."

    # delete the book
    delete_book(book_id)


def test_add_and_remove_book_tag():
    # create the book
    title = "Test Book"
    author = ["Test Author"]
    page_count = 100
    genre = "Test Genre"
    tags = ["test", "book"]
    publication_date = "2025-01-01"
    isbn = "3333333333"
    isbn13 = "3333333333333"
    cover_image = "http://example.com/test.jpg"
    language = "eng"
    publisher = "Test Publisher"
    summary = "This is a test book."
    genre_tags = ["Fiction", "Adventure"]

    book_id = create_book(
        title,
        author,
        page_count,
        genre,
        tags,
        publication_date,
        isbn,
        isbn13,
        cover_image,
        language,
        publisher,
        summary,
        genre_tags,
    )
    assert book_id != "Schema Validation Error: "
    assert book_id != "Error: ISBN or ISBN-13 must be unique!"

    # add a tag
    result = add_book_tag(book_id, "New Tag")
    assert result == "Tag added successfully."

    # remove the tag
    result = remove_book_tag(book_id, "New Tag")
    assert result == "Tag removed successfully."

    # delete the book
    delete_book(book_id)


@pytest.fixture(autouse=True)
def cleanup_test_books():
    yield
    books_collection.delete_many(
        {"isbn": {"$in": ["111111111", "2222222222", "3333333333"]}}
    )

@pytest.fixture
def test_book():
    # create a fresh book with a unique ISBN/ISBN13
    isbn = uuid.uuid4().hex[:9]
    isbn13 = uuid.uuid4().hex[:13]
    book_id = create_book(
        title="Test Book",
        author="Author1",
        page_count=50,
        genre="Test",
        tags=["tag1"],
        publication_date="2025-01-01",
        isbn=isbn,
        isbn13=isbn13,
        cover_image="",
        language="en",
        publisher="Pub",
        summary="Summary",
        genre_tags=["genre"],
    )
    yield book_id
    # clean up
    delete_book(book_id)

def test_update_book_details_validation_error(test_book):
    # invalid type for page_count
    res = update_book_details(test_book, page_count="not-an-int")
    assert res.startswith("Schema Validation Error:")

def test_add_book_author_invalid_id():
    assert add_book_author("not_an_id", "New Author") == "Invalid book ID."

def test_add_book_author_empty_name(test_book):
    assert add_book_author(test_book, "") == "Author name cannot be empty."

def test_add_book_author_duplicate(test_book):
    # "Author1" was already set as the author
    assert add_book_author(test_book, "Author1") == "Author was already in the list or book not found."

def test_remove_book_author_invalid_id():
    assert remove_book_author("12345", "Author1") == "Invalid book ID."

def test_remove_book_author_empty_name(test_book):
    assert remove_book_author(test_book, "") == "Author name cannot be empty."

def test_remove_book_author_not_found(test_book):
    assert remove_book_author(test_book, "DoesNotExist") == "Author not found in the list or book not found."

def test_add_book_tag_invalid_id():
    assert add_book_tag("foo", "newtag") == "Invalid book ID."

def test_add_book_tag_empty_name(test_book):
    assert add_book_tag(test_book, "") == "Tag cannot be empty."

def test_add_book_tag_duplicate(test_book):
    # "tag1" was already set as the tag
    assert add_book_tag(test_book, "tag1") == "Tag was already in the list or book not found."

def test_remove_book_tag_invalid_id():
    assert remove_book_tag("foo", "tag1") == "Invalid book ID."

def test_remove_book_tag_empty_name(test_book):
    assert remove_book_tag(test_book, "") == "Tag cannot be empty."

def test_remove_book_tag_not_found(test_book):
    assert remove_book_tag(test_book, "no_such_tag") == "Tag not found in the list or book not found."

def test_delete_book_invalid_format():
    # invalid ObjectId string
    assert delete_book("not-a-hex-id") == "Invalid book ID format"

def test_delete_book_not_found():
    # valid format but no such book
    fake = str(ObjectId())
    assert delete_book(fake) == "Error: Book not found."

def test_create_book_schema_validation_error():
    # tags must be list[str], passing None triggers a ValidationError
    result = create_book(
        "ErrTest", ["A"], 1, "G", None,
        "2025-01-01", "test_sch_001", "test_sch_0013",
        "", "en", "Pub", "S", []
    )
    assert result.startswith("Schema Validation Error:")

def test_create_book_value_error_on_date():
    # invalid date format triggers the ValueError branch
    result = create_book(
        "ErrTest", ["A"], 1, "G", ["t"],
        "01/01/2025", "test_val_002", "test_val_0023",
        "", "en", "Pub", "S", []
    )
    assert result == "Error: Invalid date format. Use YYYY-MM-DD."

def test_create_book_duplicate_key_error():
    # ensure unique indexes on isbn and isbn13
    books_collection.create_index("isbn", unique=True)
    books_collection.create_index("isbn13", unique=True)

    isbn = "test_dup_003"
    isbn13 = "test_dup_0033"
    # first insert should succeed
    first = create_book(
        "DupTest", ["A"], 1, "G", ["t"],
        "2025-01-01", isbn, isbn13,
        "", "en", "Pub", "S", []
    )
    assert isinstance(first, str) and len(first) == 24

    # second insert should hit duplicate key
    second = create_book(
        "DupTest", ["A"], 1, "G", ["t"],
        "2025-01-01", isbn, isbn13,
        "", "en", "Pub", "S", []
    )
    assert second == "Error: ISBN or ISBN-13 must be unique!"

def test_read_book_by_bookId_invalid_format():
    res = read_book_by_bookId("not_a_valid")
    assert "Invalid book ID format" in res

def test_read_book_by_bookId_not_found():
    fake = str(ObjectId())
    res = read_book_by_bookId(fake)
    assert res == "Book not found."

def test_read_book_by_bookId_schema_validation_error():
    # insert a doc with invalid publication_date to trigger schema error
    bad_id = ObjectId()
    bad_doc = {
        "_id": bad_id,
        "author": ["A"],
        "title": "T",
        "page_count": 10,
        "genre": "G",
        "tags": ["t"],
        "publication_date": "not-a-date",
        "isbn": "test_err_004",
        "isbn13": "test_err_0043",
        "cover_image": "",
        "language": "en",
        "publisher": "",
        "summary": "",
        "genre_tags": [],
        "embedding": [],
    }
    books_collection.insert_one(bad_doc)
    try:
        res = read_book_by_bookId(str(bad_id))
        assert res.startswith("Schema Validation Error:")
    finally:
        books_collection.delete_one({"_id": bad_id})

def test_read_book_by_identifier_invalid_identifier():
    res = read_book_by_identifier("whatever", "foo")
    assert res == "Error: Invalid identifier. Use 'title', 'isbn', or 'isbn13'."

def test_read_book_by_identifier_not_found():
    res = read_book_by_identifier("test_nf_005", "isbn")
    assert res == "Book not found."

def test_read_book_by_identifier_schema_validation_error():
    # insert bad_doc, then query by its isbn
    bad_id = ObjectId()
    isbn = "test_err_006"
    isbn13 = "test_err_0063"
    bad_doc = {
        "_id": bad_id,
        "author": ["A"],
        "title": "T",
        "page_count": 10,
        "genre": "G",
        "tags": ["t"],
        "publication_date": "not-a-date",
        "isbn": isbn,
        "isbn13": isbn13,
        "cover_image": "",
        "language": "en",
        "publisher": "",
        "summary": "",
        "genre_tags": [],
        "embedding": [],
    }
    books_collection.insert_one(bad_doc)
    try:
        res = read_book_by_identifier(isbn, "isbn")
        assert res.startswith("Schema Validation Error:")
    finally:
        books_collection.delete_one({"_id": bad_id})
