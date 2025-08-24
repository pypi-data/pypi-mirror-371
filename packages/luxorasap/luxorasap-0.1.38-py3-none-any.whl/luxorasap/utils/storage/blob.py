import io, os
from pathlib import PurePosixPath
from datetime import timezone
import pandas as pd
import pyarrow as pa, pyarrow.parquet as pq
from azure.storage.blob import BlobServiceClient
import pickle

from ..dataframe import read_bytes


class BlobParquetClient:
    """Leitura/gravacao de Parquet em Azure Blob – stateless & reutilizável."""

    def __init__(self, container: str = "luxorasap", adls_connection_string: str = None):
        if adls_connection_string is None:
            adls_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
        self._svc = BlobServiceClient.from_connection_string(adls_connection_string)
        self._container = container

    # ---------- API pública ----------
    def read_df(self, blob_path: str) -> (pd.DataFrame, bool):
        buf = io.BytesIO()
        try:
            self._blob(blob_path).download_blob().readinto(buf)
            return (
                read_bytes(buf.getvalue(), filename=PurePosixPath(blob_path).name),
                True,
            )
        except Exception:
            return None, False
            

    def write_df(self, df, blob_path: str):
        
        blob = self._blob(blob_path)
        table = pa.Table.from_pandas(df)
        buf = io.BytesIO()
        pq.write_table(table, buf)
        buf.seek(0)
        blob.upload_blob(buf, overwrite=True)
            
        
    def get_df_update_time(self, blob_path: str) -> float:
        try:
            properties = self._blob(blob_path).get_blob_properties()
            return properties['last_modified'].replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            return 0.0
    
    
    def exists_df(self, blob_path: str) -> bool:
        try:
            self._blob(blob_path).get_blob_properties()
            return True
        except Exception:
            return False


    def list_blob_files(self, blob_path: str, ends_with: str = None) -> list:
        """
        Lista os arquivos em um diretório do blob storage.

        Args:
            blob_path (str): O caminho do diretório no blob storage.
            ends_with (str, optional): Filtra os arquivos que terminam com esta string.(Ex.: '.parquet')

        Returns:
            list: Uma lista de nomes de blob.
            
        """
        try:
            container_client = self._svc.get_container_client(self._container)
            blob_list = container_client.list_blobs(name_starts_with=blob_path)
            if ends_with:
                return [blob.name for blob in blob_list if blob.name.endswith(ends_with)]
            return [blob.name for blob in blob_list]
        except Exception:
            return []
            

    def table_exists(self, table_path: str) -> bool:
        """
            Checa se uma tabela existe no blob storage.
        """
        return self.exists_df(table_path)
    
    
    # ---------- interno --------------
    def _blob(self, path: str):
        path = str(PurePosixPath(path))
        return self._svc.get_blob_client(self._container, path)
    

class BlobPickleClient:
    def __init__(self, *, adls_connection_string: str = None, container: str = "luxorasap"):
        if adls_connection_string is None:
            adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            
        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(adls_connection_string)
        self.container_client = self.blob_service_client.get_container_client(container)

    def write_pickle(self, obj, blob_name: str):
        """Salva objeto Python (ex: DataFrame) como pickle no blob"""
        buf = io.BytesIO()
        pickle.dump(obj, buf)
        buf.seek(0)
        self.container_client.upload_blob(name=blob_name, data=buf, overwrite=True)

    def read_pickle(self, blob_name: str):
        """Lê pickle do blob e retorna objeto Python"""
        downloader = self.container_client.download_blob(blob_name)
        buf = io.BytesIO(downloader.readall())
        return pickle.load(buf)

    def exists(self, blob_name: str) -> bool:
        return self.container_client.get_blob_client(blob_name).exists()
    