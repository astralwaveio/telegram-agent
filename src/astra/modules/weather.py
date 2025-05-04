import os

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.astra.constants import WEATHER_INPUT, WEATHER_RESULT

WEATHER_CITYS_PATH = os.path.join(os.path.dirname(__file__), "data", "weather_citys.csv")


async def weather_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "weather_cancel":
        await query.edit_message_text("期待下次为你服务！😊", parse_mode="HTML")
        return ConversationHandler.END

    city_map = {
        "weather_hangzhou": ("杭州", 120.1551, 30.2741),
        "weather_shanghai": ("上海", 121.4737, 31.2304),
        "weather_beijing": ("北京", 116.4074, 39.9042),
        "weather_luohe": ("漯河", 114.0168, 33.5815),
    }
    key = query.data
    if key in city_map:
        city, lon, lat = city_map[key]
        weather_info = get_weather_detail(lon, lat)
        await send_weather_result(update, context, city, weather_info)
        return WEATHER_RESULT
    else:
        await query.edit_message_text("⚠️ 未识别的城市按钮。", parse_mode="HTML")
    return ConversationHandler.END


async def weather_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    city_map = {
        "杭州": (120.1551, 30.2741),
        "上海": (121.4737, 31.2304),
        "北京": (116.4074, 39.9042),
        "漯河": (114.0168, 33.5815),
    }
    if city in city_map:
        lon, lat = city_map[city]
        weather_info = get_weather_detail(lon, lat)
        await send_weather_result(update, context, city, weather_info)
        return WEATHER_RESULT
    else:
        await update.effective_chat.send_message(
            "⚠️ <b>暂不支持该城市</b>\n\n"
            "目前仅支持：<b>杭州</b>、<b>上海</b>、<b>北京</b>、<b>漯河</b>\n"
            "请重新输入城市名，或点击下方按钮。",
            parse_mode="HTML"
        )
        return WEATHER_INPUT


async def send_weather_result(update, context, city, weather_info):
    """发送天气结果并附带退出按钮"""
    keyboard = [
        [InlineKeyboardButton("🔚 退出", callback_data="weather_exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(
        f"📍 <b>{city}</b>天气：\n\n{weather_info}",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def weather_exit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理退出按钮，发送退出提示，不删除原消息"""
    query = update.callback_query
    await query.answer()
    await update.effective_chat.send_message("🔚 已退出当前操作。", parse_mode="HTML")
    return ConversationHandler.END


async def weather_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("<b>已取消天气查询</b>\n期待下次为你服务！", parse_mode="HTML")
    return ConversationHandler.END


def get_weather_detail(lon, lat):
    """获取详细天气信息（7天预报+生活指数+实时）"""
    caiyun_token = os.environ.get("CAIYUN_TOKEN")
    # 实时天气
    realtime_url = f"https://api.caiyunapp.com/v2.6/{caiyun_token}/{lon},{lat}/realtime"
    # 7天预报+生活指数
    daily_url = f"https://api.caiyunapp.com/v2.6/{caiyun_token}/{lon},{lat}/daily?dailysteps=7"
    try:
        realtime = requests.get(realtime_url, timeout=5).json()
        daily = requests.get(daily_url, timeout=5).json()
        # 解析实时天气
        rt = realtime.get("result", {}).get("realtime", {})
        temp = rt.get("temperature")
        skycon = rt.get("skycon")
        desc, emoji = skycon_desc(skycon)
        humidity = rt.get("humidity", None)
        humidity_str = f"{int(humidity * 100)}%" if humidity is not None else "未知"
        wind_speed = rt.get("wind", {}).get("speed", None)
        wind_str = f"{wind_speed} m/s" if wind_speed is not None else "未知"
        aqi = rt.get("air_quality", {}).get("aqi", {}).get("chn", None)
        aqi_str = f"{aqi}" if aqi is not None else "未知"

        # 解析生活指数（当天）
        life_index = daily.get("result", {}).get("daily", {}).get("life_index", {})
        dressing = life_index.get("dressing", [{}])[0]
        dressing_desc = dressing.get("desc", "暂无建议")
        uv = life_index.get("ultraviolet", [{}])[0]
        uv_desc = uv.get("desc", "暂无建议")
        cold = life_index.get("coldRisk", [{}])[0]
        cold_desc = cold.get("desc", "暂无建议")
        car_washing = life_index.get("carWashing", [{}])[0]
        car_washing_desc = car_washing.get("desc", "暂无建议")

        # 解析7天预报
        daily_data = daily.get("result", {}).get("daily", {})
        dates = daily_data.get("date", [])
        skycons = daily_data.get("skycon", [])
        temp_max = daily_data.get("temperature", [])
        msg_7d = ""
        for i in range(min(7, len(dates))):
            day = dates[i]
            sky = skycon_desc(skycons[i]['value'])[0] if i < len(skycons) else "未知"
            tmax = temp_max[i]['max'] if i < len(temp_max) else "?"
            tmin = temp_max[i]['min'] if i < len(temp_max) else "?"
            msg_7d += f"{day[5:]} {sky} {tmin}~{tmax}℃\n"

        # 组装消息
        msg = (
            f"{emoji} <b>当前天气</b>\n"
            f"🌡️ 温度：<b>{temp}℃</b>\n"
            f"🌥️ 天气：<b>{desc}</b>\n"
            f"💧 湿度：<b>{humidity_str}</b>\n"
            f"💨 风速：<b>{wind_str}</b>\n"
            f"🌫️ 空气质量指数：<b>{aqi_str}</b>\n"
            f"\n👕 <b>穿衣指数</b>：{dressing_desc}\n"
            f"🌞 <b>紫外线</b>：{uv_desc}\n"
            f"🤧 <b>感冒风险</b>：{cold_desc}\n"
            f"🚗 <b>洗车指数</b>：{car_washing_desc}\n"
            f"\n📅 <b>未来7天天气</b>：\n"
            f"<pre>{msg_7d}</pre>\n数据来源：彩云天气"
        )
        return msg
    except Exception as e:
        return f"⚠️ <b>获取天气失败</b>\n请稍后再试。\n\n<code>{e}</code>"


def skycon_desc(skycon):
    """天气现象代码转中文+emoji"""
    mapping = {
        "CLEAR_DAY": ("晴天", "☀️"),
        "CLEAR_NIGHT": ("晴夜", "🌙"),
        "PARTLY_CLOUDY_DAY": ("多云", "⛅"),
        "PARTLY_CLOUDY_NIGHT": ("多云夜", "🌤️"),
        "CLOUDY": ("阴", "☁️"),
        "LIGHT_HAZE": ("轻度雾霾", "🌫️"),
        "MODERATE_HAZE": ("中度雾霾", "🌫️"),
        "HEAVY_HAZE": ("重度雾霾", "🌫️"),
        "LIGHT_RAIN": ("小雨", "🌦️"),
        "MODERATE_RAIN": ("中雨", "🌧️"),
        "HEAVY_RAIN": ("大雨", "🌧️"),
        "STORM_RAIN": ("暴雨", "⛈️"),
        "FOG": ("雾", "🌁"),
        "LIGHT_SNOW": ("小雪", "🌨️"),
        "MODERATE_SNOW": ("中雪", "❄️"),
        "HEAVY_SNOW": ("大雪", "❄️"),
        "STORM_SNOW": ("暴雪", "🌨️"),
        "DUST": ("浮尘", "🌪️"),
        "SAND": ("沙尘", "🌪️"),
        "WIND": ("大风", "💨"),
    }
    # 如果找不到，返回原始代码和问号
    return mapping.get(skycon, (skycon, "❓"))
