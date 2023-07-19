import json
from common_module.util.connect_redis import sessions_cache,permission_cache


def check_cookie(obj:object) -> list:
    session_cookie = obj.get_cookie('short_url_session')
    if not session_cookie or session_cookie == "":
        return None,"请先登录账号"
    # 根据cookie值获取用户名
    redis_cli = sessions_cache()
    username = redis_cli.get(session_cookie)
    if username == None:
        return None,"请先登录账号"
    roleid_list = eval(redis_cli.hget(username,'roleid') if redis_cli.hget(username,'roleid') is not None else "[]")
    # 根据用户名获取角色表，及用户状态
    user_status = redis_cli.hget(username,'status')
    redis_cli.close()
    if not roleid_list or roleid_list == [] or user_status != '启用':
        return username,"用户无角色，或用户不可用"
    redis_cli = permission_cache()
    per_list = []
    for i in roleid_list:
        p_list = redis_cli.get(i)
        if p_list != None or p_list != '':
            for n in eval(p_list):
                if n not in per_list:
                    per_list.append(n)
    redis_cli.close()
    return username,per_list