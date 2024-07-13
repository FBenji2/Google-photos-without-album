import os
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
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None


client_secret_file = "OAuth Client.json"
API_NAME = "photoslibrary"
API_VERSION = "v1"
SCOPES = ["https://www.googleapis.com/auth/photoslibrary",
          "https://www.googleapis.com/auth/photoslibrary.sharing"]
service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)

#######################################################################################

mediaItemsInAlbums = []
mediaItemsNotInAlbums = []

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

for album in albums:
    page = 1
    searchbody = {
        "albumId": album["id"],
        "pageSize": 100,
    }
    print(album["title"] + ": " + str(page) + " Fetching first page...")
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
        print(album["title"] + ": " + str(page) + " Fetching next page...")
        response = service.mediaItems().search(body=searchbody).execute()
        mediaItemsInAlbums.extend(response["mediaItems"])
        nextPageToken = response.get("nextPageToken")
        searchbody["pageToken"] = nextPageToken
    print("-------------------------------------------")

for i in range(len(mediaItemsInAlbums)):
    mediaItemsInAlbums[i] = mediaItemsInAlbums[i]["id"]

print("An image exists in multiple albums: " +
      str(len(mediaItemsInAlbums) != len(set(mediaItemsInAlbums))))
print("Total number of images in albums: " + str(len(mediaItemsInAlbums)))


response = service.mediaItems().list(pageSize=100).execute()
mediaItems = response["mediaItems"]
nextPageToken = response.get("nextPageToken")

for mediaItem in mediaItems:
    if mediaItem["id"] not in mediaItemsInAlbums:
        mediaItemsNotInAlbums.extend(mediaItem["productUrl"])

page = 1
while nextPageToken:
    page += 1
    print(str(page) + " Fetching next page...")
    response = service.mediaItems().list(
        pageSize=100, pageToken=nextPageToken).execute()
    mediaItems = response["mediaItems"]
    nextPageToken = response.get("nextPageToken")

    for mediaItem in mediaItems:
        if mediaItem["id"] not in mediaItemsInAlbums:
            mediaItemsNotInAlbums.append(mediaItem["productUrl"])

print("Number of images not in albums: " + str(len(mediaItemsNotInAlbums)))

with open('Images not in albums.txt', 'w') as f:
    for mediaItemNotInAlbums in mediaItemsNotInAlbums:
        print(mediaItemNotInAlbums, file=f)
