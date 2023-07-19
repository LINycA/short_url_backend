import json
from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit

class change_pass(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        try:
            params = json.loads(self.request.body)
        except Exception as e:
            print(e)