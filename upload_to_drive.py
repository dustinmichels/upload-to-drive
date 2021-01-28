import os.path
import pickle
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from termcolor import colored

# ================ CONFIG ================
# ID of Google Drive folder to upload to
DRIVE_FOLDER_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# If file with given name already exists in folder,
# Add revision instead of new file.
REVISE_EXISTING = True

# MIMETYPE of file uploading (can be blank)
MIMETYPE = ""  # eg, "application/json" or "text/csv"
# =========================================


# formatting
boldify = lambda x: colored(x, attrs=["bold"])
blueify = lambda x: colored(x, "blue", attrs=["bold"])
greenify = lambda x: colored(x, "green", attrs=["bold"])
redify = lambda x: colored(x, "red", attrs=["bold"])


def prompt(text, options="y/n", default="y"):
    """
    Helper function for dealing with user prompts.
        - Prompts user for input
        - Formats the options, highlighting the default.
        - Returns the default if input is empty
    """
    options = options.replace(default, blueify(default))
    msg = f"{text} [{options}]: "
    user_input = input(msg)
    if user_input:
        return user_input
    else:
        return default


class Uploader:
    """For uploading files to Google Drive"""

    scopes = ["https://www.googleapis.com/auth/drive.file"]
    drive_folder_id = DRIVE_FOLDER_ID
    mimetype = MIMETYPE or None

    def __init__(self):
        self.service = self.get_creds()

    def get_creds(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", self.scopes
                    )
                except FileNotFoundError:
                    msg = (
                        f"\n{redify('Error!')} "
                        + "You must create a credentials.json file.\n"
                        + "  See quickstart guide: https://developers.google.com/drive/api/v3/quickstart/python\n"
                    )
                    print(msg)
                    sys.exit()
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build("drive", "v3", credentials=creds)

    def upload_to_drive(self, filename, upload_name):
        if REVISE_EXISTING:
            items = self._check_for_existing(filename, upload_name)
            if items:
                existing_item_id = items[0]["id"]
                return self._update_existing(filename, upload_name, existing_item_id)
        return self._upload_new(filename, upload_name)

    def _check_for_existing(self, filename, upload_name):
        q = f"name = '{upload_name}' and '{self.drive_folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=q, fields="files(id, name)").execute()
        items = results.get("files", [])
        return items

    def _update_existing(self, filename, upload_name, existing_item_id):
        print("\n> Updating existing file...")
        file_metadata = dict(name=upload_name)
        media = MediaFileUpload(filename, mimetype=self.mimetype)
        file = (
            self.service.files()
            .update(
                fileId=existing_item_id,
                body=file_metadata,
                media_body=media,
                fields="id",
            )
            .execute()
        )
        return file.get("id")

    def _upload_new(self, filename, upload_name):
        print("\n> Adding new file...")
        file_metadata = dict(name=upload_name, parents=[self.drive_folder_id])
        media = MediaFileUpload(filename, mimetype=self.mimetype)
        file = (
            self.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
            )
            .execute()
        )
        return file.get("id")


def upload(filename):
    """Prompt for new file name, then upload to drive"""
    try:
        default_name = filename.split("/")[-1]
    except IndexError:
        default_name = ""
    while True:
        new_name = prompt("> Upload name", options=default_name, default=default_name)
        confirm = prompt(
            f"> File will be uploaded as `{new_name}`. Okay?",
            options="y/n",
            default="y",
        )
        if confirm.lower() == "y":
            break

    # upload to drive
    uploader = Uploader()
    file_id = uploader.upload_to_drive(filename, new_name)
    if file_id:
        print(greenify("> Success.\n"))


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error! No filename given.")
        sys.exit()

    print("\n(Default option is given in blue)\n")
    confirm = prompt(
        f"> Upload `{filename}` to Google Drive?", options="y/n", default="y"
    )
    if confirm.lower() == "y":
        upload(filename)
    else:
        print(redify("Aborted.\n"))
