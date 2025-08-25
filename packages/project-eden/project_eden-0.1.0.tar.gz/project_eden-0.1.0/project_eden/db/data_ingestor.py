import pandas as pd
import certifi
import json
import time
import os
import datetime
import ssl
from enum import Enum
from typing import Optional, Dict, Any, List
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from collections import defaultdict
from psycopg2.extras import execute_values

from project_eden.db.utils import (
    connect,
    insert_records_from_df,
)
from project_eden.db.create_tables import (
    DEFAULT_COMPANY_TABLE_COLUMNS_TO_TYPE,
    DEFAULT_SHARES_COLUMNS_TO_TYPE,
    FMP_COLUMN_NAMES_TO_POSTGRES_COLUMN_NAMES,
    DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE,
    DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE,
    DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE,
    postgres_type_to_python_type,
    DEFAULT_PRICE_COLUMNS_TO_TYPE,
)


INCOME_STATEMENT = "income-statement"
BALANCE_SHEET_STATEMENT = "balance-sheet-statement"
CASH_FLOW_STATEMENT = "cash-flow-statement"
PROFILE = "profile"
ENTERPRISE_VALUES = "enterprise-values"
HISTORTICAL_PRICE_EOD_FULL = "historical-price-eod/full"


class Datasets(Enum):
    INCOME_STATEMENT = INCOME_STATEMENT
    BALANCE_SHEET_STATEMENT = BALANCE_SHEET_STATEMENT
    CASH_FLOW_STATEMENT = CASH_FLOW_STATEMENT
    ENTERPRISE_VALUES = ENTERPRISE_VALUES
    PROFILE = PROFILE
    HISTORTICAL_PRICE_EOD_FULL = HISTORTICAL_PRICE_EOD_FULL


dataset_to_base_url_key = {
    Datasets.INCOME_STATEMENT: "base_url",
    Datasets.BALANCE_SHEET_STATEMENT: "base_url",
    Datasets.CASH_FLOW_STATEMENT: "base_url",
    Datasets.ENTERPRISE_VALUES: "base_url",
    Datasets.PROFILE: "base_url",
    Datasets.HISTORTICAL_PRICE_EOD_FULL: "base_url_new",
}


def get_default_params_for_dataset(dataset: Datasets, period: str) -> dict:
    if period not in ["quarter", "fy"]:
        raise ValueError("period must be either 'quarter' or 'period'.")

    dataset_to_default_params = {
        Datasets.BALANCE_SHEET_STATEMENT: {"period": period},
        Datasets.CASH_FLOW_STATEMENT: {"period": period},
        Datasets.INCOME_STATEMENT: {"period": period},
        Datasets.HISTORTICAL_PRICE_EOD_FULL: {
            "from": "1900-01-01",
            "to": datetime.date.today().strftime("%Y-%m-%d"),
        },
    }

    return dataset_to_default_params.get(dataset, {})


datasets_to_api_version = {
    Datasets.HISTORTICAL_PRICE_EOD_FULL: "stable",
    Datasets.PROFILE: "v3",
    Datasets.INCOME_STATEMENT: "v3",
    Datasets.BALANCE_SHEET_STATEMENT: "v3",
    Datasets.CASH_FLOW_STATEMENT: "v3",
}


dataset_to_table_name_fy = {
    Datasets.INCOME_STATEMENT: "income_statement_fy",
    Datasets.BALANCE_SHEET_STATEMENT: "balance_sheet_fy",
    Datasets.CASH_FLOW_STATEMENT: "cash_flow_statement_fy",
    # Datasets.ENTERPRISE_VALUES: "shares_fy",
    Datasets.PROFILE: "company",
    Datasets.HISTORTICAL_PRICE_EOD_FULL: "price",
}


dataset_to_table_name_quarter = {
    Datasets.INCOME_STATEMENT: "income_statement_quarter",
    Datasets.BALANCE_SHEET_STATEMENT: "balance_sheet_quarter",
    Datasets.CASH_FLOW_STATEMENT: "cash_flow_statement_quarter",
    Datasets.PROFILE: "company",
    Datasets.HISTORTICAL_PRICE_EOD_FULL: "price",
}


