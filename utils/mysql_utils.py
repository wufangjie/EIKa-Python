import numpy as np
import mysql.connector
import json
import os


try:
    PATH = os.path.split(os.path.realpath(__file__))[0]
except NameError:
    PATH = os.getcwd() or os.getenv('PWD')

with open(os.path.join(PATH, '.config'), 'rt', encoding='utf-8') as f:
    config = json.load(f)


class ConnectMysqlGetCursor:
    def __init__(self, database='',
                 user='', password='',
                 host='', port=3306,
                 default_config='mysql_ml',
                 raise_on_warnings=True, autocommit=True, **kwargs):
        self.params = locals()
        for useless in ['self', 'kwargs', 'default_config']:
            self.params.pop(useless)
        for k, v in config.get(default_config, {}).items():
            if not self.params[k]:
                self.params[k] = v
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = mysql.connector.connect(**self.params)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, *args):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()


def iter_buf_to_numpy(cur, buf_size=50000, dtype=None, output=True):
    """
    Get large data from mysql.

    list is fast to append, but its extension is exponential,
    while numpy is tight but slow to append.
    """
    # TODO: use ProgressBar
    assert buf_size >= 10000
    ret = []
    temp = []
    for i, row in enumerate(cur, 1):
        temp.append(row)
        if i % buf_size == 0: # and temp: # temp may be empty
            if output:
                print('#', end='', flush=True)
            ret.append(np.array(temp, dtype=dtype))
            temp.clear()
    if temp:
        ret.append(np.array(temp, dtype=dtype))
    if ret:
        if output:
            print()
        return np.concatenate(ret)
    else:
        return np.array([], dtype=dtype)
