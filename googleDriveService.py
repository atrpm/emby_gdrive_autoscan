from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import concurrent.futures
import time
from functools import reduce
import iso8601
import db

def getFile(driveService, fileId):
    time.sleep(.350)
    file = db.getFolderName(fileId)
    if file is None:
        file = driveService.files().get(fileId=fileId, supportsAllDrives=True, fields='name, id, parents').execute()
    return file

def getFoldersList(driveService, parentReferenceList, folderList):
    for parentFileId in parentReferenceList:
        parentFile = getFile(driveService, parentFileId)
        folderList.append(parentFile.get('name'))

        if parentFile.get('parents'):
            parentReferenceList2 = parentFile.get('parents')
            getFoldersList(driveService, parentReferenceList2, folderList)

def getFilePath(config, driveService, file):
    fullFilePath = ''

    parentReferenceList = file.get('parents')
    folderList = []

    getFoldersList(driveService, parentReferenceList, folderList)
    folderList.reverse()

    pathList = []
    index = 0
    for folder in folderList:
        if folder == 'Drive':
            if config['physicalDriveMountLetter']:
                pathList.append(config['physicalDriveMountLetter'] + os.path.sep)
        else:
            if config['mountPoint']:
                mountPathArray = config['mountPoint'].split('/')
                if index < len(mountPathArray):
                    if folder.lower() != str(mountPathArray[index]).lower():
                        pathList.append(folder)
                    index += 1
                else:
                    pathList.append(folder)
            else:
                pathList.append(folder)

    pathList.append(file.get('name'))
    fullFilePath = reduce(os.path.join, pathList)

    return fullFilePath

def getEmbyChange(config, change, creds):
    # Process change
    filePath = None
    file = change.get('file')
    if file:
        if '.folder' in file.get('mimeType'):
            #change is for a folder save folder info
            folderInfo = {}
            folderInfo['fileId'] = change.get('fileId')
            folderInfo['name'] = file.get('name')
            db.saveFolderInfo(folderInfo)
            return None
        else:
            driveService = driveService = build('drive', 'v3', credentials=creds)
            filePath = getFilePath(config, driveService, file)

    #Create emby change for file
    fileChange = {}
    fileChange['path'] = filePath
    fileChange['removed'] = change.get('removed')
    fileChange['fileId'] = change.get('fileId')
    
    return db.saveFileChange(fileChange)

def getEmbyChanges(config, creds, validChanges):
    embyChanges = []
    error = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futureToEmbyChange = {executor.submit(getEmbyChange, config, change, creds): change for change in validChanges}
        for future in concurrent.futures.as_completed(futureToEmbyChange):
            embyChange = futureToEmbyChange[future]
            try:
                if future.result():
                    embyChanges.append(future.result())
            except Exception as exc:
                print('%r generated an exception: %s' % (embyChange.get('name'), exc))
                error = True
                raise exc
    
    return embyChanges, error

def getCreds(config):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config['credentialsPath'], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def getChanges(config, currentPageToken):
    creds = getCreds(config)
    driveService = build('drive', 'v3', credentials=creds)
    response = driveService.changes().getStartPageToken().execute()

    if currentPageToken is None:
        currentPageToken = response.get('startPageToken')
    print (f'Current token: {currentPageToken}')

    response = driveService.changes().list(pageToken=currentPageToken, spaces='drive', 
        driveId = config['driveId'], includeItemsFromAllDrives=config['includeItemsFromAllDrives'], 
        supportsAllDrives=config['supportsAllDrives'], includeRemoved=config['includeRemoved'], 
        fields='changes(removed, fileId, file(name, parents, mimeType), time), nextPageToken, newStartPageToken', 
        pageSize=config['pageSize']).execute()

    changes = response.get('changes')
    if response.get('nextPageToken'):
        nextPageToken = response.get('nextPageToken')
    else:
        nextPageToken = response.get('newStartPageToken')

    #filter changes by date
    startDate = iso8601.parse_date(config['changesStartDate'])
    validChanges = []
    for change in changes:
        if change.get('time'):
            changeDate = iso8601.parse_date(change.get('time'))
            if startDate < changeDate:
                validChanges.append(change)
    
    if len(changes) == 0:
        print('No changes found.')
        return None, nextPageToken, False
    
    if len(validChanges) == 0:
        print('No valid changes found.')
        getChanges(config, currentPageToken)

    print(f'Found {len(validChanges)} changes')
    print('Getting changes details...')

    embyChanges, error = getEmbyChanges(config, creds, validChanges)
    updates = {}
    updates['Updates'] = embyChanges
    return updates, nextPageToken, error
