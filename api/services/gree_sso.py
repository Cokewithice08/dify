# from flask import request
# from pydantic import BaseModel
# from extensions.ext_redis import redis_client
# from .account_service import AccountService, RegisterService, TokenPair
# import requests
#
# # 格力单点登录
# GREE_SSO_URL_GET_TOKEN = 'http://wfserver.gree.com/sso/ssoapi/GetToken'
# GREE_SSO_URL_GET_USER_INFO = 'http://wfserver.gree.com/sso/ssoapi/GetUserInfo'
# GREE_SSO_APP_ID = '0347f117-1b67-46a1-b4ec-a173f7bffa14'
# GREE_SSO_APP_KEY = '2ce5a8c1-3a99-4036-92cc-a8f434b1a17c'
# # redis key
# GREE_REDIS_KEY = 'gree:user:mail:'
#
#
# # 用户数据
# class userInfo(BaseModel):
#     Success: str
#     OpenID: str
#     AppAccount: str
#     StaffID: str
#     EmpID: str
#     HREmpID: str
#     OrgL1Alias: str
#     OrgL1Name: str
#     OrgL2Alias: str
#     OrgL2Name: str
#     OrgL3Alias: str
#     OrgL3Name: str
#     Job: str
#     Token: str
#     UserName: str
#     DepartmentID: str
#     DepartmentName: str
#     CompanyID: str
#     CompanyName: str
#     Title: str
#     Office: str
#     InService: str
#     Phone: str
#     OfficeLeader: str
#     DeptLeader: str
#     IP: str
#
#
# # 调用接口返回的数据
# class result_info(BaseModel):
#     Success: str
#     Message: str
#
#
# # 根据callback获取token
# def get_token(callback: str) -> str:
#     ip = request.remote_addr
#     forwarded_ip = request.headers.get('X-Forwarded-For')
#     if forwarded_ip:
#         ip = forwarded_ip.split(',')[0].split()
#     params = {
#         'appid': GREE_SSO_APP_ID,
#         'appkey': GREE_SSO_APP_KEY,
#         'ip': ip,
#         'callback': callback
#     }
#     try:
#         response = requests.get(GREE_SSO_URL_GET_TOKEN, params=params)
#         if response.status_code == 200:
#             json_data = response.json()
#             if 'Success' in json_data or 'Message' in json_data:
#                 json_data = result_info(**json_data)
#                 if json_data['Success'] == 'true':
#                     return json_data['Message']
#     except Exception as e:
#         print(e)
#
#
# # 根据token查询用户信息
# def get_user_info(token: str) -> userInfo:
#     ip = request.remote_addr
#     forwarded_ip = request.headers.get('X-Forwarded-For')
#     if forwarded_ip:
#         ip = forwarded_ip.split(',')[0].split()
#     params = {
#         'appid': GREE_SSO_APP_ID,
#         'appkey': GREE_SSO_APP_KEY,
#         'ip': ip,
#         'token': token
#     }
#     response = requests.get(GREE_SSO_URL_GET_USER_INFO, params=params)
#     if response.status_code == 200:
#         json_data = response.json()
#         user_info = userInfo(**json_data)
#         if json_data['Success'] == 'true':
#             return user_info
#
#
# # 获取redis——key
# def get_redis_key(mail: str) -> str:
#     return GREE_REDIS_KEY + mail
#
#
# class GreeSsoService:
#
#     @staticmethod
#     def gree_sso(callback: str) -> TokenPair:
#         token = get_token(callback)
#         user_info = get_user_info(token)
#         if user_info:
#             redis_key = get_redis_key(user_info['StaffID'])
#             redis_client.set(redis_key, user_info)
#             account = AccountService.get_user_through_email(user_info['OpenID'])
#             if not account:
#                 #  没有账号信息新注册再登录
#                 email = user_info['OpenID']
#                 name = user_info['name']
#                 password = user_info['account'] + "@GreeSSO2025"
#                 language = 'zh-Hans'
#                 status = 'active'
#                 account = RegisterService.register(email, password, name, language, status)
#                 return AccountService.login(account)
# #               调用注册
# #         获取数据库、查看是否有这个人的信息，没有就注册、有就调用登录接口（注意sso的token问题）
