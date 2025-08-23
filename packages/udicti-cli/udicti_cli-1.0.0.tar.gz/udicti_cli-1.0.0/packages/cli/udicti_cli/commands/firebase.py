# File: packages/cli/udicti_cli/commands/firebase.py

"""
This module provides utility functions for connecting to and interacting with
a Firebase Firestore database. It centralizes all database logic.
"""
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def init_firebase(firebase_config: dict):
    """
    Initializes the Firebase Admin SDK if it hasn't been initialized already.

    Args:
        firebase_config: The Firebase configuration dictionary.
        This dictionary should contain your Firebase service account key details.
    """
    if not firebase_admin._apps:
        # Check if the config is a path to a file or the direct JSON content
        # For security, storing the path to a JSON file as an environment variable
        # and loading it from there is recommended in production.
        try:
            # If firebase_config looks like a file path (string)
            if isinstance(firebase_config, str):
                cred = credentials.Certificate(firebase_config)
            # If firebase_config is the direct dictionary content
            elif isinstance(firebase_config, dict):
                cred = credentials.Certificate(firebase_config)
            else:
                raise ValueError(
                    "Firebase config must be a dictionary or a file path string."
                )

            firebase_admin.initialize_app(cred)
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase: {e}")


def get_developers() -> list[dict]:
    """
    Fetches the list of all registered developers from the Firestore database.
    Each developer document is expected to have 'name', 'email', 'github',
    'interests', and 'skills' fields. Default empty lists are provided for
    'interests' and 'skills' if they are missing from a document.

    Returns:
        A list of developer dictionaries.
    """
    db = firestore.client()
    developers_ref = db.collection("developers")
    docs = developers_ref.stream()

    devs = []
    for doc in docs:
        dev_data = doc.to_dict()
        # Ensure all required keys exist, providing defaults for optional ones
        dev_data["interests"] = dev_data.get("interests", [])
        dev_data["skills"] = dev_data.get("skills", [])

        if all(key in dev_data for key in ["name", "email", "github"]):
            devs.append(dev_data)
        else:
            # Log a warning if a document is missing essential data, but don't crash
            print(f"Warning: Skipping malformed developer document: {dev_data}")

    return devs


def add_developer(
    name: str, email: str, github: str, interests: list = None, skills: list = None
):
    """
    Adds a new developer to the Firestore database. The email is used as the
    document ID to ensure uniqueness.

    Args:
        name: The full name of the new developer.
        email: The email address of the new developer (used as document ID).
        github: The GitHub username of the new developer.
        interests: An optional list of programming interests (e.g., ['Web Dev', 'AI/ML']).
        skills: An optional list of programming skills (e.g., ['Python', 'JavaScript']).
    """
    db = firestore.client()
    developers_ref = db.collection("developers")

    new_developer_data = {
        "name": name,
        "email": email,
        "github": github,
        "interests": interests if interests is not None else [],
        "skills": skills if skills is not None else [],
    }

    # Set the document with the email as the ID. This will overwrite if email already exists.
    developers_ref.document(email).set(new_developer_data)


def get_timetable() -> list[dict]:
    """
    Fetches all timetable entries from the Firestore database.

    Returns:
        A list of timetable entry dictionaries.
    """
    db = firestore.client()
    timetable_ref = db.collection("timetable")
    docs = timetable_ref.stream()

    entries = []
    for doc in docs:
        entries.append(doc.to_dict())

    # Optional: You might want to sort these entries here for consistent display
    # For example, by day of the week, then by time. This would require parsing
    # the 'day' and 'time_range' fields into a sortable format.

    return entries


def add_timetable_entry(entry_data: dict):
    """
    Adds a new timetable entry to the Firestore database. Firestore will
    automatically generate a unique ID for this document.

    Args:
        entry_data: A dictionary containing the timetable entry data.
                    Expected keys: 'day', 'time_range', 'course_code', 'venue', 'details'.
    """
    db = firestore.client()
    timetable_ref = db.collection("timetable")

    # Using .add() will automatically create a document with a unique ID
    timetable_ref.add(entry_data)
