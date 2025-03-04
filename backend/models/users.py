from pymongo import errors
from bson.objectid import ObjectId
from pydantic import ValidationError
from backend.schemas import UserSchema, OAuthSchema
from backend.database import collections

users_collection = collections["Users"]

# require username, email address, and refresh tokens to be unique
users_collection.create_index("username", unique=True)
users_collection.create_index("email_address", unique=True)
users_collection.create_index("refresh_token", unique=True)


def create_user(
    first_name,
    last_name,
    username,
    email_address,
    oauth,
    profile_image,
    interests,
    demographics,
):
    try:
        # Validate OAuth
        oauth_data = OAuthSchema(**oauth)

        # Validate demographics
        demographics = OAuthSchema(**demographics)

        # Validate UserSchema
        user_data = UserSchema(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email_address=email_address,
            oauth=oauth_data,
            profile_image=profile_image,
            interests=interests if isinstance(interests, list) else [interests],
            demographics=(
                demographics if isinstance(demographics, list) else [demographics]
            ),
            # ADDED EMPTY GENRE WEIGHTS & EMBEDDING TO INITIALIZE
            genre_weights={},
            embedding=[],
        )

        # Insert
        return str(
            users_collection.insert_one(user_data.model_dump(by_alias=True)).inserted_id
        )

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except errors.DuplicateKeyError:
        return "Error: Username, Email Address, or Refresh Token must be unique!"


def read_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return (
            UserSchema(**user).model_dump(by_alias=True) if user else "User not found."
        )
    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except ValueError:
        return "Error: Invalid ObjectId format."


def read_user_by_username(username):
    user = users_collection.find_one({"username": username})
    return UserSchema(**user).model_dump(by_alias=True) if user else "User not found."


def read_user_by_email(email):
    user = users_collection.find_one({"email_address": email})
    return UserSchema(**user).model_dump(by_alias=True) if user else "User not found."


def update_user(user_id, **kwargs):
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            return "Error: User not found."

        updated_data = {**existing_user, **kwargs}

        validated_data = UserSchema(**updated_data).model_dump(by_alias=True)

        users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": validated_data}
        )
        return "User updated successfully."

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except ValueError:
        return "Error: Invalid ObjectId format."


# theoretically used for users to update their names, interests, demographics, & interests
def update_user_settings(
    user_id, first_name=None, last_name=None, interests=None, demographics=None
):
    try:
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            return "Error: User not found."

        update_data = {**existing_user}

        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if interests is not None:
            update_data["interests"] = (
                interests if isinstance(interests, list) else [interests]
            )
        if demographics is not None:
            update_data["demographics"] = (
                demographics if isinstance(demographics, list) else [demographics]
            )

        validated_data = UserSchema(**update_data).model_dump(by_alias=True)

        users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": validated_data}
        )
        return "User settings updated successfully."

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except ValueError:
        return "Error: Invalid ObjectId format."


# ADDED FOR BOOK REC MODEL (anna)
def update_genre_weights(user_id, new_genre_weights):
    """
    Update the genre weight dictionary for a user.
    Expects new_genre_weights to be a dictionary with genre names as keys and float values as weights.
    """
    if not isinstance(new_genre_weights, dict):
        return "Error: Genre weights must be a dictionary."

    if not all(
        isinstance(k, str) and isinstance(v, (int, float))
        for k, v in new_genre_weights.items()
    ):
        return "Error: Genre keys must be strings and weights must be numerical values."

    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"genre_weights": new_genre_weights}}
    )


def retrieve_genre_weights(user_id):
    """
    Retrieve the genre weight dictionary for a user.
    """
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"genre_weights": 1})
    return user.get("genre_weights", {}) if user else "Error: User not found."


def update_embedding(user_id, new_embedding):
    """
    Update the user's embedding vector.
    Expects new_embedding to be an array (list) of floats.
    """
    if not isinstance(new_embedding, list) or not all(
        isinstance(x, (int, float)) for x in new_embedding
    ):
        return "Error: Embedding must be a list of numerical values."

    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"embedding": new_embedding}}
    )


def retrieve_embedding(user_id):
    """
    Retrieve the embedding vector for a user.
    """
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"embedding": 1})
    return user.get("embedding", []) if user else "Error: User not found."


### End of new update/retrieval functions


def update_username(user_id, new_username):  # TODO: ask if this is necessary
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"username": new_username}}
    )


def update_email(user_id, new_email):  # TODO: ask if this is necessary
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"email_address": new_email}}
    )


def update_profile_image(user_id, new_image):
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"profile_image": new_image}}
    )


def add_interest(user_id, new_interest):
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$addToSet": {"interests": new_interest}}
    )


def remove_interest(user_id, interest):
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$pull": {"interests": interest}}
    )


def add_demographic(user_id, new_demographic):
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$addToSet": {"demographics": new_demographic}}
    )


def update_demographics(user_id, new_demographics):
    if not isinstance(new_demographics, list):
        return "Error: Demographics must be a list of strings."

    if not all(isinstance(d, str) for d in new_demographics):
        return "Error: Each demographic must be a string."

    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"demographics": new_demographics}}
    )


def remove_demographic(user_id, demographic_to_remove):
    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$pull": {"demographics": demographic_to_remove}}
    )


def delete_user(user_id):
    try:
        user_id = ObjectId(user_id)

        if not users_collection.find_one({"_id": user_id}):
            return "Error: User not found."

        db = collections
        db["Posts"].delete_many({"user_id": user_id})
        db["Comments"].delete_many({"user_id": user_id})
        db["Chat_Messages"].delete_many({"user_id": user_id})
        db["User_Bookshelf"].delete_many({"user_id": user_id})

        users_collection.delete_one({"_id": user_id})
        return "User and related records deleted successfully."

    except ValueError:
        return "Error: Invalid ObjectId format."
