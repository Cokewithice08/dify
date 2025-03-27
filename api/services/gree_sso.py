import json

from flask import request, redirect
from pydantic import BaseModel

import models
from extensions.ext_redis import redis_client
from .account_service import AccountService, RegisterService, TokenPair, TenantService

import requests

# 格力单点登录
GREE_SSO_URL_GET_TOKEN = 'http://wfserver.gree.com/sso/ssoapi/GetToken'
GREE_SSO_URL_GET_USER_INFO = 'http://wfserver.gree.com/sso/ssoapi/GetUserInfo'
GREE_SSO_APP_ID = '0347f117-1b67-46a1-b4ec-a173f7bffa14'
GREE_SSO_APP_KEY = '2ce5a8c1-3a99-4036-92cc-a8f434b1a17c'
# redis key
GREE_REDIS_KEY = 'gree:user:mail:'


# 用户数据
class userInfo(BaseModel):
    OpenID: str | None = None
    AppAccount: str | None = None
    StaffID: str | None = None
    EmpID: str | None = None
    HREmpID: str | None = None
    OrgL1Alias: str | None = None
    OrgL1Name: str | None = None
    OrgL2Alias: str | None = None
    OrgL2Name: str | None = None
    OrgL3Alias: str | None = None
    OrgL3Name: str | None = None
    Job: str | None = None
    Token: str | None = None
    UserName: str | None = None
    DepartmentID: str | None = None
    DepartmentName: str | None = None
    CompanyID: str | None = None
    CompanyName: str | None = None
    Title: str | None = None
    Office: str | None = None
    InService: bool | None = None
    Phone: str | None = None
    OfficeLeader: str | None = None
    DeptLeader: str | None = None
    IP: str | None = None


# 调用接口返回的数据
class result_info(BaseModel):
    Success: bool
    Message: str


# 根据callback获取token
def get_token(callback: str) -> result_info:
    ip = request.remote_addr
    forwarded_ip = request.headers.get('X-Forwarded-For')
    if forwarded_ip:
        ip = forwarded_ip.split(',')[0].split()
    params = {
        'appid': GREE_SSO_APP_ID,
        'appkey': GREE_SSO_APP_KEY,
        'ip': ip,
        'callback': callback
    }
    response = requests.get(GREE_SSO_URL_GET_TOKEN, params=params)
    if response.status_code == 200:
        json_data = response.json()
        if 'Success' in json_data or 'Message' in json_data:
            json_data = result_info(**json_data)
            return json_data


# 根据token查询用户信息
def get_user_info(data_token: result_info) -> userInfo:
    ip = request.remote_addr
    token = data_token.Message
    forwarded_ip = request.headers.get('X-Forwarded-For')
    if forwarded_ip:
        ip = forwarded_ip.split(',')[0].split()
    params = {
        'appid': GREE_SSO_APP_ID,
        'appkey': GREE_SSO_APP_KEY,
        'ip': ip,
        'token': token
    }
    response = requests.get(GREE_SSO_URL_GET_USER_INFO, params=params)
    if response.status_code == 200:
        json_data = response.json()
        user_info = userInfo(**json_data)
        return user_info


# 获取redis——key
def get_redis_key(mail: str) -> str:
    return GREE_REDIS_KEY + mail


class GreeSsoService:

    @staticmethod
    def gree_sso(callback: str) -> TokenPair:
        token = get_token(callback)
        user_info = get_user_info(token)
        redis_key = get_redis_key(user_info.StaffID)
        redis_client.set(redis_key, json.dumps(user_info.__dict__))
        account = AccountService.get_user_through_email(user_info.OpenID)
        if not account:
            #  没有账号信息新注册再登录
            email = user_info.OpenID
            name = user_info.UserName
            password = user_info.AppAccount + "@GreeSSO2025"
            language = 'zh-Hans'
            status = models.AccountStatus.ACTIVE
            is_setup = True
            create_worksapce_require = False
            account = RegisterService.register(email, name, password, None, None, language, status, is_setup, create_worksapce_require)
            # TenantService.create_owner_tenant_if_not_exist(account=account, is_setup=True)
        return AccountService.login(account)
        # return tokenPair
        # return tokenPair
        # redirect(f"http://localhost:3000/apps?console_token={console_token}&refresh_token={refresh_token}")
        # return RedirectResponse(f"http://localhost:3000/apps?console_token={console_token}&refresh_token={refresh_token}")
#               调用注册
#         获取数据库、查看是否有这个人的信息，没有就注册、有就调用登录接口（注意sso的token问题）
