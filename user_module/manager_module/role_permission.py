import json
from tornado.web import RequestHandler
from common_module.check_cookie import check_cookie
from common_module.util.connect_redis import permission_cache
from common_module.util.connect_mysql import exec_many_sql,exec_sql2dict
from traceback import format_exc

class role_permission(RequestHandler):
    def post(self):
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
        print(username,'修改权限')
        if "0" in per_list:
            # 角色权限列表
            if action == "role_per_list":
                try:
                    role_id = str(params.get('id'))
                    res = self.role_per_list(roleid=role_id)
                    if res != ():
                        self.write({'ret':200,'data':res})
                        return
                    else:
                        self.write({'ret':203,'msg':'查询失败'})
                        return
                except:
                    print(format_exc())
                    self.write({'ret':203,'msg':'查询失败'})
                    return
            # 修改角色的权限
            if action == "role_per_modify":
                role_id = str(params.get('id'))
                add_per = params.get('add_per')
                del_per = params.get('del_per')
                if role_id == "0":
                    self.write({'ret':203,'msg':'该角色权限无法修改'})
                    return
                if type(add_per) is not list or type(del_per) is not list:
                    self.write({'ret':306,'msg':'参数错误'})
                    return
                add_per_list = [[role_id,i] for i in add_per]
                del_per_list = [[role_id,i] for i in del_per]
                res,res1 = self.role_per_modify(add_per=add_per_list,del_per=del_per_list)
                # 缓存中，角色权限信息修改
                self.role_per_modify_cache(roleid=role_id,add_per=add_per)
                if res != 0 or res1 != 0:
                    self.write({'ret':200,'msg':'权限修改完成'})
                    return
                else:
                    self.write({'ret':203,'msg':'权限修改失败'})
                    return
        else:
            self.write({'ret':203,'msg':'没有权限'})
            return

    # 执行角色权限添加与删除的sql语句
    def role_per_modify(self,add_per:list,del_per:list) -> int:
        res = res1 = 0
        if add_per != []:
            sql = 'insert ignore into role_permission(roleid,permissionid) values(%s,%s);'
            res = exec_many_sql(sql=sql,values=add_per)
        if del_per != []:
            sql1 = 'delete from role_permission where roleid="%s" and permissionid="%s";'
            res1 = exec_many_sql(sql=sql1,values=del_per)
        return res,res1
    # 角色权限修改，缓存
    def role_per_modify_cache(self,roleid:str,add_per:list):
        redis_cli = permission_cache()
        redis_cli.set('role_'+roleid,str(add_per))
        redis_cli.close()
    # 角色权限查询
    def role_per_list(self,roleid:str) -> list:
        redis_cli = permission_cache()
        res = redis_cli.get('role_'+roleid)
        if res != None:
            res = eval(res)
        else:
            res = []
        redis_cli.close()
        return res