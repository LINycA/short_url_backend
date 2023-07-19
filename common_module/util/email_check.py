import sys
sys.path.append('./')
from random import randint
from common_module.util.connect_redis import permission_cache
from common_module.util.connect_mysql import exec_sql2dict
from hashlib import md5

from smtplib import SMTP
from common_module.util.connect_redis import sessions_cache
from common_module.util.auto_retry import auto_retry
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

def get_user(email:str) -> str:
    sql = f'select username from auth_user where email="{email}";'
    res = exec_sql2dict(sql=sql)
    if res != ():
        return res[0].get('username')
    return None

@auto_retry
def send_check_code(to_user:str):
    redis_cli = permission_cache()
    host = redis_cli.get('邮箱服务器')
    port = redis_cli.get('邮箱端口')
    access_token = redis_cli.get('邮箱登录口令')
    user = redis_cli.get('邮箱用户名')
    domain = redis_cli.get('域名')
    redis_cli.close()
    con = SMTP(host=host,port=port)
    con.login(user=user,password=access_token)
    msg = MIMEMultipart()
    subject = Header('Short_url_tornado验证码','utf-8').encode()
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to_user
    # 生成验证码并写入缓存
    redis_cli = sessions_cache()
    if redis_cli.keys(to_user) != []:
        redis_cli.close()
        return False
    username = get_user(email=to_user)
    check_code = randint(100000,999999)
    check_code = md5(str(check_code).encode('utf-8')).hexdigest().upper()
    redis_cli.set(to_user,check_code)
    redis_cli.expire(name=to_user,time=600)
    redis_cli.close()
    if username != None:
        content = f"""
    <h2>Short_url✨验证码</h2>
    <p>✨您已注册，用户名：
        <span style="font-size:xx-large;font-weight: bold;">{username}</span>
        <span>如果您不知道密码，或重置密码，请通过重置密码接口<a href="http://{domain}/#reset_pass">重置密码</a></span>
    <p/>
    <p>✨<span style="font-size:xx-large;font-weight: bold;">{check_code}</span></p>
    <img src="http://znana.top:8089/i/xiaohei.gif">
    """
    else:
        content = f"""
    <h2>Short_url✨验证码</h2>
    <p>✨<span style="font-size:xx-large;font-weight: bold;">{check_code}</span></p>
    <img src="http://znana.top:8089/i/xiaohei.gif">
    """
    html = MIMEText(content,'html','utf-8')
    msg.attach(html)
    con.sendmail(from_addr=user,to_addrs=to_user,msg=msg.as_string())
    con.quit()
    return True

# 验证验证码
def ensure_check_code(email:str,check_code:str) -> bool:
    redis_cli = sessions_cache()
    code = redis_cli.get(email)
    if check_code == code:
        redis_cli.delete(email)
        redis_cli.close()
        return True
    redis_cli.close()
    return False

if __name__ == "__main__":
    # send_check_code('1002941793@qq.com')
    print(ensure_check_code('1002941793@qq.com','1C175BEEC2572D454ABD4D19994C1E2D'))