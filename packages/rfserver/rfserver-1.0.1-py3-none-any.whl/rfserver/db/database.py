"""
Database connector with searching capabilties.

This module contains a class that tries to connect to the database, if the database was missing it will call the create_db() function to create one.
It also provides a method to search inside the database for a specific range of the data.
"""

import os.path
import sqlite3
from pathlib import Path

from rfserver.db.create_database import create_db

s = os.path.dirname(__file__)
p = Path(s).parent.parent.parent.joinpath("database")

# class RowDataBaseManager():
#    db_raw_path = str(p) + os.path.sep + "raw.db" # raw database
#
#    def __init__(self)->None:
#        pass
#
#    @classmethod
#    def insert_high_power_frequency(cls,data:str)->None:
#        con = sqlite3.connect(cls.db_raw_path)
#        cur = con.cursor()
#        cur.execute("INSERT INTO HighPowerFrequency VALUES(NULL,?)", (data,))
#        con.commit()
#        con.close() # not effecient
#
#    @classmethod
#    def insert_high_power_sample(cls,data:str)->None:
#        con = sqlite3.connect(cls.db_raw_path)
#        cur = con.cursor()
#        cur.execute("INSERT INTO HighPowerSample VALUES(NULL,?)", (data,))
#        con.commit()
#        con.close() # not effecient


class DetailDataBaseManager:
    """
    Connect to the database.
    Call the create_db() to create one if database not found.
    """

    db_detail_path = str(s) + os.path.sep + "detail.db"  # detail database
    if not os.path.exists(db_detail_path):
        create_db()

    @classmethod
    def search_power_frequency(
        cls, min_power: float, max_power: float, min_frequency: float, max_frequency: float
    ) -> list[tuple[int, float, float, str]]:
        """
        Fetch data readings from the database within a power and frequency range.

        Args:
            min_power (float): The minimum power in the range.
            max_power (float): The maximum power in the range.
            min_frequency (float): The minimum frequency in the range.
            max_frequency (float): The maximum frequency in the range.

        Returns:
            list: A list of tuples, were each tuple contains:
                - int: Record ID.
                - float: Power value.
                - float: Frequency value.
                - str: Timestamp of the reading.

        Example:
            >>> from database import DetialDataBaseManager
            >>> DetialDataBaseManager.search_power_frequency(20.12, 20.54, 103.7, 105.1)
            >>> [(90, 103.7, 20.54, '06-06-2025 12:16:18'), (91, 104.3, 20.18, '06-06-2025 12:16:18')]
        """
        con = sqlite3.connect(cls.db_detail_path)
        cur = con.cursor()
        cur.execute(
            "select * from Frequency where frequency BETWEEN :min_f AND :max_f AND power BETWEEN :min_p AND :max_p;",
            {
                "max_f": max_frequency,
                "max_p": max_power,
                "min_f": min_frequency,
                "min_p": min_power,
            },
        )
        result = cur.fetchall()
        con.commit()
        con.close()  # not effecient

        return result
