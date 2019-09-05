# EMBY GDrive AUTOSCAN

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg?style=flat-square)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%203-blue.svg?style=flat-square)](https://github.com/atrpm/emby_gdrive_autoscan/blob/master/LICENSE.md)

---
- [Introduction](#introduction)
    - [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
---

# Introduction

Emby GDrive Autoscan is a python library that assists in notifying Emby of any changes  
that are detected from the Google Drive API.

## Notes

This has only been tested on a Windows server.

##### TODOs:
- [ ] Add logging
- [ ] Improve error handling with retries


---

### How it works

This library relies heavily on the Google Drive API to [retrieve changes](https://developers.google.com/drive/api/v3/manage-changes). It pulls changes on an interval  
that can be configure to avoid API bans.

Once the list of changes is retrieved, it gets the path for each file (this is done by  
walking back all the parent folders via the files API). After that a call is made to the  
Emby `Library/Media/Updated` API.

##### Local DB

The library uses a local DB to store important information about the drive. It stores:  
- PageToken: to know it's place on the changes stream.
- Folders info: to avoid unnecessary call to the API when possible.
- Files path: to help determine when a file is deleted from the drive.
    - File deletion: when a file is deleted from google drive the only info that we can  
    retrieve about the file is it's ID, it tries to match the ID of the deleted file in  
    the local database get the path so we can notify Emby that a file has been deleted.

# Requirements

1. Python 3.0 or higher
2. requirements.txt modules

# Installation

1. `git clone https://github.com/atrpm/emby_gdrive_autoscan` - clone repo 
2. `cd emby_gdrive_autoscan` - change directory
3. `python -m pip install -r requirements.txt` - install all requirements
4. Go to Google developers [getting started](https://developers.google.com/drive/api/v3/quickstart/go) page and follow step 1.  
Save the credentials.json file inside the emby_gdrive_autoscan directory
5. [Configure](#Configure) the config.json. (do this before moving on)
6. `python scan.py` - to run the script
7. Enjoy!

# Configuration

- General
    - `scanIntervalMinutes` - how often show scans happen
- Drives (supports multiple drives)
    - `driveId` - google drive Id
    - `currentPageToken: default = null` - the script will get the start page token  
    for the user and save the next page token after every scan. This is intended t  
    override that behavior if you know where to start from.
    - `pageSize: default = 100` - limit the change to get per scan, to avoid API ban.
    - `changesStartDate (iso8601 format)` - only care about changes after this date  
    and time.
    - `credentialsPath` - path for the credentials.json file
    - `includeItemsFromAllDrives: default - True` - Google API parameter
    - `supportsAllDrives: default = True` - Google API parameter
    - `includeRemoved: default = True` - Google API parameter
    - `physicalDriveMountLetter: default = null` - if mounted to a letter. ex. Windows X: drive
    - `mountPoint: default = null` - ex. RClone mount point of 'Media/'. null = root 
- Emby
    - `apiKey` - Emby API Key
    - `ip: default = localhost` - Emby IP
    - `port: default = 8096` - Emby Port
    - `protocol: default = http` - Emby URL protocol  
  




