from bson.objectid import ObjectId
from datetime import datetime
from backend.database import collections
from backend.models.books import (
    read_book_field,
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


def test_read_book_by_identifier():
    identifier = "title"
    value = "Animal Farm"
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
    author = ["Test Author"]
    page_count = 100
    genre = "Test Genre"
    tags = ["test", "book"]
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


def test_add_and_remove_book_author():
    # create the book
    title = "Test Book"
    author = ["Test Author"]
    page_count = 100
    genre = "Test Genre"
    tags = ["test", "book"]
    publication_date = "2025-03-17"
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
    publication_date = "2025-03-17"
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

    # add a tag
    result = add_book_tag(book_id, "New Tag")
    assert result == "Tag added successfully."

    # remove the tag
    result = remove_book_tag(book_id, "New Tag")
    assert result == "Tag removed successfully."

    # delete the book
    delete_book(book_id)
