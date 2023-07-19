import sys
sys.path.append('./')

from threading import Thread
import time
from hashlib import md5
from random import randint
from datetime import datetime
from common_module.util.connect_redis import permission_cache

# 生成邀请码并写入缓存
def load_invite_code(interval_time):
    while True:
        cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        random_num = randint(100000,999999)
        invite_code = md5((cur_time+str(random_num)).encode('utf-8')).hexdigest().upper()
        # print('邀请码',invite_code)
        redis_cli = permission_cache()
        redis_cli.set('invite_code',invite_code)
        redis_cli.close()
        time.sleep(interval_time)

# 验证邀请码
def ensure_invite_code(invite_code:str) -> bool:
    redis_cli = permission_cache()
    inv_code = redis_cli.get('invite_code')
    if invite_code == inv_code:
        return True
    return False

def gen_invite_code(interval_time:int=15):
    t = Thread(target=load_invite_code,args=(interval_time*60,),daemon=True)
    t.start()

if __name__ == "__main__":
    load_invite_code(interval_time=15)