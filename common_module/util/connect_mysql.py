import pymysql
import json
from pymysql.cursors import DictCursor

with open('./config/mysql.config','r',encoding='utf-8') as f:
    mysql_dict = json.loads(f.read())
HOST = mysql_dict.get('host')
PORT = mysql_dict.get('port')
USER = mysql_dict.get('user')
PASSWD = mysql_dict.get('password')
DB = mysql_dict.get('db')


con = lambda : pymysql.connect(host=HOST,port=PORT,user=USER,password=PASSWD,database=DB,cursorclass=DictCursor)

# 执行sql语句返回字典
def exec_sql2dict(sql:str):
    con1 = con()
    with con1.cursor() as cur:
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
    con1.close()
    return res

# 执行sql语句并提交事务
def exec_sql_commit(sql:str) -> int:
    con2 = con()
    with con2.cursor() as cur:
        rows = cur.execute(sql)
        con2.commit()
        cur.close()
    con2.close()
    return rows

# 执行多个重复的sql语句，常用于插入值或更新数据
def exec_many_sql(sql:str,values:list) -> int:
    con3 = con()
    with con3.cursor() as cur:
        rows = cur.executemany(sql,values)
        con3.commit()
        cur.close()
    con3.close()
    return rows

if __name__ == "__main__":
    sql = 'select 1 from auth_user where username="arn";'
    res = exec_sql2dict(sql=sql)
    print(res)