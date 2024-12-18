import os
import streamlit as st
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
import pyodbc  # For connecting to Azure SQL Database

# Configuration pour Azure Blob Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=blobscan1;AccountKey=X6mTfjDomZS4Iptfowl0Cp00jRdCdVX9h6SjmmXNorEDHHpPnxOWNkTUlaLlTBp9JRskaLRctqOq+AStQtlpnQ==;EndpointSuffix=core.windows.net"
container_name = "ocr"  # Remplacez par le nom de votre conteneur

# Configuration pour la base de données Azure SQL
sql_connection_string = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:ocrser.database.windows.net,1433;"
    "Database=OCRDatabase1;"
    "Uid=anas;"
    "Pwd=Othmane2003;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=200;"
)

# Variable globale pour stocker le nom du fichier
global_filename = None

# Fonction pour uploader une image sur Azure Blob Storage
def upload_to_blob(uploaded_file):
    try:
        # Créer un client pour interagir avec le service Blob
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Créer un nom de fichier sécurisé pour éviter les conflits
        filename = secure_filename(uploaded_file.name)

        # Créer un BlobClient pour uploader l'image dans un conteneur
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

        # Uploader le fichier vers Azure Blob Storage
        with uploaded_file:
            blob_client.upload_blob(uploaded_file, overwrite=True)

        return filename  # Retourner le nom du blob
    except Exception as e:
        return f"Erreur lors de l'upload : {str(e)}"

# Fonction pour récupérer le texte extrait depuis Azure SQL Database
def get_extracted_text_from_db(document_id):
    try:
        # Connexion à la base de données Azure SQL
        connection = pyodbc.connect(sql_connection_string)
        cursor = connection.cursor()

        # Récupérer le texte extrait de la base de données
        cursor.execute("SELECT TextContent FROM ExtractedText WHERE DocumentID = ?", (document_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]  # Retourner le texte extrait
        else:
            return "Aucun texte trouvé pour cette image."
    except pyodbc.Error as e:
        return f"Erreur lors de la récupération du texte : {str(e)}"

# Interface Streamlit pour uploader une image
st.title("Uploader une image vers Azure Blob Storage")
st.write("Uploader une image pour la stocker dans Azure Blob Storage.")

# Widget d'upload de fichier
uploaded_file = st.file_uploader("Choisissez un fichier image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Afficher l'image téléchargée dans l'application
    st.image(uploaded_file, caption="Image téléchargée", use_column_width=True)

    # Uploader l'image vers Blob Storage
    with st.spinner("Upload vers Azure Blob Storage..."):
        global_filename = upload_to_blob(uploaded_file)
        st.success(f"Fichier {global_filename} uploadé avec succès.")

# Interface Streamlit pour récupérer le texte extrait depuis la base de données
st.title("Récupérer le texte extrait depuis la base de données")
st.write("Entrez le nom du fichier pour récupérer le texte extrait associé.")

if global_filename:
    # Bouton pour récupérer le texte
    if st.button("Afficher le texte extrait"):
        with st.spinner(f"Récupération du texte pour {global_filename}..."):
            extracted_text = get_extracted_text_from_db(global_filename)
            st.write("Texte extrait :")
            st.text_area("Texte extrait", extracted_text, height=200)
else:
    st.warning("Veuillez uploader une image pour récupérer son texte.")
