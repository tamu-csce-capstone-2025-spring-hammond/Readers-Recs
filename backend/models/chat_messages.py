from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from schemas import ChatMessageSchema
from mongo_id_utils import is_valid_object_id
from database import collections
from models.users import read_user
import pytz

chat_messages_collection = collections["Chat_Messages"]


def create_chat_message(book_id, user_id, message_text):
    try:
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        if not message_text or not message_text.strip():
            return "Error: Chat message must contain text."
        chat_message = ChatMessageSchema(
            book_id=book_id,
            user_id=user_id,
            message_text=message_text.strip(),
            date_posted=datetime.now(pytz.timezone("America/Chicago")),
        )
        data = chat_message.model_dump(by_alias=True)
        data.pop("_id", None)
        result = chat_messages_collection.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        return f"Error: {str(e)}"


def read_chat_message(message_id):
    try:
        if not is_valid_object_id("Chat_Messages", message_id):
            return "Error: Invalid message_id."

        document = chat_messages_collection.find_one({"_id": ObjectId(message_id)})
        if document:
            chat_message = ChatMessageSchema(**document)
            return chat_message.model_dump(by_alias=True)
        else:
            return "Message not found."
    except Exception as e:
        return f"Error: {str(e)}"


def read_chat_message_text(message_id):
    try:
        if not is_valid_object_id("Chat_Messages", message_id):
            return "Error: Invalid message_id."

        document = chat_messages_collection.find_one({"_id": ObjectId(message_id)})
        chat_message = ChatMessageSchema(**document)
        return chat_message.message_text
    except Exception as e:
        return f"Error: {str(e)}"


def update_chat_message(message_id, message_text):
    try:
        if not is_valid_object_id("Chat_Messages", message_id):
            return "Error: Invalid message_id."
        if not message_text or not message_text.strip():
            return "Error: Chat message must contain text."

        update_data = {
            "message_text": message_text.strip(),
            "date_edited": datetime.now(pytz.timezone("America/Chicago")),
        }
        result = chat_messages_collection.update_one(
            {"_id": ObjectId(message_id)}, {"$set": update_data}
        )
        updated_document = chat_messages_collection.find_one(
            {"_id": ObjectId(message_id)}
        )
        chat_message = ChatMessageSchema(**updated_document)
        return chat_message.model_dump(by_alias=True)

    except Exception as e:
        return f"Error: {str(e)}"


def delete_chat_message(message_id):
    try:
        if not is_valid_object_id("Chat_Messages", message_id):
            return "Error: Invalid message_id."

        result = chat_messages_collection.delete_one({"_id": ObjectId(message_id)})
        return "Message deleted successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def get_all_chat_messages_for_book(book_id):
    try:
        messages = list(chat_messages_collection.find({"book_id": ObjectId(book_id)}))

        serialized_messages = []
        for message in messages:
            serialized = {}

            # Serialize each field (convert ObjectId to str)
            for key, value in message.items():
                if isinstance(value, ObjectId):
                    serialized[key] = str(value)
                else:
                    serialized[key] = value

            # Attach username using user_id
            user_id = message.get("user_id")
            if user_id:
                user_data = read_user(user_id)
                serialized["username"] = (
                    user_data["username"]
                    if isinstance(user_data, dict)
                    else "Unknown user"
                )
            else:
                serialized["username"] = "Unknown user"

            serialized_messages.append(serialized)

        return serialized_messages

    except Exception as e:
        return f"Error: {str(e)}"
