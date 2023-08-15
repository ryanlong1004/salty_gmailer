"""Abstracts mailing functions (ie Gmail, Yahoo, Hotmail)"""

# scopes: https://developers.google.com/identity/protocols/oauth2/scopes
# sending: https://developers.google.com/gmail/api/guides/sending

from __future__ import print_function

import base64
import json
import os.path
from email.message import EmailMessage
from enum import Enum
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.logger import get_logger

logger = get_logger(__name__, "./gmailer.log")

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    # "https://www.googleapis.com/auth/gmail.metadata",
]


class Labels(Enum):
    """represents gmail static label names"""

    CHAT = "CHAT"
    SENT = "SENT"
    INBOX = "INBOX"
    IMPORTANT = "IMPORTANT"
    TRASH = "TRASH"
    DRAFT = "DRAFT"
    SPAM = "SPAM"
    STARRED = "STARRED"
    UNREAD = "UNREAD"


class Mailer:
    """represents a mailer service"""

    def __init__(self, service=None):
        self._service = service

    @property
    def service_user(self):
        """returns service.users"""
        return self.service.users()

    @property
    def service_settings(self):
        """returns service.users.settings"""
        return self.service_user.settings()

    @property
    def service(self, **kwargs):
        """returns a bootstrapped service if one does not already exist"""
        if self._service is None:
            token_path = kwargs.get("token_path", "./creds/token.json")
            credentials_path = kwargs.get(
                "credentials_path", "./creds/credentials.json"
            )
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(credentials_path).exists():
                        raise FileNotFoundError(
                            "credentials.json is missing...  https://console.cloud.google.com"
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())

            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def modify_labels(self, messages, remove_labels=None, add_labels=None):
        """update lables for a list of messages"""
        if len(messages) == 0:
            return []
        try:
            body = {
                "ids": list(message["id"] for message in messages),
                "removeLabelIds": remove_labels if remove_labels else [],
                "addLabelIds": add_labels if add_labels else [],
            }
            getattr(self.service_user, "messages")().batchModify(
                userId="me",
                body=body,
            ).execute()
        except HttpError as error:
            logger.error("An error occurred: %s", error)
            return []

    @property
    def labels(self):
        """returns list of labels objects"""
        try:
            return (
                getattr(self.service_user, "labels")()
                .list(userId="me")
                .execute()
                .get("labels", [])
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    @property
    def filters(self):
        """returns a list of filter objects"""
        return (
            self.service.users()
            .settings()
            .filters()
            .list(userId="me")
            .execute()
            .get("filter", [])
        )

    def search(self, search_query):
        """searches all messages against Google style search query"""
        return (
            getattr(self.service_user, "messages")()
            .list(
                userId="me",
                q=" ".join(search_query),
            )
            .execute()
            .get("messages", [])
        )

    @property
    def threads(self):
        """returns a list of thread objects"""
        try:
            threads = (
                getattr(self.service_user, "threads")()
                .list(userId="me")
                .execute()
                .get("threads", [])
            )
            return (
                json.dumps(
                    self.service.users()
                    .threads()
                    .get(userId="me", id=thread["id"])
                    .execute()
                )
                for thread in threads
            )

        except HttpError as error:
            print(f"error {error}")
            return []

    @property
    def messages(self):
        """returns a list of message objects"""
        try:
            messages = (
                getattr(self.service_user, "messages")()
                .list(userId="me")
                .execute()
                .get("messages", [])
            )
            return (
                self.service.users()
                .messages()
                .get(userId="me", id=message["id"])
                .execute()
                for message in messages
            )
        except HttpError as error:
            print(f"error {error}")
            return []

    def create_draft(self):
        """Create and insert a draft email.
        Print the returned draft's message and id.
        Returns: Draft object, including draft id and message meta data.

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        # creds, _ = google.auth.default()

        try:
            # create gmail api client
            message = EmailMessage()
            assert message is not None

            message.set_content("This is automated draft mail")

            message["To"] = "hllbz86@gmail.com"
            message["From"] = "hllbz86@gmail.com"
            message["Subject"] = "Automated draft"

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"message": {"raw": encoded_message}}
            # pylint: disable=E1101
            draft = (
                self.service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )

            logger.info(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

        except HttpError as error:
            print(f"An error occurred: {error}")
            draft = None

        return draft

    def create_filter(self, name):
        """create_filter Not implemented

        Args:
            name (str): the name of the filter

        Returns:
            None:
        """
        label_name = name
        filter_content = {
            "criteria": {"from": "gsuder1@workspacesamples.dev"},
            "action": {"addLabelIds": [label_name], "removeLabelIds": ["INBOX"]},
        }

        # pylint: disable=E1101
        result = (
            self.service.users()
            .settings()
            .filters()
            .create(userId="me", body=filter_content)
            .execute()
        )
        return result.get("id")
