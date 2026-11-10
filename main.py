# ═══════════════════════════════════════════════════════════════
# main.py — LUCKY TCP  |  TCP BOT
# © 2025 LUCKY TCP — Bảo lưu mọi quyền
# ═══════════════════════════════════════════════════════════════

import asyncio
import time
import sys
import os
import signal
import aiohttp
from aiohttp import web
from cfonts import render

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

import login_engine
import bot_core
import xC4

from bot_core import (
    TcPOnLine, TcPChaT,
    build_ob55_online_auth, create_auth_token_chat,
)
import random


# ═══════════════════════════════════════════════════════════════
# ⚠️ THÔNG TIN TÀI KHOẢN GUEST VÀ QUẢN TRỊ VIÊN
# ═══════════════════════════════════════════════════════════════

BOT_UID       = os.getenv("BOT_UID", "8420585840")
BOT_PASSWORD  = os.getenv("BOT_PASSWORD", "telegram@raigenffofc-qozc10")
REGION_PREF   = os.getenv("REGION_PREF", "VN")
ADMIN_UID     = os.getenv("ADMIN_UID", "2996528672")  # Thay UID Free Fire của bạn vào đây nếu muốn
BASE_EMOTE_ID = int(os.getenv("BASE_EMOTE_ID", "909000001"))  # ID hành động nền acc Bot đang sở hữu (mặc định: 909000001 = HI)
START_TIME    = time.time()
BOT_ACC_NAME  = "Đang khởi tạo..."


def _clear_screen():
    if sys.stdout.isatty() and os.getenv("TERM"):
        os.system("clear")


def log(level, message):
    icons = {
        "INFO":  ("\033[1;36m", "ℹ"),
        "OK":    ("\033[1;32m", "✔"),
        "WAIT":  ("\033[1;33m", "⏳"),
        "WARN":  ("\033[1;33m", "⚠"),
        "ERROR": ("\033[1;31m", "✘"),
        "BOT":   ("\033[1;35m", "★"),
    }
    color, icon = icons.get(level, ("\033[1;37m", "•"))
    reset = "\033[0m"
    ts = time.strftime("%H:%M:%S")
    print(f"\033[1;90m[{ts}]{reset} {color}{icon} {level:<5}{reset} │ {message}", flush=True)


