import sys
sys.path.append('./')
from common_module.util.connect_redis import permission_cache

redis_cli = permission_cache()
retry_time = redis_cli.get('操作重试次数')
redis_cli.close()

def auto_retry(func):
    '''
    重试装饰器
    '''
    def wraps(*args,**kwargs):
        for i in range(int(retry_time)):
            try:
                return func(*args,**kwargs)
            except Exception as e:
                print(e)
    return wraps