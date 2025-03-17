# backend/app.py
from backend.database import open_connection, close_connection


def main():
    print("Starting the application...")

    client = open_connection()
    db = client["Readers-Recs"]

    collections = {
        "Books": db["Books"],
        "Chat_Messages": db["Chat_Messages"],
        "Comments": db["Comments"],
        "Posts": db["Posts"],
        "User_Bookshelf": db["User_Bookshelf"],
        "Users": db["Users"],
    }

    print("Available collections:")
    for name in collections.keys():
        print(f"- {name}")

    print("Collections in the database:", db.list_collection_names())

    run_application_logic(collections)

    print("Closing the application.")
    close_connection(client)


def run_application_logic(collections):
    # Application logic goes here
    print("Running application logic.")


if __name__ == "__main__":
    main()
