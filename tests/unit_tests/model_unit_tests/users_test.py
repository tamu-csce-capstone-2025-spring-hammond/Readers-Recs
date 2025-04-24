import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pydantic import ValidationError
from bson.errors import InvalidId
from models.users import (
    create_user,
    update_user,
    update_user_settings,
    update_genre_weights,
    update_embedding,
    retrieve_embedding,
)


@pytest.fixture
def fake_user_id():
    return str(ObjectId())


@pytest.fixture
def mock_users_collection():
    with patch("models.users.users_collection") as mock:
        yield mock


@pytest.fixture
def mock_valid_user(monkeypatch):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "first_name": "Mock",
        "last_name": "User",
        "username": "mockuser",
        "profile_image": "mock.png",
        "interests": [],
        "demographics": {},
    }
    monkeypatch.setattr("models.users.read_user", lambda uid: mock_user)
    return user_id


def test_create_update_and_delete_user(monkeypatch):
    import models.users as users
    from bson import ObjectId

    fake_user_id = str(ObjectId())
    mock_collection = MagicMock()

    monkeypatch.setattr(users, "users_collection", mock_collection)
    monkeypatch.setattr(users, "read_user", lambda uid: {"_id": ObjectId(uid)})

    # Patch is_valid_object_id used in your own models (optional if not used here)
    monkeypatch.setattr(users, "is_valid_object_id", lambda col, oid: True)

    # Ensure uniqueness check returns no matches
    mock_collection.find_one.side_effect = [
        None,
        {"_id": ObjectId(fake_user_id)},
        {"_id": ObjectId(fake_user_id)},
    ]

    # Mock behavior
    mock_collection.insert_one.return_value.inserted_id = ObjectId(fake_user_id)
    mock_collection.update_one.return_value.matched_count = 1
    mock_collection.delete_one.return_value.deleted_count = 1

    result = users.create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )
    assert isinstance(result, str)
    assert not result.startswith("Error")

    result = users.update_user(fake_user_id, last_name="Smith")
    assert result == "User updated successfully."

    result = users.delete_user(fake_user_id)
    assert result == "User and related records deleted successfully."


def test_create_user_invalid_email(mock_users_collection):
    from models.users import create_user

    mock_users_collection.insert_one.side_effect = [
        MagicMock(inserted_id=ObjectId()),
        Exception("duplicate key error"),
    ]

    # First attempt (should succeed)
    create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_2@gmail.com",
        oauth={"access_token": "12345", "refresh_token": "54321"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    # Second attempt with duplicate email
    result = create_user(
        first_name="Jane",
        last_name="Smith",
        username="johndoe1",
        email_address="test_user_2@gmail.com",
        oauth={"access_token": "67890", "refresh_token": "543219"},
        profile_image="https://example.com/image2.jpg",
        interests=["Cooking"],
        demographics={"age": 21},
    )
    assert result == "Error: Username, Email Address, or Access Token must be unique!"


def test_create_user_invalid_schema(monkeypatch):
    import models.users as users

    mock_collection = MagicMock()
    monkeypatch.setattr(users, "users_collection", mock_collection)

    # First insert works, second raises a DB exception
    mock_collection.insert_one.side_effect = [
        MagicMock(inserted_id=ObjectId()),
        Exception("duplicate key error"),
    ]

    # First user (should succeed)
    users.create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_4@gmail.com",
        oauth={"access_token": "12345", "refresh_token": "54321"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    # Second user with duplicate info (should return error string)
    result = users.create_user(
        first_name="Alice",
        last_name="Wonderland",
        username="johndoe",
        email_address="test_user_3@gmail.com",
        oauth={"access_token": "11111", "refresh_token": "54321"},
        profile_image="https://example.com/image3.jpg",
        interests=["Adventure"],
        demographics={"age": 21},
    )

    assert result == "Error: Username, Email Address, or Access Token must be unique!"


def test_read_user_invalid():
    from models.users import read_user

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.users_collection.find_one", return_value=None
    ):
        result = read_user("111111111111111111111111")
        assert result == "User not found."

    with patch("mongo_id_utils.is_valid_object_id", return_value=False):
        result = read_user("1111111111111111111")
        assert result == "Error: Invalid ObjectId format."


def test_read_user_by_username():
    mock_user = {
        "_id": ObjectId(),
        "username": "johndoe",
        "email_address": "test_user_1@gmail.com",
    }

    with patch("models.users.users_collection.find_one", return_value=mock_user):
        from models.users import read_user_by_username

        result = read_user_by_username("johndoe")
        assert "User not found." not in result
        assert result["username"] == "johndoe"


def test_read_user_by_email():
    mock_user = {
        "_id": ObjectId(),
        "username": "johndoe",
        "email_address": "test_user_1@gmail.com",
    }

    with patch("models.users.users_collection.find_one", return_value=mock_user):
        from models.users import read_user_by_email

        result = read_user_by_email("test_user_1@gmail.com")
        assert "User not found." not in result
        assert result["email_address"] == "test_user_1@gmail.com"


def test_update_user_settings_success(monkeypatch, mock_valid_user):
    from models import users

    mock_collection = MagicMock()
    monkeypatch.setattr(users, "users_collection", mock_collection)
    mock_collection.update_one.return_value = MagicMock(matched_count=1)

    result = users.update_user_settings(
        mock_valid_user, first_name="Updated", last_name="Name"
    )
    assert result == "User settings updated successfully."


def test_update_profile_image():
    user_id = str(ObjectId())
    new_url = "https://example.com/image2.jpg"

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(modified_count=1),
    ), patch("models.users.read_user", return_value={"profile_image": new_url}):

        from models.users import update_profile_image, read_user

        result = update_profile_image(user_id, new_url)
        assert result.modified_count == 1
        assert read_user(user_id)["profile_image"] == new_url


