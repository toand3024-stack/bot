# ═══════════════════════════════════════════════════════════════
# bot_core.py (1/3) — LUCKY TCP SUPER BOT
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════

import asyncio, random, json, os, time, math, pickle, ast, re, operator as _op
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import *
from xP import JoinSq, OpenCh, MsqSq, ExitSq, PrOtO
from byte import Encrypt_ID, encrypt_api
from Pb2 import DEcwHisPErMsG_pb2, sQ_pb2, RemoveFriend_Req_pb2

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_random_color():
    return random.choice([
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]",
        "[FF00FF]", "[00FFFF]", "[FF66CC]", "[FFD700]", "[FFFFFF]"
    ])


h1_color = get_random_color()
h2_color = get_random_color()
h3_color = get_random_color()
h4_color = get_random_color()


# ═══════════════════════════════════════════════════════════════
# GLOBALS
# ═══════════════════════════════════════════════════════════════

SPAM_TARGETS_FILE = "spam_targets.json"
online_writer = None
whisper_writer = None
spam_running = False
SPAM_INTERVAL = 0.5
bot_uid = None
ToKen = None
region = None
admin_uid = "2996528672"   # ⚠️ UID Admin Free Fire (có thể đặt từ main.py)
server_url = "https://clientbp.ppmainecoonghj.com"

pending_ghost_future = None
ghost_team_id = None
ghost_squad_code = None
in_squad = False
current_squad_uid = None
current_squad_code = None
squad_opened_event = None
squad_create_lock = None
active_squad_members = set()

spm_tasks = {}
ban_task = None
ban_running = False
ban_targets = set()
evo_cycle_running = False
evo_cycle_task = None
random_cycle_running = False
random_cycle_task = None
freeze_running = False
freeze_task = None
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
msg_spam_running = False
msg_spam_task = None
mg_spam_task = None
reject_spam_running = False
reject_spam_task = None
room_spam_running = False
room_spam_task = None
emote_hijack = False
bot_enabled = True


def is_admin(u):
    return bool(admin_uid) and str(u) == str(admin_uid)


_ALLOWED_BINOPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.FloorDiv: _op.floordiv,
    ast.Mod: _op.mod,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}


def _safe_calc(expr: str):
    if len(expr) > 64:
        raise ValueError("Expression too long")
    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
            return _ALLOWED_UNARYOPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Pow):
                if abs(right) > 100 or abs(left) > 10 ** 6:
                    raise ValueError("Exponent out of range")
                val = left ** right
            elif type(node.op) in _ALLOWED_BINOPS:
                val = _ALLOWED_BINOPS[type(node.op)](left, right)
            else:
                raise ValueError("Unsupported operator")
            if isinstance(val, (int, float)) and abs(val) > 10 ** 100:
                raise ValueError("Result out of range")
            return val
        raise ValueError("Invalid syntax")

    return _eval(tree)

BOT_UID_FOR_HI = None
BOT_PW_FOR_HI  = None

BLOCK_EMOTE_UID = admin_uid
CACHE_FILE      = "status_cache.pkl"
CACHE_TIMEOUT   = 30

_clan_msg_key = None
_clan_msg_iv = None
_clan_msg_bot_uid = None
_clan_msg_clan_id = None
_clan_message_task = None

BADGE_VALUES = {
    "s1": 1048576,
    "s2": 32768,
    "s3": 2048,
    "s4": 64,
    "s5": 262144
}
BADGE_REQUESTS = 5
PACKET_DELAY_ULTRA_FAST = 0.1

EVO_IDS = [
    909000063, 909000075, 909040010, 909000081, 909039011,
    909045001, 909038012, 909042008, 909051003, 909035012,
    909000098, 909033002, 909037011, 909049010, 909041005,
    909038010, 909033001, 909035007, 909000090, 909000085,
    909000068
]


# ═══════════════════════════════════════════════════════════════
# EMOTE SYSTEMS
# ═══════════════════════════════════════════════════════════════

GENERAL_EMOTES_MAP = {}
EMOTE_MAP          = {}
NAME_TO_EMOTE_ID   = {}
EMOTE_MENU         = {}

try:
    with open("emotes.json", "r", encoding="utf-8") as _f:
        _raw = json.load(_f)
    for _num, _info in _raw.items():
        _id   = int(_info["id"])
        _name = str(_info.get("name", f"emote_{_num}"))
        GENERAL_EMOTES_MAP[str(_num)] = _id
        EMOTE_MAP[int(_num)]          = _id
        EMOTE_MENU[str(_num)]         = _name
        _n = _name.lower().strip()
        if _n and not _n.startswith("emote_") and _n not in NAME_TO_EMOTE_ID:
            NAME_TO_EMOTE_ID[_n] = _id
    print(f"✅ Loaded {len(GENERAL_EMOTES_MAP)} emotes from emotes.json")
    print(f"✅ Built {len(NAME_TO_EMOTE_ID)} name→emote mappings")
except Exception as _e:
    print(f"❌ emotes.json load error: {_e}")

try:
    with open("emote_menu.json", "r", encoding="utf-8") as _f:
        _custom_menu = json.load(_f)
        if isinstance(_custom_menu, dict):
            EMOTE_MENU.update({str(k): str(v) for k, v in _custom_menu.items()})
except Exception:
    pass

NAME_EMOTES = {
    "ak": 909000063, "scar": 909000068, "mp40": 909000075,
    "m1014": 909000081, "xm8": 909000085, "famas": 909000090,
    "ump": 909000098, "m1887": 909035007, "woodpecker": 909042008,
    "groza": 909041005, "m4a1": 909033001, "thompson": 909038010,
    "g18": 909038012, "parafal": 909045001, "p90": 909049010,
    "m60": 909051003, "fist": 909037011, "ring": 909050009,
    "heart": 909038004, "love": 909000010, "dance": 909000027,
    "hello": 909000001, "hi": 909000001, "money": 909000129,
    "lol": 909000002, "sad": 909038005, "angry": 909000014,
    "chicken": 909000006, "dab": 909000005, "selfie": 909000040,
    "shower": 909051004, "flower": 909051002, "petals": 909051013,
}
for _k, _v in NAME_EMOTES.items():
    NAME_TO_EMOTE_ID.setdefault(_k.lower(), _v)
NUMBER_EMOTES = GENERAL_EMOTES_MAP


def get_menu_page(page=1, per_page=5):
    try:
        items = sorted(EMOTE_MENU.items(), key=lambda x: int(x[0]))
    except Exception:
        items = list(EMOTE_MENU.items())

    total_items = len(items)
    if total_items == 0:
        return "[B][C][FF0000]❌ Emote menu is empty."

    total_pages = max(1, math.ceil(total_items / per_page))
    try:
        page = int(page)
    except Exception:
        page = 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end   = start + per_page

    text  = f"[B][C][FF0000]🎭 MENU {page}/{total_pages}\n"
    text += f"[C][FFFFFF]────────────────\n"

    for num, name in items[start:end]:
        text += f"[C][FFFFFF]{num} ➤ [FFFF00]{name}\n"

    text += f"[C][FFFFFF]────────────────\n"
    nav = []
    if page > 1:
        nav.append(f"[00FF00]/menu {page-1} ◀")
    if page < total_pages:
        nav.append(f"[00FF00]/menu {page+1} ▶")
    if nav:
        text += f"[C]{'  '.join(nav)}\n"

    return text


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def load_spam_targets():
    if os.path.exists(SPAM_TARGETS_FILE):
        with open(SPAM_TARGETS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_spam_targets():
    with open(SPAM_TARGETS_FILE, "w") as f:
        json.dump(list(spam_targets), f)


spam_targets = load_spam_targets()


def get_random_avatar():
    avatar_list = [
        902050001, 902050002, 902050003, 902039016, 902050004,
        902047011, 902047010, 902049015, 902050006, 902049020
    ]
    return random.choice(avatar_list)


def get_random_sticker():
    sticker_packs = [
        ("1200000001", 1, 24),
        ("1200000004", 1, 15),
        ("1200000002", 1, 13),
    ]
    pack_id, start, end = random.choice(sticker_packs)
    sticker_no = random.randint(start, end)
    return f"[1={pack_id}-{sticker_no}]"


def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))


def fix_num(number):
    fixed = ""
    count = 0
    num_str = str(number)
    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0
    return fixed


def fixnum(num):
    num_str = str(num)
    return "[C]" + "[C]".join(num_str) + "[C]"


def dec_to_hex(decimal):
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()


async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    return cipher.encrypt(padded_packet).hex()


async def nmnmmmmn(packet_hex, key, iv):
    return await encrypt_packet(packet_hex, key, iv)


# ═══════════════════════════════════════════════════════════════
# AUTH TOKEN BUILDERS
# ═══════════════════════════════════════════════════════════════

def build_ob55_online_auth(account_uid, token, kts, key, iv):
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token


def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        jwt_bytes = jwt_token.encode('utf-8')
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
        uid_b = int(account_id).to_bytes(8, 'big')
        ts_b = int(timestamp).to_bytes(4, 'big')
        len_b = len(ct).to_bytes(4, 'big')
        header = bytes.fromhex('6d19') + uid_b + ts_b + len_b
        return (header + ct).hex()
    except Exception as e:
        print(f"[AUTH TOKEN ERROR] {e}")
        return None


async def cHTypE(H):
    if not H:
        return 'Squid'
    elif H == 1:
        return 'CLan'
    elif H == 2:
        return 'PrivaTe'


async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto


async def GeTSQDaTa(D):
    try:
        return D['5']['data']['1']['data'], D['5']['data']['17']['data'], D['5']['data']['31']['data']
    except KeyError:
        return None, None, None


async def get_colorful_message(message_text, message_number):
    color = "FF0000" if message_number % 2 else "FFFFFF"
    return f"[C][B][{color}]{message_text}"


# ═══════════════════════════════════════════════════════════════
# PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════

