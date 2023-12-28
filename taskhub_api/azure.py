import os, uuid, base64
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


"""
Example Usage
    File Upload starting in views.py
    from . import azure
    c = request.FILES.get("profile_image").read()
    azure.upload_profile_picture(user.username, c)
    


"""

# Storage Account Location
ACCOUNT_URL = "https://taskhub.blob.core.windows.net"
CONST_BLOB_CLIENT = None

# Container Name Constants
PFP_CONTAINER_NAME = 'pfp'
TASK_IMAGES_CONTAINER_NAME = 'task-images'


def upload_profile_picture(file_name, content) -> None:
    """
    Uploads a profile picture to Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :param content: base64 encoded content of the file
    :return: None
    :raises: Exception
    """
    __upload_file(__authenticate_blob_client(), __get_container_name('pfp'), file_name, content)


def download_profile_picture(file_name) -> bytes:
    """
    Downloads a profile picture from Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :return: the content of the file as string
    :raises: Exception
    """
    return __download_file(__authenticate_blob_client(), __get_container_name('pfp'), file_name)


def delete_profile_picture(file_name) -> None:
    """
    Deletes a profile picture from Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :return: None
    :raises: Exception
    """
    __delete_blob(__authenticate_blob_client(), __get_container_name('pfp'), file_name)


def upload_task_image(file_name, content) -> None:
    """
    Uploads a profile picture to Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :param content: base64 encoded content of the file
    :return: None
    :raises: Exception
    """
    __upload_file(__authenticate_blob_client(), __get_container_name('task-images'), file_name, content)


def download_task_image(file_name) -> bytes:
    """
    Downloads a profile picture from Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :return: the content of the file as string
    :raises: Exception
    """
    return __download_file(__authenticate_blob_client(), __get_container_name('task-images'), file_name)


def delete_task_image(file_name) -> None:
    """
    Deletes a profile picture from Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :return: None
    :raises: Exception
    """
    __delete_blob(__authenticate_blob_client(), __get_container_name('task-images'), file_name)


def __authenticate_blob_client() -> BlobServiceClient:
    """
    Authenticates the blob client with DefaultAzureCredential
    :return: BlobServiceClient
    :raises: Exception
    """
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=DefaultAzureCredential())


def __get_container_name(str_input: str) -> str:
    """
    Matches the string input to a concrete container name
    :param str_input: the string input to match
    :return: the container name
    :raises: Exception
    """
    match str_input:
        case 'pfp':
            return PFP_CONTAINER_NAME
        case 'task-images':
            return TASK_IMAGES_CONTAINER_NAME
        case _:
            raise Exception("Invalid container name")


# Create a blob client using the local file name as the name for the blob
def __upload_file(blob_service_client: BlobServiceClient, container: str, file_name: str, content: bytes) -> None:
    """
    Uploads a file to Azure Blob Storage
    :param blob_service_client: the client to use
    :param container: the sub-container to upload to
    :param file_name: the name of the file in azure storage
    :param content: base64 encoded content of the file
    :return: None
    :raises: Exception
    """
    blob_client = blob_service_client.get_blob_client(container=container, blob=file_name)
    blob_client.upload_blob(content, blob_type="BlockBlob")
    print("Successfully uploaded blob: " + file_name)


def __download_file(blob_service_client: BlobServiceClient, container: str, file_name: str) -> bytes:
    """
    Downloads a file from Azure Blob Storage
    :param blob_service_client: the client to use
    :param container: the sub-container to download from
    :param file_name: the name of the file in azure storage
    :return: the content of the file as string
    :raises: Exception
    """
    blob_client = blob_service_client.get_blob_client(container=container, blob=file_name)
    downloader = blob_client.download_blob(max_concurrency=1)
    blob_content = downloader.readall()
    print('Successfully downloaded blob to text: ' + file_name)
    return blob_content


def __delete_blob(blob_service_client: BlobServiceClient, container: str, file_name: str) -> None:
    """
    Deletes a blob from Azure Blob Storage
    :param blob_service_client: the client to use
    :param container: the sub-container to delete from
    :param file_name: the name of the file in azure storage
    :return: None
    """
    blob_client = blob_service_client.get_blob_client(container=container, blob=file_name)
    blob_client.delete_blob()
    print("Successfully deleted blob: " + file_name)