dataset_to_table_columns = {
    Datasets.INCOME_STATEMENT: list(DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE.keys()),
    Datasets.BALANCE_SHEET_STATEMENT: list(DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE.keys()),
    Datasets.CASH_FLOW_STATEMENT: list(DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE.keys()),
    Datasets.ENTERPRISE_VALUES: list(DEFAULT_SHARES_COLUMNS_TO_TYPE.keys()),
    Datasets.PROFILE: list(DEFAULT_COMPANY_TABLE_COLUMNS_TO_TYPE.keys()),
    Datasets.HISTORTICAL_PRICE_EOD_FULL: list(DEFAULT_PRICE_COLUMNS_TO_TYPE.keys()),
}


def get_jsonparsed_data(
    dataset_name: str,
    ticker: str,
    key: str = None,
    base_url: str = None,
    config: Dict[str, Any] = None,
    api_version: str = "v3",
    **kwargs,
) -> dict:
    """
    Receive the content of from a url of the form f"{base_url}/{dataset_name}/{ticker}?apikey={key}".

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to retrieve
    ticker : str
        The stock ticker symbol
    key : str, optional
        The API key for authentication. If None, uses the key from config
    base_url : str, optional
        The base URL for the API. If None, uses the URL from config
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json
    api_version : str, default="v3"
        The API version to use.  Options are "v3" and "stable"
    **kwargs
        Additional query parameters to include in the URL

    Returns
    -------
    dict
        The parsed JSON response from the API
    """
    if config is None:
        config = load_config()

    if key is None:
        key = config["api"]["key"]

    if base_url is None:
        base_url = config["api"]["base_url"]

    if api_version == "v3":
        url = f"{base_url}/{dataset_name}/{ticker}?apikey={key}"
        for wkargs_key, value in kwargs.items():
            url += f"&{wkargs_key}={value}"
    elif api_version == "stable":
        url = f"{base_url}/{dataset_name}?symbol={ticker}"
        for wkargs_key, value in kwargs.items():
            url += f"&{wkargs_key}={value}"
        url += f"&apikey={key}"
    else:
        raise ValueError(f"Invalid api_version: {api_version}.  Options are 'v3' and 'stable'.")

    context = ssl.create_default_context(cafile=certifi.where())
    response = urlopen(url, context=context)
    data = response.read().decode("utf-8")
    return json.loads(data)


def gather_dataset(
    ticker: str, dataset: str, key: str = None, config: Dict[str, Any] = None, **kwargs
) -> pd.DataFrame:
    """
    Gather dataset from the financial API and convert to DataFrame.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol
    dataset : str
        The dataset name to retrieve
    key : str, optional
        The API key for authentication. If None, uses the key from config
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json
    **kwargs
        Additional parameters to pass to the API

    Returns
    -------
    pd.DataFrame
        DataFrame containing the retrieved data
    """
    kwargs = kwargs if kwargs else {}
    kwargs_to_use = {}
    if "base_url" not in kwargs:
        kwargs_to_use["base_url"] = config["api"][dataset_to_base_url_key[Datasets(dataset)]]

    kwargs_to_use.update(kwargs)

    api_version = datasets_to_api_version.get(Datasets(dataset), "v3")

    json_data = get_jsonparsed_data(
        dataset, ticker, key, config=config, api_version=api_version, **kwargs_to_use
    )
    return pd.DataFrame.from_records(json_data)


