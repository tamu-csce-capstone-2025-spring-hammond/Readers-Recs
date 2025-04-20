import pytest
from bson import ObjectId
from backend.database import collections
from backend.models.users import (
    create_user,
    read_user,
    read_user_by_username,
    read_user_by_email,
    update_user,
    update_user_settings,
    update_profile_image,
    add_interest,
    remove_interest,
    add_demographic,
    update_demographics,
    remove_demographic,
    delete_user,
    update_genre_weights,
    retrieve_genre_weights,
    update_embedding,
    retrieve_embedding,
)
from pymongo.results import UpdateResult

users_collection = collections["Users"]


def test_create_update_and_delete_user():
    result = create_user(
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
    assert (
        "Error: Username, Email Address, or Access Token must be unique!" not in result
    )
    assert "Schema Validation Error" not in result

    user_id = result
    result = update_user(user_id, last_name="Smith")
    assert result == "User updated successfully."

    result = delete_user(user_id)
    assert result == "User and related records deleted successfully."

    result = users_collection.find_one({"_id": ObjectId(user_id)})
    assert result is None


def test_create_user_invalid_email():
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
    # Attempt to create a second user with the same username or refresh token.
    result = create_user(
        first_name="Jane",
        last_name="Smith",
        username="johndoe1",
        email_address="test_user_2@gmail.com",  # duplicate email
        oauth={"access_token": "67890", "refresh_token": "543219"},
        profile_image="https://example.com/image2.jpg",
        interests=["Cooking"],
        demographics={"age": 21},
    )
    assert result == "Error: Username, Email Address, or Access Token must be unique!"


def test_create_user_invalid_schema():
    # Create the first user.
    create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_4@gmail.com",
        oauth={"access_token": "12345", "refresh_token": "54321"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )
    # Attempt to create another user with duplicate values.
    result = create_user(
        first_name="Alice",
        last_name="Wonderland",
        username="johndoe",
        email_address="test_user_3@gmail.com",
        oauth={
            "access_token": "11111",
            "refresh_token": "54321",
        },  # duplicate refresh token
        profile_image="https://example.com/image3.jpg",
        interests=["Adventure"],
        demographics={"age": 21},
    )
    assert result == "Error: Username, Email Address, or Access Token must be unique!"


def test_read_user():
    result = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_3@gmail.com",
        oauth={"access_token": "67890", "refresh_token": "543219"},
        profile_image="https://example.com/image2.jpg",
        interests=["Cooking"],
        demographics={"age": 21},
    )
    user = read_user(result)
    assert "Schema Validation Error" not in user
    assert "User not found." not in user
    assert "Error: Invalid ObjectId format." not in user


def test_read_user_invalid():
    user_id = "111111111111111111111111"
    result = read_user(user_id)
    assert result == "User not found."

    user_id = "1111111111111111111"
    result = read_user(user_id)
    assert result == "Error: Invalid ObjectId format."


def test_read_user_by_username():
    create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    result = read_user_by_username("johndoe")
    assert "User not found." not in result
    assert result["username"] == "johndoe"


def test_read_user_by_email():
    create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    result = read_user_by_email("test_user_1@gmail.com")
    assert "User not found." not in result
    assert result["email_address"] == "test_user_1@gmail.com"


def test_update_user_settings():
    result = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    user_id = result
    result = update_user_settings(user_id, first_name="John")
    assert result == "User settings updated successfully."


def test_update_profile_image():
    result = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    user_id = result
    result = update_profile_image(user_id, "https://example.com/image2.jpg")
    assert result.modified_count == 1
    assert read_user(user_id)["profile_image"] == "https://example.com/image2.jpg"


def test_add_and_remove_interest():
    result = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    user_id = result
    result = add_interest(user_id, "Cooking")
    assert result.modified_count == 1
    assert "Cooking" in read_user(user_id)["interests"]

    result = remove_interest(user_id, "Cooking")
    assert result.modified_count == 1
    assert "Cooking" not in read_user(user_id)["interests"]


def test_add_update_remove_demographics():
    user_id = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={
            "age": 21,
            "country": "Canada",
            "birthday": "2003-05-14",
            "gender": "F",
        },
    )

    # Add a new demographic field: set country to "USA"
    result = add_demographic(user_id, {"country": "USA"})
    assert result.modified_count == 1
    user = read_user(user_id)
    assert user["demographics"]["country"] == "USA"

    # Update the demographics: change age to 22
    result = update_demographics(user_id, {"age": 22})
    assert result.modified_count == 1
    user = read_user(user_id)
    assert user["demographics"]["age"] == 22

    # Remove the demographic for age (reset it to default, which is 0)
    result = remove_demographic(user_id, "age")
    assert result.modified_count == 1
    user = read_user(user_id)
    assert user["demographics"]["age"] == 0

    # remove demographic for country
    result = remove_demographic(user_id, "country")
    assert result.modified_count == 1
    user = read_user(user_id)
    assert user["demographics"]["country"] == ""

    # remove demographic for birthday
    result = remove_demographic(user_id, "birthday")
    assert result.modified_count == 1
    user = read_user(user_id)
    assert user["demographics"]["birthday"] is None


