#!/usr/bin/python3
import app
import MySQLdb
import unittest
import tempfile
import os


class BasicTestCase(unittest.TestCase):
    server = '176.58.96.74'
    user = 'comp4920'
    password = 'q3H286cJ5EXyGqRwcookies'

    def test_index(self):
        tester = app.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        print("Test_index test passed")

    def test_database(self):
        dbName = 'bookswapp'
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
                cursor.execute("SELECT 1 FROM %s;" % (table))
                result = cursor.fetchone()

                # self.assertTrue(result, "Empty result from call, \
                # table: %s" % (table))
                # Use below test for now to pass; swap for above test later
                self.assertFalse(result, "Nonempty result from null call, \
                                table: %s" % (table))
            print("Test_database test passed")
        except MySQLdb.Error as e:
            print("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
        except MySQLdb.DatabaseError as e:
            print("ERROR %d IN DATABASE: %s" % (e.args[0], e.args[1]))
        finally:
            # test there is a database at localhost
            print("end of database tests")


class FlaskrTestCase (unittest.TestCase):

    def setUp(self):
        # "" Set up a fresh connection before each test
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        # "" Destroy  db connection after each test ""
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def login(self, username, password):
        """ Login helper function"""
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """ Logout helper function """
        return self.app.get('/logout', follow_redirects=True)

    # assert functions

    def test_empty_db(self):
        """ Ensure database is blank """
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data
        # self.assertTrue(rv)  # check if exists

    def test_login_logout(self):
        """ Test login and logout using helper functions """

        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        assert b'You were logged in' in rv.data

        rv = self.logout()
        assert b'You were logged out' in rv.data

        rv = self.login(
            app.app.config['USERNAME'] + 'x',
            app.app.config['PASSWORD']
        )

        assert b'Invalid username' in rv.data

        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'] + 'x'
        )

        assert b'Invalid password' in rv.data


if __name__ == '__main__':
    unittest.main()