def add_datasets_to_db(
    connection,
    symbol,
    datasets,
    key=None,
    failure_list=None,
    config=None,
    period="quarter",
    **kwargs,
):
    """
    Add datasets for a symbol to the database.

    Parameters
    ----------
    connection
        Database connection
    symbol : str
        Stock symbol to process
    datasets : list
        List of datasets to process
    key : str, optional
        API key for the financial data provider. If None, uses the key from config
    failure_list : list, optional
        List to append failed symbols to
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json
    period : str, default="quarter"
        Data period ("quarter" or "fy")
    **kwargs
        Additional arguments for dataset gathering
    """
    if config is None:
        config = load_config()

    if key is None:
        key = config["api"]["key"]
    datasets = Datasets if datasets is None else datasets

    if period == "quarter":
        dataset_to_table_name_to_use = dataset_to_table_name_quarter
    elif period == "fy":
        dataset_to_table_name_to_use = dataset_to_table_name_fy
    else:
        raise ValueError("period must be either 'quarter' or 'fy'")

    try:
        with connection.cursor() as cursor:
            for dataset in datasets:
                table_name = dataset_to_table_name_to_use[dataset]
                print(f"--Processing {symbol} for {table_name} table.")

                # Fetch new data from API
                default_params = get_default_params_for_dataset(Datasets(dataset), period)
                kwargs_to_use = kwargs.copy()
                for param, value in default_params.items():
                    if param not in kwargs:
                        kwargs_to_use.update({param: value})
                new_data_df = gather_dataset(
                    symbol, dataset.value, key, config=config, **kwargs_to_use
                )

                if new_data_df.empty:
                    print(f"--No new data found for {symbol} in {table_name}, skipping.")
                    continue

                # Standardize column names to match database
                new_data_df.rename(columns=FMP_COLUMN_NAMES_TO_POSTGRES_COLUMN_NAMES, inplace=True)
                columns_to_compare = get_columns_to_compare(dataset)

                # Convert calendaryear to int for proper comparison
                if "calendaryear" in new_data_df.columns:
                    new_data_df["calendaryear"] = new_data_df["calendaryear"].astype(int)

                process_dataset(
                    cursor, symbol, table_name, new_data_df, columns_to_compare, dataset
                )

        connection.commit()
        print(f"{symbol} processing complete.")
        print("")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        import traceback

        traceback.print_exc()
        connection.rollback()
        if failure_list is not None:
            failure_list.append(symbol)


def get_columns_to_compare(dataset):
    """
    Get the columns to compare for a given dataset.

    Parameters
    ----------
    dataset
        The dataset to get columns for

    Returns
    -------
    list
        A list of column names to compare
    """
    columns_to_compare = [
        FMP_COLUMN_NAMES_TO_POSTGRES_COLUMN_NAMES.get(col, col)
        for col in dataset_to_table_columns[dataset]
        if col not in ["id", "company_id"]
    ]
    return list(set(columns_to_compare))


def process_dataset(cursor, symbol, table_name, new_data_df, columns_to_compare, dataset):
    """
    Process a dataset by either updating existing records or inserting new ones.

    Parameters
    ----------
    cursor
        Database cursor
    symbol : str
        Stock symbol being processed
    table_name : str
        Name of the database table
    new_data_df : DataFrame
        DataFrame containing new data
    columns_to_compare : list
        List of columns to compare
    dataset
        The dataset being processed
    """
    # Fetch existing data from database
    cursor.execute(f"SELECT * FROM {table_name} WHERE symbol = '{symbol}'")
    existing_records = cursor.fetchall()

    if existing_records:
        process_existing_records(
            cursor, symbol, table_name, new_data_df, columns_to_compare, existing_records, dataset
        )
    else:
        # If no existing records, insert all new data
        print(f"--Inserting new records for {symbol} in {table_name}")
        insert_records_from_df(cursor, new_data_df[columns_to_compare], table_name)


def process_existing_records(
    cursor, symbol, table_name, new_data_df, columns_to_compare, existing_records, dataset
):
    """
    Process records when there are existing entries in the database.

    Parameters
    ----------
    cursor
        Database cursor
    symbol : str
        Stock symbol being processed
    table_name : str
        Name of the database table
    new_data_df : DataFrame
        DataFrame containing new data
    columns_to_compare : list
        List of columns to compare
    existing_records : list
        Existing records from the database
    dataset
        The dataset being processed
    """
    # Convert existing records to DataFrame
    existing_df = pd.DataFrame(existing_records, columns=[desc[0] for desc in cursor.description])

    # Identify records to update or insert
    merge_keys = get_merge_keys(dataset, new_data_df)

    # Handle date in merge_keys, since JSON returns date as string
    if "date" in merge_keys:
        new_data_df["date"] = pd.to_datetime(new_data_df["date"]).dt.date

    comparison = new_data_df.merge(
        existing_df[columns_to_compare], on=merge_keys, how="left", indicator=True
    )

    # Handle new records (left_only)
    process_new_records(cursor, symbol, table_name, comparison, columns_to_compare, merge_keys)

    # Handle updates (both present but different values)
    process_updates(cursor, symbol, table_name, comparison, columns_to_compare, merge_keys)