def test_add_demographics_invalid_type():
    user_id = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    # not provided as a dictionary
    result = add_demographic(user_id, "age")
    assert result == "Error: Demographics must be provided as a dictionary."

    # empty input
    result = add_demographic(user_id, {})
    assert result == "Error: Demographics update cannot be empty."

    # not an approved demographic field
    result = add_demographic(user_id, {"height": 5})
    assert (
        result
        == "Error: Demographics must contain only age, country, birthday, and/or gender."
    )


def test_update_demographics_invalid_type():
    user_id = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

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
    user_id = create_user(
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email_address="test_user_1@gmail.com",
        oauth={"access_token": "123450", "refresh_token": "543210"},
        profile_image="https://example.com/image.jpg",
        interests=["Reading", "Writing"],
        demographics={"age": 21},
    )

    # includes invalid demographic field
    result = remove_demographic(user_id, "height")
    assert result == "Error: height is not a valid demographic field."


def test_delete_user_doesnt_exist():
    result = delete_user("54f0e5aa313f5d824680d6c9")
    assert result == "Error: User not found."


def test_delete_user_invalid_objectid():
    result = delete_user("1111111111111111111111")
    assert result == "Error: Invalid ObjectId format."


def test_retrieve_genre_weights_default_empty_and_not_found():
    # new user has empty genre_weights
    user_id = create_user(
        first_name="Genre",
        last_name="Test",
        username="genre_test",
        email_address="genre_test@example.com",
        oauth={"access_token": "token", "refresh_token": "token"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        assert retrieve_genre_weights(user_id) == {}
        # valid but nonexistent user
        fake = str(ObjectId())
        assert retrieve_genre_weights(fake) == "User not found"
    finally:
        delete_user(user_id)


def test_update_genre_weights_errors_and_success():
    # invalid user
    fake = str(ObjectId())
    assert update_genre_weights(fake, {"fantasy": 1.0}) == "Error: User not found."

    # create real user
    user_id = create_user(
        first_name="Genre",
        last_name="Update",
        username="genre_update",
        email_address="genre_update@example.com",
        oauth={"access_token": "token2", "refresh_token": "token2"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        # bad type
        assert (
            update_genre_weights(user_id, ["not", "a", "dict"])
            == "Error: Genre weights must be a dictionary."
        )
        # bad contents
        assert (
            update_genre_weights(user_id, {"fantasy": "high"})
            == "Error: Genre keys must be strings and weights must be numerical values."
        )

        # successful update
        weights = {"fantasy": 2.5, "sci-fi": 1.0}
        assert (
            update_genre_weights(user_id, weights) == "Success. Genre weights updated."
        )
        assert retrieve_genre_weights(user_id) == weights

        # no change
        assert (
            update_genre_weights(user_id, weights)
            == "Error: Genre weights were not updated, or no changes detected."
        )
    finally:
        delete_user(user_id)


def test_retrieve_embedding_default_and_after_update():
    # new user, no embedding
    user_id = create_user(
        first_name="Embed",
        last_name="Test",
        username="embed_test",
        email_address="embed_test@example.com",
        oauth={"access_token": "tok3", "refresh_token": "tok3"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        # default: no embedding stored
        assert retrieve_embedding(user_id) is None

        # update_embedding invalid user
        fake = str(ObjectId())
        assert update_embedding(fake, [0.1]) == "Error: User not found."

        # invalid payloads
        assert (
            update_embedding(user_id, "notalist")
            == "Error: Embedding must be a list of numerical values."
        )
        assert (
            update_embedding(user_id, [1, "two"])
            == "Error: Embedding must be a list of numerical values."
        )

        # valid update, now returns the list
        result: UpdateResult = update_embedding(user_id, [0.1, 0.2, 0.3])
        assert isinstance(result, UpdateResult) and result.modified_count == 1
        assert retrieve_embedding(user_id) == [0.1, 0.2, 0.3]

        # overwrite with empty list, treated as “no embedding”
        result2: UpdateResult = update_embedding(user_id, [])
        assert isinstance(result2, UpdateResult) and result2.modified_count == 1
        assert retrieve_embedding(user_id) is None

        # no-op on same empty, still no embedding
        result3: UpdateResult = update_embedding(user_id, [])
        assert isinstance(result3, UpdateResult) and result3.modified_count == 0
        assert retrieve_embedding(user_id) is None

    finally:
        delete_user(user_id)


def test_update_embedding_user_not_found():
    # Proper 24‑hex ID that doesn't exist
    fake = "bad_id"
    assert update_embedding(fake, "New") == "Error: Invalid ObjectId format."


def test_update_genre_weights_invalid_id_format():
    # Malformed ObjectId in update_genre_weights should surface the InvalidId message
    bad = "not_hex"
    res = update_genre_weights(bad, {"fantasy": 1.0})
    assert res == "Error: Invalid ObjectId format."


def test_update_user_settings_invalid_id_format():
    # Malformed ObjectId in update_user_settings should surface the InvalidId message
    bad = "not_hex"
    res = update_user_settings(bad, first_name="X")
    assert res == "Error: Invalid ObjectId format."


def test_update_user_settings_no_fields_provided():
    user_id = create_user(
        first_name="NoField",
        last_name="Test",
        username="nofield_test",
        email_address="nofield@example.com",
        oauth={"access_token": "tok_nf", "refresh_token": "tok_nf"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        # No kwargs at all
        assert update_user_settings(user_id) == "Error: No update fields provided."
        # Provided only blank/whitespace names
        assert (
            update_user_settings(user_id, first_name="   ", last_name="\t")
            == "Error: No update fields provided."
        )
    finally:
        delete_user(user_id)


def test_update_user_settings_username_already_taken():
    # Create two users
    u1 = create_user(
        first_name="User",
        last_name="One",
        username="unique_one",
        email_address="one@example.com",
        oauth={"access_token": "tok1", "refresh_token": "tok1"},
        profile_image="",
        interests=[],
        demographics={},
    )
    u2 = create_user(
        first_name="User",
        last_name="Two",
        username="unique_two",
        email_address="two@example.com",
        oauth={"access_token": "tok2", "refresh_token": "tok2"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        # Attempt to change u1's username to u2's
        assert (
            update_user_settings(u1, username="unique_two")
            == "Error: Username already taken."
        )
    finally:
        delete_user(u1)
        delete_user(u2)


def test_update_user_settings_trim_and_multi_field_update():
    user_id = create_user(
        first_name="OrigFirst",
        last_name="OrigLast",
        username="origuser",
        email_address="orig@example.com",
        oauth={"access_token": "tok3", "refresh_token": "tok3"},
        profile_image="http://orig.img",
        interests=[],
        demographics={},
    )
    try:
        res = update_user_settings(
            user_id,
            first_name="  NewFirst  ",
            last_name="\tNewLast\n",
            username=" newuser ",
            profile_image=" https://new.img/path ",
        )
        assert res == "User settings updated successfully."

        updated = read_user(user_id)
        assert updated["first_name"] == "NewFirst"
        assert updated["last_name"] == "NewLast"
        assert updated["username"] == "newuser"
        assert updated["profile_image"] == "https://new.img/path"
    finally:
        delete_user(user_id)


def test_update_user_settings_invalid_field_types():
    user_id = create_user(
        first_name="TypeTest",
        last_name="User",
        username="typetest",
        email_address="typetest@example.com",
        oauth={"access_token": "tok4", "refresh_token": "tok4"},
        profile_image="",
        interests=[],
        demographics={},
    )
    try:
        # Passing an int for username should hit a strip() AttributeError
        err = update_user_settings(user_id, username=12345)
        assert err.startswith("Error:")
        assert "has no attribute 'strip'" in err
    finally:
        delete_user(user_id)


def test_create_user_invalid_email_schema_error():
    # Email must be a valid EmailStr
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
    # Demographics.age must be an int
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


def test_update_user_validation_error_on_email():
    # First create a valid user
    uid = create_user(
        first_name="Up",
        last_name="Date",
        username="update_test",
        email_address="update_test@example.com",
        oauth={"access_token": "u1", "refresh_token": "u1"},
        profile_image="",
        interests=[],
        demographics={"age": 30},
    )
    try:
        # Now attempt to set an invalid email
        res = update_user(uid, email_address="still-not-email")
        assert res.startswith("Schema Validation Error:")
    finally:
        delete_user(uid)


def test_update_user_validation_error_on_demographics():
    # Create valid user
    uid = create_user(
        first_name="Up",
        last_name="Demo",
        username="update_demo",
        email_address="update_demo@example.com",
        oauth={"access_token": "u2", "refresh_token": "u2"},
        profile_image="",
        interests=[],
        demographics={"age": 30},
    )
    try:
        # Attempt to inject a bad demographics field
        res = update_user(uid, demographics={"age": "NaN"})
        assert res.startswith("Schema Validation Error:")
    finally:
        delete_user(uid)


@pytest.fixture(autouse=True)
def cleanup_test_books():
    yield
    users_collection.delete_many(
        {
            "email_address": {
                "$in": [
                    "test_user_1@gmail.com",
                    "test_user_2@gmail.com",
                    "test_user_3@gmail.com",
                    "test_user_4@gmail.com",
                ]
            }
        }
    )
