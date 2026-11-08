

import requests
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
import os
import sys
import psutil

from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ═══════════════════════════════════════════════════════════════
#              ★ Khóa AES và IV (Mã hóa API) ★
# ═══════════════════════════════════════════════════════════════

Key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
Iv  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])


# ═══════════════════════════════════════════════════════════════
#              ★ Bộ tạo màu và thông tin thiết bị ★
# ═══════════════════════════════════════════════════════════════

def generate_random_color():
    """Thẻ màu chat ngẫu nhiên"""
    color_list = ["[FF0000][b][c]", "[FFFFFF][b][c]"]
    return random.choice(color_list)


def Device():
    """Hồ sơ thiết bị ngẫu nhiên (dự phòng tương lai)"""
    versions = [
        '4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8',
        '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3',
        '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3'
    ]
    models = [
        'SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV',
        'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085',
        'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD',
    ]
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    return (
        random.choice(versions),
        random.choice(models),
        random.choice(android_versions),
        random.choice(languages),
        random.choice(countries),
    )


# ═══════════════════════════════════════════════════════════════
#              ★ Mã hóa / Giải mã AES ★
# ═══════════════════════════════════════════════════════════════

def EnC_AEs(HeX):
    """Mã hóa payload API (hex → hex)"""
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()


def DEc_AEs(HeX):
    """Giải mã payload API (hex → hex)"""
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()


def EnC_PacKeT(HeX, K, V):
    """Mã hóa gói tin TCP"""
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()


def DEc_PacKeT(HeX, K, V):
    """Giải mã gói tin TCP"""
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()


# ═══════════════════════════════════════════════════════════════
#              ★ Mã hóa / Giải mã UID và Varint ★
# ═══════════════════════════════════════════════════════════════

def EnC_Uid(H, Tp):
    """Chuyển đổi UID sang varint hex"""
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None


def EnC_Vr(N):
    """Chuyển đổi số sang byte varint"""
    if N < 0:
        return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N:
            BesTo |= 0x80
        H.append(BesTo)
        if not N:
            break
    return bytes(H)


def DEc_Uid(H):
    """Chuyển đổi varint hex sang số nguyên"""
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80:
            break
        s += 7
    return n


# ═══════════════════════════════════════════════════════════════
#              ★ Bộ tạo trường Protobuf ★
# ═══════════════════════════════════════════════════════════════

def CrEaTe_VarianT(field_number, value):
    """Tạo trường Varint"""
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)


def CrEaTe_LenGTh(field_number, value):
    """Tạo trường Length-delimited"""
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value


def CrEaTe_ProTo(fields):
    """Dictionary → Nội dung protobuf"""
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet


# ═══════════════════════════════════════════════════════════════
#              ★ Bộ giải mã Hex và Gói tin ★
# ═══════════════════════════════════════════════════════════════

def DecodE_HeX(H):
    """Số → Chuỗi Hex 2 chữ số"""
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1:
        F = "0" + F
        return F
    else:
        return F


def Fix_PackEt(parsed_results):
    """Sửa kết quả phân tích protobuf"""
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict


def DeCode_PackEt(input_text):
    """Phân tích gói tin hex và trả về JSON"""
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_dict = Fix_PackEt(parsed_results)
        return json.dumps(parsed_results_dict)
    except Exception as e:
        print(f"error {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#              ★ Tiện ích — Banner, Màu sắc, Tin nhắn ★
# ═══════════════════════════════════════════════════════════════

def xBunnEr():
    """Trả về ID Banner"""
    bN = [902000306]
    return random.choice(bN)


def xMsgPr(Msg, Tp, Tp2, id, K, V):
    """Gói tin nhắn chat"""
    feilds = {
        1: id,
        2: Tp2,
        3: Tp,
        4: Msg,
        5: 1735129800,
        7: 2,
        9: {
            1: "xBesTo - C4",
            2: xBunnEr(),
            3: 901048018,
            4: 330,
            5: 909000014,
            8: "xBesTo - C4",
            10: 1,
            11: random.choice([1]),
            13: {1: 2, 2: 1},
            14: {
                1: 1158053040,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            }
        },
        10: "en",
        13: {2: 1, 3: 1},
        14: {}
    }
    Pk = str(CrEaTe_ProTo(feilds).hex())
    Pk = "080112" + EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return GeneRaTePk(str(Pk), '1215', K, V)


def ArA_CoLor():
    """Màu hex sáng ngẫu nhiên"""
    Tp = [
        "FF9999", "99FF99", "99CCFF", "FFD700", "FFB6C1", "FFA07A",
        "98FB98", "E6E6FA", "AFEEEE", "F0E68C", "FFE4B5", "D8BFD8",
        "FFFACD", "87CEFA", "FFDEAD", "B0E0E6", "FFDAB9", "E0FFFF",
        "F5DEB3", "FFC0CB", "FFF0F5", "ADD8E6"
    ]
    return random.choice(Tp)


# ═══════════════════════════════════════════════════════════════
#              ★ Gói tin Chat / Squad ★
# ═══════════════════════════════════════════════════════════════

def OpenCh(idT, sq, K, V):
    """Mở kênh chat"""
    fields = {1: 3, 2: {1: idT, 3: "fr", 4: sq}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '1215', K, V)


def OpenSq(K, V):
    """Mở Squad"""
    fields = {
        1: 1,
        2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1,
            14: {2: 5756, 6: 11, 8: "1.111.5", 9: 2, 10: 4}}
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)


def ChSq(Nu, Uid, K, V):
    """Thay đổi kích thước Squad"""
    fields = {
        1: 17,
        2: {1: int(Uid), 2: 1, 3: int(Nu - 1), 4: 62, 5: "\u001a", 8: 5, 13: 329}
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)


