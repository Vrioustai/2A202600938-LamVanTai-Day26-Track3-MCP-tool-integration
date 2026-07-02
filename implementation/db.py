import sqlite3
import json

class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""
    pass

class SQLiteAdapter:
    def __init__(self, db_path="app.db"):
        self.db_path = db_path
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def list_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            tables = [row['name'] for row in cursor.fetchall()]
        finally:
            conn.close()
        return tables
        
    def get_table_schema(self, table):
        self._validate_table(table)
        query = f"PRAGMA table_info({table});"
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
        return columns
        
    def _validate_table(self, table):
        tables = self.list_tables()
        if table not in tables:
            raise ValidationError(f"Invalid table: {table}")
            
    def _validate_columns(self, table, columns):
        schema = self.get_table_schema(table)
        valid_columns = {col['name'] for col in schema}
        for col in columns:
            if col not in valid_columns:
                raise ValidationError(f"Invalid column: {col} for table {table}")
                
    def _validate_metric(self, metric):
        allowed_metrics = {'COUNT', 'AVG', 'SUM', 'MIN', 'MAX'}
        if metric.upper() not in allowed_metrics:
            raise ValidationError(f"Invalid metric: {metric}")

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        self._validate_table(table)
        
        select_cols = "*"
        if columns:
            self._validate_columns(table, columns)
            select_cols = ", ".join(columns)
            
        query = f"SELECT {select_cols} FROM {table}"
        params = []
        
        if filters:
            # filters is a dictionary of col: value
            self._validate_columns(table, filters.keys())
            conditions = []
            for col, val in filters.items():
                conditions.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
            
        if order_by:
            self._validate_columns(table, [order_by])
            direction = "DESC" if descending else "ASC"
            query += f" ORDER BY {order_by} {direction}"
            
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
            
        return results

    def insert(self, table, values):
        self._validate_table(table)
        if not values:
            raise ValidationError("Values cannot be empty")
            
        self._validate_columns(table, values.keys())
        
        cols = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, list(values.values()))
            conn.commit()
            lastrowid = cursor.lastrowid
        finally:
            conn.close()
            
        return {"inserted": True, "id": lastrowid, "values": values}

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        self._validate_table(table)
        self._validate_metric(metric)
        
        metric_sql = metric.upper()
        if column:
            self._validate_columns(table, [column])
            select_clause = f"{metric_sql}({column}) AS value"
        else:
            if metric_sql != "COUNT":
                raise ValidationError(f"Column is required for metric {metric}")
            select_clause = "COUNT(*) AS value"
            
        if group_by:
            self._validate_columns(table, [group_by])
            select_clause = f"{group_by}, " + select_clause
            
        query = f"SELECT {select_clause} FROM {table}"
        params = []
        
        if filters:
            self._validate_columns(table, filters.keys())
            conditions = []
            for col, val in filters.items():
                conditions.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
            
        if group_by:
            query += f" GROUP BY {group_by}"
            
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
            
        return results
