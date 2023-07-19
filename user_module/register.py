from tornado.web import RequestHandler
from common_module.util.password import encrypt_passwd
from common_module.util.connect_mysql import exec_sql_commit
from common_module.util.email_check import send_check_code,ensure_check_code
from common_module.util.invite_code import ensure_invite_code
import json
from common_module.util.connect_redis import permission_cache

class register(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        self.set_header('Content-Type','application/json charset=utf-8;')
        try:
            params = json.loads(self.request.body)
            action = params.get('action')
            data = params.get('data')
        except:
            self.write({'ret':306,'msg':'参数错误'})
            return
        try:
            redis_cli = permission_cache()
            status = redis_cli.get('用户注册')
            user_type = redis_cli.get('注册默认角色')
            mode = redis_cli.get('注册模式')
            redis_cli.close()
            if not status or not user_type or status != '开启' or user_type == '':
                self.write({'ret':406,'msg':'注册通道未开启,请联系管理员'})
                return
        except:
            self.write({'ret':406,'msg':'注册通道未开启,请联系管理员'})
            return
        # 验证注册通道是否开启
        if status != None or status != '关闭':
            # 获取验证码
            if action == "get_check_code":
                if mode == '邮箱':
                    print(real_ip,'获取验证码')
                    email = data.get('email')
                    if len(email.split('@')) > 2:
                        self.write({'ret':306,'msg':'参数错误'})
                        return
                    if email.split('@')[0] == '' or email.split('@')[1] == "":
                        self.write({'ret':306,'msg':'参数错误'})
                        return
                    if send_check_code(email):
                        self.write({'ret':200,'msg':'验证码发送成功，验证码10分钟内有效'})
                        return
                    else:
                        self.write({'ret':306,'msg':'验证码已发送，请10分钟后再试'})
                        return
                elif mode == "邀请码":
                    self.write({'ret':203,'msg':'请联系管理员获取邀请码'})
                    return
            # 验证验证码并写入数据库
            if action == "register":
                print(real_ip,'账号注册')
                username = data.get('username')
                password = data.get('password')
                nickname = data.get('nickname')
                email = data.get('email')
                check_code = data.get('check_code')
                if not username or len(username)<4 or len(username)>16 or not password or len(password)<6 or len(password)>16 or not password or not nickname or len(nickname)<4 or len(nickname)>16 or not check_code or len(check_code) != 32 or '@' not in email or len(email.split('@')) != 2 or email.split('@')[0] == '' or email.split('@')[1] == '':
                    self.write({'ret':306,'msg':'参数错误'})
                    return
                # 邮箱验证模式
                if mode == "邮箱":
                    if ensure_check_code(email=email,check_code=check_code):
                        password = encrypt_passwd(passwd=password)
                        sql = f'insert ignore into auth_user(username,password,nickname,email) values("{username}","{password}","{nickname}","{email}");'
                        res = exec_sql_commit(sql=sql)
                        sql1 = f'insert ignore into user_role(username,roleid) values("{username}","{user_type}");'
                        res1 = exec_sql_commit(sql=sql1)
                        if not res or not res1:
                            self.write({'ret':306,'msg':'注册失败'})
                            return
                        self.write({'ret':200,'msg':'注册成功'})
                        return
                    else:
                        self.write({'ret':305,'msg':'验证码错误'})
                        return
                # 邀请码模式
                elif mode == "邀请码":
                    if ensure_invite_code(invite_code=check_code):
                        password = encrypt_passwd(passwd=password)
                        sql = f'insert ignore into auth_user(username,password,nickname,email) values("{username}","{password}","{nickname}","{email}");'
                        res = exec_sql_commit(sql=sql)
                        sql1 = f'insert ignore into user_role(username,roleid) values("{username}","{user_type}");'
                        res1 = exec_sql_commit(sql=sql1)
                        if not res or not res1:
                            self.write({'ret':306,'msg':'注册失败'})
                            return
                        self.write({'ret':200,'msg':'注册成功'})
                        return
                    else:
                        self.write({'ret':305,'msg':'验证码错误'})
                        return
        else:
            self.write({'ret':406,'msg':'注册通道未开启,请联系管理员'})
            return
