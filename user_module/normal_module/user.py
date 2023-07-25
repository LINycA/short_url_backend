import json

from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit
from common_module.util.connect_redis import sessions_cache
from common_module.check_cookie import check_cookie

class user(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        self.set_header('Content-Type','application/json charset=utf-8;')
        try:
            params = json.loads(self.request.body)
            action = params.get('action')
        except:
            self.write({'ret':306,'msg':'参数错误'})
            return
        username,per_list = check_cookie(obj=self)
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list})
            return
        print(real_ip,username,'用户操作')
        # 查询用户信息
        if action == "user_list":
            res = self.user_list(username=username)
            self.write({'ret':200,'data':res})
            return
        # 修改用户信息
        elif action == "user_modify":
            email = params.get('email')
            nickname = params.get('nickname')
            res = self.user_modify(username=username,email=email,nickname=nickname)
            if res == 1:
                self.write({'ret':200,'msg':'信息修改完成'})
                return
            else:
                self.write({'ret':203,'msg':'信息修改失败'})
                return
    # 获取用户信息
    def user_list(self,username:str) -> list:
        sql = f'select username,nickname,email from auth_user where username="{username}";'
        res = exec_sql2dict(sql=sql)
        return res
    # 修改用户信息
    def user_modify(self,nickname:str,email:str,username:str) -> int:
        try:
            sql = f'update auth_user set nickname="{nickname}",email="{email}" where username="{username}";'
            res = exec_sql_commit(sql=sql)
            return res
        except:
            return 0