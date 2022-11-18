import asyncio
import aiohttp
import time
from iclass import SSO
from datetime import datetime


class Tronclass():
    def __init__(self, std_id, passwd):
        self.HOST = 'https://iclass.tku.edu.tw'
        self.LOGIN = '/api/login?login=email'
        self.ROLL_CALL = '/api/rollcall/{}/answer_number_rollcall'
        self.std_id = std_id
        self.passwd = passwd
        self.session_id = ''

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.main())

    async def login(self, session):
        client = SSO(self.std_id, self.passwd, session)
        cookies = await client.login()
        session_id = cookies.split(';')[0].replace('session=', '')
        self.session_id = session_id

    async def get_roll_call(self, session):
        async with session.get(
                'https://iclass.tku.edu.tw' + '/api/radar/rollcalls?api_version=1.1.0',
                headers={
                    'Accept': 'application/json, text/plain, */*',
                    'X-Requested-With': 'XMLHttpRequest', 'Accept-Language': 'zh-Hant',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate',
                    'X-SESSION-ID': self.session_id,
                }, proxy='http://127.0.0.1:8888') as resp:
            data = await resp.json()
            print('[%s]' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data)
            roll_call_list = [data['rollcall_id']
                              for data in data['rollcalls'] if data['status'] == 'absent']

            # session_id = resp.headers.get('Set-Cookie')
            # self.session_id = session_id.replace('session=', '').split(';')[0]

            return roll_call_list

    async def send_roll_call(self, session, url, number_code):
        print('send roll call number:', number_code)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
            'Content-Type': 'application/json',
            'X-SESSION-ID': self.session_id
        }
        data = '{\"numberCode\":\"%s\"}' % number_code
        async with session.put(url, headers=headers, data=data, proxy='http://127.0.0.1:8888') as resp:
            await resp.json()
            if resp.status == 200:
                t1 = time.time()
                print('[ {} ] [ target number code: {}] [ cost: {} seconds ]\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), number_code, t1-self.t0))
                with open('success.txt', 'a', encoding='utf-8') as file:
                    file.write('[ {} ] [ target number code: {}] [ cost: {} seconds ]\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), number_code, t1-self.t0))
                asyncio.current_task().cancel()

    async def listen_roll_call(self, session):
        await asyncio.sleep(5)
        get_roll_call_task = [asyncio.create_task(
            self.get_roll_call(session))]
        roll_call_list = await asyncio.gather(*get_roll_call_task)
        
        if roll_call_list == [[]]:
            return False
        else:
            return True
        
    async def main(self):
        async with aiohttp.ClientSession() as session:
            login_task = [asyncio.create_task(self.login(session))]
            await asyncio.gather(*login_task)
            while True:
                listen_roll_call_task = [asyncio.create_task(
                    self.listen_roll_call(session))]
                condition = await asyncio.gather(*listen_roll_call_task)
                if condition[0]:
                    print('roll call is found.')
                    get_roll_call_task = asyncio.create_task(
                        self.get_roll_call(session))
                    roll_call_list = await get_roll_call_task
                    print(roll_call_list)
                    send_roll_call_tasks = []
                    for roll_call in roll_call_list:
                        url = "https://tronclass.com.tw/api/rollcall/%s/answer_number_rollcall" % roll_call
                        for number_code in range(10000):
                            number_code = '%04d' % number_code
                            send_roll_call_tasks.append(asyncio.create_task(
                                self.send_roll_call(session, url, number_code)))
                    self.t0 = time.time()
                    try:
                        print('start')
                        await asyncio.gather(*send_roll_call_tasks)
                    except asyncio.CancelledError:
                        for task in send_roll_call_tasks:
                            task.cancel()
                        print('success')
                else:
                    print('roll call is not found.')
