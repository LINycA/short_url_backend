import json
from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit
from common_module.check_cookie import check_cookie
from common_module.util.connect_redis import permission_cache

class system_setting(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        try:
            params = json.loads(self.request.body)
            action = params.get('action')
            if action is None or action == "":
                self.write({'ret':203,'msg':'参数错误'})
                return
        except:
            self.write({'ret':203,'msg':'参数错误'})
            return
        username,per_list = check_cookie(obj=self)
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list})
            return
        print(real_ip,username,'操作系统设置')
        if '0' in per_list:
            if action == "sys_list":
                res = self.sys_list()
                self.write({'ret':200,'data':res})
                return
            elif action == "sys_modify":
                sys_dict = params.get('sys_dict')
                res = self.sys_modify(sys_dict=sys_dict)
                if res != 0:
                    self.write({'ret':200,'msg':'修改成功'})
                    return
                else:
                    self.write({'ret':203,'msg':'修改失败'})
                    return
    # 查询系统设置参数
    def sys_list(self):
        sql = 'select name,sys_v from sys_conf;'
        res = [{i.get('name'):i.get('sys_v')} for i in exec_sql2dict(sql=sql)]
        return res
    # 修改系统设置
    def sys_modify(self,sys_dict:dict) -> int:
        try:
            rows = 0
            redis_cli = permission_cache()
            for n in sys_dict:
                sql = f'update sys_conf set sys_v="{sys_dict[n]}" where name="{n}";'
                res = exec_sql_commit(sql=sql)
                rows += res
                redis_cli.set(n,sys_dict[n])
            redis_cli.close()
        except:
            rows = 0
        return rows