def get_merge_keys(dataset, new_data_df):
    """
    Determine the merge keys based on the dataset.

    Parameters
    ----------
    dataset
        The dataset being processed
    new_data_df : DataFrame
        DataFrame containing new data

    Returns
    -------
    list
        A list of column names to use as merge keys
    """
    if dataset == Datasets.PROFILE:
        return ["symbol"]
    elif dataset == Datasets.HISTORTICAL_PRICE_EOD_FULL:
        return ["symbol", "date"]
    else:
        return (
            ["symbol", "calendaryear", "period"]
            if "period" in new_data_df.columns
            else ["symbol", "calendaryear"]
        )


def process_new_records(cursor, symbol, table_name, comparison, columns_to_compare, merge_keys):
    """
    Process records that exist in the new data but not in the database.

    Parameters
    ----------
    cursor
        Database cursor
    symbol : str
        Stock symbol being processed
    table_name : str
        Name of the database table
    comparison : DataFrame
        DataFrame containing comparison results
    columns_to_compare : list
        List of columns to compare
    merge_keys : list
        List of columns used as merge keys
    """
    new_records = comparison[comparison["_merge"] == "left_only"]
    if not new_records.empty:
        new_records_str = "\n".join(
            [
                f"{', '.join([f'{key}={row[key]}' for key in merge_keys])}"
                for _, row in new_records.iterrows()
            ]
        )
        print(
            f"--Found {len(new_records)} new records: {new_records_str}\nfor {symbol} in {table_name}"
        )
        new_records_clean = new_records.rename(
            columns={f"{col}_x": col for col in columns_to_compare}
        )[columns_to_compare]
        insert_records_from_df(cursor, new_records_clean, table_name)


def process_updates(cursor, symbol, table_name, comparison, columns_to_compare, merge_keys):
    """
    Process records that exist in both datasets but may have different values.

    Parameters
    ----------
    cursor
        Database cursor
    symbol : str
        Stock symbol being processed
    table_name : str
        Name of the database table
    comparison : DataFrame
        DataFrame containing comparison results
    columns_to_compare : list
        List of columns to compare
    merge_keys : list
        List of columns used as merge keys
    """
    updates = comparison[comparison["_merge"] == "both"]
    # {index: [i1, ...], <merge_key1>: [val, ...], <merge_key2>: [val, ...],... , col: [(old_val, new_val), ...], ...}
    update_values = defaultdict(list)
    for index, row in updates.iterrows():
        for col in columns_to_compare:
            if col in merge_keys:
                # update_values[col].append(row[col])
                continue

            new_val = row[f"{col}_x"] if f"{col}_x" in row else row[col]
            old_val = row[f"{col}_y"] if f"{col}_y" in row else None

            if should_update_value(new_val, old_val, col) and col not in merge_keys:
                # update_values[col].append((old_val, new_val))
                update_values[col].append(new_val)
            elif col not in merge_keys:
                update_values[col].append(pd.NA)
        update_values["index"].append(index)

        # if update_needed:
        #     apply_updates(cursor, symbol, table_name, row, update_values, merge_keys)

    # apply updates in bulk
    update_values = pd.DataFrame(update_values, index=update_values["index"])
    update_values = update_values.drop(columns=["index"])
    update_values = update_values.dropna(how="all", axis=0)
    update_values = update_values.dropna(how="all", axis=1)
    apply_updates(
        cursor,
        symbol,
        table_name,
        update_values,
        merge_keys,
    )


def should_update_value(new_val, old_val, col):
    """
    Determine if a value should be updated based on comparison logic.

    Parameters
    ----------
    new_val
        The new value from the API
    old_val
        The existing value in the database
    col : str
        The column name

    Returns
    -------
    bool
        True if the value should be updated, False otherwise
    """
    # If both values are present, compare them
    if pd.notna(new_val) and pd.notna(old_val):
        # Handle date comparisons
        if isinstance(new_val, str) and isinstance(old_val, (datetime.date, datetime.datetime)):
            try:
                new_date = datetime.datetime.strptime(
                    new_val, "%Y-%m-%d" if " " not in new_val else "%Y-%m-%d %H:%M:%S"
                ).date()
                old_date = old_val
                if hasattr(old_val, "date") and callable(getattr(old_val, "date")):
                    old_date = old_val.date()
                return new_date != old_date
            except ValueError:
                return True
        # Handle type differences
        elif type(new_val) != type(old_val):
            try:
                new_val = postgres_type_to_python_type(col)(new_val)
                return new_val != old_val
            except ValueError:
                return True
        # Handle numeric comparisons
        elif isinstance(new_val, (int, float)) and isinstance(old_val, (int, float)):
            try:
                # Convert both to float for consistent comparison
                new_float = float(new_val)
                old_float = float(old_val)

                # For very small values, use absolute difference
                if abs(new_float) < 1e-10 and abs(old_float) < 1e-10:
                    return abs(new_float - old_float) > 1e-10

                # For PostgreSQL numeric/decimal fields, round to 5 decimal places
                # This matches PostgreSQL's typical numeric precision
                new_rounded = round(new_float, 4)
                old_rounded = round(old_float, 4)

                # Compare the rounded values
                return new_rounded != old_rounded
            except (ValueError, TypeError):
                return True
        # Direct comparison
        else:
            return new_val != old_val
    # If new value exists but old is null
    elif pd.notna(new_val) and pd.isna(old_val):
        return True
    return False


