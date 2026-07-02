import json
import os
from fastmcp import FastMCP
from db import SQLiteAdapter, ValidationError

# Create the server object.
mcp = FastMCP("SQLite Lab MCP Server")

# Initialize database path. We will assume app.db is in the same directory for this lab.
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
adapter = SQLiteAdapter(DB_PATH)

@mcp.tool(name="search", description="Search for rows in a database table")
def search(table: str, filters: dict = None, columns: list[str] = None, limit: int = 20, offset: int = 0, order_by: str = None, descending: bool = False) -> str:
    """
    Search for rows in a database table.
    """
    try:
        results = adapter.search(
            table=table, 
            columns=columns, 
            filters=filters, 
            limit=limit, 
            offset=offset, 
            order_by=order_by, 
            descending=descending
        )
        return json.dumps({"status": "success", "data": results}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Internal error: {str(e)}"})

@mcp.tool(name="insert", description="Insert a new row into a database table")
def insert(table: str, values: dict) -> str:
    """
    Insert a new row into a database table.
    """
    try:
        result = adapter.insert(table=table, values=values)
        return json.dumps({"status": "success", "data": result}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Internal error: {str(e)}"})

@mcp.tool(name="aggregate", description="Compute aggregate metrics (COUNT, AVG, SUM, MIN, MAX) on a table")
def aggregate(table: str, metric: str, column: str = None, filters: dict = None, group_by: str = None) -> str:
    """
    Compute aggregate metrics (COUNT, AVG, SUM, MIN, MAX) on a table.
    """
    try:
        results = adapter.aggregate(
            table=table, 
            metric=metric, 
            column=column, 
            filters=filters, 
            group_by=group_by
        )
        return json.dumps({"status": "success", "data": results}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Internal error: {str(e)}"})


@mcp.resource("schema://database")
def database_schema() -> str:
    """
    Get the schema for all tables in the database.
    """
    try:
        tables = adapter.list_tables()
        schema = {}
        for table in tables:
            schema[table] = adapter.get_table_schema(table)
        return json.dumps(schema, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """
    Get the schema for a specific table in the database.
    """
    try:
        schema = adapter.get_table_schema(table_name)
        return json.dumps(schema, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # run stdio by default
    mcp.run()
