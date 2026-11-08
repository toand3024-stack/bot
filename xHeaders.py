

import requests
import os
import psutil
import sys
import jwt
import pickle
import json
import binascii
import time
import urllib3
import base64
import datetime
import re
import socket
import threading
import random

from protobuf_decoder.protobuf_decoder import Parser
from xC4 import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ═══════════════════════════════════════════════════════════════
#                    ★ Hằng số (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

TOKEN_API = "https://tokens-asfufvfshnfkhvbb.francecentral-01.azurewebsites.net/ReQuesT"
LIKE_API  = "https://tokens-asfufvfshnfkhvbb.francecentral-01.azurewebsites.net/ReQuesT"
UID_API   = "https://panel-g2ccathtf6gdcmdw.polandcentral-01.azurewebsites.net/Uids"

DEFAULT_OB_HEADERS = {
    'X-Unity-Version': '2018.4.11f1',
    'ReleaseVersion':   'OB53',
    'Content-Type':     'application/x-www-form-urlencoded',
    'X-GA':             'v1 1',
    'Content-Length':   '16',
    'User-Agent':       'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
    'Host':             'clientbp.ggblueshark.com',
    'Connection':       'Keep-Alive',
    'Accept-Encoding':  'gzip',
}


# ═══════════════════════════════════════════════════════════════
# #              ★ Token Auto-Refresh  (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def ToK():
    """Tự động làm mới token định kỳ"""
    while True:
        try:
            r = requests.get(f'{TOKEN_API}?&type=ToKens')
            t = r.text
            i = t.find("ToKens : [")
            if i != -1:
                j = t.find("]", i)
                L = [x.strip(" '\"") for x in t[i+11:j].split(',') if x.strip()]
                if L:
                    with open("token.txt", "w") as f:
                        f.write(random.choice(L))
        except Exception:
            pass
        time.sleep(5 * 60 * 60)


def start_token_refresh():
    """Khởi chạy luồng làm mới token nền khi cần thiết"""
    Thread(target=ToK, daemon=True).start()


if __name__ == "__main__":
    start_token_refresh()


# ═══════════════════════════════════════════════════════════════
#              ★ Hàm tiện ích (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def GeTToK():
    """token.txt Đọc token từ tập tin"""
    with open("token.txt") as f:
        return f.read().strip()


def equie_emote(JWT, url):
    """Yêu cầu cài đặt Emote"""
    url = f"{url}/ChooseEmote"

    headers = {
        "Accept-Encoding": "gzip",
        "Authorization":   f"Bearer {JWT}",
        "Connection":      "Keep-Alive",
        "Content-Type":    "application/x-www-form-urlencoded",
        "Expect":          "100-continue",
        "ReleaseVersion":  "OB53",
        "User-Agent":      "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "X-GA":            "v1 1",
        "X-Unity-Version": "2018.4.11f1",
    }

    data = bytes.fromhex("CA F6 83 22 2A 25 C7 BE FE B5 1F 59 54 4D B3 13")

    requests.post(url, headers=headers, data=data)


# ═══════════════════════════════════════════════════════════════
#              ★ Likes Lấy thông tin (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def Likes(id):
    """Lấy thông tin lượt thích (Likes) của người chơi"""
    try:
        text = requests.get(f"{LIKE_API}?id={id}&type=likes").text
        get = lambda p: re.search(p, text)
        name, lvl, exp, lb, la, lg = (
            get(r).group(1) if get(r) else None
            for r in [
                r"PLayer NamE\s*:\s*(.+)",
                r"PLayer SerVer\s*:\s*(.+)",
                r"Exp\s*:\s*(\d+)",
                r"LiKes BeFore\s*:\s*(\d+)",
                r"LiKes After\s*:\s*(\d+)",
                r"LiKes GiVen\s*:\s*(\d+)",
            ]
        )
        return (
            name,
            f"{lvl}" if lvl else None,
            int(lb) if lb else None,
            int(la) if la else None,
            int(lg) if lg else None,
        )
    except Exception:
        return None, None, None, None, None


def Requests_SPam(id):
    """Gửi yêu cầu spam"""
    Api = requests.get(f'{TOKEN_API}?id={id}&type=spam')
    if Api.status_code in [200, 201] and '[SuccessFuLy] -> SenDinG Spam ReQuesTs !' in Api.text:
        return True
    else:
        return False


# ═══════════════════════════════════════════════════════════════
# #              ★ Player Name  (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def GeT_Name(uid, Token):
    """Lấy tên người chơi"""
    data = bytes.fromhex(EnC_AEs(f"08{EnC_Uid(uid, Tp='Uid')}1007"))
    url = "https://clientbp.common.ggbluefox.com/GetPlayerPersonalShow"

    headers = DEFAULT_OB_HEADERS.copy()
    headers['Authorization'] = f'Bearer {GeTToK()}'

    response = requests.post(url, headers=headers, data=data, verify=False)
    if response.status_code in (200, 201):
        packet = binascii.hexlify(response.content).decode('utf-8')
        BesTo_data = json.loads(DeCode_PackEt(packet))
        try:
            a1 = BesTo_data["1"]["data"]["3"]["data"]
            return a1
        except Exception:
            return ''
    else:
        return ''


