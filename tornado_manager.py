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
from user_module.manager_module.user import user
from user_module.manager_module.user_role import user_role
from user_module.manager_module.role import role
from user_module.manager_module.role_permission import role_permission
from user_module.manager_module.permission import permission
from user_module.normal_module.user import user as no_user
from common_module.system_setting import system_setting

def make_app():
    return Application([
        (r"/api/login",login),
        (r"/api/logout",logout),
        (r"/api/register",register),
        (r"/api/check_username",check_username),
        (r"/api/get_invite_code",get_invite_code),
        (r"/api/cookie_active",cookie_active),
        (r"/api/reset_pass",reset_pass),
        (r"/api/manage/user",user),
        (r"/api/manage/user_role",user_role),
        (r"/api/manage/role",role),
        (r"/api/manage/role_permission",role_permission),
        (r"/api/manage/permission",permission),
        (r"/api/normal/user",no_user),
        (r"/api/system_setting",system_setting),
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