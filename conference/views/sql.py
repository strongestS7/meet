from DBUtils.PooledDB import PooledDB
import pymysql
POOL=PooledDB(
    creator=pymysql,
    maxconnections = 10,
    mincached=1,
    maxcached=0,
    blocking=True,
    maxusage=None,
    ping=4,
    host='127.0.0.1',
    user='root',
    password='123',
    database='conference',
    charset='utf8'
)

class SQLHelper(object):

    @staticmethod
    def fetch_all(sql,args=None):
        conn = POOL.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql,args)
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def create_many(sql,args):
        conn=POOL.connection()
        cursor = conn.cursor()
        result=cursor.executemany(sql,args)
        conn.commit()
        conn.close()
        return result








