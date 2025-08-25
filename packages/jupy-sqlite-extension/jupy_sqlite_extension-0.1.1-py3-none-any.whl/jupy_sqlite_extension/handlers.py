import io
import json
import os
import sqlite3
from pathlib import Path

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from rich import box
from rich.console import Console
from rich.table import Table


def format_table_with_rich(columns, rows, max_rows=25):
    """
    Format query results as ASCII table using rich library.

    Args:
        columns: List of column names
        rows: List of row tuples
        max_rows: Maximum number of rows to display

    Returns:
        Formatted string with ASCII table and truncation message if needed
    """
    total_rows = len(rows)
    display_rows = rows[:max_rows]

    # Create rich table with ASCII box style
    table = Table(box=box.ASCII, show_header=True)

    # Add columns with proper alignment and no truncation
    for col in columns:
        # Check if column contains numeric data (right-align numbers)
        is_numeric = False
        if display_rows:
            col_index = columns.index(col)
            sample_values = [row[col_index] for row in display_rows[:5] if row[col_index] is not None]
            is_numeric = all(isinstance(val, (int, float)) for val in sample_values) if sample_values else False

        table.add_column(col, justify='right' if is_numeric else 'left', overflow='fold')

    # Add rows to table
    for row in display_rows:
        table.add_row(*[str(val) if val is not None else '' for val in row])

    # Create console for plain ASCII output (no colors/formatting)
    console = Console(file=io.StringIO(), force_terminal=False, legacy_windows=False)
    console.print(table)
    output = console.file.getvalue().rstrip()

    # Add truncation message if needed
    if total_rows > max_rows:
        output += f'\n(Output limit exceeded, {max_rows} of {total_rows} total rows shown)'

    return output


class RouteHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "This is /jupy-sqlite-extension/get-example endpoint!"
        }))

class SQLExecuteHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            data = json.loads(self.request.body)
            sql = data.get('sql', '').strip()
            db_file = data.get('db_file', '')

            if not sql:
                self.finish(json.dumps({
                    "error": "No SQL statement provided"
                }))
                return

            if not db_file:
                self.finish(json.dumps({
                    "error": "No database file specified"
                }))
                return

            # Ensure db_file is relative to current working directory for security
            db_path = Path(db_file)
            if db_path.is_absolute():
                self.finish(json.dumps({
                    "error": "Database file must be a relative path"
                }))
                return

            # Check if database file exists
            if not os.path.exists(db_file):
                self.finish(json.dumps({
                    "error": f"Database file '{db_file}' not found"
                }))
                return

            # Execute SQL
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            try:
                cursor.execute(sql)

                # Check if this is a SELECT statement
                if sql.upper().strip().startswith('SELECT'):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    conn.close()

                    # Format table using rich library
                    formatted_output = format_table_with_rich(columns, rows)

                    self.finish(json.dumps({
                        "formatted_output": formatted_output
                    }))
                else:
                    # For INSERT, UPDATE, DELETE, etc.
                    conn.commit()
                    rows_affected = cursor.rowcount
                    conn.close()

                    self.finish(json.dumps({
                        "message": f"Query executed successfully. {rows_affected} row(s) affected."
                    }))

            except sqlite3.Error as e:
                conn.close()
                self.finish(json.dumps({
                    "error": f"SQLite error: {str(e)}"
                }))

        except json.JSONDecodeError:
            self.finish(json.dumps({
                "error": "Invalid JSON in request body"
            }))
        except Exception as e:
            self.finish(json.dumps({
                "error": f"Server error: {str(e)}"
            }))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]

    route_pattern = url_path_join(base_url, "jupy-sqlite-extension", "get-example")
    sql_execute_pattern = url_path_join(base_url, "jupy-sqlite-extension", "execute-sql")

    handlers = [
        (route_pattern, RouteHandler),
        (sql_execute_pattern, SQLExecuteHandler)
    ]
    web_app.add_handlers(host_pattern, handlers)
