import json
from tornado.web import RequestHandler
from common_module.check_cookie import check_cookie
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit

class permission(RequestHandler):
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
        if "0" in per_list:
            # 查询权限信息
            if action == "permission_list":
                res = self.permission_list()
                self.write({'ret':200,'data':res})
                return
        else:
            self.write({'ret':203,'msg':'没有权限'})
            return
    # 查询权限信息
    def permission_list(self):
        sql = 'select id,name,info from permission;'
        res = exec_sql2dict(sql=sql)
        return res
    