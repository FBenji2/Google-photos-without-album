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
    response = service.albums().list(pageSize=25).execute()
    albums = response["albums"]
    nextPageToken = response.get("nextPageToken")
    page = 1
    while nextPageToken:
        page += 1
        print(str(page) + " Fetching next page...")
        response = service.albums().list(pageToken=nextPageToken).execute()
        albums.extend(response["albums"])
        nextPageToken = response.get("nextPageToken")

    return albums


def getImagesInAGivenAlbum_sync(service, album):
    mediaItemsInAlbums = []
    page = 1
    searchbody = {
        "albumId": album["id"],
        "pageSize": 100,
    }
    response = service.mediaItems().search(body=searchbody).execute()
    mediaItemsInAlbums.extend(response["mediaItems"])
    nextPageToken = response.get("nextPageToken")
    searchbody = {
        "albumId": album["id"],
        "pageSize": 100,
        "pageToken": nextPageToken
    }

    while nextPageToken:
        page += 1
        response = service.mediaItems().search(body=searchbody).execute()
        mediaItemsInAlbums.extend(response["mediaItems"])
        nextPageToken = response.get("nextPageToken")
        searchbody["pageToken"] = nextPageToken

    for i in range(len(mediaItemsInAlbums)):
        mediaItemsInAlbums[i] = mediaItemsInAlbums[i]["id"]

    print(album["title"] + ": " +
          str(len(mediaItemsInAlbums)) + " Image ids downloaded")
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


async def getImagesInAllAlbums(albumList):
    # Adjust the number of workers as needed
    executor = ThreadPoolExecutor(max_workers=len(albumList))
    tasks = []
    for album in albumList:
        tasks.append(asyncio.create_task(
            getImagesInAGivenAlbum(album, executor)))

    results = await asyncio.gather(*tasks)
    executor.shutdown(wait=True)
    imagesInAllAlbums = []
    for result in results:
        imagesInAllAlbums += result
    print("-------------------------------------------------------------------")
    return imagesInAllAlbums


async def main():
    client_secret_file = "OAuth Client.json"
    API_NAME = "photoslibrary"
    API_VERSION = "v1"
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary",
              "https://www.googleapis.com/auth/photoslibrary.sharing"]
    main_service = create_service(
        client_secret_file, API_NAME, API_VERSION, SCOPES)

    #######################################################################################

    mediaItemsNotInAlbums = []

    albums = getAlbumList(service=main_service)
    imagesInAllAlbums = await getImagesInAllAlbums(albums)

    print("An image exists in multiple albums: " +
          str(len(imagesInAllAlbums) != len(set(imagesInAllAlbums))))

    if len(imagesInAllAlbums) != len(set(imagesInAllAlbums)):
        print("Removing duplicate IDs... (this does not delete any images)")
        imagesInAllAlbums = list(set(imagesInAllAlbums))
    print("Total number of images in albums: " + str(len(imagesInAllAlbums)))
    print("Fetching all images to compare with list of images in albums...")

    response = main_service.mediaItems().list(pageSize=100).execute()
    mediaItems = response["mediaItems"]
    nextPageToken = response.get("nextPageToken")

    for mediaItem in mediaItems:
        if mediaItem["id"] not in imagesInAllAlbums:
            mediaItemsNotInAlbums.append(mediaItem["productUrl"])

    page = 1
    while nextPageToken:
        page += 1
        response = main_service.mediaItems().list(
            pageSize=100, pageToken=nextPageToken).execute()
        mediaItems = response["mediaItems"]
        nextPageToken = response.get("nextPageToken")

        for mediaItem in mediaItems:
            if mediaItem["id"] not in imagesInAllAlbums:
                mediaItemsNotInAlbums.append(mediaItem["productUrl"])

    print("Number of images not in albums: " + str(len(mediaItemsNotInAlbums)))

    with open('Images not in albums.txt', 'w') as f:
        for mediaItemNotInAlbums in mediaItemsNotInAlbums:
            print(mediaItemNotInAlbums, file=f)

asyncio.run(main())

# TODO make the "getting all images" part async and quick as well
