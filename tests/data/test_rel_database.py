import io

# Standard Dist
import pytest

# Third Party Imports
import sqlalchemy

# Project Level Imports

from cvp.data.rel_database import *

TEST_DB_PATH = 'tests/data/test.db'
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

class TestRelDatabase():

    @pytest.fixture
    def db(self):
        DB_PATH = 'tests/data/test.db'
        db = Database(DB_PATH)
        return db

    @pytest.fixture
    def table_name1(self):
        return 'table1'

    @pytest.fixture
    def table_name2(self):
        return 'table2'

    def test_init(self, db):
        #=== Test Inputs ===#
        DB_PATH = 'tests/data/test.db'

        #=== Trigger Output ===#
        conn = db.conn
        engine = db.engine
        cursor = db.cursor

        assert os.path.exists(DB_PATH)

        assert conn is not None and isinstance(db.conn, sqlite3.Connection)
        assert engine is not None and isinstance(db.engine, sqlalchemy.engine.base.Engine)
        assert cursor is not None and isinstance(db.cursor, sqlite3.Cursor)

        db.close_connection()

    def test_close_connection(self, db):
        # === Trigger Output ===#
        db.close_connection()

        with pytest.raises(Exception):
            db.select('*', 'name')

    def test_create_table(self, db, table_name1, table_name2):
        #=== Test Inputs ===#
        attr1 = {
            'id': 'INTEGER NOT NULL PRIMARY KEY',
            'sentence': 'VARCHAR'
        }
        attr2 = {
            'id': 'INTEGER NOT NULL PRIMARY KEY',
            'status': 'VARCHAR NOT NULL'
        }
        foreign_key = {
            'id': 'table1 (id)'
        }

        # === Trigger Output ===#
        db.create_table(attr1, table_name1)
        db.create_table(attr2, table_name2, foreign_key)

        empty1 = db.select('*', table_name1)
        empty2 = db.select('*', table_name2)

        # Check if table is created and there no values in the table
        # If table exists, db.select won't raise error and fail the test
        # If a returned list is not empty, the assert below will fail
        assert not empty1
        assert not empty2

        db.close_connection()

    def test_insert(self, db, table_name1, table_name2):
        #=== Test Inputs ===#
        values1 = (1, 'Dummy Sentence')
        values2 = (1, 'Dummy')

        #=== Trigger Output ===#
        db.insert(values1, table_name1)
        db.insert(values2, table_name2)

        selection1 = db.select('*', table_name1)
        selection2 = db.select('*', table_name2)

        assert selection1 and selection2

        id1, id2 = selection1[0][0], selection2[0][0]
        sentence, status = selection1[0][1], selection2[0][1]

        assert id1 == values1[0]
        assert id2 == values2[0]
        assert sentence == values1[1]
        assert status == values2[1]

        with pytest.raises(Exception):
            wrong_table = 'wrong_table'
            db.insert(values1, wrong_table)

        db.close_connection()

    def test_select(self, db, table_name1):
        #=== Expected Output ===#
        expected = (1, 'Dummy Sentence')
        condition = 'id = 1'

        #=== Trigger Output ===#
        selection = db.select('*', table_name1, condition)

        assert selection

        id = selection[0][0]
        sentence = selection[0][1]

        assert id == expected[0]
        assert sentence == expected[1]

        with pytest.raises(Exception):
            WRONG_COL = 'WRONG_COL'
            selection = db.select(WRONG_COL, table_name1)

        db.close_connection()

    def test_update(self, db, table_name1):
        # === Test Inputs ===#
        values = ('Updated Dummy',)
        table_col = ('sentence',)
        condition = 'id = 1'

        # === Trigger Output ===#
        db.update(values, table_col, table_name1, condition)

        selection = db.select('*', table_name1)

        assert selection

        id = selection[0][0]
        sentence = selection[0][1]

        assert id == 1
        assert sentence == values[0]

        with pytest.raises(Exception):
            WRONG_COL = ('WRONG_COL',)
            db.update(values, WRONG_COL, table_name1, condition)

        with pytest.raises(Exception):
            WRONG_TABLE = 'WRONG_TABLE'
            db.update(values, table_col, WRONG_TABLE, condition)

        with pytest.raises(Exception):
            WRONG_CONDITION = 'WRONG_CONDITION'
            db.update(values, table_col, table_name1, WRONG_CONDITION)

        db.close_connection()

    def test_delete(self, db, table_name2):
        # === Test Inputs ===#
        condition = 'id = 1'

        # === Trigger Output ===#
        db.delete(table_name2, condition)

        selection = db.select('*', table_name2)

        # Check if table is empty
        assert not selection

        with pytest.raises(Exception):
            WRONG_TABLE = 'WRONG_TABLE'
            db.delete(WRONG_TABLE, condition)

        with pytest.raises(Exception):
            WRONG_CONDITION = 'WRONG_CONDITION'
            db.delete(table_name2, WRONG_CONDITION)

    def test_main(self):
        #=== Test Inputs ===#
        account_path = 'tests/data/test_accounts.txt'
        hist_log_path = 'tests/data/hist_log.csv'
        test_db_path = {
            'cvp': 'tests/data/test_cvp.db',
            'cdc': 'tests/data/test_cdc.db'
        }
        if os.path.exists(test_db_path.get('cvp')):
            os.remove(test_db_path.get('cvp'))

        if os.path.exists(test_db_path.get('cdc')):
            os.remove(test_db_path.get('cdc'))

        # === Expected Output ===#
        df = pd.read_csv(account_path, sep='\t')
        cvp_expected_size = df.shape[0]
        cdc_expected_size = df.shape[0] + 4

        # === Trigger Output ===#
        main(test_db_path, account_path, hist_log_path)

        db = Database(test_db_path.get('cvp'))
        selection1 = db.select('COUNT(*)', 'profile')
        selection2 = db.select('COUNT(*)', 'account')
        profile_size = selection1[0][0]
        account_size = selection2[0][0]

        assert profile_size == cvp_expected_size
        assert account_size == cvp_expected_size

        db = Database(test_db_path.get('cdc'))
        selection1 = db.select('COUNT(*)', 'profile')
        profile_size = selection1[0][0]
        assert profile_size == cdc_expected_size

        assert os.path.exists(hist_log_path)


        with pytest.raises(FileNotFoundError):
            WRONG_PATH = "WRONG/PATH"
            main(test_db_path, WRONG_PATH)


