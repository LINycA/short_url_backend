from common_module.util.connect_redis import sessions_cache

# 清除cookie会话缓存（当用户密码变动或用户被删除时使用）
def clear_cookie(username:str):
    redis_cli = sessions_cache()
    session_name = redis_cli.hget(username,'session')
    if session_name != None:
        redis_cli.delete(session_name)
    redis_cli.delete(username)
    redis_cli.close()
    return True