async def NewClanChatPacket(message_text, key, iv, clan_id=3102281341):
    fields = {
        1: 16801068917, 2: 18, 4: 1,
        5: {
            1: 16801068917, 2: clan_id, 3: 1, 4: 'LUCKY TCP',
            5: 1785944381, 7: 6,
            9: {
                1: message_text, 4: 301, 8: '♧LUCKY TCP♧', 13: '',
                14: {1: 16801068917},
                18: {1: 16801068917, 3: 1, 4: ''}
            },
            10: 'ar', 13: {2: 1, 3: 1}, 14: '',
            16: int(time.time() * 1000)
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def AuthClan(clan_id, clan_compiled_data, key, iv):
    if isinstance(clan_compiled_data, str):
        try:
            clan_compiled_data = clan_compiled_data.encode(
                'latin-1', errors='surrogateescape'
            )
        except Exception:
            clan_compiled_data = clan_compiled_data.encode(
                'utf-8', errors='surrogateescape'
            )
    fields = {1: 3, 2: {1: int(clan_id), 2: 1, 4: clan_compiled_data}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1201', key, iv)


async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid':
        return await xSEndMsgsQ(message, chat_id, key, iv, region or "VN")
    elif TypE == 'CLan':
        try:
            return await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
        except Exception as e:
            print(f"Guild old packet error, fallback: {e}")
            return await NewClanChatPacket(message, key, iv, chat_id)
    elif TypE == 'PrivaTe':
        return await xSEndMsg(message, 2, Uid, Uid, key, iv)


async def SEndPacKeT(ChaT, OnLinE, TypE, PacKeT):
    if not PacKeT:
        return False
    if TypE == 'ChaT':
        w = ChaT or whisper_writer
        if w is not None and not w.is_closing():
            w.write(PacKeT)
            await w.drain()
            return True
    elif TypE == 'OnLine':
        w = OnLinE or online_writer
        if w is not None and not w.is_closing():
            w.write(PacKeT)
            await w.drain()
            return True
    return False


async def safe_send_message(chat_type, message, uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            packet = await SEndMsG(chat_type, message, uid, chat_id, key, iv)
            if packet:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', packet)
                return True
        except Exception as e:
            print(f"❌ Send fail (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False


# ═══════════════════════════════════════════════════════════════
# WELCOME (Fixed Boxes)
# ═══════════════════════════════════════════════════════════════

HELP_DELAY = 0.1
WELCOME_DELAY = 1
WELCOME_COOLDOWN = 1800

WELCOME_TEXT = (
    "[B][C][FFFF00]╔════════════════════╗\n"
    "[B][C][FFFF00]║  [FFFFFF]LUCKY TCP BOT[FFFF00]     ║\n"
    "[B][C][FFFF00]║  [FFFFFF]CHÀO MỪNG BẠN[FFFF00]     ║\n"
    "[B][C][FFFF00]╚════════════════════╝\n"
    "\n"
    "[B][C][FFFFFF]Xin chào, chào mừng đến với LUCKY TCP!\n"
    "\n"
    "[B][C][00FFFF]╭───── ✦ TÍNH NĂNG ✦ ─────╮\n"
    "[B][FFFFFF]  ➤ Hệ thống AI thông minh\n"
    "[B][FFFFFF]  ➤ Lệnh giải trí vui nhộn\n"
    "[B][FFFFFF]  ➤ Công cụ tra cứu UID\n"
    "[B][FFFFFF]  ➤ Hệ thống Emote & Danh hiệu\n"
    "[B][FFFFFF]  ➤ Phản hồi siêu tốc\n"
    "[B][C][00FFFF]╰────────────────────────╯\n"
    "\n"
    "[B][C][FFFFFF]Gõ /help để xem toàn bộ lệnh\n"
    "[B][C][FFFFFF]Gõ /menu để mở danh sách emote\n"
    "\n"
    "[B][C][00FF00]━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "[B][C][FFD700]      LUCKY TCP PREMIUM  \n"
    "[B][C][FFFFFF]   Nhanh • An Toàn • Thông Minh\n"
    "[B][C][00FF00]━━━━━━━━━━━━━━━━━━━━━━━━━━"
)
WELCOMED = {}


async def send_welcome(chat_code, key, iv, delay=None):
    now = time.time()
    last = WELCOMED.get(chat_code)
    if last and now - last < WELCOME_COOLDOWN:
        return
    WELCOMED[chat_code] = now
    await asyncio.sleep(WELCOME_DELAY if delay is None else delay)
    await safe_send_message(0, WELCOME_TEXT, None, chat_code, key, iv)


# ═══════════════════════════════════════════════════════════════
# ⭐ CLAN AUTO MESSAGE ⭐
# ═══════════════════════════════════════════════════════════════

async def clan_message_loop():
    global _clan_msg_key, _clan_msg_iv, _clan_msg_bot_uid, _clan_msg_clan_id
    try:
        await asyncio.sleep(5)
        if _clan_msg_clan_id and _clan_msg_clan_id > 0 and _clan_msg_key and _clan_msg_iv:
            clan_msg = "[b][c]Dev : [00ffff]RᴇᴅLᴜᴄᴋʏXʏᴢ"
            await safe_send_message(1, clan_msg, _clan_msg_bot_uid, _clan_msg_clan_id, _clan_msg_key, _clan_msg_iv)
            print(f"[CLAN] Startup message sent to clan {_clan_msg_clan_id}")

        while True:
            await asyncio.sleep(18000)  # 5 hours
            if _clan_msg_clan_id and _clan_msg_clan_id > 0 and _clan_msg_key and _clan_msg_iv:
                clan_msg = "[b][c]Dev : [00ffff]RᴇᴅLᴜᴄᴋʏXʏᴢ"
                await safe_send_message(1, clan_msg, _clan_msg_bot_uid, _clan_msg_clan_id, _clan_msg_key, _clan_msg_iv)
                print(f"[CLAN] 5-hour message sent to clan {_clan_msg_clan_id}")
    except asyncio.CancelledError:
        print("[CLAN] Message loop cancelled")
    except Exception as e:
        print(f"[CLAN] Message loop error: {e}")


# ═══════════════════════════════════════════════════════════════
# BANNER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def base_to_hex(number):
    hex_str = hex(number)[2:]
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str.upper()


async def DEVIL(client_id, key, iv):
    banner_text = f"""   
.
.
.
[B][C][00FF00]★  L U C K Y   B O T ★
[FF0000]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF9900]D O N E   H A C K I N G
[B][C][E75480]Y O U R   A C C O U N T
[81DACA]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF0000]F U C K   Y O U
[CCFFCC]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]P O W E R E D   B Y   L U C K Y
[FFFF00]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][00FF00]F O L L O W   M E   O N   T I K T O K
[B][C][FFFFFF]@rlx_lucky_
[00008B]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]I F   Y O U   D O N T   F O L L O W   M E
[B][C][FF0000]I   W I L L   B A N   Y O U R   A C C O U N T
        """
    fields = {
        1: 5,
        2: {1: int(client_id), 2: 1, 3: int(client_id), 4: banner_text}
    }
    packet = await CrEaTe_ProTo(fields)
    packet_hex = packet.hex()
    encrypted_packet = await EnC_PacKeT(packet_hex, key, iv)
    header_length = len(encrypted_packet) // 2
    header_length_final = await DecodE_HeX(header_length)
    if len(header_length_final) == 2:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 3:
        final_packet = "051500000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 4:
        final_packet = "05150000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 5:
        final_packet = "0515000" + header_length_final + encrypted_packet
    else:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    return bytes.fromhex(final_packet)


async def DEVIL1(client_id, key, iv):
    gay_text = f"""   
.
.
.
[B][C][00FF00]★  L U C K Y   B O T ★
[FF0000]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF9900]D O N E   H A C K I N G
[B][C][E75480]Y O U R   A C C O U N T
[81DACA]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF0000]F U C K   Y O U
[CCFFCC]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]P O W E R E D   B Y   L U C K Y
[FFFF00]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][00FF00]F O L L O W   M E   O N   T I K T O K
[B][C][FFFFFF]@rlx_lucky_
[00008B]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]I F   Y O U   D O N T   F O L L O W   M E
[B][C][FF0000]I   W I L L   B A N   Y O U R   A C C O U N T
        """
    fields = {1: int(client_id), 2: 5, 4: 50, 5: {1: int(client_id), 2: gay_text}}
    packet = await CrEaTe_ProTo(fields)
    packet_hex = packet.hex()
    encrypted_packet = await EnC_PacKeT(packet_hex, key, iv)
    header_length = len(encrypted_packet) // 2
    header_length_final = await DecodE_HeX(header_length)
    if len(header_length_final) == 2:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 3:
        final_packet = "051500000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 4:
        final_packet = "05150000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 5:
        final_packet = "0515000" + header_length_final + encrypted_packet
    else:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    return bytes.fromhex(final_packet)

# ═══════════════════════════════════════════════════════════════
# bot_core.py (2/3) — LUCKY TCP SUPER BOT
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# BADGE COMMAND FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def request_join_with_badge(target_uid, badge_value, key, iv, region):
    fields = {
        1: 33,
        2: {
            1: int(target_uid),
            2: region.upper(),
            3: 1,
            4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: "iG:[C][B][FF0000] LUCKY TCP",
            7: 330,
            8: 1000,
            10: region.upper(),
            11: bytes([49, 97, 99, 52, 98, 56, 48, 101, 99, 102, 48, 52, 55, 56, 97, 52, 52, 50, 48, 51, 98, 102, 56, 102, 97, 99, 54, 49, 50, 48, 102, 53]),
            12: 1,
            13: int(target_uid),
            14: {
                1: 2203434355,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            16: 1,
            17: 1,
            18: 312,
            19: 46,
            23: bytes([16, 1, 24, 1]),
            24: int(get_random_avatar()),
            26: "",
            28: "",
            31: {
                1: 1,
                2: int(badge_value)
            },
            32: int(badge_value),
            34: {
                1: int(target_uid),
                2: 8,
                3: bytes([15, 6, 21, 8, 10, 11, 19, 12, 17, 4, 14, 20, 7, 2, 1, 5, 16, 3, 13, 18])
            }
        },
        10: "en",
        13: {
            2: 1,
            3: 1
        }
    }
    packet = (await CrEaTe_ProTo(fields)).hex()
    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
    return await GeneRaTePk(packet, packet_type, key, iv)


async def handle_badge_command(cmd, inPuTMsG, uid, chat_id, key, iv, region, chat_type):
    parts = inPuTMsG.strip().split()
    if len(parts) < 2:
        error_msg = f"[B][C][FF0000]❌ Cách dùng: /{cmd} <uid>\nVí dụ: /{cmd} 123456789\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    target_uid = parts[1]
    badge_value = BADGE_VALUES.get(cmd, 1048576)
    if not target_uid.isdigit():
        error_msg = f"[B][C][FF0000]❌ Vui lòng nhập UID hợp lệ!\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    total_requests = BADGE_REQUESTS
    packet_delay = PACKET_DELAY_ULTRA_FAST
    badge_names = {
        's1': 'Huy hiệu Craftland 🏆',
        's2': 'Huy hiệu V-Badge Mới 🔥',
        's3': 'Huy hiệu Điều Hành Viên 👮',
        's4': 'Huy hiệu V-Badge Nhỏ ⚡',
        's5': 'Huy hiệu Tuyển Thủ 💎'
    }
    badge_name = badge_names.get(cmd, 'Huy hiệu đặc biệt')
    initial_msg = f"[B][C][1E90FF]🌀 {badge_name}\n🎯 Mục tiêu: {target_uid}\n📦 Số lượt: {total_requests}\n⚡ Tốc độ: {packet_delay}s\n"
    await safe_send_message(chat_type, initial_msg, uid, chat_id, key, iv)
    try:
        leave_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
        await asyncio.sleep(0.3)

        join_packet = await request_join_with_badge(target_uid, badge_value, key, iv, region)
        for i in range(total_requests):
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await asyncio.sleep(packet_delay)

        success_msg = f"[B][C][00FF00]✅ HOÀN THÀNH {badge_name}!\n🎯 Mục tiêu: {target_uid}\n📦 Đã gửi: {total_requests} yêu cầu\n⚡ Tốc độ: {packet_delay}s\n"
        await safe_send_message(chat_type, success_msg, uid, chat_id, key, iv)
    except Exception as e:
        error_msg = f"[B][C][FF0000]❌ Lỗi lệnh /{cmd}: {str(e)}\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)


async def Room_Spam(Uid, Rm, Nm, K, V, chat_type=None, sender_uid=None, chat_id=None):
    global room_spam_running
    badge_sequence = [1048576, 32768, 2048, 64, 262144]
    badge_index = 0
    for i in range(3000):
        if not room_spam_running:
            break
        try:
            current_badge_value = badge_sequence[badge_index % 5]
            fields = {
                1: 78,
                2: {
                    1: int(Rm), 2: f"iG:[C][B][FF0000] {Nm}", 3: {2: 1, 3: 1},
                    4: 330, 5: 6000, 6: 201,
                    10: int(get_random_avatar()), 11: int(Uid), 12: 1,
                    15: {1: 1, 2: current_badge_value}, 16: current_badge_value,
                    18: {1: 11481904755, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
                    31: {1: 1, 2: current_badge_value}, 32: current_badge_value,
                    34: {1: int(Uid), 2: 8, 3: bytes([15, 6, 21, 8, 10, 11, 19, 12, 17, 4, 14, 20, 7, 2, 1, 5, 16, 3, 13, 18])}
                }
            }
            spam_packet = await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_packet)
            badge_index += 1
            if (i + 1) % 100 == 0:
                print(f"Tiến độ spam phòng {Rm}: {i + 1}/3000")
            await asyncio.sleep(PACKET_DELAY_ULTRA_FAST)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.1)
    was_running = room_spam_running
    room_spam_running = False
    if was_running and chat_type is not None and chat_id is not None:
        await safe_send_message(
            chat_type,
            f"[B][C][FFFFFF]✅ Đã hoàn thành spam phòng {Rm}",
            sender_uid, chat_id, K, V
        )
    return True


# ═══════════════════════════════════════════════════════════════
# FULL PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════

_OB55_SQUAD_SECURITY = {
    1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
    2: 130,
    3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
    4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.132.1", 9: 3, 10: 2,
    11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="
}


async def JoinSq_original(code, K, V):
    reg = (region or "VN").upper()
    lang = "vi" if reg == "VN" else "en"
    skinz = {
        1: 4,
        2: {
            4: "\u0001\u0007\t\n\u000b\u0012\u0019 '",
            5: str(code),
            6: 6,
            8: 1,
            9: dict(_OB55_SQUAD_SECURITY),
            11: {1: "IDC4", 2: 281, 3: reg},
            13: lang, 16: "7OR\u0019", 20: "\b\u0015", 27: "\bH\u0010\u0003"
        }
    }
    pkt_type = '0514' if reg == "IND" else ('0519' if reg == "BD" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(skinz)).hex(), pkt_type, K, V)


async def SKANHAIYAAccepted(uid, code, K, V, region):
    reg = (region or "VN").upper()
    lang = "vi" if reg == "VN" else "en"
    fields = {
        1: 4,
        2: {
            1: int(uid), 3: int(uid),
            4: "\u0001\u0007\t\n\u000b\u0012\u0019 '",
            8: 1,
            9: dict(_OB55_SQUAD_SECURITY),
            10: str(code),
            11: {1: "IDC3", 2: 84, 3: reg},
            13: lang, 16: "7OR\u0019",
            20: "\b\u0015", 27: "\bH\u0010\u0003"
        }
    }
    pkt_type = '0514' if reg == "IND" else ('0519' if reg == "BD" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt_type, K, V)


async def accept_squad_invite(group_id, joiner_account_id, invitee_type, key, iv, region="bd"):
    fields = {1: 38, 2: {1: int(group_id), 2: int(joiner_account_id), 8: int(invitee_type)}}
    pkt_type = '0514' if region.lower() == "ind" else ('0519' if region.lower() == "bd" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt_type, key, iv)


async def leave_channel_req(channel_id, channel_type, key, iv):
    fields = {1: 4, 2: {1: int(channel_id), 2: int(channel_type), 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)


async def SPamSqForSpm(Uid, K, V):
    same_value = random.choice([4096, 16384, 8192])
    fields = {
        1: 33,
        2: {
            1: int(Uid), 2: "ME", 3: 1, 4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: "TT:[C][B][FF0000] @rlx_lucky_",
            7: 330, 8: 1000, 10: "ME",
            11: bytes([49,97,99,52,98,56,48,101,99,102,48,52,55,56,97,52,52,50,48,51,98,102,56,102,97,99,54,49,50,48,102,53]),
            12: 1, 13: int(Uid),
            14: {1: 2203434355, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
            16: 1, 17: 1, 18: 312, 19: 46,
            23: bytes([16, 1, 24, 1]),
            24: await xBunnEr(), 26: "", 28: "",
            31: {1: 1, 2: same_value}, 32: same_value,
            34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}
        },
        10: "en", 13: {2: 1, 3: 1}
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)


async def GhostPakcet(player_id, nm, secret_code, key, iv):
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {
                1: int(player_id), 2: 1159,
                3: f"[b][c]{get_random_color()}{nm}", 5: 12, 6: 999, 7: 1,
                8: {2: 1, 3: 1}, 9: 3
            },
            3: secret_code
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def xSKINZxLag(K, I):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 15, 2: {1: 804266360, 2: 1}})).hex(), '0515', K, I)


async def xBaNchaTxSkInZ(uidd, K, V):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 3, 2: {1: int(uidd), 3: "fr", 4: "1750728024661459697_3qind8eeqs"}})).hex(), '1215', K, V)