def test_add_and_remove_interest():
    user_id = str(ObjectId())
    updated_user_with = {"interests": ["Reading", "Writing", "Cooking"]}
    updated_user_without = {"interests": ["Reading", "Writing"]}

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(modified_count=1),
    ), patch(
        "models.users.read_user", side_effect=[updated_user_with, updated_user_without]
    ):

        from models.users import add_interest, remove_interest, read_user

        assert add_interest(user_id, "Cooking").modified_count == 1
        assert "Cooking" in read_user(user_id)["interests"]

        assert remove_interest(user_id, "Cooking").modified_count == 1
        assert "Cooking" not in read_user(user_id)["interests"]


def test_add_update_remove_demographics():
    user_id = str(ObjectId())

    demographics_sequence = [
        {"demographics": {"country": "USA"}},  # after add
        {"demographics": {"country": "USA", "age": 22}},  # after update
        {"demographics": {"country": "USA", "age": 0}},  # after reset
        {"demographics": {"country": ""}},  # after clear
        {"demographics": {"birthday": None}},  # after nullify
    ]

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(modified_count=1),
    ), patch("models.users.read_user", side_effect=demographics_sequence):

        from models.users import (
            add_demographic,
            update_demographics,
            remove_demographic,
            read_user,
        )

        assert add_demographic(user_id, {"country": "USA"}).modified_count == 1
        assert read_user(user_id)["demographics"]["country"] == "USA"

        assert update_demographics(user_id, {"age": 22}).modified_count == 1
        assert read_user(user_id)["demographics"]["age"] == 22

        assert remove_demographic(user_id, "age").modified_count == 1
        assert read_user(user_id)["demographics"]["age"] == 0

        assert remove_demographic(user_id, "country").modified_count == 1
        assert read_user(user_id)["demographics"]["country"] == ""

        assert remove_demographic(user_id, "birthday").modified_count == 1
        assert read_user(user_id)["demographics"]["birthday"] is None


def test_add_demographics_invalid_type():
    user_id = str(ObjectId())

    from models.users import add_demographic

    assert (
        add_demographic(user_id, "age")
        == "Error: Demographics must be provided as a dictionary."
    )
    assert add_demographic(user_id, {}) == "Error: Demographics update cannot be empty."
    assert add_demographic(user_id, {"height": 5}) == (
        "Error: Demographics must contain only age, country, birthday, and/or gender."
    )


def test_update_demographics_invalid_type():
    user_id = str(ObjectId())

    from models.users import update_demographics

    # not provided as a dictionary
    result = update_demographics(user_id, "age")
    assert result == "Error: Demographics must be provided as a dictionary."

    # empty input
    result = update_demographics(user_id, {})
    assert result == "Error: Demographics update cannot be empty."

    # not an approved demographic field
    result = update_demographics(user_id, {"height": 5})
    assert (
        result
        == "Error: Demographics must contain only age, country, birthday, and/or gender."
    )


def test_remove_demographics_invalid_type():
    user_id = str(ObjectId())

    from models.users import remove_demographic

    result = remove_demographic(user_id, "height")
    assert result == "Error: height is not a valid demographic field."


def test_delete_user_doesnt_exist():
    fake_id = str(ObjectId())
    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.read_user", return_value="User not found."
    ):
        from models.users import delete_user

        result = delete_user(fake_id)
        assert result == "Error: User not found."


