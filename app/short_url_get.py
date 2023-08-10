from tornado.web import RequestHandler
import datetime
import time
from common_module.util.connect_redis import short_url_cache,request_cache
from common_module.util.connect_mysql import exec_sql_commit

class short_url_get(RequestHandler):
    def get(self):
        self.set_header('Content-Type','application/json;charset:utf-8')
        real_ip = self.request.headers.get('X-Forwarded-For')
        url = self.request.full_url().split('/')
        if len(url) >= 5:
            self.write({'ret':201,'msg':'地址不存在'})
            return
        url = url[-1]
        redis_cli = short_url_cache()
        real_url = redis_cli.get(url)
        redis_cli.close()
        if real_url != None:
            self.redirect(url=real_url)
            self.log_request_info(url=url,ip=real_ip)
            return
        self.write({'ret':203,'url':url,'msg':'连接不存在'})
        return
    # 记录短链接被访问
    def log_request_info(self,url:str,ip:str):
        def insert_request_log(url:str,nums:str,cur_date:str,ip:str):
            print(ip)
            sql = f'insert ignore into short_url_pv(short_url,log_date,req_nums) values("{url}","{cur_date}","{nums}")as t on duplicate key update req_nums=t.req_nums;'
            rows = exec_sql_commit(sql=sql)
            sql1 = f'insert ignore into short_url_uv(short_url,log_date,ip) values("{url}","{cur_date}","{ip}");'
            rows1 = exec_sql_commit(sql=sql1)
            print(rows1)
            return rows
        curdate = datetime.datetime.now().strftime('%Y-%m-%d')
        redis_cli = request_cache()
        res = redis_cli.hget(url,curdate)
        if res != None:
            nums = int(res) + 1
            redis_cli.hset(url,curdate,str(nums))
            redis_cli.close()
        else:
            nums = 1
            redis_cli.hset(url,curdate,str(nums))
            redis_cli.close()
        rows = insert_request_log(url=url,cur_date=curdate,nums=nums,ip=ip)
        return rows
        
        