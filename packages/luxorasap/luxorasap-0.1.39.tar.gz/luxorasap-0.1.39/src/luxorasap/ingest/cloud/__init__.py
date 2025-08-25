"""Camada moderna de ingestão: grava / incrementa tabelas em ADLS (Parquet)."""

import pandas as pd
import datetime as dt
import numpy as np

from luxorasap.utils.storage import BlobParquetClient, BlobExcelClient, BlobPickleClient
from luxorasap.utils.dataframe import prep_for_save, astype_str_inplace
from luxorasap.datareader import LuxorQuery


__all__ = ["save_table", "incremental_load"]

_client = BlobParquetClient()   # instância única para o módulo
_client_excel = None
_client_pickle = None


# ────────────────────────────────────────────────────────────────
def save_table(
    table_name: str,
    df,
    *,
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
    override=False,
    format='parquet'
):
    """Salva DataFrame como Parquet em ADLS (sobrescrevendo)."""
    
    if 'Last_Updated' not in df.columns:
        df['Last_Updated'] = dt.datetime.now()
    else:
        # usando numpy, vamos substituir NaN ou 'nan' pela data e hora de agora
        df["Last_Updated"] = np.where(((df["Last_Updated"].isna()) | (df["Last_Updated"] == 'nan')),
                                      dt.datetime.now(),
                                      df["Last_Updated"]
                                      )    
    
    if override == False:
        lq = LuxorQuery()
        if lq.table_exists(table_name):
            return
    
    df = prep_for_save(df, index=index, index_name=index_name, normalize=normalize_columns)
    
    if format == 'parquet':
        #_client.write_df(df.astype(str), f"{directory}/{table_name}.parquet")
        astype_str_inplace(df)
        _client.write_df(df, f"{directory}/{table_name}.parquet")
    
    elif format == 'excel':
        global _client_excel
        if _client_excel is None:
            _client_excel = BlobExcelClient()
        if index:
            df = df.reset_index().rename(columns={"index": index_name})
        _client_excel.write_excel(df, f"{directory}/{table_name}.xlsx")
    
    elif format == 'pickle':
        global _client_pickle
        if _client_pickle is None:
            _client_pickle = BlobPickleClient()
        _client_pickle.write_pickle(df, f"{directory}/{table_name}.pkl")
    
    else:
        raise ValueError(f"Formato '{format}' não suportado. Use 'parquet', 'excel' ou 'pickle'.")



def incremental_load(
    lq: LuxorQuery,
    table_name: str,
    df,
    *,
    increment_column: str = "Date",
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
    unique_columns: list = None
):
    """Concatena novos dados aos existentes, cortando duplicados pela data."""
    df["Last_Updated"] = dt.datetime.now()
    
    if lq.table_exists(table_name):
        prev = lq.get_table(table_name)
        if increment_column is not None:
            if increment_column not in df.columns:
                raise ValueError(f"Coluna de incremento '{increment_column}' não existe no DataFrame.")
            cutoff = df[increment_column].max()
            prev = prev.query(f"{increment_column} < @cutoff")
        df = pd.concat([prev, df], ignore_index=True)
        # remover duplicados
    
    if unique_columns is not None:
        df = df.drop_duplicates(subset=unique_columns, keep='last')

    save_table(
        table_name,
        df,
        index=index,
        index_name=index_name,
        normalize_columns=normalize_columns,
        directory=directory,
        override=True
    )