from tornado.web import RequestHandler
from common_module.util.connect_redis import permission_cache
from common_module.check_cookie import check_cookie


class get_invite_code(RequestHandler):
    def get(self):
        self.set_header('Content-Type','application/json charset=utf-8;')
        real_ip = self.request.headers.get('X-Forwarded-For')
        username,per_list = check_cookie(obj=self)
        print(real_ip,username,'获取邀请码')
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list})
            return
        if '0' in per_list:
            redis_cli = permission_cache()
            invite_code = redis_cli.get('invite_code')
            redis_cli.close()
            self.write({'ret':200,'invite_code':invite_code})
            return
        self.write({'ret':306,'msg':'无法获取邀请码'})
        return