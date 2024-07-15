import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

    # Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(
            os.path.join(working_dir, token_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION,
                        credentials=creds, static_discovery=False)
        # print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None


def getAlbumList(service):
    print("Downloading album list...")
    response = service.albums().list(pageSize=25).execute()
    albums = response["albums"]
    nextPageToken = response.get("nextPageToken")

    while nextPageToken:
        response = service.albums().list(pageToken=nextPageToken).execute()
        albums.extend(response["albums"])
        nextPageToken = response.get("nextPageToken")

    for album in albums:
        album["mediaItemsCount"] = int(album["mediaItemsCount"])

    sortedAlbums = sorted(
        albums, key=lambda d: d['mediaItemsCount'], reverse=True)

    print("Album list downloaded.")
    return sortedAlbums


def getImagesInAGivenAlbum_sync(service, album):
    print("Album \"" + album["title"] +
          "\": Downlading images' data...")

    searchbody = {
        "albumId": album["id"],
        "pageSize": 100,
    }

    response = service.mediaItems().search(body=searchbody).execute()
    mediaItemsInAlbums = response["mediaItems"]
    nextPageToken = response.get("nextPageToken")

    searchbody = {
        "albumId": album["id"],
        "pageSize": 100,
        "pageToken": nextPageToken
    }

    while nextPageToken:
        response = service.mediaItems().search(body=searchbody).execute()
        mediaItemsInAlbums.extend(response["mediaItems"])
        nextPageToken = response.get("nextPageToken")
        searchbody["pageToken"] = nextPageToken

    print("Album \"" + album["title"] + "\": " +
          str(len(mediaItemsInAlbums)) + " image data downloaded.")
    return mediaItemsInAlbums


async def getImagesInAGivenAlbum(album, executor):
    client_secret_file = "OAuth Client.json"
    API_NAME = "photoslibrary"
    API_VERSION = "v1"
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary",
              "https://www.googleapis.com/auth/photoslibrary.sharing"]
    service = create_service(
        client_secret_file, API_NAME, API_VERSION, SCOPES)
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(executor, getImagesInAGivenAlbum_sync, service, album)


def getAll_sync(service):
    print("Downloading all images' data...")
    response = service.mediaItems().list(pageSize=100).execute()
    mediaItems = response["mediaItems"]
    nextPageToken = response.get("nextPageToken")

    while nextPageToken:
        response = service.mediaItems().list(
            pageSize=100, pageToken=nextPageToken).execute()
        mediaItems.extend(response["mediaItems"])
        nextPageToken = response.get("nextPageToken")

    print("Downloaded all images' data.")
    return mediaItems


async def getAll(executor):
    client_secret_file = "OAuth Client.json"
    API_NAME = "photoslibrary"
    API_VERSION = "v1"
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary",
              "https://www.googleapis.com/auth/photoslibrary.sharing"]
    service = create_service(
        client_secret_file, API_NAME, API_VERSION, SCOPES)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, getAll_sync, service)


async def getAllImages(albumList):
    # Adjust the number of workers as needed
    executor = ThreadPoolExecutor(max_workers=len(albumList) + 1)
    tasks = []
    tasks.append(asyncio.create_task(getAll(executor)))
    for album in albumList:
        tasks.append(asyncio.create_task(
            getImagesInAGivenAlbum(album, executor)))

    results = await asyncio.gather(*tasks)
    executor.shutdown(wait=True)
    imagesInAlbums = []

    for i in range(1, len(results)):
        imagesInAlbums.extend(results[i])

    return results[0], imagesInAlbums


async def main():
    client_secret_file = "OAuth Client.json"
    API_NAME = "photoslibrary"
    API_VERSION = "v1"
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary",
              "https://www.googleapis.com/auth/photoslibrary.sharing"]
    main_service = create_service(
        client_secret_file, API_NAME, API_VERSION, SCOPES)

    #######################################################################################

    albums = getAlbumList(service=main_service)

    allImages, imagesInAlbums = await getAllImages(albums)

    imageIdsInAlbums = {image["id"] for image in imagesInAlbums}

    print("Writing URLs for photos which are not in an album nor archived...")
    with open('Images not in albums.txt', 'w') as f:
        for image in allImages:
            if image["id"] not in imageIdsInAlbums:
                print(image["productUrl"], file=f)

    print("Done, see \"Images not in albums\".txt at the same path as this program.")

asyncio.run(main())
