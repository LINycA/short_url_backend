import json
from random import choice
from tornado.web import RequestHandler
from common_module.util.connect_mysql import exec_sql2dict,exec_sql_commit
from common_module.util.connect_redis import short_url_cache,permission_cache
from common_module.check_cookie import check_cookie


class short_url(RequestHandler):
    def post(self):
        real_ip = self.request.headers.get('X-Forwarded-For')
        try:
            params = json.loads(self.request.body)
            action = params.get('action')
        except:
            self.write({'ret':306,'msg':'参数错误'})
            return
        username,per_list = check_cookie(obj=self)
        if type(per_list) is not list:
            self.write({'ret':306,'msg':per_list})
            return
        # 查询短链接对应
        if action == "short_url_list":
            res = self.short_url_list(per_list=per_list,username=username)
            if res == None:
                self.write({'ret':203,'msg':'没有权限'})
                return
            self.write({'ret':200,'data':res})
            return
        # 增加短链接
        elif action == "short_url_add":
            res = self.short_url_add(per_list=per_list,username=username,params=params)    
            if res != 0:
                self.write({'ret':200,'msg':'添加成功'})
                return
            else:
                self.write({'ret':203,'msg':'添加失败'})
                return
        # 删除短链接
        elif action == "short_url_del":
            res = self.short_url_del(per_list=per_list,username=username,params=params)
            if res != 0 and res != None:
                self.write({'ret':200,'msg':'删除成功'})
                return
            else:
                self.write({'ret':203,'msg':'删除失败'})
                return
        # 修改短链接
        elif action == "short_url_modify":
            res = self.short_url_modify(per_list=per_list,username=username,params=params)
            if res != 0 and res != None:
                self.write({'ret':200,'msg':'修改成功'})
                return
            else:
                self.write({'ret':203,'msg':'修改失败'})
                return
        # 短链接数据展示
        elif action == "show_view_data":
            return self.show_view_data(per_list=per_list,username=username,params=params)

    # 展示现有的短链接
    def short_url_list(self,per_list:list,username:str):
        if "0" in per_list:
            sql = 'select username,short_url,real_url from short_url;'
            return exec_sql2dict(sql=sql)
        elif "1" in per_list:
            sql = f'select username,short_url,real_url from short_url where username="{username}";'
            return exec_sql2dict(sql=sql)
        else:
            return None
    # 增加短链接
    def short_url_add(self,per_list:list,username:str,params:dict):
        # 检测短链接是否存在
        def check_url_exists(url:str):
            sql = f'select count(1) as exi_nums from short_url where short_url="{url}";'
            res = exec_sql2dict(sql=sql)[0].get('exi_nums')
            return res
        # 检测相应用户短链接数量
        def short_url_num(username:str):
            sql = f'select count(1) as num from short_url where username="{username}";'
            res = exec_sql2dict(sql=sql)[0].get('num')
            return res
        # 短链接新增入库
        def insert_short_url(username:str,short_url:str,real_url:str) -> int:
            redis_cli = short_url_cache()
            redis_cli.set(short_url,real_url)
            redis_cli.close()
            sql = f'insert ignore into short_url(username,short_url,real_url) values("{username}","{short_url}","{real_url}");'
            res = exec_sql_commit(sql=sql)
            return res
        # 生成随机短链接
        def random_url(url_length:int=6) -> str:
            rand_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            res = ''
            for i in range(url_length):
                res += choice(rand_list)
            return res

        short_url_info = params.get('short_url')
        real_url = params.get('real_url')
        url_length = params.get('url_length')
        if '0' in per_list:
            if short_url_info == None or short_url_info == '':
                if url_length != None and url_length != '':
                    short_url_info = random_url(url_length=url_length)
                else:
                    return 0
            res = check_url_exists(url=short_url_info)
            if res == 0:
                return insert_short_url(username=username,short_url=short_url_info,real_url=real_url)
            else:
                return 0
        elif '1' in per_list:
            nums = short_url_num(username=username)
            redis_cli = permission_cache()
            enable_nums = redis_cli.get('普通用户可用数量')
            redis_cli.close()
            if url_length is None or url_length == '' or url_length < 6:
                # self.write({'ret':201,'msg':'短链接长度不低于6个字符'})
                return 0
            if nums > int(enable_nums):
                return 0
            else:
                short_url_info = random_url(url_length=url_length)
                res = check_url_exists(url=short_url_info)
                if res == 0:
                    return insert_short_url(username=username,short_url=short_url_info,real_url=real_url)
                else:
                    return 0
    # 删除短链接
    def short_url_del(self,per_list:list,username:str,params:dict):
        if "1" in per_list:
            redis_cli = short_url_cache()
            short_url_info = params.get('short_url')
            redis_cli.delete(short_url_info)
            redis_cli.close()
            sql = f'delete from short_url where username="{username}" and short_url="{short_url_info}";'
            res = exec_sql_commit(sql=sql)
            return res
        elif "0" in per_list:
            redis_cli = short_url_cache()
            short_url_info = params.get('short_url')
            username = params.get('username')
            redis_cli = short_url_cache()
            redis_cli.hdel(username,short_url_info)
            redis_cli.close()
            sql = f'delete from short_url where username="{username}" and short_url="{short_url_info}";'
            res = exec_sql_commit(sql=sql)
            return res
        else:
            return None
    # 修改短链接
    def short_url_modify(self,per_list:list,username:str,params:dict):
        print(username)
        if "0" not in per_list and "1" not in per_list:
            return None
        else:
            short_url_info = params.get('short_url')
            real_url = params.get('real_url')
            redis_cli = short_url_cache()
            redis_cli.set(short_url_info,real_url)
            redis_cli.close()
            sql = f'update short_url set real_url="{real_url}" where username="{username}" and short_url="{short_url_info}";'
            return exec_sql_commit(sql=sql)
    # 访问数据展示
    def show_view_data(self,per_list:list,username:str,params:dict):
        # 获取短链接统计数据
        def get_data_view(short_url_info:str) -> tuple:
            sql = f'select req_nums,log_date from short_url_pv where short_url="{short_url_info}";'
            res = [{i.get('log_date').strftime('%Y-%m-%d'):i.get('req_nums')} for i in exec_sql2dict(sql=sql)]
            sql1 = f'select distinct log_date,count(ip) as uv_nums from short_url_uv where short_url="{short_url_info}" group by log_date;'
            res1 = [{i.get('log_date').strftime('%Y-%m-%d'):i.get('uv_nums')} for i in exec_sql2dict(sql=sql1)]
            return res,res1
        # 确认数据查看权限
        def ensure_url_auth(short_url_info:str,username:str):
            sql = f'select count(1) as en from short_url where username="{username}" and short_url="{short_url_info}";'
            res = exec_sql2dict(sql=sql)[0].get('en')
            print(res)
            if res == 1:
                return True
            else:
                return False
        short_url_info = params.get('short_url')
        if short_url_info == '' or short_url_info == None:
            self.write({'ret':306,'msg':'参数错误'})
            return
        if "0" not in per_list and "1" not in per_list:
            self.write({'ret':306,'msg':'没有查看权限'})
            return 
        elif "0" in per_list:
            res,res1 = get_data_view(short_url_info=short_url_info)
            self.write({'ret':200,'data':{"pv":res,"uv":res1}})
            return
        else:
            if ensure_url_auth(short_url_info=short_url_info,username=username):
                res,res1 = get_data_view(short_url_info=short_url_info)
                self.write({'ret':200,'data':{"pv":res,"uv":res1}})
                return
            else:
                self.write({'ret':203,'msg':'没有查看权限'})
                return