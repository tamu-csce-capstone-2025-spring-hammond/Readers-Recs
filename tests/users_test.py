import pytest
from bson import ObjectId
from datetime import datetime
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

users_collection = collections["Users"]


# Additional tests to write:
#  - update_genre_weights
#  - retrieve_genre_weights
#  - update_embedding
#  - retrieve_embedding


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
        "Error: Username, Email Address, or Refresh Token must be unique!" not in result
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
    assert result == "Error: Username, Email Address, or Refresh Token must be unique!"


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
    assert result == "Error: Username, Email Address, or Refresh Token must be unique!"


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
        demographics={"age": 21},
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
