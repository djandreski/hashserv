import json
import sqlite3
from flask import Flask, g

# Application imports
from hashserv.MerkleTree import MerkleTree


# Initialize the Flask application
app = Flask(__name__)
app.config['DATABASE'] = '/db/hashserv.db'


# Database code
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


class DataBlock:
    def __init__(self, block_num):
        """Validating and inserting data hashes into the database."""
        self.block_num = int(block_num)
        self.merkle_tree = MerkleTree()
        self.closed = False
        self.tx_id = None

    def close(self):
        self.closed = True

    def find_leaves(self):
        """Find leaves from database and generate tree."""
        g.db = connect_db()

        """Get the items for this block."""
        query = 'SELECT * FROM hash_table where block=? ORDER BY id DESC'
        cur = g.db.execute(query, (self.block_num,))

        for row in cur.fetchall():
            self.merkle_tree.add_hash(row[1])

    def merkle_root(self):
        """Find the data Merkle root."""
        if self.closed:
            return self.merkle_tree.merkle_root()

    def to_json(self):
        self.find_leaves()

        block_data = {
            'block_num': self.block_num,
            'closed': False,
            'merkle_root': self.merkle_root(),
            'tx_id': self.tx_id,
            'leaves': self.merkle_tree.leaves
        }

        return block_data
