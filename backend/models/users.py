# database/models/users.py
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
from pydantic import ValidationError
from schemas import UserSchema, OAuthSchema, DemographicSchema
from database import collections

users_collection = collections["Users"]

# require username, email address, and refresh tokens to be unique
# users_collection.create_index("username", unique=True)
# users_collection.create_index("email_address", unique=True)
# users_collection.create_index("refresh_token", unique=True)


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
        demographics = DemographicSchema(**demographics)

        if users_collection.find_one(
            {
                "$or": [
                    {"username": username},
                    {"email_address": email_address},
                    {"oauth.access_token": oauth_data.access_token},
                ]
            }
        ):
            return "Error: Username, Email Address, or Access Token must be unique!"

        # Validate and create user data using UserSchema
        user_data = UserSchema(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email_address=email_address,
            oauth=oauth_data,
            profile_image=profile_image,
            interests=interests if isinstance(interests, list) else [interests],
            demographics=demographics,
            genre_weights=dict(),
            embedding=[],
        )

        # Dump the model to a dict using aliases
        data = user_data.model_dump(by_alias=True)
        # Remove _id if it's empty so MongoDB auto-generates one
        if (
            "demographics" in data
            and "birthday" in data["demographics"]
            and data["demographics"]["birthday"] is not None
        ):
            bday = data["demographics"]["birthday"]
            # if it's a date but not a datetime, convert it:
            if isinstance(bday, date) and not isinstance(bday, datetime):
                data["demographics"]["birthday"] = datetime.combine(
                    bday, datetime.min.time()
                )
        if not data.get("_id"):
            data.pop("_id", None)
        result = users_collection.insert_one(data)
        return str(result.inserted_id)

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"


def read_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return (
            UserSchema(**user).model_dump(by_alias=True) if user else "User not found."
        )
    except (ValueError, InvalidId):
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
    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."


# theoretically used for users to update their name, username, and profile image
def update_user_settings(
    user_id, first_name=None, last_name=None, username=None, profile_image=None
):
    try:
        # Handle user_id as either string or ObjectId
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        # Find existing user
        existing_user = users_collection.find_one({"_id": user_id})
        if not existing_user:
            return "Error: User not found."

        update_data = {}

        # Validate username uniqueness
        if username:
            existing_username = users_collection.find_one(
                {"username": username, "_id": {"$ne": user_id}}  # Exclude current user
            )
            if existing_username:
                return "Error: Username already taken."

            update_data["username"] = username.strip()

        if first_name is not None and first_name.strip():
            update_data["first_name"] = first_name.strip()
        if last_name is not None and last_name.strip():
            update_data["last_name"] = last_name.strip()
        if profile_image is not None and profile_image.strip():
            update_data["profile_image"] = profile_image.strip()

        if not update_data:
            return "Error: No update fields provided."

        # Validate full document
        new_document = {**existing_user, **update_data}
        validated_document = UserSchema(**new_document).model_dump(by_alias=True)

        users_collection.update_one({"_id": user_id}, {"$set": validated_document})

        return "User settings updated successfully."

    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


# ADDED FOR BOOK REC MODEL (anna)
def update_genre_weights(user_id, new_genre_weights):
    try:
        u_id = ObjectId(user_id)  # Ensure the user_id is an ObjectId
        existing_user = users_collection.find_one({"_id": u_id})

        if not existing_user:
            return "Error: User not found."

        if not isinstance(new_genre_weights, dict):
            return "Error: Genre weights must be a dictionary."

        # Ensure keys are strings and values are numerical
        if not all(
            isinstance(k, str) and isinstance(v, (int, float))
            for k, v in new_genre_weights.items()
        ):
            return "Error: Genre keys must be strings and weights must be numerical values."

        result = users_collection.update_one(
            {"_id": u_id}, {"$set": {"genre_weights": new_genre_weights}}
        )

        if result.modified_count == 0:
            return "Error: Genre weights were not updated, or no changes detected."

        return "Success. Genre weights updated."

    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
    except Exception as e:
        return f"Error: {str(e)}"


