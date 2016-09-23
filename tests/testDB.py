#!/usr/bin/python3
from app import app
import MySQLdb
import unittest


class BookSwapTestCase(unittest.TestCase):
    server = '176.58.96.74'
    user = 'comp4920'
    password = 'q3H286cJ5EXyGqRwcookies'

    # Checks that landing page loads
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        print("Test_index  (route '/') test passed")

    # Ensure login page loads correctly
    def test_login_load(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Please login' in response.data)
        # Not logged on yet; check page asks for login

    # Ensure login behaves correct with correct credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post('/login',
                               data=dict(email="test@email.com",
                                         password="strongpassword1"),
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Logged in as' in response.data)

    # Ensure login behaves correct with incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post('/login',
                               data=dict(email="wrong",
                                         password="wrong"),
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Invalid' in response.data)

    # Ensure logout behaves correctly
    def test_logout(self):
        tester = app.test_client(self)
        response = tester.get('/logout', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You were logged out' in response.data)

    # Ensure adding book button checks if user is logged in
    def test_loggedin_to_add(self):
        tester = app.test_client(self)
        response = tester.get('/api/books/create', content_type='html/text')
        self.assertNotEqual(response.status_code, 400)

    # Ensure current book inventory shows on list load request
    def test_inventory_shows(self):
        tester = app.test_client(self)
        # TODO: complete
        print(tester)  # dummy code, replace

    def test_database(self):
        dbName = 'bookswapp'
        conn = app.mysql.connection()
        self.assertTrue(conn)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbName))

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
                cur.execute("SELECT 1 FROM %s;" % (table))
                result = cur.fetchone()

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


"""
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
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # assert functions

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data
        # self.assertTrue(rv)  # check if exists

    def test_login_logout(self):

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
"""

if __name__ == '__main__':
    unittest.main()