def ExitSq(id, K, V):
    """Rời khỏi Squad"""
    fields = {1: 7, 2: {1: int(11037044965)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)


def MsqSq(msg, idT, K, V):
    """Tin nhắn Squad"""
    fields = {
        1: 1,
        2: {
            1: 12404281032,
            2: idT,
            4: msg,
            7: 2,
            10: "fr",
            9: {
                1: "C4 TEAM",
                2: xBunnEr(),
                4: 330,
                5: 909000014,
                8: "C4 TEAM",
                10: 1,
                11: 1,
                12: {1: 2},
                14: {
                    1: 1158053040,
                    2: 8,
                    3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
                }
            },
            13: {1: 2, 2: 1},
            14: {}
        }
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '1215', K, V)


def SendSq(Nu, Uid, K, V):
    """Gửi lời mời vào Squad"""
    fields = {1: 2, 2: {1: int(Uid), 2: "ME", 4: int(Nu)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)


def JoinSq(code, key, iv):
    """Vào Squad bằng Team Code"""
    fields = {}
    fields[1] = 4
    fields[2] = {}
    fields[2][4] = bytes.fromhex("01090a0b121920")
    fields[2][5] = str(code)
    fields[2][6] = 6
    fields[2][8] = 1
    fields[2][9] = {}
    fields[2][9][2] = 800
    fields[2][9][6] = 11
    fields[2][9][8] = "1.111.1"
    fields[2][9][9] = 5
    fields[2][9][10] = 1
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)


def GhostSq(player_id, nm, secret_code, key, iv):
    """Gói tin Squad tàng hình Ghost"""
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {
                1: int(player_id),
                2: 1159,
                3: f"[b][c][{ArA_CoLor()}]{nm}",
                5: 12,
                6: 999,
                7: 1,
                8: {2: 1, 3: 1},
                9: 3,
            },
            3: secret_code,
        },
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)


# ═══════════════════════════════════════════════════════════════
#              ★ Định dạng UID và Phân tích Proto ★
# ═══════════════════════════════════════════════════════════════

def xMsGFixinG(n):
    """Nhóm 3 chữ số để hiển thị UID đẹp hơn"""
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))


def _V(b, i):
    """Bộ đọc varint nội bộ"""
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        if c < 0x80:
            break
        s += 7
    return r, i


def PrOtO(hx):
    """Bộ phân tích protobuf cấp thấp"""
    b, i, R = bytes.fromhex(hx), 0, {}
    while i < len(b):
        H, i = _V(b, i)
        F, T = H >> 3, H & 7
        if T == 0:
            R[F], i = _V(b, i)
        elif T == 2:
            L, i = _V(b, i)
            S = b[i:i + L]
            i += L
            try:
                R[F] = S.decode()
            except Exception:
                try:
                    R[F] = PrOtO(S.hex())
                except Exception:
                    R[F] = S
        elif T == 5:
            R[F] = int.from_bytes(b[i:i + 4], 'little')
            i += 4
        else:
            raise ValueError(f'Unknown wire type: {T}')
    return R


def GeT_KEy(obj, target):
    """Tìm kiếm key cụ thể từ dictionary"""
    values = []

    def collect(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == target:
                    values.append(v)
                collect(v)
        elif isinstance(o, list):
            for v in o:
                collect(v)

    collect(obj)
    return values[-1] if values else None


# ═══════════════════════════════════════════════════════════════
#              ★ Bộ tạo gói tin chính ★
# ═══════════════════════════════════════════════════════════════

def GeneRaTePk(Pk, N, K, V):
    """Mã hóa gói tin và gắn header hoàn chỉnh"""
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2:
        HeadEr = N + "000000"
    elif len(_) == 3:
        HeadEr = N + "00000"
    elif len(_) == 4:
        HeadEr = N + "0000"
    elif len(_) == 5:
        HeadEr = N + "000"
    else:
        print('ErroR => GeneRatinG ThE PacKeT !!')
        return None
    return bytes.fromhex(HeadEr + _ + PkEnc)


# ═══════════════════════════════════════════════════════════════
#              ★ Kiểm tra quyền truy cập Quân đoàn (Guild) ★
# ═══════════════════════════════════════════════════════════════

def GuiLd_AccEss(Tg, Nm, Uid, BLk, OwN, AprV):
    """Xác minh quyền truy cập Quân đoàn"""
    return Tg in Nm and Uid not in BLk and Uid in (OwN | AprV)


def ChEck_Commande(id):
    """Kiểm tra ký tự không hợp lệ trong lệnh"""
    return "<" not in id and ">" not in id and "[" not in id and "]" not in id


# ═══════════════════════════════════════════════════════════════
#              ★ Khởi động lại Bot và Tiện ích Thời gian ★
# ═══════════════════════════════════════════════════════════════

def ResTarT_BoT():
    """Tự động khởi động lại bot khi gặp lỗi"""
    print('\nError In Src! ')
    p = psutil.Process(os.getpid())
    open_files = p.open_files()
    connections = p.net_connections()
    for handler in open_files:
        try:
            os.close(handler.fd)
        except Exception:
            pass
    for conn in connections:
        try:
            conn.close()
        except Exception:
            pass
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)


def GeT_Time(timestamp):
    """Chuyển timestamp thành ngày/giờ/phút/giây"""
    last_login = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - last_login
    d = diff.days
    h, rem = divmod(diff.seconds, 3600)
    m, s = divmod(rem, 60)
    return d, h, m, s


# ═══════════════════════════════════════════════════════════════
#                    ★ ᏚAMI YT — END OF FILE ★
# ═══════════════════════════════════════════════════════════════