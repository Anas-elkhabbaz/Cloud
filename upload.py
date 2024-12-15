import os
import streamlit as st
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename

# Configuration
connection_string = "DefaultEndpointsProtocol=https;AccountName=blobscan1;AccountKey=X6mTfjDomZS4Iptfowl0Cp00jRdCdVX9h6SjmmXNorEDHHpPnxOWNkTUlaLlTBp9JRskaLRctqOq+AStQtlpnQ==;EndpointSuffix=core.windows.net"
container_name = "ocr"  # Replace with your Blob container name

# Function to upload an image to Azure Blob Storage
def upload_to_blob(uploaded_file):
    try:
        # Create a BlobServiceClient to interact with the Blob service
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a secure filename to avoid conflicts
        filename = secure_filename(uploaded_file.name)

        # Create a BlobClient to upload the image to a container
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

        # Upload the file to Azure Blob Storage
        with uploaded_file:
            blob_client.upload_blob(uploaded_file, overwrite=True)

        return f"File {filename} uploaded successfully to Blob Storage."

    except Exception as e:
        return f"Error uploading file: {str(e)}"


# Streamlit Interface
st.title("Upload Image to Azure Blob Storage")
st.write("Upload an image to store it in Azure Blob Storage.")

# File uploader widget
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image in the app for preview
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Upload the image to Blob Storage
    with st.spinner("Uploading to Blob Storage..."):
        result = upload_to_blob(uploaded_file)
        st.success(result)