def print_banner():
    """Hiển thị banner LUCKY TCP và thông tin bản quyền"""
    _clear_screen()
    print()
    print(render("LUCKY", colors=["red", "white"], align="center"))
    print(render("TCP", colors=["yellow", "white"], align="center"))
    print()
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;33m{'TCP BOT  •  PREMIUM (VIỆT NAM)'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;37m{'EVO  •  TEAM  •  MATCH  •  ONLINE'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;36m{'© LUCKY TCP PREMIUM'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print()


def print_box(title, lines, color="\033[1;35m"):
    width = 58
    reset = "\033[0m"
    print(f"\n{color}┌{'─' * width}┐{reset}")
    print(f"{color}│{reset} {title.center(width - 1)}{color}│{reset}")
    print(f"{color}├{'─' * width}┤{reset}")
    for line in lines:
        print(f"{color}│{reset} {line:<{width - 1}}{color}│{reset}")
    print(f"{color}└{'─' * width}┘{reset}")


def print_line(title, value, icon="➤"):
    print(f"  {icon} \033[1;36m{title:<14}\033[0m : \033[1;33m{value}\033[0m")


async def MaiiiinE():
    Uid = BOT_UID
    Pw  = BOT_PASSWORD

    # Đồng bộ thông tin bot và admin sang bot_core
    bot_core.admin_uid = ADMIN_UID
    bot_core.BLOCK_EMOTE_UID = ADMIN_UID
    bot_core.BOT_UID_FOR_HI = BOT_UID
    bot_core.BOT_PW_FOR_HI = BOT_PASSWORD

    print_banner()
    log("INFO", "Đang bắt đầu quá trình đăng nhập...")
    log("INFO", f"Khu vực máy chủ mục tiêu: {REGION_PREF}")

    try:
        result = await login_engine.do_login(Uid, Pw, REGION_PREF)
    except Exception as e:
        log("ERROR", f"Lỗi trong quá trình đăng nhập: {e}")
        return

    if not result:
        log("ERROR", "Đăng nhập thất bại. Kiểm tra lại thông tin tài khoản hoặc trạng thái khoá từ Garena.")
        await asyncio.sleep(10)
        return

    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen = result["token"]
    bot_core.region = result["region"]
    bot_core.server_url = result.get("server_url", "https://clientbp.ppmainecoonghj.com")
    xC4.bot_uid = result["bot_uid"]
    xC4.ToKen = result["token"]
    xC4.region = result["region"]
    xC4.base_emote_id = BASE_EMOTE_ID

    # Tự động trang bị biểu cảm nền (mặc định HI 909000001) trước khi vào TCP Online
    hi_ok, hi_detail = await bot_core.auto_equip_hi_emote(
        result["token"], bot_core.server_url, emote_id=BASE_EMOTE_ID
    )
    if hi_ok:
        log("OK", f"Đã tự động trang bị biểu cảm nền ({BASE_EMOTE_ID}) cho Bot.")
    elif hi_detail == "NOT_OWNED":
        log("WARN", f"Acc Bot CHƯA SỞ HỮU biểu cảm nền ({BASE_EMOTE_ID}) trong kho đồ — lệnh /e sẽ không hiện nếu acc Bot chưa có ít nhất 1 hành động!")
    else:
        log("WARN", f"Không thể tự động trang bị biểu cảm nền: {hi_detail}")

    # Tự động gửi lời mời kết bạn tới Admin khi khởi động
    if ADMIN_UID:
        asyncio.create_task(bot_core.send_friend_request(ADMIN_UID, result["token"], result["region"]))

    key         = result["key"]
    iv          = result["iv"]
    timestamp   = result["timestamp"]
    online_ip   = result["online_ip"]
    online_port = result["online_port"]
    chat_ip     = result["chat_ip"]
    chat_port   = result["chat_port"]
    acc_name    = result["account_name"]
    global BOT_ACC_NAME
    BOT_ACC_NAME = acc_name
    clan_id     = result.get("clan_id")
    clan_data   = result.get("clan_data")

    _clear_screen()

    RESET  = "\033[0m"
    CYAN   = "\033[1;36m"
    GREEN  = "\033[1;32m"
    PURPLE = "\033[1;35m"

    print()
    print(render("LUCKY", colors=["red", "white"], align="center"))
    print(render("TCP", colors=["yellow", "white"], align="center"))
    print()
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print(f"\033[1;33m{'BOT ONLINE'.center(60)}\033[0m")
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print()

    print_box("THÔNG TIN TÀI KHOẢN BOT", [
        f"UID          : {result['bot_uid']}",
        f"TÊN          : {acc_name}",
        f"KHU VỰC      : {result['region']}",
        f"QUÂN ĐOÀN ID : {clan_id or 'Không có'}",
        f"CHAT SERVER  : {chat_ip}:{chat_port}",
        f"GAME SERVER  : {online_ip}:{online_port}",
    ], GREEN)

    print_box("TRẠNG THÁI BOT", [
        "ĐĂNG NHẬP THÀNH CÔNG",
        "XÁC THỰC SẴN SÀNG",
        "ĐANG KHỞI TẠO KẾT NỐI TCP",
    ], PURPLE)

    log("INFO", "Đang tạo Auth Token...")

    ChatAutH = create_auth_token_chat(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )
    OnlineAutH, _ = build_ob55_online_auth(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )

    log("OK", "Auth Token đã sẵn sàng.")
    log("WAIT", "Đang kết nối tới Chat Server TCP...")

    ready_event = asyncio.Event()
    t1 = asyncio.create_task(
        TcPChaT(
            chat_ip, chat_port, ChatAutH, key, iv,
            ready_event, result["region"],
            clan_id=clan_id,
            clan_data=clan_data,
        )
    )

    await ready_event.wait()
    log("OK", "Kết nối Chat Server thành công!")
    await asyncio.sleep(1)

    log("WAIT", "Đang kết nối tới Online Server TCP...")
    t2 = asyncio.create_task(
        TcPOnLine(online_ip, online_port, key, iv, OnlineAutH)
    )

    print()
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print(render("LUCKY", colors=["red", "white"], align="center"))
    print(render("TCP", colors=["yellow", "white"], align="center"))
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print_line("Chủ sở hữu",   "RED LUCKY XYZ")
    print_line("Khu vực",      result['region'])
    print_line("Bot UID",      result['bot_uid'])
    print_line("Tên Bot",      acc_name)
    print_line("Quân đoàn",    str(clan_id) if clan_id else "Không có")
    print_line("Trạng thái",   "\033[1;32m● ĐANG CHẠY (RUNNING)\033[0m")
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print()

    done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    try:
        if bot_core.online_writer:
            bot_core.online_writer.close()
        if bot_core.whisper_writer:
            bot_core.whisper_writer.close()
    except Exception:
        pass


async def _handle_status(request):
    online_ok = bool(bot_core.online_writer and not bot_core.online_writer.is_closing())
    chat_ok = bool(bot_core.whisper_writer and not bot_core.whisper_writer.is_closing())
    return web.json_response({
        "status": "running",
        "bot_uid": str(bot_core.bot_uid or BOT_UID),
        "account_name": BOT_ACC_NAME,
        "region": str(bot_core.region or REGION_PREF),
        "online_connected": online_ok,
        "chat_connected": chat_ok,
        "in_squad": bool(bot_core.in_squad),
        "squad_code": bot_core.current_squad_code,
        "uptime_seconds": int(time.time() - START_TIME),
    })


async def _handle_health(request):
    return web.Response(text="OK", status=200)


async def start_render_web_server():
    """Mở cổng HTTP (PORT) cho Render Free Web Service và UptimeRobot."""
    port = int(os.getenv("PORT", "10000"))
    app = web.Application()
    app.router.add_get("/", _handle_status)
    app.router.add_get("/health", _handle_health)
    app.router.add_get("/ping", _handle_health)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    try:
        site = web.TCPSite(runner, host="0.0.0.0", port=port, reuse_address=True)
        await site.start()
        log("OK", f"Đã mở cổng Web Keep-Alive tại 0.0.0.0:{port} (sẵn sàng cho Render / UptimeRobot)")
        return runner
    except Exception as e:
        log("WARN", f"Không thể mở cổng HTTP {port} ({e}) — tiếp tục chạy chế độ TCP thuần.")
        return None


async def _self_keepalive_loop():
    """Tự động ping RENDER_EXTERNAL_URL (nếu có) mỗi 10 phút để giữ kết nối."""
    ext_url = (os.getenv("RENDER_EXTERNAL_URL") or os.getenv("KEEPALIVE_URL") or "").rstrip("/")
    if not ext_url:
        return
    ping_url = f"{ext_url}/health"
    log("INFO", f"Đã bật tự động ping giữ thức: {ping_url}")
    while True:
        await asyncio.sleep(600)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(ping_url, timeout=aiohttp.ClientTimeout(total=10)) as _:
                    pass
        except Exception:
            pass


def _handle_sigterm(signum, frame):
    log("WARN", f"Nhận tín hiệu dừng ({signum}) từ hệ thống — đóng kết nối cũ ngay lập tức...")
    try:
        if bot_core.online_writer:
            bot_core.online_writer.close()
        if bot_core.whisper_writer:
            bot_core.whisper_writer.close()
    except Exception:
        pass
    os._exit(0)


async def StarTinG():
    try:
        signal.signal(signal.SIGTERM, _handle_sigterm)
    except Exception:
        pass
    await start_render_web_server()
    asyncio.create_task(_self_keepalive_loop())
    if os.getenv("RENDER"):
        log("WAIT", "Đợi 10 giây để Render đóng hẳn phiên container cũ trước khi đăng nhập...")
        await asyncio.sleep(10)

    attempt = 0
    while True:
        attempt += 1
        try:
            log("BOT", f"Bắt đầu phiên kết nối #{attempt}")
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            log("WARN", "Hết phiên kết nối. Đang khởi động lại sau 3 giây...")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            log("WARN", "Bot đã dừng bởi người dùng.")
            sys.exit(0)
        except Exception as e:
            log("ERROR", f"Lỗi xảy ra trong phiên: {e}")
            await asyncio.sleep(5)


if __name__ == '__main__':
    try:
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        print("\nBot đã dừng hoạt động.")