def retrieve_genre_weights(user_id):
    """
    Retrieve the genre weight dictionary for a user.
    """
    try:
        user = users_collection.find_one({"_id": user_id})
        if not user:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        # print("USER:", user)
        # print("Genre weights:", user["genre_weights"])
        if user:
            return user["genre_weights"] if user else dict()
        else:
            return "User not found"
    except (ValueError, InvalidId):
        return "User not found"


def update_embedding(user_id, new_embedding):
    """
    Update the user's embedding vector.
    Expects new_embedding to be an array (list) of floats.
    """
    u_id = user_id
    try:
        u_id = ObjectId(user_id)
    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."

    existing_user = users_collection.find_one({"_id": u_id})
    if not existing_user:
        return "Error: User not found."

    if not isinstance(new_embedding, list) or not all(
        isinstance(x, (int, float)) for x in new_embedding
    ):
        return "Error: Embedding must be a list of numerical values."

    result = users_collection.update_one(
        {"_id": u_id},
        {"$set": {"embedding": new_embedding}},
    )

    return result


def retrieve_embedding(user_id):
    """
    Retrieve the embedding vector for a user.
    """
    user = users_collection.find_one({"_id": user_id})
    if (
        user and "embedding" in user and user["embedding"]
    ):  # Check if "embedding" exists and is not empty
        return user["embedding"]
    else:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if (
            user and "embedding" in user and user["embedding"]
        ):  # Check if "embedding" exists and is not empty
            return user["embedding"]
        else:
            return None


### End of new update/retrieval functions


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


def add_demographic(user_id, new_demographics):
    allowed = {"age", "country", "birthday", "gender"}

    if not isinstance(new_demographics, dict):
        return "Error: Demographics must be provided as a dictionary."

    if not new_demographics:
        return "Error: Demographics update cannot be empty."

    # Verify that every key in the update is allowed.
    if not all(key in allowed for key in new_demographics.keys()):
        return "Error: Demographics must contain only age, country, birthday, and/or gender."

    update_fields = {
        f"demographics.{key}": value for key, value in new_demographics.items()
    }

    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_fields}
    )


def update_demographics(user_id, new_demographics):
    allowed = {"age", "country", "birthday", "gender"}

    if not isinstance(new_demographics, dict):
        return "Error: Demographics must be provided as a dictionary."

    if not new_demographics:
        return "Error: Demographics update cannot be empty."

    # Verify that every key in the update is allowed.
    if not all(key in allowed for key in new_demographics.keys()):
        return "Error: Demographics must contain only age, country, birthday, and/or gender."

    update_fields = {
        f"demographics.{key}": value for key, value in new_demographics.items()
    }

    return users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_fields}
    )


def remove_demographic(user_id, demographic_field):
    allowed = {"age", "country", "birthday", "gender"}
    if demographic_field not in allowed:
        return f"Error: {demographic_field} is not a valid demographic field."

    if demographic_field == "age":
        default_value = 0
    elif demographic_field in ["country", "gender"]:
        default_value = ""
    elif demographic_field == "birthday":
        default_value = None

    return users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {f"demographics.{demographic_field}": default_value}},
    )


def delete_user(user_id):
    try:
        db = collections
        db["Posts"].delete_many({"user_id": user_id})
        db["Comments"].delete_many({"user_id": user_id})
        db["Chat_Messages"].delete_many({"user_id": user_id})
        db["User_Bookshelf"].delete_many({"user_id": user_id})

        user_id = ObjectId(user_id)

        if not users_collection.find_one({"_id": user_id}):
            return "Error: User not found."

        db["Posts"].delete_many({"user_id": user_id})
        db["Comments"].delete_many({"user_id": user_id})
        db["Chat_Messages"].delete_many({"user_id": user_id})
        db["User_Bookshelf"].delete_many({"user_id": user_id})

        users_collection.delete_one({"_id": user_id})
        return "User and related records deleted successfully."

    except (ValueError, InvalidId):
        return "Error: Invalid ObjectId format."
