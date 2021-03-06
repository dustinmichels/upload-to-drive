# Upload to Drive

**Reusable Python script for uploading files to Google Drive.**

It will upload the given file to the specified folder. If a file with that name already exists, it will add a revision instead of a new file. This can be changed in the config section.

## Usage

```sh
python upload_to_drive.py my_data.csv
```

The first time you run you will be asked to authenticate with your Google account. Credentials will be stored here in a pickle file, so you don't have to authenticate on subsequent runs.

## Getting Setup

### Step 1: Enable Google Drive API

1. Follow the [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the) guide. Just as it tells you, press "Enable the Drive API", name your project, select "desktop app", and then download `credentials.json` and store it in this directory.

2. Once the project is created, update its "OAuth consent screen" settings on [console.cloud.google.com/apis/dashboard](https://console.cloud.google.com/apis/dashboard). Under "scopes" select:

   | API              | Scope               | User-facing description                                                                      |
   | ---------------- | ------------------- | -------------------------------------------------------------------------------------------- |
   | Google Drive API | .../auth/drive.file | View and manage Google Drive files and folders that you have opened or created with this app |

> This is a non-sensitive scope that seems to be sufficient for this script. Since it's considered "non-sensitive" the app doesn't need to be verified.
> Users can authenticate and run without seeing a "app has not been verified!" warning.

### Step 2: Install Requirements

```sh
# Google client libraries
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# colorful terminal output
pip install termcolor
```

### Step 3: Configure Options

At the top of `upload_to_drive.py` there is a config section you should fill out before running the script.

Config:

- **`DRIVE_FOLDER_ID`** - You can get the ID of a Google Drive folder from the URL. It is the 33 character string at the end of the URL.
- **`REVISE_EXISTING`** - If there is a file with the same name in the upload folder, the script will add a revision instead of uploading a new file if True. If False, will add a new file every time.
- **`MIMETYPE`** - If you are uploading the same kind of file each time you may want to specify the MIME type. Options are given [here](https://developers.google.com/drive/api/v3/ref-export-formats). Examples include `"application/json"` or `"text/csv"`. It can be left blank.
