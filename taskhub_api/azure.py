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
account_url = "https://taskhubtktest.blob.core.windows.net"

# Container Name Constants
PFP_CONTAINER_NAME = 'pfp'
XXXXXX_CONTAINER_NAME = 'XXXXXX'


def upload_profile_picture(file_name, content):
    """
    Uploads a profile picture to Azure Blob Storage
    :param file_name: the name of the file in azure storage
    :param content: base64 encoded content of the file
    :return: None
    :raises: Exception
    """
    __upload_file__(__authenticate_blob_client__(), __get_container_name__('pfp'), file_name, content)


def __authenticate_blob_client__():
    """
    Authenticates the blob client with DefaultAzureCredential
    :return: BlobServiceClient
    """
    return BlobServiceClient(account_url, credential=DefaultAzureCredential())


def __get_container_name__(str_input):
    """
    Matches the string input to a concrete container name
    :param str_input: the string input to match
    :return: the container name
    :raises: Exception
    """
    match str_input:
        case 'pfp':
            return PFP_CONTAINER_NAME
        case 'XXXXXX':
            return XXXXXX_CONTAINER_NAME
        case _:
            raise Exception("Invalid container name")


# Create a blob client using the local file name as the name for the blob
def __upload_file__(blob_service_client, container, file_name, content):
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
    print("\nUploading to Azure Storage as blob:\n\t" + file_name)
