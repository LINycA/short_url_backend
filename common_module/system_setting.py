import json
from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict,exec_many_sql
from common_module.check_cookie import check_cookie

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
        value_list = []
        for n in sys_dict:
            value_list.append([sys_dict[n],n])
        try:
            sql = 'update sys_conf set sys_v="%s" where name="%s";'
            res = exec_many_sql(sql=sql,values=value_list)
        except:
            res = 0
        return res