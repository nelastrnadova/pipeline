import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, db_file: str = "database.db"):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            raise e
        self.cursor = self.conn.cursor()

    def single_select(
        self,
        table: str,
        to_select: list,
        where_fields: [str] = None,
        where_values: list = None,
    ):
        return self.select(table, to_select, where_values, where_fields)[0]

    def select(
        self,
        table: str,
        to_select: list,
        where_fields: [str] = None,
        where_values: list = None,
    ):
        if where_fields is not None:
            self.cursor.execute(
                f"SELECT {', '.join(to_select)} FROM {table} WHERE {', '.join([field + ' = ?' for field in where_fields])}",
                where_values,
            )
        else:
            self.cursor.execute(f"SELECT {', '.join(to_select)} FROM {table}")
        return self.cursor.fetchall()

    def update(
        self,
        table: str,
        set_fields: [str],
        set_values: list,
        where_fields: [str] = None,
        where_values: list = None,
    ):
        if where_fields is not None:
            values = set_values + where_values
            self.cursor.execute(
                f'UPDATE {table} SET {", ".join([field + " = ?" for field in set_fields])} WHERE {", ".join([field + " = ?" for field in where_fields])}',
                values,
            )
        else:
            self.cursor.execute(
                f'UPDATE {table} SET {", ".join([field + " = ?" for field in set_fields])}',
                set_values,
            )

    def delete(self, table: str, where_fields: [str], where_values: list):
        self.cursor.execute(
            f'DELETE from {table} WHERE {", ".join([field + " = ?" for field in where_fields])}',
            where_values,
        )

    def exec(self, command: str):
        self.cursor.execute(command)