def test_delete_user_invalid_objectid():
    with patch("mongo_id_utils.is_valid_object_id", return_value=False):
        from models.users import delete_user

        result = delete_user("1111111111111111111111")
        assert result == "Error: Invalid ObjectId format."


def test_retrieve_genre_weights_default_empty_and_not_found(monkeypatch):
    from models import users

    user_id = str(ObjectId())

    mock_collection = MagicMock()
    monkeypatch.setattr(users, "users_collection", mock_collection)

    # 1st call: valid user with empty genre_weights
    # 2nd call: raise InvalidId
    mock_collection.find_one.side_effect = [{"genre_weights": {}}, InvalidId("invalid")]

    monkeypatch.setattr(
        users,
        "ObjectId",
        lambda x: (
            ObjectId(x) if x != "notavalidid" else (_ for _ in ()).throw(InvalidId())
        ),
    )

    assert users.retrieve_genre_weights(user_id) == {}
    assert users.retrieve_genre_weights("notavalidid") == "User not found"


def test_update_genre_weights_errors_and_success():
    real_id = ObjectId()
    fake_id = "notavalidid"
    genre_weights = {"fantasy": 2.5, "sci-fi": 1.0}

    def fake_ObjectId(x):
        if x == fake_id:
            raise InvalidId("invalid")
        return real_id if x == str(real_id) else ObjectId(x)

    with patch("models.users.ObjectId", side_effect=fake_ObjectId), patch(
        "models.users.users_collection.find_one",
        side_effect=lambda query: (
            None if query["_id"] == "notavalidid" else {"_id": real_id}
        ),
    ), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(modified_count=1),
    ):
        # Invalid ObjectId format
        assert (
            update_genre_weights(fake_id, genre_weights)
            == "Error: Invalid ObjectId format."
        )
        # Successful update
        assert (
            update_genre_weights(str(real_id), genre_weights)
            == "Success. Genre weights updated."
        )


def test_retrieve_embedding_default_and_after_update():
    real_id = ObjectId()
    fake_id = "notavalidid"

    def safe_objectid(x):
        if x == fake_id:
            raise InvalidId("Invalid ObjectId")
        return real_id

    with patch("models.users.ObjectId", side_effect=safe_objectid), patch(
        "models.users.users_collection.find_one",
        side_effect=[
            {"embedding": None},  # retrieve
            None,  # update fake
            {"embedding": None},  # invalid type
            {"embedding": None},  # invalid element
            {"embedding": [0.1, 0.2, 0.3]},  # retrieve updated
            {"embedding": []},  # retrieve cleared
            {"embedding": []},  # retrieve still cleared
        ],
    ), patch(
        "models.users.users_collection.update_one",
        side_effect=[
            MagicMock(modified_count=1),  # update success
            MagicMock(modified_count=1),  # clear success
            MagicMock(modified_count=0),  # noop
        ],
    ):
        assert retrieve_embedding(str(real_id)) is None
        assert update_embedding(fake_id, [0.1]) == "Error: Invalid ObjectId format."


def test_update_embedding_user_not_found():
    bad_id = "bad_id"
    with patch("mongo_id_utils.is_valid_object_id", return_value=False):
        assert update_embedding(bad_id, "New") == "Error: Invalid ObjectId format."


def test_update_genre_weights_invalid_id_format():
    bad = "not_hex"
    with patch("mongo_id_utils.is_valid_object_id", return_value=False):
        assert (
            update_genre_weights(bad, {"fantasy": 1.0})
            == "Error: Invalid ObjectId format."
        )


def test_update_user_settings_invalid_id_format():
    bad = "not_hex"
    with patch("mongo_id_utils.is_valid_object_id", return_value=False):
        res = update_user_settings(bad, first_name="X")
        assert res == "Error: Invalid ObjectId format."


def test_update_user_settings_no_fields_provided(monkeypatch):
    import models.users as users

    user_id = str(ObjectId())

    # Patch is_valid_object_id to return True
    monkeypatch.setattr(users, "is_valid_object_id", lambda col, oid: True)

    # Patch read_user to simulate a real user
    monkeypatch.setattr(users, "read_user", lambda uid: {"_id": ObjectId(uid)})

    # Patch users_collection.update_one to prevent real DB call
    monkeypatch.setattr(users, "users_collection", MagicMock())

    # No kwargs provided at all
    assert users.update_user_settings(user_id) == "Error: No update fields provided."

    # Only whitespace provided
    assert (
        users.update_user_settings(user_id, first_name="   ", last_name="\t")
        == "Error: No update fields provided."
    )


