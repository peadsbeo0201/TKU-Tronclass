import aiohttp
import asyncio

class SSO:
    def __init__(self, std_id, passwd, aiohttp_client_session):
        self.reqs = aiohttp_client_session
        self.std_id = std_id
        self.passwd = passwd
        
    async def get_user_id(self):
        async with self.reqs.get('https://sso.tku.edu.tw/iclass/api/cas-login?ln=zh_TW', proxy='http://127.0.0.1:8888') as resp:
            res = await resp.json()
            return res
    
    async def login(self):
        async with self.reqs.get(Url.ICLASS_LOGIN_PAGE_URL, headers=Headers.LOGIN_PAGE_HEADERS, proxy='http://127.0.0.1:8888') as resp:
            await resp.text()
        
        async with self.reqs.get(Url.ICLASS_LOGIN_PAGE_URL, headers=Headers.LOGIN_PAGE_HEADERS, proxy='http://127.0.0.1:8888') as resp:
            await resp.text()

        async with self.reqs.get(Url.VERICODE_URL, headers=Headers.VIDCODE_HEADERS, proxy='http://127.0.0.1:8888') as resp:
            await resp.read()

        async with self.reqs.post(Url.VERICODE_URL, data={'outType': 2}, headers=Headers.VIDCODE_HEADERS, proxy='http://127.0.0.1:8888') as resp:
            text = await resp.text()
            vidcode = text.replace('\r\n', '')
            print(vidcode)
        login_payload = self.set_login_payload(vidcode)
        async with self.reqs.post(Url.LOGIN_URL, headers=Headers.VIDCODE_HEADERS, data=login_payload, proxy='http://127.0.0.1:8888') as resp:
            result = await resp.json()
            if resp.headers.get('Set-Cookie') != None:
                print(result)
                print("Login!!")
                return(resp.headers.get('Set-Cookie'))
            else:
                print("ERROR!! Can't login!!")
        
    def set_login_payload(self, vidcode):
        login_payload = DataPayload.ICLASS_LOGIN_PAYLOAD
        login_payload['username'] = self.std_id
        login_payload['password'] = self.passwd
        login_payload['vidcode']  = vidcode
        return login_payload
        
        
class DataPayload:
    ICLASS_LOGIN_PAYLOAD   =   {
        'myurl': 'https://sso.tku.edu.tw/iclass/api/cas-login?ln=zh_TW',
        'ln': 'zh_TW',
        'embed': 'No',
        'vkb': 'No',
        'logintype': 'loginrwd',
        'username': '',
        'password': '',
        'vidcode': ''
    }
    
class Url:
    BASE_URL            =   'https://sso.tku.edu.tw'
    LOGIN_URL           =   BASE_URL + '/NEAI/login2.do?action=EAI'
    VERICODE_URL        =   BASE_URL + '/NEAI/ImageValidate'
    ICLASS_LOGIN_PAGE_URL    =   BASE_URL + '/NEAI/loginrwd.jsp?myurl=https://sso.tku.edu.tw/iclass/api/cas-login'
    
    
class Headers:
    USER_AGENT          =   'Mozilla/5.0 (Linux; Android 7.1.2; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:18340;packageName:com.wisdomgarden.trpc'
    
    LOGIN_PAGE_HEADERS  =   {
        'User-Agent': USER_AGENT,
        'Referer': 'https://sso.tku.edu.tw/NEAI/loginrwd.jsp?myurl=https://sso.tku.edu.tw/iclass/api/cas-login'
        
    }
    
    VIDCODE_HEADERS     =   {
        'User-Agent': USER_AGENT,
        'Referer': 'https://sso.tku.edu.tw/NEAI/loginrwd.jsp?myurl=https://sso.tku.edu.tw/iclass/api/cas-login'
    }
    