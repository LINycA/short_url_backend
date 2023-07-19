import json
from common_module.util.connect_redis import client_ip_cache
from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict

class check_username(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        redis_cli = client_ip_cache()
        if redis_cli.keys(real_ip) != []:
            redis_cli.close()
            self.write({'ret':203,'msg':'请稍后再试'})
            return
        # ip地址隔离，防止爆破查询，ddos
        redis_cli.set(real_ip,'')
        redis_cli.expire(real_ip,10)
        redis_cli.close()
        print(real_ip,'查询用户名可用性')
        self.set_header('Content-Type','application/json charset=utf-8;')
        params = json.loads(self.request.body)

        username = params.get('username')
        if not username or username == "" or type(username) != str:
            self.write({'ret':306,'msg':'参数错误'})
            return
        if len(username) < 4 or len(username) > 16:
            self.write({'ret':200,'msg':'用户名不可用'})
            return    
        sql = f'select 1 from auth_user where username="{username}";'
        res = exec_sql2dict(sql=sql)
        if res == ():
            self.write({'ret':200,'msg':'用户名可用'})
            return
        self.write({'ret':200,'msg':'用户名不可用'})
        return