async def create_lw5_packet1(key, iv):
    fields = {
        1: 1,
        2: {
            2: "0b", 3: 43, 4: 1, 5: "en",
            8: {1: "IDC3", 2: 109, 3: "BD"},
            9: 1, 10: "01090a0b12192027", 11: 1, 13: 1,
            14: {
                1: "08FBA33CFF11B915020FEB099999000002BF000C02B3024798E574700E9B7471467625142200004375a63c900e748c3f6a311e04000000ff42002b09cacfa16d",
                2: 1023,
                3: "715c5f561b06054a03530500570555590f5100040250000255010e520653000303525306570c02501500064d72584347411f051a001e1206074f184a677f5a564775765b554a6d74451d58584902574440625b64670c14004b600a7d4d740c670100040264586b7d586c02016e657c5b60574b03081500044d60795258726206047f04600f405b18710347746242085f055442530a160e4d58496f0c7c4501750763605c575f02765a485e5f4c407f4b625e400e1b054973535b40655e5151566e6507797e6b47727a1c6e455762637d650708100a447e704c1e530200437a604b66065d595f58444c5a06095a6c44677a0c14040b4f705b7d75624374067840416d60067353017f5972506356014354680a12044950406940046265725c4f5d56416250737b7c42035b7d43667f645e0b12034d5262577f13554f574b0e76580201766b50520347756947616747000a1604014b6473441869176f795f5d78755c58057d4d545e53747b08725274580514004a08666b585654050b5c7f5e584d725a4f69755056055c61475566740e100f4b76514178587d5f727f00077a070953507f72467d40794f667b42560a16054f7a627d4778417a047c7e717b7c4c78557b4b7807627a01714573600a",
                4: "{Y_R", 6: 13, 7: "136601706b6f54001513", 8: "2.126.20", 9: 2, 10: 1,
                11: "0362625351367a6e2f56386835416456324b796f566c576a3265735033734558335070623443526c656c47355732327673496e477a425a49677375684a664336766942532f4277526d3632374a624a724c562b586b664c516c6749424634615664544e34473869494c456e4c7643347754354670754e66444b7746367765466d675a2b2b36704d57694549677343415756457144554a454d737271515a306b544266635a45334959485661774d5332622b4f6b5a477a755171576e3645624c6a3932646c31307754614d55714e355556796742506f454572376651673249754332545a773333796c71493838627562512f6e425072353577785436617955544d63624d2b756d4542345a736c5165504d58725365737864622f30577967786849384a352f73484f685730494a49643450534b6d6a41734b315251495257634c35646355554b457a6d33334475735877384a5267483364412b66414b336433726a4241317954327451326c2f73584c6d4b4b6456707062624b4f3272694c384947382b634a3863506533314241456d517876744f495631323658394c4b35414c6a38533631526d6159617077676e4579724a5a7a624d4c596c3542554b6d7934473546334c6152454c4e6d726a684f557065462f39686f64356c526378623250777244566d455665715355764a456548644e375279344c707035563466392f6f6d3837426b5a6c6159364c5439396b5579554266434c5538647a4a2b43655a35784a44585064654a51686e46496945506e7a506d32334b637a2b512b384a51307a522b5a5a41762b694873454748516a536e61467862356a517a526c374f5a793241385731437263513d"
            },
            19: 329, 21: "374f5219", 24: {1: 21}, 27: "a_1477547277882450725"
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def create_lw5_packet2(key, iv):
    return await GeneRaTePk(
        (await CrEaTe_ProTo({1: 17, 2: {1: 17165783357, 2: 1, 3: 4, 4: 6100, 5: b'\x1a', 8: 5, 13: 329}})).hex(),
        '0515', key, iv
    )


async def send_sticker_packet(target_uid, chat_id, key, iv, nickname="LUCKY TCP"):
    try:
        sticker_value = get_random_sticker()
        fields = {
            1: 1,
            2: {
                1: int(target_uid), 2: int(chat_id),
                5: int(time.time()),
                8: f'{{"StickerStr" : "{sticker_value}", "type":"Sticker"}}',
                9: {
                    1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                    8: "LUCKY TCP TEAM", 10: 1, 11: 66, 12: 66, 13: {1: 2},
                    14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}
                },
                10: "en", 13: {2: 2, 3: 1}, 14: {}
            }
        }
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Sticker error: {e}")
        return None


async def animation_packet(animation_id, key, iv, region="VN"):
    fields = {1: 88, 2: {1: {1: int(animation_id)}}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    if region.lower() == "ind":
        pt = "0514"
    elif region.lower() == "bd":
        pt = "0519"
    else:
        pt = "0515"
    return await GeneRaTePk(packet_hex, pt, key, iv)


async def Look_Changer(bundle_id, key, iv, look_type=1, region="bd"):
    fields = {1: 88, 2: {1: {1: bundle_id, 2: look_type}, 2: 2}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if region.lower() == "ind":
        pt = "0514"
    elif region.lower() == "bd":
        pt = "0519"
    else:
        pt = "0515"
    if len(hl) == 2:
        h = f"{pt}000000"
    elif len(hl) == 3:
        h = f"{pt}00000"
    elif len(hl) == 4:
        h = f"{pt}0000"
    elif len(hl) == 5:
        h = f"{pt}000"
    else:
        h = f"{pt}000000"
    return bytes.fromhex(h + hl + encrypted)


async def banecipher(target_uid, key, iv):
    banner_text = ".\n.\n.\n[b][FF0000]LUCKY TCP[FFFFFF] ⚡\n.\n.\n."
    fields = {1: 5, 2: {1: int(target_uid), 2: 1, 3: int(target_uid), 4: banner_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)


async def banecipher1(target_uid, key, iv):
    gay_text = ".\n.\n.\n[b][FF0000]LUCKY TCP ⚡[FFFFFF]\n.\n.\n."
    fields = {1: int(target_uid), 2: 5, 4: 50, 5: {1: int(target_uid), 2: gay_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)


async def convert_kyro_to_your_system(target_uid, chat_id, key, iv, nickname="LUCKY TCP", title_id=None):
    try:
        if title_id is None:
            available_titles = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015,
                                904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
            title_id = random.choice(available_titles)
        fields = {
            1: 1,
            2: {
                1: int(target_uid), 2: int(chat_id),
                5: int(time.time()),
                8: f'{{"TitleID":{title_id},"type":"Title"}}',
                9: {
                    1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                    8: "LUCKY TCP TEAM", 10: 1, 11: 1, 13: {1: 2},
                    14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}
                },
                10: "en", 13: {2: 2, 3: 1}, 14: {}
            }
        }
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Title error: {e}")
        return None
# ═══════════════════════════════════════════════════════════════
# 3bot_core.py — LUCKY TCP SUPER BOT (Loops)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


async def spm_loop(uid, key, iv, interval=0.5):
    while True:
        try:
            if online_writer is not None:
                packet = await SPamSqForSpm(uid, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', packet)
            else:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"spm_loop error for {uid}: {e}")
        await asyncio.sleep(interval)


async def ban_loop(key, iv, interval=0.5):
    global ban_running, ban_targets
    ban_running = True
    while ban_running:
        if online_writer is not None and ban_targets:
            for uid in list(ban_targets):
                try:
                    ban_pkt = await xBaNchaTxSkInZ(uid, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ban_pkt)
                except Exception as e:
                    print(f"Ban error: {e}")
        await asyncio.sleep(interval)


async def evo_gun_cycle(uids, evo_ids_list, key, iv, region):
    global evo_cycle_running
    cc = 0
    while evo_cycle_running:
        cc += 1
        for emote_id in evo_ids_list:
            if not evo_cycle_running:
                break
            for uid_str in uids:
                try:
                    H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                except Exception as e:
                    print(f"Emote error: {e}")
            if evo_cycle_running:
                for i in range(5):
                    if not evo_cycle_running:
                        break
                    await asyncio.sleep(1)
        if evo_cycle_running:
            await asyncio.sleep(2)


async def random_emote_cycle(uids, key, iv, region, interval=4):
    global random_cycle_running
    # Tập hợp danh sách các ID emote hợp lệ từ hệ thống
    candidates = list(set(list(EMOTE_MAP.values()) + list(NAME_EMOTES.values()) + EVO_IDS))
    if not candidates:
        candidates = EVO_IDS
    while random_cycle_running:
        emote_id = random.choice(candidates)
        for uid_str in uids:
            try:
                H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Random emote error: {e}")
        if random_cycle_running:
            for _ in range(interval):
                if not random_cycle_running:
                    break
                await asyncio.sleep(1)


async def fast_emote_spam(uids, emote_id, key, iv, region):
    global fast_spam_running
    count = 0
    while fast_spam_running and count < 25:
        for uid in uids:
            try:
                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception:
                pass
        count += 1
        await asyncio.sleep(0.1)


async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    global custom_spam_running
    count = 0
    while custom_spam_running and count < times:
        try:
            H = await Emote_k(int(uid), int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)
        except Exception:
            break


async def reject_spam_loop(target_uid, key, iv):
    global reject_spam_running
    count = 0
    while reject_spam_running and count < 150:
        try:
            p1 = await banecipher1(target_uid, key, iv)
            p2 = await banecipher(target_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p1)
            await asyncio.sleep(0.1)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p2)
            count += 1
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"Reject error: {e}")
            break
    return count


async def msg_spam_loop(message_text, times, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    while msg_spam_running and count < times:
        try:
            colorful = await get_colorful_message(message_text, count + 1)
            msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
            if msg_packet and whisper_writer:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                count += 1
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Msg error: {e}")
            break
    return count


async def xSEndMsgsQQ(Msg, id, K, V):
    fields = {
        1: id, 2: id, 4: Msg, 5: 1756580149, 7: 2, 8: 904990072,
        9: {
            1: "LUCKY TCP - C4", 2: get_random_avatar(), 4: 330, 5: 1001000001,
            8: "LUCKY TCP - C4", 10: 1, 11: 1, 13: {1: 2},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
        },
        10: "en", 13: {2: 2, 3: 1}
    }
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


async def send_wave_messages(message_text, repeats, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    total_cycles = 0
    while msg_spam_running and total_cycles < repeats:
        try:
            for i in range(1, len(message_text) + 1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            for i in range(len(message_text) - 1, 0, -1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            total_cycles += 1
        except Exception as e:
            print(f"Wave error: {e}")
            break
    return count, total_cycles


async def freeze_emote_spam(uid, key, iv, region, chat_type, chat_id, sender_uid):
    global freeze_running
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    cycles = 0
    while freeze_running and cycles < 10:
        for emote_id in FREEZE_EMOTES:
            if not freeze_running:
                break
            try:
                emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                await asyncio.sleep(0.1)
            except Exception:
                pass
        cycles += 1
        await asyncio.sleep(1)
    return cycles
# ═══════════════════════════════════════════════════════════════
# 4bot_core.py — LUCKY TCP SUPER BOT (API + Helpers)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# API CALLS
# ═══════════════════════════════════════════════════════════════

async def send_friend_request(target_uid, token, region):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        ep = cipher.encrypt(pad(bytes.fromhex(payload), AES.block_size)).hex()
        base = server_url.rstrip('/') if server_url else "https://clientbp.ppmainecoonghj.com"
        url = f"{base}/RequestAddingFriend"
        headers = {
            "Authorization": f"Bearer {token}", "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1", "ReleaseVersion": "OB55",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=bytes.fromhex(ep), ssl=False) as r:
                return (True, "✅ Đã gửi lời mời kết bạn thành công") if r.status == 200 else (False, f"❌ Trạng thái: {r.status}")
    except Exception as e:
        return False, f"❌ Lỗi: {str(e)}"


async def remove_friend(target_uid, token, region):
    try:
        msg = RemoveFriend_Req_pb2.RemoveFriend()
        msg.AuthorUid = int(bot_uid) if bot_uid else int(admin_uid)
        msg.TargetUid = int(target_uid)
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        eb = cipher.encrypt(pad(msg.SerializeToString(), AES.block_size))
        base = server_url.rstrip('/') if server_url else "https://clientbp.ppmainecoonghj.com"
        url = f"{base}/RemoveFriend"
        headers = {
            'Authorization': f"Bearer {token}", 'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)",
            'Content-Type': "application/x-www-form-urlencoded", 'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1", 'ReleaseVersion': "OB55"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=eb, headers=headers, ssl=False) as r:
                return (True, "✅ Đã huỷ kết bạn thành công") if r.status == 200 else (False, f"❌ Trạng thái: {r.status}")
    except Exception as e:
        return False, f"❌ Lỗi: {str(e)}"


async def check_banned(player_id):
    try:
        url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Thất bại: {r.status}"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"


async def get_player_info(player_id):
    try:
        url = f"https://nirob-x-info.vercel.app/info?uid={player_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Thất bại: {r.status}"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"


def format_player_info(data):
    basic = data.get("basicInfo", {})
    clan = data.get("clanBasicInfo", {})
    captain = data.get("captainBasicInfo", {})
    pet = data.get("petInfo", {})
    social = data.get("socialInfo", {})
    credit = data.get("creditScoreInfo", {})
    diamond = data.get("diamondCostRes", {})

    def x(v):
        return str(v) if v else "0"

    m1 = (f"[b][c]{get_random_color()} 🎮 PLAYER INFO\n"
          f"[b][c][FFFFFF]Name : {captain.get('nickname', basic.get('nickname', 'Unknown'))}\n"
          f"[b][c][FFFFFF]UID : {x(captain.get('accountId', basic.get('accountId', '0')))}\n"
          f"[b][c][FFFFFF]Likes : {x(captain.get('liked', basic.get('liked', '0')))}\n"
          f"[b][c][FFFFFF]Level : {captain.get('level', basic.get('level', '0'))}\n"
          f"[b][c][FFFFFF]Region : {captain.get('region', basic.get('region', 'Unknown'))}")

    m2 = (f"[b][c]{get_random_color()} 🏰 GUILD INFO\n"
          f"[b][c][FFFFFF]Guild : {clan.get('clanName', 'No Guild')}\n"
          f"[b][c][FFFFFF]Guild ID : {x(clan.get('clanId', '0'))}\n"
          f"[b][c][FFFFFF]Leader : {x(clan.get('captainId', 'Unknown'))}\n"
          f"[b][c][FFFFFF]Members : {clan.get('memberNum', '0')}/{clan.get('capacity', '0')}\n"
          f"[b][c][FFFFFF]Level : {clan.get('clanLevel', '0')}")

    m3 = (f"[b][c]{get_random_color()} ℹ️ EXTRA INFO\n"
          f"[b][c][FFFFFF]Pet : {pet.get('name', 'N/A')} (Lv {pet.get('level', 'N/A')})\n"
          f"[b][c][FFFFFF]Credit : {credit.get('creditScore', 'N/A')}\n"
          f"[b][c][FFFFFF]Diamond : {diamond.get('diamondCost', 'N/A')}\n"
          f"[b][c][FFFFFF]Bio : {social.get('signature', 'N/A')}")

    return m1, m2, m3


def format_check_result(data):
    try:
        return (f"[b][c]{get_random_color()} 🔍 KIỂM TRA BAN\n"
                f"[b][c][FFFFFF]Loại: {data.get('ban_type', 'Không rõ')}\n"
                f"[b][c][FFFFFF]Thời hạn: {data.get('ban_duration', 'Không rõ')}")
    except Exception as e:
        return f"[b][c]Lỗi: {str(e)}"
# ═══════════════════════════════════════════════════════════════
# 4bot_core.py (B) — Status cache + Mimic + /hi + /check
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# /status helpers
# ═══════════════════════════════════════════════════════════════

async def createpacketinfo(uid, key, iv):
    try:
        ida = await EnC_Uid(uid, Tp='Uid')
        if len(ida) == 8:
            packet = f'080112080a04{ida}1005'
        elif len(ida) == 10:
            packet = f"080112090a05{ida}1005"
        else:
            packet = f"080112090A05{ida}1005"
        return await GeneRaTePk(packet, '0f15', key, iv)
    except Exception as e:
        print(f"createpacketinfo error: {e}")
        return None


def get_available_room(hex_packet):
    try:
        return json.dumps(PrOtO(hex_packet))
    except Exception as e:
        print(f"get_available_room error: {e}")
        return None


def get_player_status(packet):
    j = get_available_room(packet)
    if not j:
        return "OFFLINE"
    p = json.loads(j)
    try:
        data = p["5"]["data"]["1"]["data"]
        st   = data["3"]["data"]
        if st == 1:
            return "SOLO"
        if st == 2:
            if "9" in data and "data" in data["9"]:
                gc = data["9"]["data"]
                mx = data["10"]["data"] + 1
                return f"INSQUAD ({gc}/{mx})"
            return "INSQUAD"
        if st in (3, 5):
            return "INGAME"
        if st == 4:
            return "IN ROOM"
        if st in (6, 7):
            return "IN SOCIAL ISLAND MODE"
        return "NOTFOUND"
    except Exception:
        return "OFFLINE"


def get_idroom_by_idplayer(packet):
    try:
        p = json.loads(get_available_room(packet))
        return p["5"]["data"]["1"]["data"]["15"]["data"]
    except Exception:
        return None


def get_leader(packet):
    try:
        p = json.loads(get_available_room(packet))
        return p["5"]["data"]["1"]["data"]["8"]["data"]
    except Exception:
        return None


def save_to_cache(player_id, data):
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
        except Exception:
            cache = {}
    data["saved_at"] = time.time()
    cache[str(player_id)] = data
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


def load_from_cache(player_id):
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
    except Exception:
        return None
    key = str(player_id)
    if key in cache:
        if time.time() - cache[key].get("saved_at", 0) > CACHE_TIMEOUT:
            del cache[key]
            with open(CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
            return None
        return cache[key]
    return None


def clear_cache_entry(player_id):
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
            cache.pop(str(player_id), None)
            with open(CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
        except Exception:
            pass


def debug_file_cache():
    if not os.path.exists(CACHE_FILE):
        print("Cache: file does not exist")
        return
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        print(f"Cache: {len(cache)} entries")
        for k, v in cache.items():
            age = time.time() - v.get("saved_at", 0)
            print(f"  {k}: {v.get('status','?')} (age {age:.1f}s)")
    except Exception as e:
        print(f"Cache debug error: {e}")


# ═══════════════════════════════════════════════════════════════
# /mimic helpers
# ═══════════════════════════════════════════════════════════════

async def extract_emote_info(data_hex, key, iv):
    try:
        packet_json = json.loads(await DeCode_PackEt(data_hex[10:]))
    except Exception:
        return None
    for extractor in (extract_type_21, extract_type_26,
                      extract_type_5, generic_extract):
        info = extractor(packet_json)
        if info and info.get("sender_uid"):
            return info
    return None


def extract_type_21(packet_json):
    if packet_json.get("1") == 21:
        try:
            nested = packet_json["2"]["data"]["5"]["data"]
            sender = nested.get("1", {}).get("data")
            emote  = nested.get("3", {}).get("data")
            if sender and emote:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 21, "confidence": "high"}
        except Exception:
            pass
    return None


def extract_type_26(packet_json):
    if packet_json.get("1") == 26:
        try:
            data   = packet_json["2"]["data"]
            sender = data.get("1", {}).get("data")
            emote  = data.get("2", {}).get("data")
            if sender and emote:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 26, "confidence": "high"}
        except Exception:
            pass
    return None


def extract_type_5(packet_json):
    if packet_json.get("1") == 5:
        try:
            data   = packet_json["2"]["data"]
            sender = data.get("1", {}).get("data")
            emote  = data.get("4", {}).get("data") or 909051015
            if sender:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 5, "confidence": "medium"}
        except Exception:
            pass
    return None


def generic_extract(packet_json):
    uid, emote_id = None, None

    def search(obj):
        nonlocal uid, emote_id
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "data" and isinstance(v, (int, str)) and str(v).isdigit():
                    num = int(v)
                    if 1_000_000 < num < 99_999_999_999 and not uid:
                        uid = num
                    elif str(v).startswith("909") and len(str(v)) >= 9:
                        emote_id = num
                elif isinstance(v, dict):
                    search(v)
                elif isinstance(v, list):
                    for item in v:
                        search(item)

    search(packet_json)
    if uid:
        return {"sender_uid": uid,
                "emote_id":   emote_id or 909051015,
                "packet_type": "generic", "confidence": "medium"}
    return None
# ═══════════════════════════════════════════════════════════════
# 4bot_core.py (C) — /hi + /check
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# /hi — equip HI emote (admin only)
# ═══════════════════════════════════════════════════════════════

async def auto_equip_hi_emote(jwt_token, base_url=None, release_version="OB55", emote_id=909000001):
    """Trang bị biểu cảm nền (mặc định HI 909000001) trực tiếp bằng JWT hiện tại (không đăng nhập lại để tránh làm văng TCP)."""
    if not jwt_token:
        return False, "Thiếu JWT token"
    import xC4 as _xC4
    target_emote = int(emote_id or _xC4.base_emote_id or 909000001)
    url_base = (base_url or server_url or "https://clientbp.ppmainecoonghj.com").rstrip("/")
    raw_proto = (await CrEaTe_ProTo({6: {1: 1, 2: target_emote}})).hex()
    emote_data = bytes.fromhex(await EnC_AEs(raw_proto))
    headers = {
        "Accept-Encoding": "gzip",
        "Connection":      "Keep-Alive",
        "Content-Type":    "application/x-www-form-urlencoded",
        "Expect":          "100-continue",
        "ReleaseVersion":  str(release_version or "OB55"),
        "User-Agent":      "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "X-GA":            "v1 1",
        "X-Unity-Version": "2018.4.11f1",
        "Authorization":   f"Bearer {jwt_token}",
    }
    url = f"{url_base}/ChooseEmote"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, data=emote_data,
                ssl=False, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                status_code = resp.status
                body = await resp.read()
                if status_code == 200:
                    _xC4.base_emote_id = target_emote
                    return True, "OK"
                if b"BR_INVENTORY_NOT_ENOUGH_ITEMS" in body:
                    return False, "NOT_OWNED"
                return False, f"HTTP {status_code}: {body.decode('utf-8', errors='replace')[:120]}"
    except Exception as e:
        return False, str(e)[:120]


async def equip_hi_emote(sender_uid, chat_id, chat_type, key, iv, region_default="VN", custom_arg=None):
    def fmt_num(n):
        return str(n)

    if not is_admin(sender_uid):
        await safe_send_message(
            chat_type,
            f"[B][C][FF0000]❌ Lệnh này chỉ dành cho chủ sở hữu bot (UID {fmt_num(admin_uid)}).",
            sender_uid, chat_id, key, iv
        )
        return

    jwt_token = ToKen
    cur_region = (region or region_default or "VN").upper()
    target_url = (server_url or "https://clientbp.ppmainecoonghj.com").rstrip("/")

    if not jwt_token:
        await safe_send_message(
            chat_type,
            "[B][C][FF0000]❌ Chưa có phiên JWT hợp lệ để trang bị biểu cảm.",
            sender_uid, chat_id, key, iv
        )
        return

    target_emote = 909000001
    if custom_arg:
        arg_l = custom_arg.strip().lower()
        if arg_l.isdigit() and 900000000 <= int(arg_l) <= 999999999:
            target_emote = int(arg_l)
        elif arg_l in NUMBER_EMOTES:
            target_emote = int(NUMBER_EMOTES[arg_l])
        elif arg_l in NAME_EMOTES or arg_l in NAME_TO_EMOTE_ID:
            target_emote = int(NAME_EMOTES.get(arg_l) or NAME_TO_EMOTE_ID[arg_l])
        else:
            await safe_send_message(
                chat_type,
                f"[B][C][FF0000]❌ Không nhận diện được biểu cảm '{custom_arg}'. Gõ /hi hoặc /hi <ID_9_số>",
                sender_uid, chat_id, key, iv
            )
            return

    await safe_send_message(
        chat_type,
        (f"[B][C][FFFF00]📡 Đang gửi gói ChooseEmote (không làm ngắt kết nối TCP)\n"
         f"[FFFFFF]🌐 URL  : [FFFF00]{target_url}/ChooseEmote\n"
         f"[FFFFFF]🎭 Emote: [FFFF00]{fmt_num(target_emote)}"),
        sender_uid, chat_id, key, iv
    )

    ok, detail = await auto_equip_hi_emote(jwt_token, target_url, "OB55", emote_id=target_emote)

    if ok:
        result_msg = (
            f"[B][C][00FF00]✅ ĐÃ TRANG BỊ EMOTE NỀN THÀNH CÔNG!\n"
            f"[FFFFFF]────────────────────────────\n"
            f"[FFFF00]🆔 Bot UID  : [00FF00]{fmt_num(bot_uid or BOT_UID_FOR_HI)}\n"
            f"[FFFF00]🎭 Emote ID : [00FF00]{fmt_num(target_emote)}\n"
            f"[FFFF00]🌍 Khu vực  : [00FF00]{cur_region}\n"
            f"[FFFFFF]────────────────────────────"
        )
    elif detail == "NOT_OWNED":
        result_msg = (
            f"[B][C][FFFF00]⚠️ EMOTE CHƯA CÓ TRONG KHO ĐỒ BOT!\n"
            f"[FFFFFF]────────────────────────────\n"
            f"[FFFF00]🆔 Bot UID : [00FF00]{fmt_num(bot_uid or BOT_UID_FOR_HI)}\n"
            f"[FFFF00]📄 Lý do   : [FF0000]Acc bot chưa sở hữu biểu cảm {fmt_num(target_emote)}.\n"
            f"[FFFFFF]Hãy dùng /hi <ID_emote_bot_đang_có> hoặc nhận 1 hành động miễn phí cho acc bot!\n"
            f"[FFFFFF]────────────────────────────"
        )
    else:
        result_msg = (
            f"[B][C][FF0000]❌ TRANG BỊ THẤT BẠI!\n"
            f"[FFFFFF]────────────────────────────\n"
            f"[FFFF00]📄 Chi tiết:\n[FF0000]{detail}\n"
            f"[FFFFFF]────────────────────────────"
        )

    await safe_send_message(chat_type, result_msg, sender_uid, chat_id, key, iv)


# ═══════════════════════════════════════════════════════════════
# /check — ban status
# ═══════════════════════════════════════════════════════════════

async def check_ban_auto(uid):
    name, region_code = "Không rõ", "Không rõ"
    try:
        ok, data = await get_player_info(uid)
        if ok:
            b = data.get("basicInfo", {}) or {}
            name = b.get("nickname", "Không rõ")
            region_code = b.get("region", "Không rõ")
    except Exception:
        pass

    is_banned, period = 0, 0
    try:
        ok, bd = await check_banned(uid)
        if ok:
            is_banned = bd.get("data", {}).get("is_banned", 0)
            period    = bd.get("data", {}).get("period", 0)
    except Exception:
        pass

    status_text  = "ĐÃ BỊ KHOÁ (BANNED)" if is_banned else "HOẠT ĐỘNG TỐT"
    status_color = "FF0000"               if is_banned else "00FF00"
    if is_banned:
        period_text  = f"{period} ngày" if period else "Vĩnh viễn"
        period_color = "FF4444"
    else:
        period_text, period_color = "Không có", "00FF00"

    return (
        f"[C][B][5DA9FF]━━━━━━━━━━━━━\n"
        f"[C][B][FF6EC7]KIỂM TRA KHOÁ ACC\n"
        f"[C][5DA9FF]━━━━━━━━━━━━━\n"
        f"[C][E6E6FA]Tên     : [9AD0FF]{name}\n"
        f"[C][E6E6FA]UID     : [9AD0FF]{xMsGFixinG(uid)}\n"
        f"[C][E6E6FA]Khu vực : [9AD0FF]{region_code}\n"
        f"[C][E6E6FA]Trạng thái: [{status_color}]{status_text}\n"
        f"[C][E6E6FA]Thời hạn: [{period_color}]{period_text}\n"
        f"[C][B][5DA9FF]━━━━━━━━━━━━━"
    )
# ═══════════════════════════════════════════════════════════════
# 5bot_core.py — LUCKY TCP SUPER BOT (Online TCP Handler)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


def _iter_online_packets(data: bytes):
    chunks = []
    idx = 0
    n = len(data)
    while idx < n:
        rem = n - idx
        if rem >= 5 and data[idx] in (0x05, 0x0f, 0x12) and data[idx + 1] == 0x00:
            plen = int.from_bytes(data[idx + 2:idx + 5], "big")
            if 0 < plen <= rem - 5:
                chunks.append(data[idx:idx + 5 + plen])
                idx += 5 + plen
                continue
        chunks.append(data[idx:])
        break
    return chunks


async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, region
    global pending_ghost_future, ghost_team_id, ghost_squad_code
    global emote_hijack, bot_uid, in_squad, current_squad_uid, current_squad_code, squad_opened_event

    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            token_bytes = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            writer.write(token_bytes)
            await writer.drain()
            print(f"✅ ONLINE connected to {ip}:{port}")

            while True:
                raw_data = await reader.read(9999)
                if not raw_data:
                    print(f"⚠️ ONLINE disconnected from {ip}:{port} — đang kết nối lại...")
                    break

                for data in _iter_online_packets(raw_data):
                    hex_data = data.hex()

                    # ── Status response ──
                    if hex_data.startswith("0f00") and len(hex_data) > 100:
                        try:
                            print("📡 Received status response packet")
                            proto_part = f'08{hex_data.split("08", 1)[1]}'
                            parsed = get_available_room(proto_part)
                            if parsed:
                                pj = json.loads(parsed)
                                if "2" in pj and pj["2"]["data"] == 15:
                                    player_id     = pj["5"]["data"]["1"]["data"]["1"]["data"]
                                    player_status = get_player_status(proto_part)
                                    entry = {
                                        "status":      player_status,
                                        "packet":      proto_part,
                                        "timestamp":   time.time(),
                                        "full_packet": hex_data,
                                        "parsed_json": pj,
                                    }
                                    d1 = pj["5"]["data"]["1"]["data"]
                                    if (d1.get("3", {}).get("data") == 1 and
                                            d1.get("11", {}).get("data") == 1):
                                        entry["special_state"] = "SOLO_WITH_FLAG_1"
                                    if "IN ROOM" in player_status:
                                        rid = get_idroom_by_idplayer(proto_part)
                                        if rid:
                                            entry["room_id"] = rid
                                    elif "INSQUAD" in player_status:
                                        lid = get_leader(proto_part)
                                        if lid:
                                            entry["leader_id"] = lid
                                    save_to_cache(player_id, entry)
                                    print(f"✅ Cached status: {player_id} = {player_status}")
                        except Exception as e:
                            print(f"❌ status parse error: {e}")
                        continue

                    # ── Emote mimic ──
                    if hex_data.startswith('05') and len(hex_data) > 20 and emote_hijack:
                        try:
                            import re
                            payload = hex_data[10:]
                            packet_str = await DeCode_PackEt(payload)
                            if not packet_str or '9090' not in packet_str:
                                try:
                                    decrypted = await DEc_PacKeT(payload, key, iv)
                                    packet_str = await DeCode_PackEt(decrypted)
                                except Exception:
                                    pass

                            if packet_str and '9090' in packet_str:
                                emote_match = re.search(r'"data":\s*(9090\d{5})', packet_str)
                                if emote_match:
                                    emote_id = emote_match.group(1)
                                    all_ids = re.findall(r'"data":\s*(\d{8,12})', packet_str)
                                    sender_uid = None
                                    for u in all_ids:
                                        if str(u) != str(bot_uid) and not str(u).startswith(('9090', '9140')):
                                            active_squad_members.add(str(u))
                                            if sender_uid is None:
                                                sender_uid = u

                                    if emote_id and sender_uid and str(sender_uid) != str(bot_uid):
                                        bot_self_emote = await Emote_k(int(bot_uid), int(emote_id), key, iv, region)
                                        if online_writer:
                                            online_writer.write(bot_self_emote)
                                            await online_writer.drain()
                                        print(f"\n🎯 MIMIC SUCCESS!\n   👤 From: {sender_uid}\n   🎭 Emote: {emote_id}")
                        except Exception as e:
                            print(f"❌ Mimic error: {e}")

                    if not hex_data.startswith("0500"):
                        continue

                    try:
                        packet_json = json.loads(await DeCode_PackEt(hex_data[10:]))
                    except Exception:
                        continue

                    # ── Squad invite ──
                    try:
                        if ('5' in packet_json and 'data' in packet_json['5'] and
                            isinstance(packet_json['5']['data'], dict) and
                            '1' in packet_json['5']['data'] and '8' in packet_json['5']['data']):
                            owner = packet_json['5']['data']['1']['data']
                            code = packet_json['5']['data']['8']['data']
                            if isinstance(code, (str, int)) and str(owner) != str(bot_uid):
                                print(f"📩 Lời mời Squad từ {owner} (code={code})")
                                join_pkt = await SKANHAIYAAccepted(owner, code, key, iv, region)
                                if join_pkt and online_writer:
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
                    except Exception as e:
                        print(f"❌ Squad invite error: {e}")

                    # ── Chat join → welcome + DEVIL banner ──
                    try:
                        f5 = packet_json.get('5', {}).get('data', {})
                        if isinstance(f5, dict):
                            uid_g = f5.get('1', {}).get('data') if isinstance(f5.get('1'), dict) else None
                            chat_code = f5.get('17', {}).get('data') if isinstance(f5.get('17'), dict) else None
                            squad_code = f5.get('31', {}).get('data') if isinstance(f5.get('31'), dict) else None
                        else:
                            uid_g, chat_code, squad_code = None, None, None

                        if uid_g is not None and (chat_code is not None or squad_code is not None or packet_json.get('4', {}).get('data') in (1, 4)):
                            in_squad = True
                            current_squad_uid = uid_g
                            if squad_code is not None:
                                current_squad_code = str(squad_code)
                            if squad_opened_event is not None and not squad_opened_event.is_set():
                                squad_opened_event.set()
                            print(f"✅ Đã vào Squad thành công! (Squad ID: {uid_g}, Mã nhóm: {squad_code})")
                            if chat_code is not None:
                                INV_JOIN = await AutH_Chat(3, uid_g, chat_code, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', INV_JOIN)

                            if str(uid_g) != str(bot_uid):
                                asyncio.create_task(send_welcome(uid_g, key, iv))
                                try:
                                    p1 = await DEVIL1(uid_g, key, iv)
                                    p2 = await DEVIL(uid_g, key, iv)
                                    if p1 and online_writer:
                                        online_writer.write(p1)
                                        await online_writer.drain()
                                        await asyncio.sleep(0.2)
                                    if p2 and online_writer:
                                        online_writer.write(p2)
                                        await online_writer.drain()
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    # ── Ghost capture ──
                    try:
                        if pending_ghost_future and not pending_ghost_future.done():
                            f5 = packet_json.get('5', {}).get('data', {})
                            if '31' in f5:
                                ghost_squad_code = f5['31'].get('data')
                            if '1' in f5:
                                ghost_team_id = f5['1'].get('data')
                            if ghost_team_id and ghost_squad_code:
                                pending_ghost_future.set_result(True)
                    except Exception:
                        pass

                    # ── Kick detection ──
                    try:
                        if packet_json.get('4', {}).get('data') == 8:
                            f5 = packet_json.get('5', {}).get('data', {})
                            if f5.get('2', {}).get('data') == 5:
                                in_squad = False
                                current_squad_uid = None
                                chat_code = f5.get('17', {}).get('data')
                                if chat_code is not None:
                                    WELCOMED.pop(chat_code, None)
                                    LeAvE = await leave_channel_req(chat_code, 3, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', LeAvE)
                                    print("🚪 Bị kick khỏi phòng! Đã rời khỏi kênh chat.")
                    except Exception:
                        pass

            writer.close()
            await writer.wait_closed()
            online_writer = None
            in_squad = False
            current_squad_uid = None
        except Exception as e:
            print(f"Online error: {ip}:{port} - {e}")
            online_writer = None
            in_squad = False
            current_squad_uid = None
        await asyncio.sleep(reconnect_delay)
# ═══════════════════════════════════════════════════════════════
# 6bot_core.py — LUCKY TCP SUPER BOT (Chat TCP Handler - Part A)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


async def _run_ghost_join(teamcode, name, chat_type, sender_uid, chat_id, key, iv):
    global pending_ghost_future
    try:
        pending_ghost_future = asyncio.Future()
        await SEndPacKeT(
            whisper_writer, online_writer, 'OnLine',
            await JoinSq_original(teamcode, key, iv)
        )
        try:
            await asyncio.wait_for(pending_ghost_future, timeout=8.0)
        except asyncio.TimeoutError:
            await safe_send_message(
                chat_type, "[B][C][FF0000]❌ Không có phản hồi từ máy chủ",
                sender_uid, chat_id, key, iv
            )
            pending_ghost_future = None
            return
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
        await asyncio.sleep(0.2)
        for _ in range(4):
            await SEndPacKeT(
                whisper_writer, online_writer, 'OnLine',
                await GhostPakcet(ghost_team_id, name, ghost_squad_code, key, iv)
            )
            await asyncio.sleep(0.1)
        await safe_send_message(
            chat_type, f"[B][C][FFFFFF]✅ Đã vào Squad dưới tên tàng hình {name}",
            sender_uid, chat_id, key, iv
        )
    except Exception as e:
        await safe_send_message(
            chat_type, f"[B][C][FF0000]❌ {e}",
            sender_uid, chat_id, key, iv
        )
    finally:
        pending_ghost_future = None


async def _run_titles(chat_type, sender_uid, chat_id, key, iv):
    titles_list = [
        905090075, 904990072, 904990069, 905190079,
        904090014, 904090015, 904090024, 904090025,
        904090026, 904090027, 904990070, 904990071
    ]
    await safe_send_message(
        chat_type,
        f"[B][C][FFFFFF]🎖️ Đang gửi {len(titles_list)} danh hiệu...",
        sender_uid, chat_id, key, iv
    )
    for tid in titles_list:
        try:
            pkt = await convert_kyro_to_your_system(
                int(sender_uid), chat_id, key, iv,
                nickname="LUCKY TCP", title_id=tid
            )
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', pkt)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Title error: {e}")
    await safe_send_message(
        chat_type, "[B][C][FFFFFF]✅ Đã gửi toàn bộ danh hiệu thành công!",
        sender_uid, chat_id, key, iv
    )


async def _run_bundle(bundle_num, bid, chat_type, sender_uid, chat_id, key, iv, reg):
    try:
        anim_pkt = await animation_packet(bid, key, iv, reg or "VN")
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', anim_pkt)
        await asyncio.sleep(3)
        b_pkt = await Look_Changer(bid, key, iv, look_type=1, region=reg or "VN")
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', b_pkt)
        await safe_send_message(
            chat_type,
            f"[B][C][FFFFFF]✅ Đã gửi trang phục {bundle_num} thành công!",
            sender_uid, chat_id, key, iv
        )
    except Exception as e:
        print(f"Bundle error: {e}")


async def _run_seq_messages(msgs, delay, chat_type, sender_uid, chat_id, key, iv):
    try:
        for m in msgs:
            P = await SEndMsG(chat_type, m, sender_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            await asyncio.sleep(delay)
    except Exception as e:
        print(f"Seq message error: {e}")


async def _run_status_check(target_uid, chat_type, sender_uid, chat_id, key, iv):
    debug_file_cache()
    clear_cache_entry(target_uid)
    await safe_send_message(
        chat_type,
        f"[B][C][FFFF00]🔍 Đang kiểm tra trạng thái {fix_num(target_uid)}...",
        sender_uid, chat_id, key, iv
    )
    try:
        status_packet = await createpacketinfo(target_uid, key, iv)
        if not status_packet:
            await safe_send_message(
                chat_type,
                "[B][C][FF0000]❌ Tạo gói tin trạng thái thất bại!\n",
                sender_uid, chat_id, key, iv
            )
            return
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', status_packet)
        for _ in range(12):
            cache_data = load_from_cache(target_uid)
            if cache_data:
                status_msg = (
                    f"[B][C][FFFF00]📊 TRẠNG THÁI NGƯỜI CHƠI\n"
                    f"────────────────\n"
                    f"👤 UID: {fix_num(target_uid)}\n"
                    f"📊 Trạng thái: {cache_data['status']}\n"
                )
                if "IN ROOM" in cache_data['status'] and 'room_id' in cache_data:
                    status_msg += f"🏠 Mã phòng: {fix_num(cache_data['room_id'])}\n"
                elif "INSQUAD" in cache_data['status'] and 'leader_id' in cache_data:
                    status_msg += f"👑 Đội trưởng: {fix_num(cache_data['leader_id'])}\n"
                elif "OFFLINE" in cache_data['status']:
                    status_msg += "🔴 Người chơi Offline\n"
                elif "INGAME" in cache_data['status']:
                    status_msg += "🎮 Người chơi đang trong trận\n"
                elif "SOLO" in cache_data['status']:
                    status_msg += "👤 Người chơi đang đứng một mình\n"
                status_msg += "────────────────\n✅ Dữ liệu thời gian thực\n"
                await safe_send_message(chat_type, status_msg, sender_uid, chat_id, key, iv)
                return
            await asyncio.sleep(0.5)
        error_msg = (
            f"[B][C][FF0000]❌ KIỂM TRA THẤT BẠI\n"
            f"👤 UID: {fix_num(target_uid)}\n"
            f"📛 Máy chủ không có phản hồi\n"
        )
        await safe_send_message(chat_type, error_msg, sender_uid, chat_id, key, iv)
    except Exception as e:
        await safe_send_message(
            chat_type, f"[B][C][FF0000]❌ Lỗi: {str(e)[:50]}\n",
            sender_uid, chat_id, key, iv
        )


async def _run_ai_query(question, chat_type, sender_uid, chat_id, key, iv):
    await safe_send_message(
        chat_type, "[B][C][FFFFFF]🤖 AI đang suy nghĩ...",
        sender_uid, chat_id, key, iv
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://9x-ai.vercel.app/ask",
                params={"key": "SUMON9X", "message": question},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                if r.status == 200:
                    answer = (await r.text()).strip()
                    msg = f"[B][C][FFFFFF]🤖 Phản hồi AI:\n\n[FFFFFF]{answer}"
                else:
                    msg = f"[B][C][FF0000]❌ Lỗi AI: {r.status}"
    except Exception as e:
        msg = f"[B][C][FF0000]❌ Lỗi: {e}"
    P = await SEndMsG(chat_type, msg, sender_uid, chat_id, key, iv)
    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)


async def TcPChaT(ip, port, AutHToKen, key, iv, ready_event, region,
                  clan_id=None, clan_data=None, reconnect_delay=0.5):
    global whisper_writer, online_writer, spm_tasks, ToKen, bot_uid
    global bot_enabled, emote_hijack, spam_targets
    global evo_cycle_running, evo_cycle_task, ban_task, ban_running, ban_targets
    global random_cycle_running, random_cycle_task
    global fast_spam_running, fast_spam_task
    global custom_spam_running, custom_spam_task
    global msg_spam_running, msg_spam_task, mg_spam_task
    global reject_spam_running, reject_spam_task
    global room_spam_running, room_spam_task
    global freeze_running, freeze_task
    global in_squad, current_squad_uid
    global _clan_message_task, _clan_msg_key, _clan_msg_iv
    global _clan_msg_bot_uid, _clan_msg_clan_id

    print(f"📡 {region} → TCP CHAT connecting...")

    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            print(f"✅ CHAT connected to {ip}:{port}")

            # ── Clan auth ──
            if clan_id and clan_data:
                try:
                    pK = await AuthClan(clan_id, clan_data, key, iv)
                    whisper_writer.write(pK)
                    await whisper_writer.drain()
                    print(f"✅ AuthClan sent for clan {clan_id}")
                except Exception as e:
                    print(f"❌ AuthClan failed: {e}")
            else:
                print(f"⚠️ No clan_id/clan_data — clan chat unavailable")

            # ── Clan auto-message loop ──
            if clan_id and clan_id > 0:
                if _clan_message_task is None or _clan_message_task.done():
                    _clan_msg_key = key
                    _clan_msg_iv = iv
                    _clan_msg_bot_uid = int(bot_uid)
                    _clan_msg_clan_id = int(clan_id)
                    _clan_message_task = asyncio.create_task(clan_message_loop())
                    print(f"[CLAN] Auto-message task started for clan {_clan_msg_clan_id}")

            # ── Restart saved spam loops ──
            for tgt in spam_targets:
                if tgt not in spm_tasks or spm_tasks[tgt].done():
                    spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))

            while True:
                data = await reader.read(9999)
                if not data:
                    break
                if not data.hex().startswith("120000"):
                    continue

                try:
                    response = await DecodeWhisperMessage(data.hex()[10:])
                    uid = response.Data.uid
                    chat_id = response.Data.Chat_ID
                    XX = response.Data.chat_type
                    inPuTMsG = response.Data.msg.lower()
                    msg_raw = response.Data.msg
                    if uid and str(uid) != str(bot_uid):
                        active_squad_members.add(str(uid))
                except Exception:
                    continue

                # ═══════════════════════════════════════════════
                # ⭐ STICKER & TITLE DETECTION ⭐
                # ═══════════════════════════════════════════════
                try:
                    msg_str = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg_str) if msg_str else {}

                    if "5" in chatdata and "data" in chatdata["5"]:
                        inner = chatdata["5"]["data"]

                        if "8" in inner and "data" in inner["8"]:
                            raw_data = inner["8"]["data"]
                            try:
                                data_json = json.loads(raw_data)
                                packet_type = data_json.get("type")

                                # ── Sticker ──
                                if packet_type == "Sticker":
                                    target_uid = inner["1"]["data"]
                                    if str(target_uid) != str(bot_uid) and NUMBER_EMOTES:
                                        random_emote_key = random.choice(list(NUMBER_EMOTES.keys()))
                                        emote_id = NUMBER_EMOTES[random_emote_key]
                                        emote_packet = await Emote_k(int(target_uid), int(emote_id), key, iv, region)
                                        if emote_packet and online_writer:
                                            online_writer.write(emote_packet)
                                            await online_writer.drain()
                                            print(f"🎭 Sticker Reply: Emote {emote_id} sent to {target_uid}")
                                        sticker_reply = "[B][C][FFFF00] LUCKY TCP STYLE TCP"
                                        await safe_send_message(XX, sticker_reply, target_uid, chat_id, key, iv)

                                # ── Title ──
                                elif packet_type == "Title":
                                    sender_uid = inner["1"]["data"]
                                    title_id = data_json.get("TitleID")

                                    if str(sender_uid) != str(bot_uid):
                                        try:
                                            nickname = response.Data.Details.Nickname
                                        except Exception:
                                            nickname = "Player"

                                        if str(sender_uid) == str(admin_uid):
                                            reply_msg = (
                                                f"[B][C][00FF00]Chào mừng chủ nhân {nickname}! "
                                                f"[FFFF00]Danh hiệu của bạn rất tuyệt vời. "
                                                f"[00FFFF]Đang tiến hành sao chép ngay."
                                            )
                                        else:
                                            reply_msg = (
                                                f"[B][C][00FF00]Chào {nickname}, đã thấy danh hiệu chưa? "
                                                f"[FFFF00]Mấy món này bot đều có cả! "
                                                f"[00FFFF]Cùng chiêm ngưỡng nhé... [FFD700]LUCKY TCP ☆"
                                            )

                                        await safe_send_message(XX, reply_msg, sender_uid, chat_id, key, iv)
                                        await asyncio.sleep(0.5)

                                        title_packet = await convert_kyro_to_your_system(
                                            target_uid=sender_uid,
                                            chat_id=chat_id,
                                            key=key,
                                            iv=iv,
                                            nickname="LUCKY TCP",
                                            title_id=title_id
                                        )
                                        if title_packet and whisper_writer:
                                            whisper_writer.write(title_packet)
                                            await whisper_writer.drain()
                                            print(f"✅ Title {title_id} copied from {sender_uid}")

                                        if NUMBER_EMOTES:
                                            random_key = random.choice(list(NUMBER_EMOTES.keys()))
                                            emote_id = NUMBER_EMOTES[random_key]
                                            emote_pkt = await Emote_k(int(sender_uid), int(emote_id), key, iv, region)
                                            if emote_pkt and online_writer:
                                                online_writer.write(emote_pkt)
                                                await online_writer.drain()
                                                print(f"🎭 Title Reply: Emote {emote_id} sent to {sender_uid}")
                            except Exception:
                                pass
                except Exception:
                    pass

                # ── Bot enabled gate ──
                if not bot_enabled and not inPuTMsG.strip().startswith('/on'):
                    if inPuTMsG.strip() != '/on':
                        continue

                # ═══════════════════════════════════════════════
                # /menu
                # ═══════════════════════════════════════════════
                if inPuTMsG.strip().startswith('/menu'):
                    parts = inPuTMsG.strip().split()
                    page = 1
                    if len(parts) >= 2:
                        try:
                            page = int(parts[1])
                        except Exception:
                            page = 1
                    try:
                        menu_text = get_menu_page(page, per_page=5)
                        await safe_send_message(XX, menu_text, uid, chat_id, key, iv)
                        print(f"📋 /menu page {page} sent")
                    except Exception as e:
                        print(f"/menu error: {e}")
                        await safe_send_message(
                            XX, f"[B][C][FF0000]❌ Menu error: {str(e)[:60]}",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /on  /off
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/on':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Chỉ quản trị viên mới có thể dùng /on",
                            uid, chat_id, key, iv
                        )
                    else:
                        bot_enabled = True
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Bot hiện đang BẬT",
                            uid, chat_id, key, iv
                        )

                elif inPuTMsG.strip() == '/off':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Chỉ quản trị viên mới có thể dùng /off",
                            uid, chat_id, key, iv
                        )
                    else:
                        bot_enabled = False
                        await safe_send_message(
                            XX, "[B][C][FF0000]⛔ Bot hiện đang TẮT",
                            uid, chat_id, key, iv
                        )
# ═══════════════════════════════════════════════════════════════
# 7bot_core.py — LUCKY TCP SUPER BOT (Chat Handler - Part B)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


                # ═══════════════════════════════════════════════
                # /help (Fixed Boxes)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() in ("/help", "help", "bot help", "/lucky"):
                    h1_color = get_random_color()
                    h2_color = get_random_color()
                    h3_color = get_random_color()
                    h4_color = get_random_color()

                    h1 = f"""[B][C]{h1_color}╭━━〔 LỆNH QUẢN TRỊ 〕━━╮
[B][FFFFFF]┃ /2 - /6: Tạo & mời Team 2-6
[B][FFFFFF]┃ /join  : Vào Squad
[B][FFFFFF]┃ /exit  : Rời Squad
[B][FFFFFF]┃ /spm   : Spam lời mời
[B][FFFFFF]┃ /stp   : Dừng spam mời
[B][FFFFFF]┃ /s1-s5 : Spam huy hiệu
[B][FFFFFF]┃ /ban   : Spam gói ban
[B][FFFFFF]┃ /room  : Spam phòng
[B][C]{h1_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    h2 = f"""[B][C]{h2_color}╭━━〔 LỆNH TRONG GAME 〕━━╮
[B][FFFFFF]┃ /e <uid> : Gửi Emote
[B][FFFFFF]┃ /e <tên> : Emote theo tên
[B][FFFFFF]┃ /evo     : Emote súng Evo
[B][FFFFFF]┃ /evos    : Vòng lặp Evo
[B][FFFFFF]┃ /sevos   : Dừng vòng Evo
[B][FFFFFF]┃ /rd      : Múa ngẫu nhiên
[B][FFFFFF]┃ /srd     : Dừng múa ngẫu nhiên
[B][FFFFFF]┃ /sticker : Nhãn dán
[B][FFFFFF]┃ /b       : Trang phục
[B][FFFFFF]┃ /animation: Hoạt ảnh
[B][C]{h2_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    h3 = f"""[B][C]{h3_color}╭━━〔 GIẢI TRÍ & TIỆN ÍCH 〕━━╮
[B][FFFFFF]┃ /ai     : Hỏi đáp AI
[B][FFFFFF]┃ /info   : Thông tin UID
[B][FFFFFF]┃ /check  : Kiểm tra khoá
[B][FFFFFF]┃ /status : Trạng thái
[B][FFFFFF]┃ /mth    : Máy tính
[B][FFFFFF]┃ /love   : Thả thính
[B][FFFFFF]┃ /joke   : Truyện cười
[B][FFFFFF]┃ /quiz   : Câu đố vui
[B][C]{h3_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    h4 = f"""[B][C]{h4_color}╭━〔 LUCKY TCP PREMIUM 〕━╮
[B][FFFFFF]┃ TCP BOT » @Redluckyxyz
[B][FFFFFF]┃ GLORY   » @Redluckyxyz
[B][FFFFFF]┃ LEVELUP » @Redluckyxyz
[B][FFFFFF]┃ LIKEBOT » @Redluckyxyz
[B][C]{h4_color}╰━━━━━━━━━━━━━━━━━━━━╯
[B][C]{h4_color}╭━━━━〔 LIÊN HỆ 〕━━━━╮
[B][FFFFFF]┃ Telegram: @Redluckyxyz
[B][C]{h4_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    for m in (h1, h2, h3, h4):
                        try:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            if P:
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(HELP_DELAY)
                        except Exception:
                            pass

                # ═══════════════════════════════════════════════
                # /admin
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == "/admin":
                    msg = f"""[b][c]{get_random_color()} ═══ LUCKY TCP BOT ═══

[b][c][FFFFFF]🎯 Các loại Bot hiện có:
[b][c][FFFFFF]✅ Premium Bots
[b][c][FFFFFF]✅ Glory Bots
[b][c][FFFFFF]✅ Friend Bots
[b][c][FFFFFF]✅ Clan Bots
[b][c][FFFFFF]✅ TCP Online Bots

[b][c][FFFFFF]💎 Dev : [00FFFF]ҒᏟㅤᏞᴜᴄᴋʏㅤ!!
[b][c][FFFFFF]✈️ Telegram: @Redluckyxyz
[b][c][FFFFFF]✈️ Channel: @LuckyOfficialChannel

[b][c]{get_random_color()} Liên hệ đặt mua bot: Telegram: @Redluckyxyz"""
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /s1 - /s5 (badge spam — admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith(('/s1', '/s2', '/s3', '/s4', '/s5')):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        cmd_key = inPuTMsG.strip().split()[0][1:3]
                        asyncio.create_task(
                            handle_badge_command(cmd_key, inPuTMsG, uid, chat_id, key, iv, region or "VN", XX)
                        )

                # ═══════════════════════════════════════════════
                # /2  /3  /4  /5  /6  (Tạo Team 2–6 & mời vào nhóm)
                # ═══════════════════════════════════════════════
                elif (
                    inPuTMsG.strip().split()
                    and inPuTMsG.strip().split()[0] in (
                        "/2", "/3", "/4", "/5", "/6",
                        "/team2", "/team3", "/team4", "/team5", "/team6"
                    )
                ):
                    if not is_admin(uid) and in_squad and str(current_squad_uid) == str(admin_uid):
                        await safe_send_message(
                            XX,
                            "[B][C][FF0000]⚠️ Bot hiện đang đứng trong Tổ đội của Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        _sq_parts = inPuTMsG.strip().split()
                        _sq_size = int(_sq_parts[0][-1])
                        _sq_targets = []
                        _sq_bad_arg = False
                        if len(_sq_parts) == 1:
                            _sq_targets = [int(uid)]
                        else:
                            for _p in _sq_parts[1:]:
                                if _p in ("me", "self"):
                                    if int(uid) not in _sq_targets:
                                        _sq_targets.append(int(uid))
                                elif _p.isdigit() and 6 <= len(_p) <= 13:
                                    if int(_p) not in _sq_targets:
                                        _sq_targets.append(int(_p))
                                else:
                                    _sq_bad_arg = True
                        if _sq_bad_arg or not _sq_targets:
                            await safe_send_message(
                                XX,
                                f"[B][C][FF0000]Cách dùng: /{_sq_size} hoặc /{_sq_size} <uid>",
                                uid, chat_id, key, iv
                            )
                        else:
                            asyncio.create_task(
                                create_and_invite_squad(_sq_size, uid, _sq_targets, XX, chat_id, key, iv)
                            )

                # ═══════════════════════════════════════════════
                # /join (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/join '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        try:
                            code = inPuTMsG.split('/join ')[1].strip()
                            EM = await JoinSq_original(code, key, iv)
                            sent = await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                            if sent:
                                await safe_send_message(
                                    XX,
                                    f"[B][C]{get_random_color()}\n✅ Đã gửi yêu cầu vào Squad: {code}",
                                    uid, chat_id, key, iv
                                )
                            else:
                                await safe_send_message(
                                    XX,
                                    "[B][C][FF0000]❌ Máy chủ Online chưa kết nối, không thể vào Squad!",
                                    uid, chat_id, key, iv
                                )
                        except Exception as e:
                            print(f"Join error: {e}")

                # ═══════════════════════════════════════════════
                # /exit  /leave (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/exit') or inPuTMsG.startswith('/leave'):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        await safe_send_message(
                            XX,
                            f"[B][C]{get_random_color()}\n✅ Đã rời khỏi Squad",
                            uid, chat_id, key, iv
                        )
                        _exit_id = int(bot_uid) if bot_uid else uid
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(_exit_id, key, iv, region))
                        in_squad = False
                        current_squad_uid = None
                        current_squad_code = None
                        active_squad_members.clear()

                # ═══════════════════════════════════════════════
                # /spm <uid> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/spm '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            tgt = parts[1]
                            if tgt in spm_tasks:
                                spm_tasks[tgt].cancel()
                            spam_targets.add(tgt)
                            save_spam_targets()
                            spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]✅ Bắt đầu spam lời mời tới {tgt}",
                                uid, chat_id, key, iv
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /spm <uid>",
                                uid, chat_id, key, iv
                            )

                # ═══════════════════════════════════════════════
                # /stp <uid> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/stp '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1] in spm_tasks:
                            spm_tasks[parts[1]].cancel()
                            del spm_tasks[parts[1]]
                            if parts[1] in spam_targets:
                                spam_targets.remove(parts[1])
                                save_spam_targets()
                            await safe_send_message(
                                XX, "[B][C][FFFFFF]✅ Đã dừng spam",
                                uid, chat_id, key, iv
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]❌ Không có tiến trình spam nào đang chạy",
                                uid, chat_id, key, iv
                            )

                # ═══════════════════════════════════════════════
                # /gh <teamcode> <name> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/gh '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = msg_raw.split(' ', 2)
                        if len(parts) >= 3 and bot_uid is not None:
                            teamcode = parts[1].strip()
                            name = parts[2].strip()
                            asyncio.create_task(
                                _run_ghost_join(teamcode, name, XX, uid, chat_id, key, iv)
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /gh <mã_squad> <tên>",
                                uid, chat_id, key, iv
                            )

                # ═══════════════════════════════════════════════
                # /msg <text> <times> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/msg '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = msg_raw.strip().split()
                        if len(parts) < 3:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /msg <nội dung> <số lần>",
                                uid, chat_id, key, iv
                            )
                        else:
                            try:
                                times = min(int(parts[-1]), 100)
                                message = ' '.join(parts[1:-1])
                                if msg_spam_task and not msg_spam_task.done():
                                    msg_spam_running = False
                                    msg_spam_task.cancel()
                                    await asyncio.sleep(0.1)
                                msg_spam_running = True
                                msg_spam_task = asyncio.create_task(
                                    msg_spam_loop(message, times, chat_id, key, iv, region)
                                )
                                await safe_send_message(
                                    XX,
                                    f"[B][C][FFFFFF]✅ Đang gửi {times} lần: {message}",
                                    uid, chat_id, key, iv
                                )
                            except ValueError:
                                await safe_send_message(
                                    XX, "[B][C][FF0000]Cách dùng: /msg <nội dung> <số lần>",
                                    uid, chat_id, key, iv
                                )

                # ═══════════════════════════════════════════════
                # /stop msg (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/stop msg':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        msg_spam_running = False
                        if msg_spam_task and not msg_spam_task.done():
                            msg_spam_task.cancel()
                        if mg_spam_task and not mg_spam_task.done():
                            mg_spam_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng spam tin nhắn",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /mg <text> [repeats] (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/mg '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = msg_raw.strip().split()
                        if len(parts) < 2:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /mg <nội dung> [số lần]",
                                uid, chat_id, key, iv
                            )
                        else:
                            try:
                                message = parts[1]
                                repeats = int(parts[2]) if len(parts) > 2 else 5
                                if repeats > 10:
                                    repeats = 10
                                if mg_spam_task and not mg_spam_task.done():
                                    msg_spam_running = False
                                    mg_spam_task.cancel()
                                    await asyncio.sleep(0.1)
                                msg_spam_running = True
                                mg_spam_task = asyncio.create_task(
                                    send_wave_messages(message, repeats, chat_id, key, iv, region)
                                )
                                await safe_send_message(
                                    XX,
                                    f"[B][C][FFFFFF]✅ Bắt đầu gửi đợt tin nhắn: {message} x{repeats}",
                                    uid, chat_id, key, iv
                                )
                            except ValueError:
                                await safe_send_message(
                                    XX, "[B][C][FF0000]Cách dùng: /mg <nội dung> [số lần]",
                                    uid, chat_id, key, iv
                                )

                # ═══════════════════════════════════════════════
                # /ban <uid>  /ban_stop (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/ban '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            if ban_task and not ban_task.done():
                                ban_running = False
                                ban_task.cancel()
                                ban_targets.clear()
                                await asyncio.sleep(0.3)
                            ban_targets.add(parts[1])
                            ban_task = asyncio.create_task(ban_loop(key, iv))
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]✅ Bắt đầu gửi gói tin ban tới {parts[1]}",
                                uid, chat_id, key, iv
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /ban <uid>",
                                uid, chat_id, key, iv
                            )

                elif inPuTMsG.strip() == '/ban_stop':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        ban_running = False
                        ban_targets.clear()
                        if ban_task and not ban_task.done():
                            ban_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng gửi gói tin ban",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /reject <uid>  /reject_stop (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/reject '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            if reject_spam_task and not reject_spam_task.done():
                                reject_spam_running = False
                                reject_spam_task.cancel()
                                await asyncio.sleep(0.3)
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]🌀 Bắt đầu spam từ chối tới {parts[1]}",
                                uid, chat_id, key, iv
                            )
                            reject_spam_running = True
                            reject_spam_task = asyncio.create_task(
                                reject_spam_loop(parts[1], key, iv)
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /reject <uid>",
                                uid, chat_id, key, iv
                            )

                elif inPuTMsG.strip() == '/reject_stop':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    elif reject_spam_task and not reject_spam_task.done():
                        reject_spam_running = False
                        reject_spam_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng spam từ chối",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /evos [uids...] / /evos all  /sevos
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evos'):
                    uids = [str(uid)]
                    if bot_uid and str(bot_uid) not in uids:
                        uids.append(str(bot_uid))

                    # Trích xuất UID các thành viên thêm vào (hỗ trợ cách nhau bằng khoảng trắng, dấu +, hoặc dấu phẩy)
                    extra_uids = re.findall(r'\b\d{7,12}\b', inPuTMsG)
                    for eu in extra_uids:
                        if eu not in uids:
                            uids.append(eu)

                    # Hỗ trợ /evos all để tự động lấy toàn bộ thành viên trong phòng
                    if 'all' in inPuTMsG.lower().split():
                        for sm in active_squad_members:
                            if sm not in uids:
                                uids.append(sm)

                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await asyncio.sleep(0.3)
                    evo_cycle_running = True
                    evo_cycle_task = asyncio.create_task(
                        evo_gun_cycle(uids, EVO_IDS, key, iv, region)
                    )

                    if len(uids) <= 2:
                        reply_msg = (
                            f"[B][C][FFFFFF]✅ Bắt đầu chu kỳ Evo cho Bot & Bạn (2 người)\n"
                            f"[FAFAFA]💡 Muốn cả phòng múa: Gõ /evos <id1> <id2>... hoặc /evos all!"
                        )
                    else:
                        reply_msg = f"[B][C][FFFFFF]✅ Bắt đầu chu kỳ Evo cho {len(uids)} người (Bot, Bạn & các thành viên)!"

                    await safe_send_message(XX, reply_msg, uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/sevos':
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng chu kỳ biểu cảm Evo",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /rd [uids...] / /rd all  /srd (Random emote loop)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/rd'):
                    uids = [str(uid)]
                    if bot_uid and str(bot_uid) not in uids:
                        uids.append(str(bot_uid))

                    # Trích xuất UID các thành viên thêm vào (hỗ trợ cách nhau bằng khoảng trắng, dấu +, hoặc dấu phẩy)
                    extra_uids = re.findall(r'\b\d{7,12}\b', inPuTMsG)
                    for eu in extra_uids:
                        if eu not in uids:
                            uids.append(eu)

                    # Hỗ trợ /rd all để tự động lấy toàn bộ thành viên trong phòng
                    if 'all' in inPuTMsG.lower().split():
                        for sm in active_squad_members:
                            if sm not in uids:
                                uids.append(sm)

                    if random_cycle_task and not random_cycle_task.done():
                        random_cycle_running = False
                        random_cycle_task.cancel()
                        await asyncio.sleep(0.3)
                    random_cycle_running = True
                    random_cycle_task = asyncio.create_task(
                        random_emote_cycle(uids, key, iv, region)
                    )

                    if len(uids) <= 2:
                        reply_msg = (
                            f"[B][C][FFFFFF]🎲 Bắt đầu múa ngẫu nhiên cho Bot & Bạn (2 người)!\n"
                            f"[FAFAFA]💡 Muốn cả phòng múa: Gõ /rd <id1> <id2>... hoặc /rd all! (Gõ /srd để dừng)"
                        )
                    else:
                        reply_msg = f"[B][C][FFFFFF]🎲 Bắt đầu múa ngẫu nhiên cho {len(uids)} người! (Gõ /srd để dừng)"

                    await safe_send_message(XX, reply_msg, uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/srd':
                    if random_cycle_task and not random_cycle_task.done():
                        random_cycle_running = False
                        random_cycle_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng chu kỳ múa ngẫu nhiên",
                            uid, chat_id, key, iv
                        )
                    else:
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Không có chu kỳ múa ngẫu nhiên nào đang chạy",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /fast <uid> <emote>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/fast '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        uids = []
                        emote_id = None
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) > 3:
                                    uids.append(p)
                                else:
                                    emote_id = p
                        if uids and emote_id:
                            if fast_spam_task and not fast_spam_task.done():
                                fast_spam_running = False
                                fast_spam_task.cancel()
                            fast_spam_running = True
                            fast_spam_task = asyncio.create_task(
                                fast_emote_spam(uids, emote_id, key, iv, region)
                            )
                            await safe_send_message(
                                XX, "[B][C][FFFFFF]✅ Bắt đầu spam nhanh",
                                uid, chat_id, key, iv
                            )

                # ═══════════════════════════════════════════════
                # /p <uid> <emote> <times>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/p '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 4:
                        try:
                            tgt = parts[1]
                            emote_id = parts[2]
                            times = int(parts[3])
                            if times > 100:
                                times = 100
                            if custom_spam_task and not custom_spam_task.done():
                                custom_spam_running = False
                                custom_spam_task.cancel()
                                await asyncio.sleep(0.2)
                            custom_spam_running = True
                            custom_spam_task = asyncio.create_task(
                                custom_emote_spam(tgt, emote_id, times, key, iv, region)
                            )
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]✅ Bắt đầu spam emote tuỳ chỉnh: {emote_id} x{times}",
                                uid, chat_id, key, iv
                            )
                        except ValueError:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /p <uid> <emote> <số lần>",
                                uid, chat_id, key, iv
                            )
