import json
from tornado.web import RequestHandler
from common_module.util.connect_redis import permission_cache
from common_module.util.email_check import ensure_check_code
from common_module.clear_cookie import clear_cookie
from common_module.util.invite_code import ensure_invite_code
from common_module.util.password import encrypt_passwd
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit

class reset_pass(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        
        try:
            param = json.loads(self.request.body)
            username = param.get('username')
            email = param.get('email')
            passwd = param.get('password')
            check_code = param.get('check_code')
            if username is None or email is None or passwd is None or check_code is None or username == '' or email == '' or passwd == '' or check_code == '':
                self.write({'ret':306,'msg':'参数错误'})
                return
        except Exception as e:
            print(e)
            self.write({'ret':306,'msg':'参数错误'})
            return
        # 确认用户名是否存在
        def check_user_exists(username:str,email:str) -> bool:
            sql = f'select 1 from auth_user where username="{username}" and email="{email}";'
            res = exec_sql2dict(sql=sql)
            if res != ():
                return True
            return False
        # 更新用户密码
        def update_pass():
            password = encrypt_passwd(passwd=passwd)
            sql = f'update auth_user set password = "{password}";'
            res = exec_sql_commit(sql=sql)
            return res
        
        print(real_ip,'重置密码',username,email)
        if not username or len(username)<4 or len(username)>16 or not passwd or len(passwd)<6 or len(passwd)>16 or not check_code or len(check_code) != 32 or '@' not in email or len(email.split('@')) != 2 or email.split('@')[0] == '' or email.split('@')[1] == '':
            self.write({'ret':306,'msg':'参数错误'})
            return
        user_exists = check_user_exists(username=username,email=email)
        if not user_exists:
            self.write({'ret':203,'msg':'用户名与邮箱不匹配'})
            return

        redis_cli = permission_cache()
        mode = redis_cli.get('注册模式')
        redis_cli.close()
        print(mode)
        if mode == '邮箱':
            if ensure_check_code(email=email):
                res = update_pass()
                if res != 0:
                    clear_cookie(username=username)
                    self.write({'ret':200,'msg':'密码重置成功'})
                    return
                else:
                    self.write({'ret':203,'msg':'密码重置失败'})
                    return
            else:
                self.write({'ret':203,'msg':'验证码错误'})
                return
        elif mode == "邀请码":
            if ensure_invite_code(invite_code=check_code):
                res = update_pass()
                print(res)
                if res != 0:
                    clear_cookie(username=username)
                    self.write({'ret':200,'msg':'密码重置成功'})
                    return
                else:
                    self.write({'ret':203,'msg':'密码重置失败'})
                    return
            else:
                self.write({'ret':203,'msg':'邀请码不正确'})
                return
        else:
            self.write({'ret':306,'msg':'密码重置通道未开启'})
            return