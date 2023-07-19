from tornado.web import RequestHandler
from common_module.check_cookie import check_cookie

class cookie_active(RequestHandler):
    def get(self):
        username,per_list = check_cookie(obj=self)
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list,'cookie':'inactive'})
            return
        if '0' in per_list:
            user_type = 'manage'
        else:
            user_type = 'normal'
        self.write({'ret':200,'cookie':'active','type':user_type})
        return