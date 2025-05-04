import os
import asyncio
import aiohttp

# 预警类型编码映射
ALERT_TYPE_MAP = {
    "01": "台风",
    "02": "暴雨",
    "03": "暴雪",
    "04": "寒潮",
    "05": "大风",
    "06": "沙尘暴",
    "07": "高温",
    "08": "干旱",
    "09": "雷电",
    "10": "冰雹",
    "11": "霜冻",
    "12": "大雾",
    "13": "霾",
    "14": "道路结冰",
    "15": "森林火险",
    "16": "雷雨大风",
    "17": "春季沙尘天气趋势预警",
    "18": "沙尘",
}

# 预警级别编码映射
ALERT_LEVEL_MAP = {
    "00": "白色",
    "01": "蓝色",
    "02": "黄色",
    "03": "橙色",
    "04": "红色",
}


def format_alert(alert):
    """格式化预警内容为中文消息"""
    code = alert.get("code", "")
    alert_type = ALERT_TYPE_MAP.get(code[:2], "未知类型")
    alert_level = ALERT_LEVEL_MAP.get(code[2:], "未知级别")
    title = alert.get("title", "")
    description = alert.get("description", "")
    location = alert.get("location", "")
    pub_time = alert.get("pubtimestamp", 0)
    from datetime import datetime
    pub_time_str = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
    source = alert.get("source", "")
    msg = (
        f"⚠️ <b>{title}</b>\n"
        f"地区：{location}\n"
        f"类型：{alert_type} {alert_level}\n"
        f"发布时间：{pub_time_str}\n"
        f"来源：{source}\n"
        f"详情：{description}"
    )
    return msg


CAIYUN_TOKEN = os.environ.get("CAIYUN_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 杭州市经纬度
HZ_LON, HZ_LAT = 120.1551, 30.2741

# 已推送过的预警ID集合，防止重复推送
pushed_alert_ids = set()


async def fetch_alert():
    """请求彩云天气API获取杭州市预警信息"""
    url = (
        f"https://api.caiyunapp.com/v2.6/{CAIYUN_TOKEN}/"
        f"{HZ_LON},{HZ_LAT}/realtime?alert=true"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data


async def listen_weather(application):
    """每半小时检查一次预警并推送新预警"""
    while True:
        try:
            data = await fetch_alert()
            alert_info = data.get("result", {}).get("alert", {})
            if alert_info.get("status") == "ok":
                for alert in alert_info.get("content", []):
                    # 只推送杭州市相关预警
                    if "杭州市" in alert.get("location", ""):
                        alert_id = alert.get("alertId")
                        if alert_id not in pushed_alert_ids:
                            msg = format_alert(alert)
                            await application.send_message(
                                chat_id=TELEGRAM_CHAT_ID,
                                text=msg,
                                parse_mode="HTML"
                            )
                            pushed_alert_ids.add(alert_id)
        except Exception as e:
            print(f"预警监听异常: {e}")
        await asyncio.sleep(1800)


def run_listen_weather(coro, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro(*args, **kwargs))
    loop.close()
