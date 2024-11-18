"""
Email Management API

This module provides a RESTful API for managing emails on an IMAP server.
It enables functionalities such as connecting to an email server, 
retrieving folder lists, searching for emails based on criteria, 
and deleting emails.

The API is built using FastAPI and supports the following operations:
1. Connect to an IMAP email server with provided credentials.
2. List all folders (mailboxes) in the email account.
3. Search for emails in a specified folder based on search criteria.
4. Delete emails that match the given search criteria.

## How to Use
1. Deploy the API using a FastAPI-compatible server (e.g., Uvicorn).
2. Use the defined endpoints to perform email operations.

## Endpoints
- `/connect` (POST): Connects to the email server to verify credentials.
- `/folders` (POST): Retrieves a list of folders (mailboxes).
- `/search` (POST): Searches for emails in a specified folder.
- `/delete` (POST): Deletes emails based on search criteria.

## Data Models
- `ConnectRequest`: For connection-related operations.
- `FolderRequest`: For listing folders (inherits `ConnectRequest`).
- `SearchRequest`: For searching emails (inherits `ConnectRequest` with 
additional fields for folder and criteria).
- `DeleteRequest`: For deleting emails (inherits `SearchRequest`).

## Error Handling
If an operation fails (e.g., invalid credentials or server issues), the API 
responds with appropriate HTTP status codes and error messages.

## Dependencies
- FastAPI: Framework for building the API.
- Pydantic: For request payload validation.
- imaplib: For interacting with IMAP email servers.

Author: Your Name
Date: YYYY-MM-DD
"""

import imaplib

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI()


# Define data models for API requests using Pydantic
class ConnectRequest(BaseModel):
    """
    Model for email connection request.
    """

    server: str  # IMAP server address
    username: str  # Email username
    password: str  # Email password


class FolderRequest(ConnectRequest):
    """
    Model for retrieving folder list.
    """


class SearchRequest(ConnectRequest):
    """
    Model for searching emails in a specific folder.
    """

    folder: str = "INBOX"  # Folder name to search (default: INBOX)
    criteria: str = "ALL"  # Search criteria (default: ALL emails)


class DeleteRequest(SearchRequest):
    """
    Model for deleting emails based on search criteria.
    """


# Utility Functions
def connect_to_email(server: str, username: str, password: str) -> imaplib.IMAP4_SSL:
    """
    Connects to an IMAP email server and logs in with the provided credentials.

    Args:
        server (str): IMAP server address.
        username (str): Email username.
        password (str): Email password.

    Returns:
        imaplib.IMAP4_SSL: IMAP connection object.

    Raises:
        HTTPException: If connection fails.
    """
    try:
        mail = imaplib.IMAP4_SSL(server)  # Establish secure connection
        mail.login(username, password)  # Authenticate
        return mail
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to delete emails: {e}"
        ) from e


def list_folders(mail: imaplib.IMAP4_SSL) -> list:
    """
    Retrieves a list of folders (mailboxes) from the email account.

    Args:
        mail (imaplib.IMAP4_SSL): IMAP connection object.

    Returns:
        list: List of folder names.

    Raises:
        HTTPException: If unable to fetch folders.
    """
    try:
        status, folders = mail.list()  # Fetch folders
        if status != "OK":
            raise Exception("Unable to fetch folder list.")
        return [
            folder.decode().split(' "/" ')[-1].strip('"')  # type: ignore
            for folder in folders
            if folder is not None
        ]
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to delete emails: {e}"
        ) from e


def search_emails(mail: imaplib.IMAP4_SSL, folder: str, criteria: str) -> list:
    """
    Searches for emails in a specified folder based on the given criteria.

    Args:
        mail (imaplib.IMAP4_SSL): IMAP connection object.
        folder (str): Folder to search in.
        criteria (str): IMAP search criteria.

    Returns:
        list: List of email IDs matching the criteria.

    Raises:
        HTTPException: If search fails or no emails are found.
    """
    try:
        mail.select(folder)  # Select folder
        status, messages = mail.search(None, criteria)  # Search emails
        if status != "OK":
            raise Exception("No emails found or invalid criteria.")
        return messages[0].split()  # Return list of email IDs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search emails: {e}")


def delete_emails(mail: imaplib.IMAP4_SSL, email_ids: list) -> int:
    """
    Marks emails as deleted and expunges them from the server.

    Args:
        mail (imaplib.IMAP4_SSL): IMAP connection object.
        email_ids (list): List of email IDs to delete.

    Returns:
        int: Number of deleted emails.

    Raises:
        HTTPException: If deletion fails.
    """
    try:
        for email_id in email_ids:
            mail.store(email_id, "+FLAGS", "\\Deleted")  # Mark as deleted
        mail.expunge()  # Permanently remove emails
        return len(email_ids)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to delete emails: {e}"
        ) from e


# API Endpoints
@app.post("/connect")
async def api_connect(request: ConnectRequest):
    """
    API endpoint to connect to an email server.

    Args:
        request (ConnectRequest): Connection request payload.

    Returns:
        dict: Success message.
    """
    connect_to_email(request.server, request.username, request.password)
    return {"message": "Connected successfully"}


@app.post("/folders")
async def api_list_folders(request: FolderRequest):
    """
    API endpoint to retrieve a list of folders.

    Args:
        request (FolderRequest): Folder request payload.

    Returns:
        dict: List of folders.
    """
    mail = connect_to_email(request.server, request.username, request.password)
    folders = list_folders(mail)
    mail.logout()  # Close connection
    return {"folders": folders}


@app.post("/search")
async def api_search_emails(request: SearchRequest):
    """
    API endpoint to search for emails.

    Args:
        request (SearchRequest): Search request payload.

    Returns:
        dict: List of email IDs matching the search criteria.
    """
    mail = connect_to_email(request.server, request.username, request.password)
    email_ids = search_emails(mail, request.folder, request.criteria)
    mail.logout()  # Close connection
    return {"email_ids": [id.decode() for id in email_ids]}  # Decode email IDs


@app.post("/delete")
async def api_delete_emails(request: DeleteRequest):
    """
    API endpoint to delete emails.

    Args:
        request (DeleteRequest): Delete request payload.

    Returns:
        dict: Number of emails deleted.
    """
    mail = connect_to_email(request.server, request.username, request.password)
    email_ids = search_emails(mail, request.folder, request.criteria)
    count = delete_emails(mail, email_ids)
    mail.logout()  # Close connection
    return {"deleted_count": count}
