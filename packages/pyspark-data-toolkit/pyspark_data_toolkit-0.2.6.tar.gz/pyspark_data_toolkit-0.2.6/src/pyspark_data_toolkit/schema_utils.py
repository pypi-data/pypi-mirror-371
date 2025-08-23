from typing import List, Dict, Optional, Any
import re
import logging
from pyspark.sql import DataFrame, functions as F
from logging_metrics import configure_basic_logging
from pyspark.sql.types import IntegerType, DoubleType, StringType, BooleanType
from pyspark.sql import DataFrame, SparkSession

__all__ = [
    "apply_schema",
    "cast_columns_types_by_schema",
    "validate_dataframe_schema",
    "cast_column_to_table_schema",
    "cast_multiple_columns_to_table_schema",
    "align_dataframe_to_table_schema",
    "get_table_schema_info"
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

# spark_utils/schema_utils.py ou my_library/spark/schema.py


def cast_column_to_table_schema(
    df: DataFrame, 
    target_table: str, 
    column_name: str,
    spark: Optional[SparkSession] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Converte uma coluna para o tipo de dados definido no schema de uma tabela existente.
    
    Útil para compatibilizar schemas antes de operações como MERGE ou INSERT,
    especialmente quando há incompatibilidades de tipo entre DataFrames.
    
    Args:
        df: DataFrame de origem
        target_table: Nome da tabela de destino (formato: database.table ou table)
        column_name: Nome da coluna a ser convertida
        spark: SparkSession (opcional, tenta obter da sessão ativa se não fornecido)
        
    Returns:
        DataFrame com a coluna convertida para o tipo correto
        
    Raises:
        ValueError: Se a coluna não existir na tabela de destino
        RuntimeError: Se não conseguir acessar a tabela ou obter o SparkSession
        
    Examples:
        >>> # Converte coluna 'status' para o tipo definido na tabela 'users'
        >>> df_fixed = cast_column_to_table_schema(df, "users", "status")
        >>> 
        >>> # Com SparkSession explícito
        >>> df_fixed = cast_column_to_table_schema(df, "db.users", "created_at", spark)
    """
    if logger is None:
        logger = get_logger()

    if spark is None:
        try:
            spark = SparkSession.getActiveSession()
            if spark is None:
                raise RuntimeError("Não foi possível obter SparkSession ativa")
        except Exception as e:
            raise RuntimeError(f"Erro ao obter SparkSession: {e}")
    
    try:
        # Obtém o schema da tabela de destino
        target_schema = spark.table(target_table).schema
    except Exception as e:
        raise RuntimeError(f"Erro ao acessar tabela '{target_table}': {e}")
    
    # Encontra o tipo da coluna no schema de destino
    target_column_type = None
    for field in target_schema.fields:
        if field.name == column_name:
            target_column_type = field.dataType
            break
    
    if target_column_type is None:
        available_columns = [field.name for field in target_schema.fields]
        raise ValueError(
            f"Coluna '{column_name}' não encontrada na tabela '{target_table}'. "
            f"Colunas disponíveis: {available_columns}"
        )
    
    logger.info(f"Convertendo coluna '{column_name}' para tipo {target_column_type}")
    
    # Aplica o cast correto
    return df.withColumn(column_name, F.lit(None).cast(target_column_type))

def cast_multiple_columns_to_table_schema(
    df: DataFrame,
    target_table: str,
    column_names: List[str],
    spark: Optional[SparkSession] = None
) -> DataFrame:
    """
    Converte múltiplas colunas para os tipos definidos no schema de uma tabela.
    
    Args:
        df: DataFrame de origem
        target_table: Nome da tabela de destino
        column_names: Lista de nomes das colunas a serem convertidas
        spark: SparkSession (opcional)
        
    Returns:
        DataFrame com as colunas convertidas
        
    Examples:
        >>> columns_to_fix = ["status", "created_at", "user_id"]
        >>> df_fixed = cast_multiple_columns_to_table_schema(df, "users", columns_to_fix)
    """
    result_df = df
    for column_name in column_names:
        result_df = cast_column_to_table_schema(result_df, target_table, column_name, spark)
    return result_df

def align_dataframe_to_table_schema(
    df: DataFrame,
    target_table: str,
    cast_existing: bool = True,
    add_missing: bool = True,
    spark: Optional[SparkSession] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Alinha completamente um DataFrame ao schema de uma tabela existente.
    
    Args:
        df: DataFrame de origem
        target_table: Nome da tabela de destino
        cast_existing: Se True, converte colunas existentes para os tipos corretos
        add_missing: Se True, adiciona colunas ausentes como NULL
        spark: SparkSession (opcional)
        
    Returns:
        DataFrame alinhado ao schema da tabela
        
    Examples:
        >>> # Alinhamento completo
        >>> df_aligned = align_dataframe_to_table_schema(df, "users")
        >>> 
        >>> # Só adicionar colunas ausentes, sem cast
        >>> df_aligned = align_dataframe_to_table_schema(
        ...     df, "users", cast_existing=False, add_missing=True
        ... )
    """
    if logger is None:
        logger = get_logger()

    if spark is None:
        spark = SparkSession.getActiveSession()
        if spark is None:
            raise RuntimeError("Não foi possível obter SparkSession ativa")
    
    try:
        target_schema = spark.table(target_table).schema
    except Exception as e:
        raise RuntimeError(f"Erro ao acessar tabela '{target_table}': {e}")
    
    result_df = df
    current_columns = set(df.columns)
    target_columns = {field.name: field.dataType for field in target_schema.fields}
    
    # Adiciona colunas ausentes
    if add_missing:
        missing_columns = set(target_columns.keys()) - current_columns
        for col_name in missing_columns:
            col_type = target_columns[col_name]
            result_df = result_df.withColumn(col_name, F.lit(None).cast(col_type))
            logger.info(f"Adicionada coluna ausente '{col_name}' como {col_type}")
    
    # Converte tipos das colunas existentes
    if cast_existing:
        existing_columns = current_columns.intersection(target_columns.keys())
        for col_name in existing_columns:
            target_type = target_columns[col_name]
            current_type = dict(result_df.dtypes)[col_name]
            if str(target_type) != current_type:
                result_df = result_df.withColumn(col_name, F.col(col_name).cast(target_type))
                logger.info(f"Convertida coluna '{col_name}' de {current_type} para {target_type}")
    
    # Reordena colunas para corresponder ao schema da tabela
    target_column_order = [field.name for field in target_schema.fields if field.name in result_df.columns]
    result_df = result_df.select(*target_column_order)
    
    return result_df

def get_table_schema_info(
    table_name: str,
    spark: Optional[SparkSession] = None
) -> Dict[str, str]:
    """
    Obtém informações do schema de uma tabela.
    
    Args:
        table_name: Nome da tabela
        spark: SparkSession (opcional)
        
    Returns:
        Dicionário com {column_name: data_type}
        
    Examples:
        >>> schema_info = get_table_schema_info("users")
        >>> print(schema_info)
        {'id': 'bigint', 'name': 'string', 'created_at': 'timestamp'}
    """
    if spark is None:
        spark = SparkSession.getActiveSession()
        if spark is None:
            raise RuntimeError("Não foi possível obter SparkSession ativa")
    
    try:
        schema = spark.table(table_name).schema
        return {field.name: str(field.dataType) for field in schema.fields}
    except Exception as e:
        raise RuntimeError(f"Erro ao obter schema da tabela '{table_name}': {e}")

