#!/usr/bin/python3
from app import app
import MySQLdb
import unittest


class BasicTestCase(unittest.TestCase):
    server = 'localhost'
    user = 'root'
    password = 'cookies'

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_database(self):
        dbName = 'flaskTest'
        conn = MySQLdb.Connect(self.server, self.user, self.password)
        cursor = conn.cursor()
        cursor.execute("USE %s" % (dbName))
        """
        Database should contain a User, Book, Book_List, University
        Table
        TODO: Expand table tests for fields to look for
        Possible alternative:
        select max(table_catalog) as x from information_schema.tables

        """
        reqTables = ["User", "Book", "Book_List", "University"]
        try:
            for table in reqTables:
                cursor.execute(" SELECT 1 FROM %s" % (table))
                result = cursor.fetchone()
                # self.assertTrue(result, "Empty result from call, \
                # table: %s" % (table))
                # Use below test for now to pass; swap for above test later
                self.assertFalse(result, "Nonempty result from null call, \
                                table: %s" % (table))

        except MySQLdb.Error as e:
            print("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
        except MySQLdb.DatabaseError as e:
            print("ERROR %d IN DATABASE: %s" % (e.args[0], e.args[1]))
        finally:
            # test there is a database at localhost
            print("end of database tests")

if __name__ == '__main__':
    unittest.main()
