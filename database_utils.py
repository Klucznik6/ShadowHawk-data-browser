import sqlite3
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
import json
import csv
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

class DatabaseManager:
    """Enhanced database manager supporting multiple database types"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        
    def detect_database_type(self, filename: str) -> str:
        """Detect database type from file extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        elif ext in ['.mdb', '.accdb']:
            return 'access'
        elif ext in ['.csv']:
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext in ['.json']:
            return 'json'
        else:
            return 'unknown'
    
    def connect_sqlite(self, filename: str) -> sqlite3.Connection:
        """Connect to SQLite database"""
        # Enable thread safety for SQLite
        return sqlite3.connect(filename, check_same_thread=False)
    
    def connect_access(self, filename: str):
        """Connect to Access database"""
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc is required for Access database support")
        
        conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={filename};'
        return pyodbc.connect(conn_str)
    
    def load_csv_as_database(self, filename: str) -> sqlite3.Connection:
        """Load CSV file as in-memory SQLite database"""
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        df = pd.read_csv(filename)
        
        table_name = os.path.splitext(os.path.basename(filename))[0]
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        return conn, table_name
    
    def load_excel_as_database(self, filename: str) -> Tuple[sqlite3.Connection, List[str]]:
        """Load Excel file as in-memory SQLite database"""
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        excel_file = pd.ExcelFile(filename)
        table_names = []
        
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(filename, sheet_name=sheet_name)
            table_name = f"{base_name}_{sheet_name}".replace(' ', '_').replace('-', '_')
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            table_names.append(table_name)
            
        return conn, table_names
    
    def load_json_as_database(self, filename: str) -> sqlite3.Connection:
        """Load JSON file as in-memory SQLite database"""
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dict with array values, try to convert
            if all(isinstance(v, list) for v in data.values()):
                df = pd.DataFrame(data)
            else:
                # Convert single dict to single-row DataFrame
                df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")
        
        table_name = os.path.splitext(os.path.basename(filename))[0]
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        return conn, table_name
    
    def get_table_list(self, connection, db_type: str) -> List[str]:
        """Get list of tables from database"""
        if db_type == 'sqlite':
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
        elif db_type == 'access':
            cursor = connection.cursor()
            tables = cursor.tables(tableType='TABLE')
            return [row.table_name for row in tables]
        else:
            return []
    
    def get_table_info(self, connection, table_name: str, db_type: str) -> Dict[str, Any]:
        """Get table information including columns and row count"""
        info = {
            'columns': [],
            'row_count': 0,
            'column_types': {}
        }
        
        try:
            if db_type == 'sqlite':
                cursor = connection.cursor()
                
                # Get columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                info['columns'] = [col[1] for col in columns_info]
                info['column_types'] = {col[1]: col[2] for col in columns_info}
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                info['row_count'] = cursor.fetchone()[0]
                
            elif db_type == 'access':
                cursor = connection.cursor()
                
                # Get columns
                cursor.execute(f"SELECT TOP 1 * FROM [{table_name}]")
                info['columns'] = [desc[0] for desc in cursor.description]
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                info['row_count'] = cursor.fetchone()[0]
                
        except Exception as e:
            print(f"Error getting table info: {e}")
            
        return info
    
    def execute_query(self, connection, query: str, params: List = None) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        if params:
            return pd.read_sql_query(query, connection, params=params)
        else:
            return pd.read_sql_query(query, connection)

class DataProcessor:
    """Fast data processing utilities"""
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage"""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != 'object':
                c_min = df[col].min()
                c_max = df[col].max()
                
                if str(col_type)[:3] == 'int':
                    if c_min > -128 and c_max < 127:
                        df[col] = df[col].astype('int8')
                    elif c_min > -32768 and c_max < 32767:
                        df[col] = df[col].astype('int16')
                    elif c_min > -2147483648 and c_max < 2147483647:
                        df[col] = df[col].astype('int32')
                        
                elif str(col_type)[:5] == 'float':
                    # Try to convert to float32 if values fit
                    try:
                        df[col] = pd.to_numeric(df[col], downcast='float')
                    except:
                        pass
                        
            else:
                # Convert object columns to category if beneficial
                num_unique_values = len(df[col].unique())
                num_total_values = len(df[col])
                if num_unique_values / num_total_values < 0.5:
                    df[col] = df[col].astype('category')
                    
        return df
    
    @staticmethod
    def search_dataframe(df: pd.DataFrame, search_term: str, columns: List[str] = None) -> pd.DataFrame:
        """Fast search in DataFrame"""
        if columns is None:
            columns = df.columns
            
        # Convert search term to string
        search_term = str(search_term).lower()
        
        # Create boolean mask
        mask = pd.Series([False] * len(df))
        
        for col in columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                # String search
                mask |= df[col].astype(str).str.lower().str.contains(search_term, na=False)
            else:
                # Numeric search
                try:
                    numeric_search = float(search_term)
                    mask |= df[col] == numeric_search
                except ValueError:
                    pass
                    
        return df[mask]
    
    @staticmethod
    def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Get column statistics"""
        stats = {
            'name': column,
            'type': str(df[column].dtype),
            'null_count': df[column].isnull().sum(),
            'unique_count': df[column].nunique()
        }
        
        if pd.api.types.is_numeric_dtype(df[column]):
            stats.update({
                'min': df[column].min(),
                'max': df[column].max(),
                'mean': df[column].mean(),
                'std': df[column].std()
            })
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            stats.update({
                'min': df[column].min(),
                'max': df[column].max()
            })
        else:
            # String/categorical data
            value_counts = df[column].value_counts().head(5)
            stats['top_values'] = value_counts.to_dict()
            
        return stats
