from hashlib import sha1
from random import choice

# 生成加密盐
def gen_salt(passwd:str,length:int=16) -> str:
    salt_list = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '`', '[', ']', '{', '}', '\\', '|', "'", '"', ',', '.', '<', '>', '/', '?', ':', ';', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    salt_str = ''
    for i in range(length):
        salt_str += choice(salt_list)
    return sha1((salt_str+passwd).encode('utf-8')).hexdigest()

# 加密密码
def encrypt_passwd(passwd:str) -> str:
    salt = gen_salt(passwd=passwd)
    en_passwd = '$sb'+ str(len(salt)) + '$' + salt + sha1((passwd+salt).encode('utf-8')).hexdigest()
    # print(en_passwd)
    return en_passwd

# 解密密码
def decrypt_passwd(passwd:str,en_passwd:str) -> bool:
    pass_str = en_passwd.split('$')
    salt = pass_str[2][0:int(pass_str[1][2:])]
    en_pass = pass_str[2][int(pass_str[1][2:]):]
    pass_res = sha1((passwd + salt).encode('utf-8')).hexdigest()
    if en_pass == pass_res:
        return True
    else:
        return False
    


if __name__ == "__main__":
    # gen_salt()
    en_passwd = encrypt_passwd('arnolin')
    print(len(en_passwd),en_passwd)
    print(decrypt_passwd(passwd='arnolin',en_passwd=en_passwd))