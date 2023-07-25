import json

from tornado.web import RequestHandler
from common_module.util.connect_redis import sessions_cache
from common_module.check_cookie import check_cookie
from common_module.clear_cookie import clear_cookie
from common_module.util.password import encrypt_passwd
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit
from traceback import format_exc

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
        if "0" in per_list:
            # 查询用户列表
            if action == "user_list":
                res = self.user_list()
                self.write({'ret':200,'data':res})
                return
            # 增加用户
            elif action == "user_add":
                username = params.get('username')
                passwd = params.get('password')
                nickname = params.get('nickname')
                email = params.get('email')
                status = params.get('status')
                try:
                    if "@" not in email or len(username)<4 or len(username)>12 or len(passwd)<6 or len(passwd)>16 or len(nickname)<4 or len(nickname)>12 or (status != '启用' and status != '禁用'):
                        self.write({'ret':203,'msg':'参数错误'})
                        return
                    res = self.user_add(username=username,password=passwd,nickname=nickname,email=email,status=status)
                except Exception as e:
                    print(format_exc())
                    self.write({'ret':203,'msg':'参数错误'})
                    return
                if res == 1:
                    self.write({'ret':200,'msg':'用户添加成功'})
                    return
                else:
                    self.write({'ret':200,'msg':'用户添加失败'})
                    return
            # 删除用户
            elif action == "user_del":
                username = params.get('username')
                res = self.user_del(username=username)
                if res == 1:
                    self.write({'ret':200,'msg':'用户删除成功'})
                    return
                else:
                    self.write({'ret':200,'msg':'用户删除失败'})
                    return
            # 修改用户
            elif action == "user_modify":
                username = params.get('username')
                nickname = params.get('nickname')
                passwd = params.get('password')
                status = params.get('status')
                email = params.get('email')
                res = self.user_modify(username=username,nickname=nickname,status=status,password=passwd,email=email)             
                if res == 1:
                    self.write({'ret':200,'msg':'用户修改成功'})
                    return
                else:
                    self.write({'ret':200,'msg':'用户修改失败'})
                    return
        else:
            self.write({'ret':203,'msg':'没有权限'})
            return

    # 查询用户
    def user_list(self) -> list:
        sql = 'select username,nickname,email,status from auth_user;'
        res = exec_sql2dict(sql=sql)
        return res
    # 增加用户
    def user_add(self,username:str,password:str,nickname:str,email:str,status:str) -> int:
        password = encrypt_passwd(passwd=password)
        sql = f'insert ignore into auth_user(username,password,nickname,email,status) values("{username}","{password}","{nickname}","{email}","{status}");'
        res = exec_sql_commit(sql=sql)
        return res
    # 删除用户
    def user_del(self,username:str) -> int:
        sql = f'delete from auth_user where username="{username}";'
        res = exec_sql_commit(sql=sql)
        sql1 = f'delete from user_role where username="{username}";'
        exec_sql_commit(sql=sql1)
        clear_cookie(username=username)
        return res
    # 更新用户信息
    def user_modify(self,username:str,nickname:str,password:str,status:str,email:str) -> int:
        password = encrypt_passwd(passwd=password)
        redis_cli = sessions_cache()
        try:
            sql = f'update auth_user set nickname="{nickname}",password="{password}",status="{status}",email="{email}" where username="{username}";'
            res = exec_sql_commit(sql=sql)
            if redis_cli.keys(username) != []:
                redis_cli.hset(username,'status',status)
                redis_cli.close()
            redis_cli.close()
        except:
            res = 0
        return res