# ═══════════════════════════════════════════════════════════════
# 8bot_core.py — LUCKY TCP SUPER BOT (Chat Handler - Part C1)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


                # ═══════════════════════════════════════════════
                # /e <uid> <name/emote_id> | /e <name/emote_id>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/e '):
                    parts = inPuTMsG.strip().split()
                    try:
                        if len(parts) < 2:
                            await safe_send_message(
                                XX,
                                "[B][C][FF0000]Cách dùng: /e <tên emote> hoặc /e <uid> <tên/id>",
                                uid, chat_id, key, iv
                            )
                            continue
                        
                        last = parts[-1].lower()
                        
                        # Logic mới: Kiểm tra trực tiếp emote ID (ví dụ: 909000063)
                        is_raw_id = last.isdigit() and 900000000 <= int(last) <= 999999999
                        is_num = last.isdigit() and last in NUMBER_EMOTES
                        is_name = last in NAME_EMOTES or last in NAME_TO_EMOTE_ID
                        
                        if not (is_raw_id or is_num or is_name):
                            await safe_send_message(
                                XX,
                                f"[B][C][FF0000]❌ Không tìm thấy emote '{last}'",
                                uid, chat_id, key, iv
                            )
                            continue
                        
                        # Lấy danh sách UID mục tiêu: nếu không ghi rõ UID (chỉ /e <tên>), gửi cho cả người chơi và bot
                        if 'all' in [p.lower() for p in parts]:
                            tgt_uids = [int(uid)]
                            if bot_uid and int(bot_uid) not in tgt_uids:
                                tgt_uids.append(int(bot_uid))
                            for sm in active_squad_members:
                                if int(sm) not in tgt_uids:
                                    tgt_uids.append(int(sm))
                        elif len(parts) == 2:
                            tgt_uids = [int(uid)]
                            if bot_uid and int(bot_uid) not in tgt_uids:
                                tgt_uids.append(int(bot_uid))
                        else:
                            tgt_uids = [int(p) for p in parts[1:-1] if p.isdigit()]
                            if not tgt_uids:
                                tgt_uids = [int(uid)]
                                if bot_uid and int(bot_uid) not in tgt_uids:
                                    tgt_uids.append(int(bot_uid))
                        
                        # Lấy ID emote
                        if is_raw_id:
                            emote_id = int(last)
                        elif is_num:
                            emote_id = NUMBER_EMOTES.get(last)
                        else:
                            emote_id = NAME_EMOTES.get(last) or NAME_TO_EMOTE_ID.get(last)
                            
                        sc = 0
                        for t in tgt_uids:
                            try:
                                H = await Emote_k(t, int(emote_id), key, iv, region)
                                if await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H):
                                    sc += 1
                                await asyncio.sleep(0.1)
                            except Exception:
                                pass
                                
                        if sc > 0:
                            note = ""
                            if not in_squad and XX != 0:
                                note = "\n[FFFF00]⚠️ Bot chưa ở trong nhóm! Hãy mời Bot vào Tổ đội hoặc dùng /join <mã_nhóm> để thấy biểu cảm."
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]✅ Đã gửi emote thành công tới {sc} người{note}",
                                uid, chat_id, key, iv
                            )
                        else:
                            await safe_send_message(
                                XX,
                                "[B][C][FF0000]❌ Máy chủ Online đang mất kết nối, vui lòng thử lại sau vài giây!",
                                uid, chat_id, key, iv
                            )
                    except Exception as e:
                        print(f"E cmd error: {e}")

                # ═══════════════════════════════════════════════
                # /evo <uid> <1-21>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evo ') and not inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    try:
                        num = None
                        uids_l = []
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) <= 2 and num is None:
                                    num = p
                                else:
                                    uids_l.append(p)
                        if not num or not uids_l:
                            await safe_send_message(
                                XX,
                                "[B][C][FF0000]Cách dùng: /evo <uid> <1-21>",
                                uid, chat_id, key, iv
                            )
                            continue
                        num_i = int(num)
                        if num_i not in EMOTE_MAP:
                            await safe_send_message(
                                XX,
                                "[B][C][FF0000]❌ Số thứ tự phải từ 1 đến 21",
                                uid, chat_id, key, iv
                            )
                            continue
                        emote_id = EMOTE_MAP[num_i]
                        for t in uids_l:
                            try:
                                H = await Emote_k(int(t), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.1)
                            except Exception:
                                pass
                        await safe_send_message(
                            XX,
                            f"[B][C][FFFFFF]✅ Đã gửi emote Evo số {num_i}",
                            uid, chat_id, key, iv
                        )
                    except Exception as e:
                        print(f"Evo error: {e}")

                # ═══════════════════════════════════════════════
                # /title  /alltitles
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/title') or inPuTMsG.strip().startswith('/alltitles'):
                    asyncio.create_task(_run_titles(XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /animation
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/animation'):
                    parts = inPuTMsG.strip().split()
                    anim_ids = {
                        "1": 914000002, "2": 914000003, "3": 914038001,
                        "4": 914039001, "5": 914042001, "6": 914044001,
                        "7": 914047001, "8": 914047002, "9": 914048001,
                        "10": 914050001, "11": 914051001, "12": 914053001
                    }
                    if len(parts) < 2:
                        lst = (
                            "1-rampage\n2-cannibal\n3-devil\n4-scorpio\n5-frostfire\n"
                            "6-paradox\n7-naruto\n8-aurora\n9-midnight\n"
                            "10-itachi\n11-dreamspace\n12-eclipse"
                        )
                        await safe_send_message(
                            XX,
                            f"[B][C][FFFFFF]Hiệu ứng hoạt ảnh:\n{lst}",
                            uid, chat_id, key, iv
                        )
                    elif parts[1] in anim_ids:
                        try:
                            pkt = await animation_packet(anim_ids[parts[1]], key, iv, region or "VN")
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', pkt)
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]✅ Đã gửi hiệu ứng {parts[1]} thành công!",
                                uid, chat_id, key, iv
                            )
                        except Exception as e:
                            print(f"Anim error: {e}")
                    else:
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Không tìm thấy hiệu ứng",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /b <1-13> (bundle)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/b '):
                    parts = inPuTMsG.strip().split()
                    bundle_ids = {
                        "1": 914000002, "2": 914000003, "3": 914038001,
                        "4": 914039001, "5": 914042001, "6": 914044001,
                        "7": 914047001, "8": 914047002, "9": 914048001,
                        "10": 914050001, "11": 914051001, "12": 914053001,
                        "13": 914055001
                    }
                    if len(parts) < 2:
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]Cách dùng: /b <1-13>",
                            uid, chat_id, key, iv
                        )
                    elif parts[1] in bundle_ids:
                        asyncio.create_task(
                            _run_bundle(parts[1], bundle_ids[parts[1]], XX, uid, chat_id, key, iv, region)
                        )
                    else:
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Không tìm thấy trang phục",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /sticker
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/sticker'):
                    try:
                        pkt = await send_sticker_packet(uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', pkt)
                    except Exception as e:
                        print(f"Sticker error: {e}")
# ═══════════════════════════════════════════════════════════════
# 8bot_core.py — LUCKY TCP SUPER BOT (Chat Handler - Part C2)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


                # ═══════════════════════════════════════════════
                # /love <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/love '):
                    name = msg_raw.strip()[6:].strip()
                    if name:
                        msgs = [
                            f"[B][C][FF0000]❤️ {name} em là tình yêu của anh! ❤️",
                            f"[B][C][FF0000]💕 Không có {name} anh chẳng còn gì cả! 💕",
                            f"[B][C][FFFFFF]💖 {name} là tất cả của anh! 💖",
                            f"[B][C][FF0000]💗 {name} chính là cả thế giới của anh! 💗",
                            f"[B][C][FF0000]💘 Anh yêu {name} rất nhiều! 💘"
                        ]
                        asyncio.create_task(_run_seq_messages(msgs, 1.5, XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /gali <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/gali '):
                    name = msg_raw.strip()[6:].strip()
                    blocked = ["lucky", "red lucky", "fc lucky"]
                    if name.lower() in blocked:
                        await safe_send_message(
                            XX,
                            "[B][C][FF0000]⚠️ Không thể nhắm vào chủ sở hữu bot!",
                            uid, chat_id, key, iv
                        )
                        continue
                    if name:
                        msgs = [
                            f"[B][C][FF0000]{name} bắn như bot thế! 🤬",
                            f"[B][C][FF0000]{name} gà thế về luyện thêm đi! 🐛",
                            f"[B][C][FF0000]Gặp {name} là auto ăn điểm! 💢",
                            f"[B][C][FF0000]{name} ơi gáy to lên xem nào! 😡",
                            f"[B][C][FF0000]{name} chỉ biết ôm bo thôi à! 💀"
                        ]
                        asyncio.create_task(_run_seq_messages(msgs, 1.5, XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /rt <name> (roast)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/rt '):
                    name = msg_raw.strip()[4:].strip()
                    if name:
                        msgs = [
                            f"[B][C][FF0000]😆 {name} chỉ là một con bot ngây thơ! 🤖",
                            f"[B][C][FF0000]🎮 {name} đứng yên cho đối thủ tập bắn à! 🗿",
                            f"[B][C][FF0000]😂 {name} là trùm gánh team cho phe địch! 🎯"
                        ]
                        asyncio.create_task(_run_seq_messages(msgs, 1.5, XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /praisa <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/praisa '):
                    name = msg_raw.strip()[8:].strip()
                    if name:
                        msgs = [
                            f"[B][C][FFFFFF]🌟 {name} bạn bắn hay và tuyệt vời lắm! 🌟",
                            f"[B][C][FFFFFF]🔥 Kỹ năng của {name} sớm muộn cũng lên đỉnh cao! 🔥",
                            f"[B][C][FFFFFF]💎 {name} luôn là đồng đội xuất sắc nhất! 💎"
                        ]
                        asyncio.create_task(_run_seq_messages(msgs, 0.8, XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /later <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/later '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        msg = (
                            f"[B][C][FF0000]💌 Gửi đến {name} thân mến 💌\n\n"
                            f"Ngày ngày nhớ bóng hình ai,\n"
                            f"Vắng em một phút tháng ngày hoá đông.\n\n"
                            f"💕 Mãi yêu em 💕"
                        )
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Later error: {e}")

                # ═══════════════════════════════════════════════
                # /sadlater <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/sadlater '):
                    try:
                        name = inPuTMsG.strip()[10:].strip()
                        msg = (
                            f"[B][C][FFFFFF]💔 {name} 💔\n\n"
                            f"Lắng nghe tiếng lòng vụn vỡ,\n"
                            f"Đêm về nhớ mãi bóng hình xưa.\n\n"
                            f"💔 Cô đơn 💔"
                        )
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Sad error: {e}")

                # ═══════════════════════════════════════════════
                # /joke
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/joke':
                    jokes = [
                        "Thầy giáo: Sao em không làm bài tập?\nHọc sinh: Thưa thầy hôm qua nhà em mất điện ạ.\nThầy: Thế ban ngày sao không làm?\nHọc sinh: Ban ngày thì em buồn ngủ ạ!\n🤣",
                        "Vợ: Anh thấy em với hoa hậu ai đẹp hơn?\nChồng: Đương nhiên là em rồi, hoa hậu làm sao mà hung dữ bằng em!\n😂"
                    ]
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]😂 TRUYỆN CƯỜI 😂\n\n{random.choice(jokes)}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /dare
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/dare':
                    dares = [
                        '🔥 Nhắm mắt trong 2 phút!',
                        '😂 Cười liên tục trong 1 phút không dừng!',
                        '🐔 Gáy như gà trống trong mic thoại!'
                    ]
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🎲 THỬ THÁCH (DARE) 🎲\n\n{random.choice(dares)}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /truth
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/truth':
                    truths = [
                        '💕 Người bạn yêu quý nhất trong game là ai?',
                        '🤫 Bí mật lớn nhất chưa từng kể với ai là gì?',
                        '💔 Crush hiện tại của bạn là ai?'
                    ]
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🤔 SỰ THẬT (TRUTH) 🤔\n\n{random.choice(truths)}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /wyr (would you rather)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/wyr':
                    a, b = random.choice([
                        ("Khả năng tàng hình", "Khả năng bay lượn"),
                        ("Trở thành Siêu nhân", "Trở thành Người Dơi")
                    ])
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🤔 Bạn sẽ chọn điều gì?\n\nA) {a}\n\nB) {b}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /quiz
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/quiz':
                    q, a = random.choice([
                        ("Thủ đô của Việt Nam là gì?", "Hà Nội"),
                        ("1 kilomet bằng bao nhiêu mét?", "1000")
                    ])
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🧠 CÂU ĐỐ 🧠\n\n❓ {q}\n\n✅ Đáp án: {a}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /roll (dice)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/roll':
                    d1, d2 = random.randint(1, 6), random.randint(1, 6)
                    faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🎲 ĐỔ XÚC XẮC 🎲\n\n🎯 Xúc xắc 1: {faces[d1]} {d1}\n🎯 Xúc xắc 2: {faces[d2]} {d2}\n\n📊 Tổng điểm: {d1 + d2}/12",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /zodiac  /rashi
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() in ('/zodiac', '/rashi'):
                    signs = {
                        "Bạch Dương ♈": ("Đỏ", "9", "Thứ Ba"),
                        "Kim Ngưu ♉": ("Xanh lá", "6", "Thứ Sáu")
                    }
                    s, d = random.choice(list(signs.items()))
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🌟 CUNG HOÀNG ĐẠO 🌟\n\n🔮 Cung: {s}\n🎨 Màu sắc: {d[0]}\n🔢 Con số may mắn: {d[1]}\n📅 Ngày đẹp: {d[2]}\n\n📜 {random.choice(['Hôm nay ngày của bạn sẽ tràn ngập may mắn!', 'Đường tình duyên hôm nay có tin vui bất ngờ!'])}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /weather  /abohawa
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() in ('/weather', '/abohawa'):
                    city = random.choice(["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng"])
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🌤️ THỜI TIẾT 🌤️\n\n📍 Thành phố: {city}\n🌡️ Nhiệt độ: {random.randint(20, 40)}°C\n☁️ Thời tiết: {random.choice(['☀️ Nắng đẹp', '🌤️ Mây nhẹ', '🌧️ Có mưa'])}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /luck <name>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/luck '):
                    name = inPuTMsG.strip()[6:].strip().title()
                    P = await SEndMsG(
                        XX,
                        f"[B][C][FFFFFF]🔮 BÓI VẬN MỆNH 🔮\n\n👤 Tên: {name}\n\n{random.choice([f'🌟 {name} bạn sắp tới sẽ đón nhận thành công lớn!', f'💰 {name} tài lộc sắp đổ dồn vào tay bạn!'])}",
                        uid, chat_id, key, iv
                    )
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
# ═══════════════════════════════════════════════════════════════
# 8bot_core.py — LUCKY TCP SUPER BOT (Chat Handler - Part C3)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


                # ═══════════════════════════════════════════════
                # /info <uid>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/info '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        await safe_send_message(
                            XX,
                            f"[B][C][FFFFFF]🔍 Đang lấy thông tin của {parts[1]}...",
                            uid, chat_id, key, iv
                        )
                        try:
                            ok, data = await get_player_info(parts[1])
                            if ok:
                                m1, m2, m3 = format_player_info(data)
                                for m in (m1, m2, m3):
                                    P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    await asyncio.sleep(0.5)
                            else:
                                await safe_send_message(
                                    XX, f"[B][C][FF0000]❌ {data}",
                                    uid, chat_id, key, iv
                                )
                        except Exception as e:
                            await safe_send_message(
                                XX, f"[B][C][FF0000]❌ Lỗi: {e}",
                                uid, chat_id, key, iv
                            )
                    else:
                        await safe_send_message(
                            XX, "[B][C][FF0000]Cách dùng: /info <uid>",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /check <uid>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/check '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            reply = await check_ban_auto(parts[1])
                        except Exception as e:
                            reply = f"[B][C][FF0000]❌ Lỗi: {e}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        if P:
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else:
                        await safe_send_message(
                            XX, "[B][C][FF0000]Cách dùng: /check <uid>",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /status <uid>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/status'):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 2 or not parts[1].isdigit():
                        await safe_send_message(
                            XX,
                            "[B][C][FF0000]❌ Cách dùng: /status <player_uid>\nVí dụ: /status 123456789",
                            uid, chat_id, key, iv
                        )
                    else:
                        asyncio.create_task(_run_status_check(parts[1], XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /ai <question>
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/ai '):
                    question = msg_raw.strip()[4:].strip()
                    if question:
                        asyncio.create_task(_run_ai_query(question, XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # /mth <expr> (calculator — safe AST evaluation)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/mth'):
                    parts = inPuTMsG.strip().split(maxsplit=1)
                    if len(parts) < 2:
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]Cách dùng: /mth 2+2",
                            uid, chat_id, key, iv
                        )
                    else:
                        expr = parts[1].strip().replace("×", "*").replace("÷", "/").replace("x", "*").replace("^", "**")
                        try:
                            result = _safe_calc(expr)
                            if isinstance(result, float) and result.is_integer():
                                result = int(result)
                            elif isinstance(result, float):
                                result = round(result, 6)
                            P = await SEndMsG(
                                XX,
                                f"[B][C][FFFFFF]🧮 MÁY TÍNH\n\nBiểu thức: {expr}\nKết quả: {result}",
                                uid, chat_id, key, iv
                            )
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        except Exception:
                            await safe_send_message(
                                XX, "[B][C][FF0000]❌ Biểu thức không hợp lệ hoặc quá lớn",
                                uid, chat_id, key, iv
                            )

                # ═══════════════════════════════════════════════
                # /add <uid> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith("/add "):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            try:
                                ok, msg = await send_friend_request(parts[1], ToKen, region)
                                reply = f"[B][C]{get_random_color()} {msg}"
                            except Exception as e:
                                reply = f"[B][C][FF0000]Lỗi: {e}"
                        else:
                            reply = "[B][C][FF0000]Cách dùng: /add <uid>"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /remove <uid> (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith("/remove "):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            try:
                                ok, msg = await remove_friend(parts[1], ToKen, region)
                                reply = f"[B][C]{get_random_color()} {msg}"
                            except Exception as e:
                                reply = f"[B][C][FF0000]Lỗi: {e}"
                        else:
                            reply = "[B][C][FF0000]Cách dùng: /remove <uid>"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # /hi  /mimic_on  /mimic_off (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/hi' or inPuTMsG.strip().startswith('/hi '):
                    _hi_parts = inPuTMsG.strip().split(maxsplit=1)
                    _hi_arg = _hi_parts[1] if len(_hi_parts) > 1 else None
                    asyncio.create_task(equip_hi_emote(uid, chat_id, XX, key, iv, region or "VN", _hi_arg))
                elif inPuTMsG.strip() == '/mimic_on':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        emote_hijack = True
                        await safe_send_message(
                            XX, "[B][C][00FF00]✅ Đã BẬT chế độ nhại biểu cảm (Mimic)",
                            uid, chat_id, key, iv
                        )
                elif inPuTMsG.strip() == '/mimic_off':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        emote_hijack = False
                        await safe_send_message(
                            XX, "[B][C][FF0000]⛔ Đã TẮT chế độ nhại biểu cảm (Mimic)",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /ice <uid|me>  /ice_stop (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/ice '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 2:
                            tgt = parts[1] if parts[1].lower() not in ('me', 'self') else str(uid)
                            if not tgt.isdigit():
                                await safe_send_message(
                                    XX, "[B][C][FF0000]Cách dùng: /ice <uid|me>",
                                    uid, chat_id, key, iv
                                )
                            else:
                                if freeze_task and not freeze_task.done():
                                    freeze_running = False
                                    freeze_task.cancel()
                                    await asyncio.sleep(0.3)
                                freeze_running = True
                                freeze_task = asyncio.create_task(
                                    freeze_emote_spam(tgt, key, iv, region, XX, chat_id, uid)
                                )
                                await safe_send_message(
                                    XX,
                                    f"[B][C][FFFFFF]❄️ Bắt đầu đóng băng (Freeze) {tgt}",
                                    uid, chat_id, key, iv
                                )

                elif inPuTMsG.strip() == '/ice_stop':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        freeze_running = False
                        if freeze_task and not freeze_task.done():
                            freeze_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng đóng băng (Freeze)",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # /room <uid> <room_id>  /room_stop (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/room '):
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        parts = inPuTMsG.strip().split()
                        if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
                            tgt, rid = parts[1], parts[2]
                            if room_spam_task and not room_spam_task.done():
                                room_spam_running = False
                                room_spam_task.cancel()
                                await asyncio.sleep(0.2)
                            room_spam_running = True
                            room_spam_task = asyncio.create_task(
                                Room_Spam(tgt, rid, "LUCKY TCP", key, iv, XX, uid, chat_id)
                            )
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFFFF]🚀 Bắt đầu spam phòng {rid} (mục tiêu {tgt}) — gõ /room_stop để dừng",
                                uid, chat_id, key, iv
                            )
                        else:
                            await safe_send_message(
                                XX, "[B][C][FF0000]Cách dùng: /room <uid> <room_id>",
                                uid, chat_id, key, iv
                            )

                elif inPuTMsG.strip() == '/room_stop':
                    if not is_admin(uid):
                        await safe_send_message(
                            XX, "[B][C][FF0000]❌ Lệnh này chỉ dành cho Quản trị viên!",
                            uid, chat_id, key, iv
                        )
                    else:
                        room_spam_running = False
                        if room_spam_task and not room_spam_task.done():
                            room_spam_task.cancel()
                        await safe_send_message(
                            XX, "[B][C][FFFFFF]✅ Đã dừng spam phòng",
                            uid, chat_id, key, iv
                        )

                # ═══════════════════════════════════════════════
                # Numeric emote — ví dụ "1" hoặc "1*5"
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().isdigit() or (
                    inPuTMsG.strip().count('*') == 1 and
                    all(p.isdigit() for p in inPuTMsG.strip().split('*'))
                ):
                    number_part = inPuTMsG.strip()
                    emote_id = None
                    times = 1
                    if '*' in number_part:
                        parts = number_part.split('*')
                        number = parts[0]
                        times = min(int(parts[1]), 100)
                    else:
                        number = number_part
                    if number in NUMBER_EMOTES:
                        emote_id = NUMBER_EMOTES[number]
                    elif number.isdigit() and 900_000_000 <= int(number) <= 999_999_999:
                        emote_id = int(number)
                    if emote_id:
                        try:
                            await safe_send_message(
                                XX,
                                "[B][C][FAFAFA] Đang gửi emote vui nhộn...",
                                uid, chat_id, key, iv
                            )
                            for _ in range(times):
                                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                if bot_uid and str(bot_uid) != str(uid):
                                    H_bot = await Emote_k(int(bot_uid), int(emote_id), key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H_bot)
                                await asyncio.sleep(0.05)
                            print(f"✅ Number emote: {number} → {emote_id} x{times}")
                        except Exception as e:
                            print(f"Number emote error: {e}")

                # ═══════════════════════════════════════════════
                # Name emote — ví dụ "ak", "groza"
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().lower() in NAME_EMOTES or inPuTMsG.strip().lower() in NAME_TO_EMOTE_ID:
                    try:
                        _ename = inPuTMsG.strip().lower()
                        emote_id = NAME_EMOTES.get(_ename) or NAME_TO_EMOTE_ID[_ename]
                        H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                        if bot_uid and str(bot_uid) != str(uid):
                            H_bot = await Emote_k(int(bot_uid), int(emote_id), key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H_bot)
                        print(f"✅ Name emote: {inPuTMsG.strip()} → {emote_id}")
                    except Exception as e:
                        print(f"Name emote error: {e}")

                else:
                    if inPuTMsG.strip().startswith('/') and len(inPuTMsG.strip()) > 2:
                        pass

            # ── Connection cleanup ──
            writer.close()
            await writer.wait_closed()
            whisper_writer = None
        except Exception as e:
            print(f"Chat error: {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)
# ═══════════════════════════════════════════════════════════════
# 9bot_core.py — LUCKY TCP SUPER BOT (Legacy Squad/Chat Packets)
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# LEGACY SQUAD / GROUP PACKETS & TEAM 2–6 BUILDERS
# ═══════════════════════════════════════════════════════════════

async def OpEnSq(K, V, region, legacy=False):
    reg = (region or "VN").upper()
    lang = "vi" if reg == "VN" else "en"
    if legacy:
        fields = {
            1: 1,
            2: {
                2: "\u0001", 3: 1, 4: 1, 5: lang,
                9: 1, 11: 1, 13: 1,
                14: {2: 5756, 6: 11, 8: "1.132.1", 9: 3, 10: 2}
            }
        }
    else:
        fields = {
            1: 1,
            2: {
                2: "\u0001",
                3: 1,
                4: 1,
                5: lang,
                8: {1: "IDC3", 2: 84, 3: reg},
                9: 1,
                10: "\u0001\u0007\t\n\u000b\u0012\u0019 '",
                11: 1,
                13: 1,
                14: dict(_OB55_SQUAD_SECURITY),
                19: 329,
                21: "7OR\u0019",
                24: {1: 21},
            }
        }
    packet = '0514' if reg == "IND" else ('0519' if reg == "BD" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)


async def cHSq(Nu, Uid, K, V, region):
    reg = (region or "VN").upper()
    fields = {
        1: 17,
        2: {1: int(Uid), 2: 1, 3: max(1, int(Nu) - 1), 4: 62, 5: "\u001a", 8: 5, 13: 329}
    }
    packet = '0514' if reg == "IND" else ('0519' if reg == "BD" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)


async def SEnd_InV(Nu, Uid, K, V, region):
    reg = (region or "VN").upper()
    fields = {1: 2, 2: {1: int(Uid), 2: reg, 4: int(Nu)}}
    packet = '0514' if reg == "IND" else ('0519' if reg == "BD" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)


async def create_and_invite_squad(team_size, caller_uid, target_uids, chat_type, chat_id, key, iv):
    """Tạo Tổ đội kích thước 2–6 người (Team 2/3/4/5/6) và gửi lời mời trực tiếp vào game."""
    global in_squad, current_squad_uid, current_squad_code, squad_opened_event, squad_create_lock

    if online_writer is None or online_writer.is_closing():
        await safe_send_message(
            chat_type,
            "[B][C][FF0000]❌ Máy chủ Online chưa kết nối, không thể tạo Tổ đội!",
            caller_uid, chat_id, key, iv
        )
        return

    if squad_create_lock is None:
        squad_create_lock = asyncio.Lock()

    async with squad_create_lock:
        reg = (region or "VN").upper()
        bot_id_int = int(bot_uid) if bot_uid else int(caller_uid)
        reply_type = chat_type
        reply_chat_id = chat_id

        try:
            # Nếu người dùng gõ lệnh ngay trong khung chat Squad cũ của Bot, báo trước khi Bot rời nhóm cũ
            if (await cHTypE(chat_type)) == 'Squid':
                await safe_send_message(
                    chat_type,
                    f"[B][C][FFFF00]⏳ Đang rời nhóm cũ để tạo Team {team_size} và mời bạn...",
                    caller_uid, chat_id, key, iv
                )
                reply_type = 2
                reply_chat_id = caller_uid

            # 1. Rời Squad hiện tại (nếu có) để tạo nhóm mới sạch
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(bot_id_int, key, iv, reg))
            in_squad = False
            current_squad_uid = None
            current_squad_code = None
            await asyncio.sleep(0.25)

            # 2. Tạo Squad mới chuẩn OB55 (kèm fallback nếu máy chủ dùng cấu trúc rút gọn)
            squad_opened_event = asyncio.Event()
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, reg, legacy=False))
            try:
                await asyncio.wait_for(squad_opened_event.wait(), timeout=0.9)
            except asyncio.TimeoutError:
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, reg, legacy=True))
                try:
                    await asyncio.wait_for(squad_opened_event.wait(), timeout=0.8)
                except asyncio.TimeoutError:
                    pass

            # 3. Đổi kích thước Tổ đội sang 2 / 3 / 4 / 5 / 6 người
            leader_uid = int(current_squad_uid or bot_id_int)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(team_size, leader_uid, key, iv, reg))
            await asyncio.sleep(0.25)

            # 4. Gửi lời mời vào Tổ đội cho từng UID mục tiêu
            invited_ok = 0
            for t_uid in target_uids:
                if await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(1, int(t_uid), key, iv, reg)):
                    invited_ok += 1
                await asyncio.sleep(0.15)

            targets_str = ", ".join(str(x) for x in target_uids)
            code_line = f"\n[FFFF00]🔑 Mã nhóm : [00FFFF]{current_squad_code}" if current_squad_code else ""
            msg = (
                f"[B][C][00FF00]✅ ĐÃ TẠO TEAM {team_size} & GỬI LỜI MỜI!\n"
                f"[FFFFFF]────────────────────────────\n"
                f"[FFFF00]👥 Chế độ  : [00FF00]Team {team_size} ({team_size} người)\n"
                f"[FFFF00]🎯 Đã mời  : [FFFFFF]{targets_str}{code_line}\n"
                f"[FFFFFF]💡 Hãy bấm Chấp nhận lời mời! (Gõ /exit nếu muốn Bot nhường slot)"
            )
            await safe_send_message(reply_type, msg, caller_uid, reply_chat_id, key, iv)
            print(f"✅ Team {team_size} created & invited {targets_str} (code={current_squad_code})")
        except Exception as e:
            print(f"❌ create_and_invite_squad error: {e}")
            await safe_send_message(
                reply_type,
                f"[B][C][FF0000]❌ Lỗi khi tạo Team {team_size}: {str(e)[:80]}",
                caller_uid, reply_chat_id, key, iv
            )


async def GenJoinSquadsPacket(code, K, V):
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
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)


# ═══════════════════════════════════════════════════════════════
# LEGACY xSEndMsg — guild/private chat
# ═══════════════════════════════════════════════════════════════

async def xSEndMsg(Msg, Tp, Tp2, id, K, V):
    feilds = {
        1: id, 2: Tp2, 3: Tp, 4: Msg, 5: 1735129800, 7: 2,
        9: {
            1: "[FFFFFF]LUCKY TCP", 2: int(await xBunnEr()), 3: 901048020, 4: 330,
            5: 1001000001, 8: "LUCKY TCP - C4", 10: 1, 11: 1, 13: {1: 2},
            14: {
                1: 12484827014, 2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            12: 0
        },
        10: "en", 13: {3: 1}
    }
    Pk = (await CrEaTe_ProTo(feilds)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


# ═══════════════════════════════════════════════════════════════
# LEGACY xSEndMsgsQ — squad chat (welcome fix)
# ═══════════════════════════════════════════════════════════════

async def xSEndMsgsQ(Msg, id, K, V, region="VN"):
    avatar = await xBunnEr()

    fields = {
        1: id,
        2: id,
        4: Msg,
        5: 1756580149,
        8: 904990072,
        9: {
            1: "[FFFFFF]LUCKY TCP",
            2: avatar,
            3: 2,
            4: 329,
            5: 1001000001,
            6: 66,
            7: 66,
            8: "LUCKY TCP - C4",
            9: 66,
            10: 66,
            11: 66,
            12: 66,
            13: {1: 68, 2: 67},
            14: {
                1: 1158053040,
                2: 8,
                3: b"\x10\x15\x08\x0A\x0B\x15\x0C\x0F\x11\x04\x07\x02\x03\x0D\x0E\x12\x01\x05\x06"
            }
        },
        10: "en",
        13: {66: 66, 66: 66},
        14: {
            11: {
                1: 3, 2: 7, 3: 170, 4: 999, 5: 1,
                6: region, 7: 2, 8: 2, 9: 2
            }
        }
    }

    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


# ═══════════════════════════════════════════════════════════════
# END OF bot_core.py — LUCKY TCP
# © 2025 LUCKY TCP — All rights reserved
# ═══════════════════════════════════════════════════════════════