def test_update_user_settings_username_already_taken():
    from models.users import update_user_settings

    uid = str(ObjectId())
    taken_user = {"_id": ObjectId(), "username": "duplicate"}

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.read_user_by_username", return_value=taken_user
    ), patch(
        "models.users.users_collection.find_one", return_value={"_id": ObjectId(uid)}
    ):
        result = update_user_settings(uid, username="duplicate")
        assert result == "Error: Username already taken."


def test_update_user_settings_trim_and_multi_field_update(mock_valid_user):
    from models.users import update_user_settings

    uid = mock_valid_user

    mock_user = {
        "_id": ObjectId(uid),
        "first_name": "Old",
        "last_name": "Name",
        "username": "olduser",
        "email_address": "old@example.com",
        "oauth": {"access_token": "tok", "refresh_token": "tok"},
        "profile_image": "old.jpg",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    with patch("mongo_id_utils.is_valid_object_id", return_value=True), patch(
        "models.users.read_user_by_username", return_value=None
    ), patch(
        "models.users.users_collection.find_one",
        side_effect=[
            mock_user,  # for fetching the user by ID
            None,  # for username uniqueness check (no conflict)
        ],
    ), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(matched_count=1),
    ):
        result = update_user_settings(
            uid,
            first_name="  NewFirst  ",
            last_name="\tNewLast\n",
            username=" newuser ",
            profile_image=" https://new.img/path ",
        )
        assert result == "User settings updated successfully."


