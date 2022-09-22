from decimal import Decimal
from ntpath import join
from readline import insert_text
from sqlite3 import Connection, Cursor, connect
from logging import debug, error, info, warning
from os.path import exists
import ipaddress
from typing import Any, List

class OIM_Database:
    def __init__(self, name: str = "oim_data.db") -> None:
        self.database_name: str = name
        self.database_path: str = f"db/{self.database_name}"
        try:
            self.database_connection: Connection = connect(self.database_path)
            if(self.database_connection is None):
                raise Exception("Database error. None returned!")
            self.database_cursor: Cursor = self.database_connection.cursor()
            debug(f"Connected to database {self.database_path}")
        except Exception as ex:
            error(f"Could not connect to database!\n{str(ex)}")
        if not exists(f"db/initialized"):
            try:
                self.create_tables()
                open(f"db/initialized",mode="a").close()
            except Exception as ex:
                error(f"Failed to initialize database!\n{str(ex)}")
        self.destinations = List[str]
        return


    def create_tables(self) -> None:
        try:
            self.database_cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS destinations (
                    dest_id INTEGER PRIMARY KEY,
                    dest_name TEXT UNIQUE NOT NULL
                );
                '''
            )
            info(f"Created destinations table in database")
            self.database_cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS pings (
                    ping_id INTEGER PRIMARY KEY,
                    destination TEXT UNIQUE NOT NULL,
                    timestamp REAL UNIQUE NOT NULL,
                    success INTEGER NOT NULL,
                    ip_long INTEGER,
                    packets_tx INTEGER,
                    packets_rx INTEGER,
                    ttl INTEGER,
                    test_time_s REAL,
                    FOREIGN KEY(destination)
                        REFERENCES destinations(dest_name)
                        ON DELETE CASCADE
                );
                '''
            )
            info(f"Created pings table in database")
        except Exception as ex:
            error(f"Could not create tables\n{ex}")
        return

    def get_known_destinations(self) -> List[str]:
        destinations = List[str]
        try:
            self.database_cursor.execute(
                f'''
                SELECT *
                FROM destinations;
                '''
            )
            results: Any = self.database_cursor.fetchall()
        except Exception as e:
            warning(f"Exception occurred when fetching data:\n{e}")
        for i in results:
            debug(i)
        return

    def save_ping_result(self,
        destination: str,
        timestamp: float,
        success: bool,
        ip_str: str = None,
        packets_tx: int = None,
        packets_rx: int = None,
        ttl: int = None,
        test_time_s: float = None,
        ) -> None:
        insert_string: str = "destination, timestamp, success"
        insert_list: List[Any] = [destination, str(timestamp), str(success)]
        if ip_str is not None:
            insert_string += ", ip_long"
            insert_list.append(str(int(ipaddress.ip_address(ip_str))))
        if packets_tx is not None:
            insert_string += ", packets_tx"
            insert_list.append(str(packets_tx))
        if packets_rx is not None:
            insert_string += ", packets_rx"
            insert_list.append(str(packets_rx))
        if ttl is not None:
            insert_string += ", ttl"
            insert_list.append(str(ttl))
        if test_time_s is not None:
            insert_string += ", test_time_s"
            insert_list.append(str(test_time_s))
        try:
            #self.database_cursor.execute(
            debug(
                f'''
                INSERT INTO pings
                ({insert_string})
                VALUES
                ({", ".join(insert_list)})
                ;
                '''
            )
        except Exception as e:
            warning(f"Exception occurred when fetching data:\n{e}")
        return