# ═══════════════════════════════════════════════════════════════
# #              ★ Player   (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def GeT_PLayer_InFo(uid, Token):
    """Lấy toàn bộ hồ sơ người chơi + thông tin Quân đoàn"""
    data = bytes.fromhex(EnC_AEs(f"08{EnC_Uid(uid, Tp='Uid')}1007"))
    url = "https://clientbp.common.ggbluefox.com/GetPlayerPersonalShow"

    headers = DEFAULT_OB_HEADERS.copy()
    headers['Authorization'] = f'Bearer {GeTToK()}'

    response = requests.post(url, headers=headers, data=data, verify=False)

    if response.status_code in (200, 201):
        packet = binascii.hexlify(response.content).decode('utf-8')
        BesTo_data = json.loads(DeCode_PackEt(packet))
        NoCLan = False
        try:
            a1 = str(BesTo_data["1"]["data"]["1"]["data"])
            a2 = BesTo_data["1"]["data"]["21"]["data"]
            a3 = BesTo_data["1"]["data"]["3"]["data"]
            player_server = BesTo_data["1"]["data"]["5"]["data"]
            player_bio    = BesTo_data["9"]["data"]["9"]["data"]
            player_level  = BesTo_data["1"]["data"]["6"]["data"]
            account_date  = datetime.fromtimestamp(BesTo_data["1"]["data"]["44"]["data"]).strftime("%I:%M %p - %d/%m/%y")
            last_login    = datetime.fromtimestamp(BesTo_data["1"]["data"]["24"]["data"]).strftime("%I:%M %p - %d/%m/%y")

            try:
                clan_id         = BesTo_data["6"]["data"]["1"]["data"]
                clan_name       = BesTo_data["6"]["data"]["2"]["data"]
                clan_leader     = BesTo_data["6"]["data"]["3"]["data"]
                clan_level      = BesTo_data["6"]["data"]["4"]["data"]
                clan_members_num= BesTo_data["6"]["data"]["6"]["data"]
                clan_leader_name= BesTo_data["7"]["data"]["3"]["data"]
            except Exception:
                NoCLan = True

            if NoCLan:
                a = f'''
[b][c][FFFFFF] [SuccessFully] - Get PLayer s'InFo !

[FFFFFF][1] - ProFile InFo :
[FFFFFF]	
 Name : {a3}
 Uid : {xMsGFixinG(a1)}
 Likes : {xMsGFixinG(a2)}
 LeveL : {player_level}
 Server : {player_server}
 Bio : {player_bio}
 Creating : {account_date}
 LasT LoGin : {last_login}
 
  [FFFFFF]Dev : ᏚAMI YT\n'''
                a = a.replace('[i]', '')
                return a

            else:
                a = f'''
[b][c][FFFFFF] [SuccessFully] - Get PLayer s'InFo !

[FFFFFF][1] - ProFile InFo :
[FFFFFF]	
 Name : {a3}
 Uid : {xMsGFixinG(a1)}
 Likes : {xMsGFixinG(a2)}
 LeveL : {player_level}
 Server : {player_server}
 Bio : {player_bio}
 Creating : {account_date}
 LasT LoGin : {last_login}

[b][c][FFFFFF][2] - Guild InFo :
[FFFFFF]
 Guild Name : {clan_name}
 Guild Uid : {xMsGFixinG(clan_id)}
 Guild LeveL : {clan_level}
 Guild Members : {clan_members_num}
 Leader s'Uid : {xMsGFixinG(clan_leader)}
 Leader s'Name : {clan_leader_name}

  [FFFFFF]Dev : ᏚAMI YT\n'''
                a = a.replace('[i]', '')
                return a

        except Exception:
            return f'\n[b][c][FF0000]FaiLEd GeTinG PLayer InFo !\n'
    else:
        return f'\n[b][c][FF0000]FaiLEd GeTinG PLayer InFo !\n'


# ═══════════════════════════════════════════════════════════════
# #              ★    (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def DeLet_Uid(id, Tok):
    """Xóa người chơi khỏi danh sách bạn bè"""
    print(f' Done FuckinG > {id} ')
    url = 'https://clientbp.common.ggbluefox.com/RemoveFriend'

    headers = DEFAULT_OB_HEADERS.copy()
    headers['Authorization'] = f'Bearer {Tok}'

    data = bytes.fromhex(EnC_AEs(f"08a7c4839f1e10{EnC_Uid(id, Tp='Uid')}"))
    ResPonse = requests.post(url, headers=headers, data=data, verify=False)

    if ResPonse.status_code == 400 and 'BR_FRIEND_NOT_SAME_REGION' in ResPonse.text:
        return f'[b][c]Id : {xMsGFixinG(id)} Not In Same Region !'
    elif ResPonse.status_code == 200:
        return f'[b][c]Good Response Done Delete Id : {xMsGFixinG(id)} !'
    else:
        return f'[b][c]Erorr !'


# ═══════════════════════════════════════════════════════════════
# #              ★ UID   (ᏚAMI YT) ★
# ═══════════════════════════════════════════════════════════════

def ChEck_The_Uid(id):
    """Kiểm tra trạng thái và hạn sử dụng của UID"""
    Api = requests.get(UID_API)
    if Api.status_code not in [200, 201]:
        return False

    lines = Api.text.splitlines()
    for i, line in enumerate(lines):
        if f' - Uid : {id}' in line:
            expire, status = None, None
            for sub_line in lines[i:]:
                if "Expire In" in sub_line:
                    expire = re.search(r"Expire In\s*:\s*(.*)", sub_line).group(1).strip()
                if "Status" in sub_line:
                    status = re.search(r"Status\s*:\s*(\w+)", sub_line).group(1)
                if expire and status:
                    return status, expire
            return False
    return False


# ═══════════════════════════════════════════════════════════════
#                    ★ ᏚAMI YT — END OF FILE ★
# ═══════════════════════════════════════════════════════════════