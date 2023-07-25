import json
from common_module.check_cookie import check_cookie
from common_module.util.connect_redis import permission_cache
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit
from tornado.web import RequestHandler

class role(RequestHandler):
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
        print(real_ip,username,'角色操作')
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list})
            return
        if "0" in per_list:
            # 查询所有角色信息
            if action == "role_list":
                res = self.role_list()
                self.write({'ret':200,'data':res})
                return
            # 添加角色
            elif action == "role_add":
                role_id = str(params.get('id'))
                role_name = params.get('name')
                role_info = params.get('info')
                if role_id == '0':
                    self.write({'ret':203,'msg':'角色添加失败'})
                    return
                res = self.role_add(id=role_id,name=role_name,info=role_info)
                if res == 1:
                    self.write({'ret':200,'msg':'角色添加成功'})
                    return
                else:
                    self.write({'ret':203,'msg':'角色添加失败'})
                    return
            # 删除角色
            elif action == "role_del":
                role_id = str(params.get('id'))
                if role_id == '0':
                    self.write({'ret':203,'msg':'角色无法删除'})
                    return
                res = self.role_del(id=role_id)
                if res == 1:
                    self.write({'ret':200,'msg':'角色删除成功'})
                    return
                else:
                    self.write({'ret':203,'msg':'角色删除失败'})
                    return
            # 角色信息修改
            elif action == "role_modify":
                role_id = params.get('id')
                role_name = params.get('name')
                role_info = params.get('info')
                res = self.role_modify(id=role_id,name=role_name,info=role_info)
                if res == 1:
                    self.write({'ret':200,'msg':'角色修改完成'})
                    return
                else:
                    self.write({'ret':203,'msg':'角色修改失败'})
                    return
        else:
            self.write({'ret':203,'msg':'无权限'})
            return

    # 执行查询角色信息的sql语句
    def role_list(self) -> list:
        sql = 'select id,name,info from role;'
        res = exec_sql2dict(sql=sql)
        return res
    # 执行添加角色的sql语句
    def role_add(self,id,name,info) -> int:
        redis_cli = permission_cache()
        redis_cli.set('role_'+str(id),'[]') # 在缓存中添加新角色的id
        redis_cli.close()
        sql = f'insert ignore into role(id,name,info) values("{id}","{name}","{info}");'
        res = exec_sql_commit(sql=sql)
        return res
    # 执行删除角色的sql语句
    def role_del(self,id) -> int:
        redis_cli = permission_cache()
        redis_cli.delete('role_'+id) # 在缓存中清除响应角色的id
        redis_cli.close()
        sql = f'delete from role where id="{id}";'
        res = exec_sql_commit(sql=sql)
        sql1 = f'delete from role_permission where roleid="{id}";'
        exec_sql_commit(sql=sql1) # 删除角色并删除角色所有的权限信息
        return res
    # 执行修改角色的sql语句
    def role_modify(self,id,name,info):
        sql = f'update role set name="{name}",info="{info}" where id="{id}";'
        res = exec_sql_commit(sql=sql)
        return res