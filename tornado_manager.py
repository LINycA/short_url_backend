from tornado.web import Application
from tornado.ioloop import IOLoop
from user_module.login_out import login,logout
from user_module.register import register
from user_module.get_invite_code import get_invite_code
from common_module.cookie_active import cookie_active
from user_module.check_username import check_username
from user_module.load_permission_cache import load_permission,load_sys_conf_cache
from common_module.util.invite_code import gen_invite_code
from user_module.reset_pass import reset_pass

def make_app():
    return Application([
        (r"/api/login",login),
        (r"/api/logout",logout),
        (r"/api/register",register),
        (r"/api/check_username",check_username),
        (r"/api/get_invite_code",get_invite_code),
        (r"/api/cookie_active",cookie_active),
        (r"/api/reset_pass",reset_pass),
    ])

def main(port:int=7890):
    load_permission() # 检测redis缓存是否开启并载入角色权限
    load_sys_conf_cache() # 载入配置信息至缓存
    gen_invite_code(15) # 生成邀请码，如果是邀请码模式
    app = make_app()
    app.listen(port=port)
    IOLoop.current().start()

if __name__ == "__main__":
    main()