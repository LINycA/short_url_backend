from redis import StrictRedis
import json
import sys
sys.path.append('./')

with open('./config/redis.config','r',encoding='utf-8') as f:
    redis_dict = json.loads(f.read())
host = redis_dict.get('host')
port = redis_dict.get('port')

# 会话缓存
sessions_cache = lambda :StrictRedis(host=host,port=port,db=15,decode_responses=True)
# 权限缓存
permission_cache = lambda :StrictRedis(host=host,port=port,db=13,decode_responses=True)
# 短链接缓存
short_url_cache = lambda :StrictRedis(host=host,port=port,db=14,decode_responses=True)
# 访问缓存库
client_ip_cache = lambda :StrictRedis(host=host,port=port,db=12,decode_responses=True)
# 访问数据统计库
request_cache = lambda :StrictRedis(host=host,port=port,db=11,decode_responses=True)


if __name__ == "__main__":
    redis_cli = permission_cache()
    print(redis_cli.keys('操作重试次数'))