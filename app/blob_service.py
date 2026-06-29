from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

def get_blob_service_client():
    return BlobServiceClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    )

def get_container_client():
    container = get_blob_service_client().get_container_client(
        os.getenv("AZURE_STORAGE_CONTAINER")
    )
    try:
        container.create_container()
    except Exception:
        pass
    return container

def upload_pdf(content: bytes, filename: str):
    container = get_container_client()
    container.upload_blob(name=filename, data=content, overwrite=True)

def get_blob_url(filename: str) -> str:
    """Returns a SAS-signed URL valid for 1 hour so external Azure services
    (like Document Intelligence) can read the blob."""
    blob_service_client = get_blob_service_client()
    account_name = blob_service_client.account_name
    container_name = os.getenv("AZURE_STORAGE_CONTAINER")

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=filename,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    blob_client = get_container_client().get_blob_client(filename)
    return f"{blob_client.url}?{sas_token}"