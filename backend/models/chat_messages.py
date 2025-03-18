from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from zoneinfo import ZoneInfo
from backend.schemas import ChatMessageSchema
from backend.mongo_id_utils import is_valid_object_id
from backend.database import collections

chat_messages_collection = collections["Chat_Messages"]

def create_chat_message(book_id, user_id, message_text):
    try:
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."
        if not is_valid_object_id("Users", user_id):
            return "Error: Invalid user_id."
        
        # Create and validate using the schema; defaults (like date_posted) will be applied.
        chat_message = ChatMessageSchema(
            book_id=book_id,
            user_id=user_id,
            message_text=message_text
        )
        data = chat_message.model_dump(by_alias=True)
        # Remove _id if present so MongoDB can generate a new one.
        data.pop("_id", None)
        result = chat_messages_collection.insert_one(data)
        return str(result.inserted_id)
    
    except ValidationError as e:
        return f"Schema Validation Error: {str(e)}"
    except DuplicateKeyError:
        return "Error: Duplicate chat message!"
    except Exception as e:
        return f"Error: {str(e)}"


def read_chat_message(message_id):
    try:
        if not is_valid_object_id("ChatMessages", message_id):
            return "Error: Invalid message_id."
        
        document = chat_messages_collection.find_one({"_id": ObjectId(message_id)})
        if document:
            chat_message = ChatMessageSchema(**document)
            return chat_message.model_dump(by_alias=True)
        else:
            return "Message not found."
    
    except Exception as e:
        return f"Error: {str(e)}"


def update_chat_message(message_id, message_text):
    try:
        if not is_valid_object_id("ChatMessages", message_id):
            return "Error: Invalid message_id."
        
        update_data = {
            "message_text": message_text,
            "date_edited": datetime.now(ZoneInfo("America/Chicago"))
        }
        result = chat_messages_collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update_data}
        )
        if result.matched_count:
            # Retrieve and return the updated document.
            updated_document = chat_messages_collection.find_one({"_id": ObjectId(message_id)})
            chat_message = ChatMessageSchema(**updated_document)
            return chat_message.model_dump(by_alias=True)
        else:
            return "Message not found."
    
    except Exception as e:
        return f"Error: {str(e)}"


def delete_chat_message(message_id):
    try:
        if not is_valid_object_id("ChatMessages", message_id):
            return "Error: Invalid message_id."
        
        result = chat_messages_collection.delete_one({"_id": ObjectId(message_id)})
        if result.deleted_count:
            return "Message deleted successfully."
        else:
            return "Message not found."
    
    except Exception as e:
        return f"Error: {str(e)}"


def get_all_chat_messages_for_book(book_id):
    try:
        if not is_valid_object_id("Books", book_id):
            return "Error: Invalid book_id."
        
        # Find all messages for the book and sort chronologiclaly by date_posted
        cursor = chat_messages_collection.find({"book_id": ObjectId(book_id)}).sort("date_posted", 1)
        messages = []
        for doc in cursor:
            try:
                chat_message = ChatMessageSchema(**doc)
                messages.append(chat_message.model_dump(by_alias=True))
            except ValidationError:
                continue  
        return messages
    
    except Exception as e:
        return f"Error: {str(e)}"