def test_update_user_settings_invalid_field_types(monkeypatch):
    import models.users as users

    uid = str(ObjectId())

    mock_user = {
        "_id": ObjectId(uid),
        "first_name": "X",
        "last_name": "Y",
        "username": "mockuser",
        "email_address": "x@example.com",
        "oauth": {"access_token": "t", "refresh_token": "t"},
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    mock_collection = MagicMock()
    monkeypatch.setattr(users, "users_collection", mock_collection)
    monkeypatch.setattr(users, "is_valid_object_id", lambda col, oid: True)

    # First call = find user by ID, second call = uniqueness check (returns None to simulate unique)
    mock_collection.find_one.side_effect = [mock_user, None]

    # Username passed as int, should fail with .strip() AttributeError
    result = users.update_user_settings(uid, username=12345)
    assert result.startswith("Error:")
    assert "has no attribute 'strip'" in result


def test_create_user_invalid_email_schema_error():
    with patch("models.users.users_collection.insert_one"):
        res = create_user(
            first_name="Bad",
            last_name="Email",
            username="bademail",
            email_address="not-an-email",
            oauth={"access_token": "t", "refresh_token": "t"},
            profile_image="",
            interests=[],
            demographics={"age": 25},
        )
        assert res.startswith("Schema Validation Error:")


def test_create_user_invalid_demographics_schema_error():
    with patch("models.users.users_collection.insert_one"):
        res = create_user(
            first_name="Bad",
            last_name="Demo",
            username="baddemo",
            email_address="baddemo@example.com",
            oauth={"access_token": "t2", "refresh_token": "t2"},
            profile_image="",
            interests=[],
            demographics={"age": "not-an-int"},
        )
        assert res.startswith("Schema Validation Error:")


def test_update_user_invalid_id_format():
    # Malformed ObjectId in update_user
    res = update_user("not_a_valid_id", first_name="X")
    assert res == "Error: Invalid ObjectId format."


def test_update_user_validation_error_on_email(monkeypatch):
    import models.users as users

    user_id = str(ObjectId())

    monkeypatch.setattr(users, "users_collection", MagicMock())
    monkeypatch.setattr(users, "is_valid_object_id", lambda col, oid: True)

    users.users_collection.find_one.return_value = {
        "_id": ObjectId(user_id),
        "first_name": "Test",
        "last_name": "User",
        "username": "mockuser",
        "email_address": "mock@example.com",
        "oauth": {"access_token": "tok", "refresh_token": "tok"},
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    result = users.update_user(user_id, email_address="invalid_email")
    assert result.startswith("Schema Validation Error:")


def test_update_user_validation_error_on_demographics(monkeypatch):
    import models.users as users

    user_id = str(ObjectId())

    monkeypatch.setattr(users, "users_collection", MagicMock())
    monkeypatch.setattr(users, "is_valid_object_id", lambda col, oid: True)

    users.users_collection.find_one.return_value = {
        "_id": ObjectId(user_id),
        "first_name": "Test",
        "last_name": "User",
        "username": "mockuser",
        "email_address": "mock@example.com",
        "oauth": {"access_token": "tok", "refresh_token": "tok"},
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    result = users.update_user(user_id, demographics={"age": "not-an-int"})
    assert result.startswith("Schema Validation Error:")


def test_update_user_user_not_found():
    with patch("models.users.users_collection.find_one", return_value=None):
        result = update_user(str(ObjectId()), first_name="Test")
        assert result == "Error: User not found."


def test_update_user_settings_user_not_found():
    with patch("models.users.users_collection.find_one", return_value=None):
        result = update_user_settings(str(ObjectId()), first_name="Test")
        assert result == "Error: User not found."


def test_update_genre_weights_user_not_found():
    with patch("models.users.users_collection.find_one", return_value=None):
        result = update_genre_weights(str(ObjectId()), {"fiction": 1.0})
        assert result == "Error: User not found."


def test_retrieve_embedding_user_not_found():
    with patch("models.users.users_collection.find_one", return_value=None):
        result = retrieve_embedding(str(ObjectId()))
        assert result is None


def test_retrieve_embedding_empty():
    with patch(
        "models.users.users_collection.find_one", return_value={"embedding": []}
    ):
        result = retrieve_embedding(str(ObjectId()))
        assert result is None


def test_update_embedding_invalid_objectid():
    result = update_embedding("invalid_id", [0.1])
    assert result == "Error: Invalid ObjectId format."


def test_update_embedding_invalid_list_type():
    with patch(
        "models.users.users_collection.find_one", return_value={"_id": ObjectId()}
    ):
        result = update_embedding(str(ObjectId()), "notalist")
        assert result == "Error: Embedding must be a list of numerical values."


def test_update_embedding_invalid_elements():
    with patch(
        "models.users.users_collection.find_one", return_value={"_id": ObjectId()}
    ):
        result = update_embedding(str(ObjectId()), [1, "bad"])
        assert result == "Error: Embedding must be a list of numerical values."


def test_update_embedding_success():
    with patch(
        "models.users.users_collection.find_one", return_value={"_id": ObjectId()}
    ), patch(
        "models.users.users_collection.update_one",
        return_value=MagicMock(modified_count=1),
    ):
        result = update_embedding(str(ObjectId()), [0.1, 0.2])
        assert result.modified_count == 1


def test_update_user_settings_schema_validation_error(monkeypatch):
    import models.users as users

    uid = str(ObjectId())

    # Provide a valid user dict
    mock_user = {
        "_id": ObjectId(uid),
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email_address": "john@example.com",
        "oauth": {"access_token": "tok", "refresh_token": "tok"},
        "profile_image": "",
        "interests": [],
        "demographics": {},
        "genre_weights": {},
        "embedding": [],
    }

    # Patch the DB lookup and validation behavior
    monkeypatch.setattr(users, "users_collection", MagicMock())
    users.users_collection.find_one.side_effect = [
        mock_user,
        None,
    ]  # user found, no conflict
    monkeypatch.setattr(users, "read_user_by_username", lambda _: None)

    # Patch UserSchema to raise a ValidationError when called
    monkeypatch.setattr(
        users,
        "UserSchema",
        lambda **kwargs: (_ for _ in ()).throw(
            ValidationError.from_exception_data("UserSchema", [])
        ),
    )

    # Should catch the forced schema error
    result = update_user_settings(uid, first_name="Test")
    assert result.startswith("Schema Validation Error:")


def test_create_user_with_birthday(monkeypatch):
    import models.users as users
    from datetime import date

    fake_id = ObjectId()
    mock_collection = MagicMock()

    monkeypatch.setattr(users, "users_collection", mock_collection)
    monkeypatch.setattr(users, "read_user_by_username", lambda _: None)
    monkeypatch.setattr(users, "read_user_by_email", lambda _: None)

    # Simulate no duplicate user in uniqueness check
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = fake_id

    result = users.create_user(
        first_name="Birthday",
        last_name="Test",
        username="birthdayuser",
        email_address="bday@example.com",
        oauth={"access_token": "tokb", "refresh_token": "tokb"},
        profile_image="http://img.com/b.jpg",
        interests=["hiking"],
        demographics={
            "age": 25,
            "birthday": date(2000, 1, 1),
            "country": "US",
            "gender": "F",
        },
    )

    assert result == str(fake_id)


def test_update_genre_weights_unexpected_exception(monkeypatch):
    import models.users as users

    user_id = str(ObjectId())
    genre_weights = {"fantasy": 2.5}

    # Simulate unexpected error during find_one
    monkeypatch.setattr(users, "users_collection", MagicMock())
    users.users_collection.find_one.side_effect = Exception("database crashed")

    result = users.update_genre_weights(user_id, genre_weights)
    assert result == "Error: database crashed"
