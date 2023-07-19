-- 用户信息表
drop table if exists auth_user;
create table auth_user(
username varchar(50) not null comment'用户名',
password varchar(86) not null comment'密码',
nickname varchar(50) DEFAULT null comment '昵称',
email varchar(255) not null unique comment'用户邮箱',
status varchar(2) not null DEFAULT '启用' comment'用户启用状态',
PRIMARY KEY(username));

-- 角色表
drop table if exists role;
create table role(
id varchar(10) not null comment'角色id',
name varchar(20) DEFAULT null comment '角色名称',
info text DEFAULT null comment '角色描述',
PRIMARY key(id));

-- 权限表
drop table if exists permission;
create table permission(
id varchar(255) not null comment'权限id',
name varchar(255) not null comment'权限名称',
info text DEFAULT null comment'权限描述',
PRIMARY KEY(id));

-- 用户角色表
drop TABLE if EXISTS user_role;
create TABLE user_role(
username varchar(50) not null comment'用户名称',
roleid varchar(10) not null comment'角色id',
PRIMARY key(username,roleid));

-- 角色权限表
drop TABLE if EXISTS role_permission;
create table role_permission(
roleid varchar(10) not null comment'角色id',
permissionid varchar(255) not null comment'权限id',
PRIMARY KEY(roleid,permissionid));

-- 系统配置
drop table if exists sys_conf;
create table sys_conf(
name varchar(255) not null comment'配置名称',
sys_v varchar(255) not null comment'配置值',
PRIMARY KEY(name));



insert into auth_user(username,password,nickname,email,status) VALUES('admin','$sb40$7caa54ea423e321cf9ffd7d8649aa289afd4b58f259befd1bc7946c81ebac9b571c2ce0d3d854b0f','admin','admin@example.com','启用');
insert into role(id,name,info) VALUES('0','系统管理员','系统管理员，拥有系统最高权限');
INSERT into permission(id,name,info) VALUES('0','系统管理权限','系统最高权限');
insert into user_role(username,roleid) VALUES('admin','0');
INSERT into role_permission(roleid,permissionid) VALUES('0','0');
insert into sys_conf(name,sys_v) VALUES('用户注册','开启'),('注册默认角色','1'),('操作重试次数','5'),('邮箱服务器','smtp.qq.com'),('邮箱端口','587'),('邮箱登录口令',''),('邮箱用户名','admin@example.com'),('注册模式','邀请码'),('域名','127.0.0.1');