def convert_value_to_postgres_type(value, column_name, table_name):
    """
    Convert a value to the appropriate Python type for PostgreSQL.

    Parameters
    ----------
    value : any
        The value to convert
    column_name : str
        Name of the column
    table_name : str
        Name of the table

    Returns
    -------
    any
        Converted value
    """
    if pd.isna(value) or value is None:
        return None

    # Map table names to their column type dictionaries
    table_to_columns = {
        "company": DEFAULT_COMPANY_TABLE_COLUMNS_TO_TYPE,
        "income_statement_fy": DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "income_statement_quarter": DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "balance_sheet_fy": DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE,
        "balance_sheet_quarter": DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE,
        "cash_flow_statement_fy": DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "cash_flow_statement_quarter": DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "price": DEFAULT_PRICE_COLUMNS_TO_TYPE,
    }

    # Get the column type for this table
    column_types = table_to_columns.get(table_name, {})
    column_types = {
        FMP_COLUMN_NAMES_TO_POSTGRES_COLUMN_NAMES.get(col, col): col_type
        for col, col_type in column_types.items()
    }
    column_type = column_types.get(column_name, "text")

    # Extract base type (remove "primary key" etc.)
    base_type = column_type.split()[0]

    try:
        if base_type in ["smallint", "int", "bigint", "serial"]:
            return int(value)
        elif base_type == "real":
            return float(value)
        elif base_type == "bool":
            return bool(value)
        elif base_type == "date":
            if isinstance(value, str):
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            return value
        elif base_type == "timestamp":
            if isinstance(value, str):
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return value
        else:  # text and others
            return str(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def apply_updates(cursor, symbol, table_name, update_values, merge_keys):
    """
    Apply updates to the database.

    Parameters
    ----------
    cursor
        Database cursor
    symbol : str
        Stock symbol being processed
    table_name : str
        Name of the database table
    update_values : pd.DataFrame
        DataFrame of values to update
    merge_keys : list
        List of columns used as merge keys
    """
    if update_values.empty:
        return

    # Replace pandas NA values with None for psycopg2 compatibility
    update_values = update_values.replace({pd.NA: None})

    # Create columns list including merge keys and update columns
    all_columns = list(update_values.columns)
    for key in merge_keys:
        if key not in all_columns:
            all_columns.append(key)

    # Create data tuples for each row with proper type conversion
    data = []
    for idx, row in update_values.iterrows():
        row_data = []
        for col in all_columns:
            if col in update_values.columns:
                val = row[col]
                # Convert to proper PostgreSQL type
                converted_val = convert_value_to_postgres_type(val, col, table_name)
                row_data.append(converted_val)
            elif col == "symbol":
                row_data.append(symbol)
            else:
                row_data.append(None)
        data.append(tuple(row_data))

    # Get column type mappings for casting
    table_to_columns = {
        "company": DEFAULT_COMPANY_TABLE_COLUMNS_TO_TYPE,
        "income_statement_fy": DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "income_statement_quarter": DEFAULT_INCOME_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "balance_sheet_fy": DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE,
        "balance_sheet_quarter": DEFAULT_BALANCE_SHEET_TABLE_COLUMNS_TO_TYPE,
        "cash_flow_statement_fy": DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "cash_flow_statement_quarter": DEFAULT_CASHFLOW_STATEMENT_TABLE_COLUMNS_TO_TYPE,
        "price": DEFAULT_PRICE_COLUMNS_TO_TYPE,
    }

    column_types = table_to_columns.get(table_name, {})
    column_types = {
        FMP_COLUMN_NAMES_TO_POSTGRES_COLUMN_NAMES.get(col, col): col_type
        for col, col_type in column_types.items()
    }

    # Create SET clause with proper type casting
    set_clauses = []
    for col in update_values.columns:
        column_type = column_types.get(col, "text")
        base_type = column_type.split()[0]

        if base_type in ["smallint", "int", "bigint", "serial"]:
            set_clauses.append(f"{col} = tmp.{col}::bigint")
        elif base_type == "real":
            set_clauses.append(f"{col} = tmp.{col}::real")
        elif base_type == "bool":
            set_clauses.append(f"{col} = tmp.{col}::boolean")
        elif base_type == "date":
            set_clauses.append(f"{col} = tmp.{col}::date")
        elif base_type == "timestamp":
            set_clauses.append(f"{col} = tmp.{col}::timestamp")
        else:
            set_clauses.append(f"{col} = tmp.{col}")

    set_clause = ", ".join(set_clauses)

    # Create WHERE clause with proper type casting
    where_conditions = []
    for key in merge_keys:
        if key == "symbol":
            where_conditions.append(f"{table_name}.{key} = '{symbol}'")
        elif key == "calendaryear":
            where_conditions.append(f"{table_name}.{key} = tmp.{key}::smallint")
        elif key == "date":
            where_conditions.append(f"{table_name}.{key} = tmp.{key}::date")
        else:
            where_conditions.append(f"{table_name}.{key} = tmp.{key}")
    where_clause = " AND ".join(where_conditions)

    # SQL template for execute_values
    sql = f"""
    UPDATE {table_name}
    SET {set_clause}
    FROM (VALUES %s) AS tmp ({', '.join(all_columns)})
    WHERE {where_clause}
    """

    # Execute the bulk update
    execute_values(cursor, sql, data)


def get_company_tickers(config=None):
    """
    Fetch the latest company tickers JSON from SEC website.

    Parameters
    ----------
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json

    Returns
    -------
    dict
        A dictionary of company tickers and their information

    Notes
    -----
    Falls back to a local file if the SEC website is unavailable
    """
    if config is None:
        config = load_config()

    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": config["api"]["user_agent"],
    }

    try:
        req = Request(url, headers=headers)
        context = ssl.create_default_context(cafile=certifi.where())
        response = urlopen(req, context=context)
        data = response.read().decode("utf-8")
        return json.loads(data)
    except HTTPError as e:
        print(f"Error fetching company tickers: {e}")
        print("Falling back to local file...")
        # Fallback to local file
        fallback_file = config["paths"]["company_tickers_json"]
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), fallback_file)
        ) as user_file:
            file_contents = user_file.read()
            return json.loads(file_contents)


