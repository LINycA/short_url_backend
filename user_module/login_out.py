import json
from hashlib import sha1
from common_module.util.connect_redis import sessions_cache
from common_module.util.current_strftime import current_strftime
from common_module.util.connect_mysql import exec_sql2dict
from common_module.util.password import decrypt_passwd
from tornado.web import RequestHandler
from traceback import format_exc

# 登录接口
class login(RequestHandler):
    def post(self):
        # self.set_header('Content-Type','application/json charset=utf-8;')
        self.set_header('Content-Type','application/json charset=utf-8;')
        real_ip = self.request.headers.get('X-Forwarded-For')
        try:
            params = json.loads(self.request.body)
            username = params.get('username')
            password = params.get('password')
        except Exception as e:
            print(format_exc())
        
        # 验证用户账号密码的函数
        def check_passwd(username:str,password:str) -> tuple:
            try:
                sql = f'select password,nickname,status from auth_user where username="{username}";'
                res = exec_sql2dict(sql=sql)
                if res != ():
                    passwd = res[0].get('password')
                    nickname = res[0].get('nickname')
                    user_status = res[0].get('status')
                    return decrypt_passwd(password,passwd),nickname,user_status
                else:
                    return False,None,None
            except:
                print(format_exc())

        # 获取用户角色id
        def get_user_role(username:str) -> list:
            sql = f'select roleid from user_role where username = "{username}";'
            res = exec_sql2dict(sql=sql)
            if res != ():
                return [i.get('roleid') for i in res]
            else:
                return None
        try:
            print(real_ip,username,'登录')
            pass_check,nickname,user_status = check_passwd(username=username,password=password)
            if pass_check and user_status == "启用":
                roleid_list = get_user_role(username=username)
                if roleid_list != None or roleid_list != []:
                    cur_time = current_strftime()
                    session_cookie = sha1((str(roleid_list)+cur_time).encode('utf-8')).hexdigest()
                    # 更新cookie缓存
                    redis_cli = sessions_cache()
                    redis_cli.hset(username,'roleid',str(roleid_list))
                    print(user_status)
                    redis_cli.hset(username,'status',user_status)
                    if redis_cli.hget(username,'session') != None:
                        redis_cli.delete(redis_cli.hget(username,'session'))
                    redis_cli.hset(username,'session',session_cookie)
                    redis_cli.expire(username,time=605000)
                    redis_cli.set(session_cookie,username)
                    redis_cli.expire(session_cookie,time=605000)
                    redis_cli.close()
                    # 设置浏览器cookie
                    self.set_cookie(name='short_url_session',value=session_cookie,expires_days=7)
                    print(nickname,session_cookie)
                    self.write({'ret':200,'msg':f'欢迎您，{nickname}!'})
                    return 
                else:
                    self.write({'ret':306,'msg':'用户名或密码错误'})
                    return 
            else:
                self.write({'ret':306,'msg':'用户名或密码错误'})
                return 
        except:
            print(format_exc())
      
# 登出接口
class logout(RequestHandler):
    def get(self):
        self.set_header('Content-Type','application/json charset=utf-8;')
        cookie = self.get_cookie('short_url_session')
        redis_cli = sessions_cache()
        if redis_cli.keys(cookie) != []:
            username = redis_cli.get(cookie)
            redis_cli.delete(cookie)
            redis_cli.delete(username)
            redis_cli.close()
            self.clear_cookie('short_url_session')
            self.write({'ret':200,'msg':'登出成功'})
            return
        else:
            self.write({'ret':306,'msg':'登出失败，参数错误'})
            return