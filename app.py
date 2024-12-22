"""
Salty Gmailer API

This module provides a FastAPI application for interacting with an IMAP email server.
It includes endpoints for connecting to the server, listing folders, searching emails,
marking emails as read, deleting emails, and retrieving unread email counts by sender.

Classes:
    ConnectRequest: Pydantic model for email connection request.
    FolderRequest: Pydantic model for retrieving folder list.
    SearchRequest: Pydantic model for searching emails in a specific folder.
    UnreadCountRequest: Pydantic model for retrieving unread email count by sender.
    DeleteRequest: Pydantic model for deleting emails based on search criteria.

Functions:
    connect_to_email(server: str, username: str, password: str) -> imaplib.IMAP4_SSL:
    get_unread_emails_count_by_sender(mail: imaplib.IMAP4_SSL, folder: str = "INBOX") -> dict:
    list_folders(mail: imaplib.IMAP4_SSL) -> list:
    mark_emails_as_read(mail: imaplib.IMAP4_SSL, email_ids: list) -> int:
    search_emails(mail: imaplib.IMAP4_SSL, folder: str, criteria: str) -> list:
    delete_emails(mail: imaplib.IMAP4_SSL, email_ids: list) -> int:

API Endpoints:
    /connect (POST):
        Connects to an email server.
    /folders (POST):
        Retrieves a list of folders.
    /mark_as_read (POST):
    /search (POST):
        Searches for emails.
    /delete (POST):
        Deletes emails.
    /unread_count_by_sender (POST):
        Retrieves the count of unread emails from each sender.
"""

import imaplib

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI(
    title="Salty Gmailer API",
    summary="Salty Gmailer is a FastAPI-based project designed to interact with Gmail using a salty approach. This project aims to provide a unique and efficient way to manage your Gmail account.",
    version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Ryan Long",
        "url": "https://rlong.dev",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/mit",
    },)


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

    folder: str = "INBOX"


class SearchRequest(ConnectRequest):
    """
    Model for searching emails in a specific folder.
    """

    folder: str = "INBOX"  # Folder name to search (default: INBOX)
    criteria: str = "ALL"  # Search criteria (default: ALL emails)


class UnreadCountRequest(ConnectRequest):
    """
    Model for retrieving unread email count by sender.
    """

    folder: str = "INBOX"  # Folder name to search (default: INBOX)


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


def get_unread_emails_count_by_sender(
    mail: imaplib.IMAP4_SSL, folder: str = "INBOX"
) -> dict:
    """
    Retrieves the count of unread emails from each sender in the specified folder.

    Args:
        mail (imaplib.IMAP4_SSL): IMAP connection object.
        folder (str): Folder to search in (default: INBOX).

    Returns:
        dict: Dictionary with sender email as key and count of unread emails as value.

    Raises:
        HTTPException: If search fails.
    """
    try:
        mail.select(folder)  # Select folder
        status, messages = mail.search(None, "UNSEEN")  # Search for unread emails
        if status != "OK":
            raise Exception("Failed to search for unread emails.")

        unread_emails = messages[0].split()
        sender_count = {}

        for email_id in unread_emails:
            status, data = mail.fetch(email_id, "(BODY[HEADER.FIELDS (FROM)])")
            if status != "OK":
                raise Exception("Failed to fetch email headers.")

            sender = data[0][1].decode().strip().split(": ")[1] # type: ignore
            if sender in sender_count:
                sender_count[sender] += 1
            else:
                sender_count[sender] = 1

        return sender_count
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get unread emails count by sender: {e}"
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
            status_code=400, detail=f"Failed to list folders: {e}"
        ) from e


def mark_emails_as_read(mail: imaplib.IMAP4_SSL, email_ids: list) -> int:
    """
    Marks emails as read.

    Args:
        mail (imaplib.IMAP4_SSL): IMAP connection object.
        email_ids (list): List of email IDs to mark as read.

    Returns:
        int: Number of emails marked as read.

    Raises:
        HTTPException: If marking as read fails.
    """
    try:
        for email_id in email_ids:
            mail.store(email_id, "+FLAGS", "\\Seen")  # Mark as read
        return len(email_ids)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to mark emails as read: {e}"
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


@app.post("/mark_as_read")
async def api_mark_emails_as_read(request: SearchRequest):
    """
    API endpoint to mark emails as read.

    Args:
        request (SearchRequest): Mark as read request payload.

    Returns:
        dict: Number of emails marked as read.
    """
    mail = connect_to_email(request.server, request.username, request.password)
    email_ids = search_emails(mail, request.folder, request.criteria)
    count = mark_emails_as_read(mail, email_ids)
    mail.logout()  # Close connection
    return {"marked_as_read_count": count}


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


@app.post("/unread_count_by_sender")
async def api_get_unread_emails_count_by_sender(request: FolderRequest):
    """
    API endpoint to get the count of unread emails from each sender.

    Args:
        request (FolderRequest): Folder request payload.

    Returns:
        dict: Dictionary with sender email as key and count of unread emails as value.
    """
    mail = connect_to_email(request.server, request.username, request.password)
    unread_count = get_unread_emails_count_by_sender(mail, request.folder)
    mail.logout()  # Close connection
    return {"unread_count_by_sender": unread_count}