def connect_to_database(config=None):
    """
    Establish a connection to the database using configuration from JSON.

    Parameters
    ----------
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json

    Returns
    -------
    connection
        A database connection object
    """
    if config is None:
        config = load_config()

    db_config = config["database"]
    connection = connect(db_config)

    def _mask_password(config):
        masked_config = config.copy()
        masked_config["password"] = "*****"
        return masked_config

    if connection:
        print(f"Connected successfully to database: {_mask_password(db_config)}")
        return connection
    else:
        raise ValueError(f"Failed to connect to db: {_mask_password(db_config)}")


def handle_rate_limiting(counter, start_time, config=None):
    """
    Handle API rate limiting by sleeping if necessary.

    Parameters
    ----------
    counter : int
        Current count of API calls
    start_time : float
        Time when counting started
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json

    Returns
    -------
    tuple
        Updated counter and start_time
    """
    if config is None:
        config = load_config()

    api_limit_per_min = config["api"]["rate_limit_per_min"]
    current_time = time.time()
    elapsed_time = current_time - start_time

    # If we've reached the limit but less than a minute has passed
    if counter >= api_limit_per_min and elapsed_time < 60:
        sleep_time = 60 - elapsed_time
        if sleep_time > 0:
            print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        counter = 0
        start_time = time.time()
    # If a minute or more has passed, reset counter and timer
    elif elapsed_time >= 60:
        counter = 0
        start_time = time.time()

    return counter, start_time


