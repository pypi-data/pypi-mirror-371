from typing import List, Dict, Optional, Any
import re
import logging
from pyspark.sql import DataFrame, functions as F
from logging_metrics import configure_basic_logging
from pyspark.sql.types import IntegerType, DoubleType, StringType, BooleanType

__all__ = [
    "apply_schema",
    "cast_columns_types_by_schema",
    "validate_dataframe_schema",
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def apply_schema(df: DataFrame, schema: Dict[str, Any], log: Optional[logging.Logger] = None) -> DataFrame:
    """Applies a schema by selecting and casting columns.

    This function:
      1. Selects only columns defined in `schema["columns"]`.
      2. Casts column types as defined in schema.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key containing a list of:
            - "column_name": Name of the column.
            - "data_type": Target type (string, int, date, etc.).

    Returns:
        DataFrame: DataFrame with selected and casted columns.
    """
    logger = log or get_logger()
    logger.info("Applying schema to DataFrame.")

    columns = [col["column_name"] for col in schema["columns"]]
    df = df.select(*columns)

    return cast_columns_types_by_schema(
        df,
        schema_list=schema["columns"],
        empty_to_null=True,
        logger=logger
    )


def cast_columns_types_by_schema(
    df: DataFrame, 
    schema_list: List[Dict[str, str]], 
    empty_to_null: bool = False, 
    truncate_strings: bool = False, 
    max_string_length: int = 16382,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Converte colunas para os tipos especificados no schema.
    
    Args:
        df: DataFrame de entrada
        schema_list: Lista de dicionários com 'column_name' e 'data_type'
        empty_to_null: Converter strings vazias para null
        truncate_strings: Truncar strings longas
        max_string_length: Tamanho máximo para strings
        logger: Logger opcional
        
    Returns:
        DataFrame com colunas convertidas
    """
    if logger is None:
        logger = get_logger()
        
    if df is None or not schema_list:
        raise ValueError("DataFrame e schema não podem ser nulos ou vazios")
    
    result_df = df
    
    for column in schema_list:
        column_name = column['column_name']
        data_type = column['data_type'].lower()
        
        # Verifica se a coluna existe no DataFrame
        if column_name not in result_df.columns:
            logger.warning(f"Coluna {column_name} não encontrada no DataFrame. Pulando.")
            continue
            
        logger.debug(f"Convertendo coluna {column_name} para tipo {data_type}")
        
        try:
            # Integer
            if re.match(r'int(eger)?(?!.*big)', data_type):
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(IntegerType()))
                
            # Boolean
            elif 'bool' in data_type:
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(BooleanType()))
                
            # Numeric/Float types
            elif any(t in data_type for t in ['numeric', 'decimal', 'double', 'float', 'real', 'money', 'currency']):
                result_df = result_df.withColumn(column_name, F.col(column_name).cast(DoubleType()))
                
            # Date
            elif data_type == 'date':
                result_df = result_df.withColumn(column_name, F.to_date(F.col(column_name)))
                
            # Timestamp/Datetime
            elif data_type == 'datetime' or 'timestamp' in data_type:
                # Tenta vários formatos comuns
                result_df = result_df.withColumn(
                    column_name, 
                    F.coalesce(
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"),
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd HH:mm:ss.SSS"),
                        F.to_timestamp(F.col(column_name), "yyyy-MM-dd HH:mm:ss"),
                        F.to_timestamp(F.col(column_name))
                    )
                )
                
            # Complex types - skip
            elif data_type in ['struct', 'array', 'map']:
                logger.debug(f"Tipo complexo {data_type} para coluna {column_name}: mantendo como está")
                continue
                
            # String (default)
            else:
                result_df = result_df.withColumn(column_name, F.trim(F.col(column_name).cast(StringType())))
                
                # Limpa caracteres problemáticos
                result_df = result_df.withColumn(
                    column_name, 
                    F.regexp_replace(F.col(column_name), "[\\r\\n\\t]", ' ')
                )
                
            # Trunca strings longas se solicitado
            if truncate_strings:
                result_df = result_df.withColumn(
                column_name, 
                F.substring(F.col(column_name), 1, max_string_length)
            )
                    
            # Converte strings vazias para null
            if empty_to_null:
                result_df = result_df.withColumn(
                column_name, 
                F.when(F.trim(F.col(column_name)) == "", None).otherwise(F.col(column_name))
            )
        
        except Exception as e:
            logger.error(f"Erro ao converter coluna {column_name}: {str(e)}")
            # Continua com outras colunas em caso de erro
    
    return result_df


def validate_dataframe_schema(df: DataFrame, schema: Dict[str, Any]) -> bool:
    """Validates that all columns defined in the schema exist in the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key and list of:
            - "column_name": Column to validate.

    Returns:
        bool: True if all schema columns exist in DataFrame, False otherwise.
    """
    expected_cols = {col["column_name"] for col in schema.get("columns", [])}
    actual_cols = set(df.columns)
    return expected_cols.issubset(actual_cols)
