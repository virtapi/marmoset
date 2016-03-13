from marmoset import config as config_reader
import sqlite3
import datetime


config = config_reader.load()
DB = config['Installstatus'].get('SQLiteDB')


class DBHelper:

    @classmethod
    def _connect(cls):
        """
        connects to SQLite DB defined in marmoset config

        :return: sqlite3 connection to DB using a row cursor.
        """
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        cls._test_table_exists(con)
        return con

    @classmethod
    def _test_table_exists(cls, con):
        """
        Tests if the 'installstatus' table exists in DB,
        else it will be created.

        :param con: sqlite3 connection
        """
        result = con.execute("SELECT name FROM sqlite_master "
                             "WHERE type = 'table' AND name = 'installstatus'")
        result = result.fetchall()
        if len(result) == 0:
            cls._init_table(con)

    @classmethod
    def _init_table(cls, con):
        """
        Initializes the 'installstatus' table

        :param con: sqlite3 connection
        """
        with con:
            con.execute("CREATE TABLE IF NOT EXISTS installstatus("
                        "id INTEGER PRIMARY KEY,"
                        "date DATETIME DEFAULT CURRENT_TIMESTAMP,"
                        "uuid TEXT,"
                        "status TEXT)")

    @classmethod
    def insert_status(cls, uid, status):
        """
        Inserts a new status update into status table.

        :param uid: uuid of the installimage job
        :param status: the current status from installimage
        """
        con = cls._connect()
        with con:
            con.execute("INSERT INTO installstatus(uuid, status)"
                        "VALUES (?, ?)", (uid, status))
        con.close()

    @classmethod
    def get_history(cls, uid):
        """
        Receives a status update history for specified uuid

        :param uid: uuid of the installimage job
        :return: a list of status updates
        :rtype: list
        """
        con = cls._connect()
        with con:
            rows = con.execute("SELECT date, uuid, status "
                               "FROM installstatus "
                               "WHERE uuid = ? "
                               "ORDER BY date ASC", (uid,))
        rows = rows.fetchall()
        con.close()
        result = []
        for row in rows:
            result.append(dict(row))
        return result

    @classmethod
    def _get_all_entries(cls):
        """
        Get all status updates available in the 'installstatus' table
        Not really useful, escpecially in case of lots table entries, the
        returned list might become huge.

        TOBEDELETED!!!!

        :return: list of all installimage status updates
        :rtype: list
        """
        con = cls._connect()
        with con:
            rows = con.execute("SELECT date, uuid, status "
                               "FROM installstatus")
        rows = rows.fetchall()
        con.close()
        result = []
        for row in rows:
            result.append(dict(row))

    @classmethod
    def get_latest_status(cls, uid):
        """
        Gets the latest status update available in 'installstatus' table.

        :param uid: uuid of installimage job
        :return: latest status update
        :rtype: dict
        """
        con = cls._connect()
        with con:
            result = con.execute("SELECT date, uuid, status "
                                 "FROM installstatus "
                                 "WHERE uuid = ? "
                                 "ORDER BY date DESC LIMIT 1", (uid,))
        result = result.fetchone()
        con.close()
        if result is not None:
            result = dict(result)
        return result