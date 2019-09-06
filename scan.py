from googleDriveService import getChanges
from emby import submitMediaUpdate
import time
import json
import db

def main():
    scanIntervalMinutes = 5

    with open('configLocal.json', 'r', encoding='utf-8') as jsonConfig:
        startTime = time.time()
        configFile = json.load(jsonConfig)
        drivesConfig = configFile['drives']
        generalConfig = configFile['general']
        embyConfig = configFile['emby']

        for driveConfig in drivesConfig:
            drive = db.getDrive(driveConfig['driveId'])
            print(f'Starting scan for: {drive.driveId}')

            currentPageToken = drive.nextPageToken
            if driveConfig['currentPageToken']:
                currentPageToken = driveConfig['currentPageToken']

            embyUpdates, nextPageToken, error = getChanges(driveConfig, currentPageToken)

            if error:
                print('There was an issue with the google api... will try same change set again')
            else:
                if embyUpdates:
                    success = submitMediaUpdate(embyConfig, embyUpdates)
                    if success:
                        db.saveDriveInfo(drive.driveId, nextPageToken)
                        print (f'Updated nextPageToken to {nextPageToken}')
                    else:
                        print('There was an issue with emby... will try same change set again')

    endTime = time.time()
    totalSecs = int(endTime - startTime)
    print(f'Finished scanning for: {drive.driveId}. Took {totalSecs}secs')

    scanIntervalMinutes = generalConfig['scanIntervalMinutes']
    timeToSleep = scanIntervalMinutes * 60
    print(f'Waiting {scanIntervalMinutes} minutes before next scan')
    time.sleep(timeToSleep)

if __name__ == '__main__':
    while True:
        main()