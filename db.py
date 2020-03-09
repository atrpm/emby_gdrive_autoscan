from peewee import Model, SqliteDatabase, CharField, BooleanField, OperationalError, IntegrityError

database = SqliteDatabase("files.db")

class FileModel(Model):
    fileId = CharField(max_length=256, unique=True, null=False, primary_key=True)
    path = CharField(max_length=256, unique=False, null=False)
    removed = BooleanField

    class Meta:
        database = database

class FolderModel(Model):
    fileId = CharField(max_length=256, unique=True, null=False, primary_key=True)
    name = CharField(max_length=256, unique=False, null=False)

    class Meta:
        database = database

class DriveModel(Model):
    driveId = CharField(max_length=256, unique=True, null=False, primary_key=True)
    nextPageToken = CharField(max_length=256, unique=False, null=True)

    class Meta:
        database = database

def createDb():
    try:
        FileModel.create_table()
        FolderModel.create_table()
        DriveModel.create_table()
    except OperationalError:
        print('File table already exists')

def getDrive(driveId):
    createDb()
    return DriveModel.get_or_create(driveId = driveId)[0]

def saveDriveInfo(driveId, nextPageToken):
    drive = getDrive(driveId)
    drive.nextPageToken = nextPageToken
    drive.save()

def saveFileChange(change):
    file = FileModel.get_or_none(FileModel.fileId == change.get('fileId'))
    if file:
        if change.get('path'):
            file.path = change.get('path')
        file.removed = change.get('removed')
        file.save()
        return createEmbyChangeFromFile(file)
    else:
        if change.get('path'):
            file = FileModel(**change)
            file.save()
            return createEmbyChangeFromFile(file)

def saveFolderInfo(folderInfo):
    createDb()
    folder = FolderModel.get_or_none(FolderModel.fileId == folderInfo.get('id'))
    if folder:
        folder.name = folderInfo.get('name')
        folder.save()
    else:
        folder = FolderModel(**folderInfo)
        folder.save()
        
def getFolderName(folderId):
    folder = FolderModel.get_or_none(FolderModel.fileId == folderId)
    if folder:
        return folder.name
    return folder
    
def createEmbyChangeFromFile(file):
    #Create emby change for file
    embyChange = {}
    embyChange['Path'] = file.path
    embyChange['UpdateType'] = 'Created'
    if file.removed:
        embyChange['UpdateType'] = 'Modified'

    return embyChange

