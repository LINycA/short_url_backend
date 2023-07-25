import json

from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_many_sql,exec_sql2dict
from common_module.check_cookie import check_cookie
from common_module.util.connect_redis import sessions_cache

class user_role(RequestHandler):
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
        
        if "0" in per_list:
            # 查询用户角色信息
            if action == "user_role_list":
                username = params.get('username')
                res = self.user_role_list(username=username)
                self.write({'ret':200,'data':res})
                return
            # 修改用户角色信息
            elif action == "user_role_modify":
                username = params.get('username')
                add_role = params.get('add_role')
                del_role = params.get('del_role')
                if type(add_role) is not list or type(del_role) is not list:
                    self.write({'ret':306,'msg':'参数错误'})
                    return
                add_role_list = [[username,i] for i in add_role]
                del_role_list = [[username,i] for i in del_role]
                res,res1 = self.user_role_modify(add_role=add_role_list,del_role=del_role_list)
                # 用户角色信息修改，缓存
                self.user_role_modify_cache(username=username,add_role=add_role)
                if res != 0 or res1 != 0:
                    self.write({'ret':200,'msg':'用户角色修改完成'})
                    return
                else:
                    self.write({'ret':203,'msg':'用户角色修改失败'})
                    return
        else:
            self.write({'ret':203,'msg':'无权限'})
            return

    # 修改用户对应角色
    def user_role_modify(self,add_role:list,del_role:list) -> int:
        res = res1 = 0
        if add_role != []:
            sql = 'insert ignore into user_role(username,roleid) values(%s,%s);'
            res = exec_many_sql(sql=sql,values=add_role)
        if del_role != []:
            sql1 = 'delete from user_role where username=%s and roleid=%s;'
            res1 = exec_many_sql(sql=sql1,values=del_role)
        return res,res1
    # 用户角色修改，缓存
    def user_role_modify_cache(self,username:str,add_role:list):
        redis_cli = sessions_cache()
        if redis_cli.keys(username) != []:
            redis_cli.hset(username,'roleid',str(add_role))
        redis_cli.close()
    # 查询用户角色信息
    def user_role_list(self,username:str) -> list:
        redis_cli = sessions_cache()
        if redis_cli.keys(username) != []:
            res = eval(redis_cli.hget(username,'roleid'))
            redis_cli.close()
        else:
            redis_cli.close()
            sql = f'select roleid from user_role where username="{username}";'
            res = [i.get('roleid') for i in exec_sql2dict(sql=sql)]
        return res