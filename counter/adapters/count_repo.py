from typing import List

from pymongo import MongoClient
import psycopg2
from psycopg2 import sql

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountPostgresDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database, user, password):
        self.__host = host
        self.__port = port
        self.__database = database
        self.__user = user
        self.__password = password
    def __get_connection(self):
        """Establishes and returns a connection to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(
                dbname=self.__database,
                user=self.__user,
                password=self.__password,
                host=self.__host,
                port=self.__port,
            )
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise
    def read_values(
            self, object_classes: List[str] = None
    ) -> List[ObjectCount]:
        """Reads object counts from the PostgreSQL database."""
        conn = self.__get_connection()
        cursor = conn.cursor()
        object_counts = []

        try:
            if object_classes:
                query = sql.SQL(
                    "SELECT object_class, count FROM object_counts WHERE object_class IN %s"
                )
                cursor.execute(query, (tuple(object_classes),))
            else:
                query = "SELECT object_class, count FROM object_counts"
                cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                object_counts.append(ObjectCount(row[0], row[1]))

        except psycopg2.Error as e:
            print(f"Error reading from PostgreSQL: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        """Updates object counts in the PostgreSQL database."""
        conn = self.__get_connection()
        cursor = conn.cursor()

        try:
            for value in new_values:
                query = sql.SQL(
                    """
                    INSERT INTO object_counts (object_class, count)
                    VALUES (%s, %s)
                    """
                )
                cursor.execute(
                    query,
                    (value.object_class, value.count, value.count),
                )
            conn.commit()

        except psycopg2.Error as e:
            print(f"Error updating PostgreSQL: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