def process_symbol(
    connection,
    symbol,
    api_key=None,
    failure_list=None,
    period="quarter",
    include_daily_eod_price=True,
    config=None,
    datasets: Optional[List[Datasets]] = None,
):
    """
    Process a single symbol by adding its datasets to the database.

    Parameters
    ----------
    connection
        Database connection
    symbol : str
        Stock symbol to process
    api_key : str, optional
        API key for the financial data provider. If None, uses the key from config
    failure_list : list, optional
        List to append failed symbols to
    period : str, default="quarter"
        Data period ("quarter" or "fy")
    include_daily_eod_price: bool, default=True
        Include ingestion of daily EOD prices for symbol
    config : Dict[str, Any], optional
        Configuration dictionary. If None, loads from config.json
    datasets: List[Datasets], optional
        List of datasets to process.  If None, processes all datasets.
    """
    if config is None:
        config = load_config()

    if api_key is None:
        api_key = config["api"]["key"]
    print(f"Processing {symbol}")
    datasets = (
        datasets
        if datasets is not None
        else [
            Datasets.PROFILE,
            Datasets.INCOME_STATEMENT,
            Datasets.CASH_FLOW_STATEMENT,
            Datasets.BALANCE_SHEET_STATEMENT,
            Datasets.HISTORTICAL_PRICE_EOD_FULL,
        ]
    )
    add_datasets_to_db(
        connection,
        symbol,
        datasets=datasets,
        key=api_key,
        failure_list=failure_list,
        config=config,
        period=period,
    )


def ingest_tickers(
    tickers=None, api_key=None, config_file="config.json", period: Optional[str] = None
):
    """
    Main function to process quarterly financial data for all companies, or only selected companies.

    Parameters
    ----------
    tickers : list, optional
        List of stock symbols to process. If None, processes all companies.
    api_key : str, optional
        API key for the financial data provider. If None, uses the key from config
    config_file : str, default="config.json"
        Path to the JSON configuration file
    period : str, optional
        Period for ingestion for each ticker.  Options are "quarter", "fy", or None.  If None, both "quarter" and "fy"
        data will be ingested.

    Returns
    -------
    list
        List of symbols that failed processing
    """
    # Load configuration
    config = load_config(config_file)
    # Initialize list to track failures
    symbols_with_failure = []

    # Connect to the database
    connection = connect_to_database(config)

    # If api_key is not provided, use the one from config
    if api_key is None:
        api_key = config["api"]["key"]

    # Get company tickers
    ticker_dict = get_company_tickers(config)
    if tickers is None:
        tickers = [value_dict["ticker"] for value_dict in ticker_dict.values()]

    # Initialize rate limiting variables
    counter = 0
    start_time = time.time()

    # Process each symbol
    for symbol in tickers:
        symbol = symbol.upper()

        # Handle API rate limiting
        counter, start_time = handle_rate_limiting(counter, start_time, config)

        # Process the current symbol
        if period is None:
            process_symbol(
                connection, symbol, api_key, symbols_with_failure, period="quarter", config=config
            )
            datasets = [
                Datasets.PROFILE,
                Datasets.INCOME_STATEMENT,
                Datasets.CASH_FLOW_STATEMENT,
                Datasets.BALANCE_SHEET_STATEMENT,
            ]
            process_symbol(
                connection,
                symbol,
                api_key,
                symbols_with_failure,
                period="fy",
                config=config,
                datasets=datasets,
            )
            counter += 5 + 4  # 5 for quarter, 4 for fy
        else:
            process_symbol(
                connection, symbol, api_key, symbols_with_failure, period=period, config=config
            )
            counter += 5  # 5 for quarter

    return symbols_with_failure


def load_config(config_file="config.json") -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Parameters
    ----------
    config_file : str, default="config.json"
        Path to the JSON configuration file

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the configuration
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
    with open(config_path, "r") as f:
        return json.load(f)


def driver(config_file="config.json", tickers=None, period: Optional[str] = None):
    failed_symbols = ingest_tickers(tickers=tickers, config_file=config_file, period=period)
    print(f"The following symbols failed: {failed_symbols}")


if __name__ == "__main__":
    pass
    # # Load configuration
    # config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    #
    # # Run the main function
    # failed_symbols = main_quarter(config_file=config_file)
    #
    # # Print any failures
    # print(f"The following symbols failed: {failed_symbols}")
