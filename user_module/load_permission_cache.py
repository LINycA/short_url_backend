import sys
sys.path.append('./')
from common_module.util.connect_redis import permission_cache
from common_module.util.connect_mysql import exec_sql2dict

# 更新角色权限缓存
def load_permission():
    sql = 'select roleid,permissionid from role_permission;'
    res = exec_sql2dict(sql=sql)
    role_id = []
    role_per = {}
    for i in res:
        if i['roleid'] not in role_id:
            role_id.append(i['roleid'])
            role_per.update({i['roleid']:[i['permissionid']]})
        else:
            role_per[i['roleid']].append(i['permissionid'])
    redis_cli = permission_cache()
    redis_cli.flushdb()
    for n in role_per:
        redis_cli.set(n,str(role_per[n]))
    redis_cli.close()

# 导入系统配置缓存
def load_sys_conf_cache():
    sql = 'select name,sys_v from sys_conf;'
    res = exec_sql2dict(sql=sql)
    sys_conf_dict = {}
    for i in res:
        sys_conf_dict.update({i['name']:i['sys_v']})
    redis_cli = permission_cache()
    for n in sys_conf_dict:
        redis_cli.set(n,sys_conf_dict[n])
    redis_cli.close()


if __name__ == "__main__":
    load_permission()