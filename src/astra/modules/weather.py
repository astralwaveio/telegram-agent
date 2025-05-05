import os

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.astra.constants import MAIN_KEYBOARD, WEATHER_INPUT
from src.astra.services.caiyun_service import CaiyunWeatherClient, LocationService

WEATHER_CITYS_PATH = os.path.join(os.path.dirname(__file__), "data", "weather_citys.csv")

# 读取CSV，构建地名到经纬度的映射
caiyun_client = CaiyunWeatherClient()
location_service = LocationService()


async def weather_input(update, context):
    if update.message.text == "取消查询":
        await weather_cancel(update, context)
        return ConversationHandler.END

    if update.message.location:
        lat = update.message.location.latitude
        lng = update.message.location.longitude
        weather_data = caiyun_client.query("weather", (lng, lat))
        weather_info = assemble_weather_info(weather_data, "当前位置")
        await update.effective_chat.send_message(
            weather_info,
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    city_name = update.message.text.strip()
    result, ambiguous = location_service.search_location(city_name)
    if ambiguous is not None:
        ambiguous = list(set(ambiguous))
    if result:
        lng, lat = result['lng'], result['lat']
        weather_data = caiyun_client.query("weather", (lng, lat))
        weather_info = assemble_weather_info(weather_data, city_name)
        await update.effective_chat.send_message(
            weather_info,
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
            parse_mode="HTML"
        )
        return ConversationHandler.END
    elif ambiguous:
        # 假设 ambiguous 是你的候选地名列表
        keyboard = [[KeyboardButton(name)] for name in ambiguous]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.effective_chat.send_message(
            "地名不唯一，请补充上级地区。可能的选项有：",
            reply_markup=reply_markup
        )
        return WEATHER_INPUT
    else:
        await update.effective_chat.send_message("⚠️ 未找到该地名，请重新输入！")
        return WEATHER_INPUT


async def weather_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("<b>已取消天气查询</b>\n期待下次为你服务！", parse_mode="HTML",
                                             reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True))
    return ConversationHandler.END


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


def get_air_quality_emoji(aqi):
    """AQI数值转emoji+中文等级"""
    if aqi <= 50:
        return "🟢 优"
    elif aqi <= 100:
        return "🟡 良"
    elif aqi <= 150:
        return "🟠 轻度"
    elif aqi <= 200:
        return "🔴 中度"
    else:
        return "🟣 重度"


def format_date(date_str):
    """日期字符串转YYYY-MM-DD"""
    return date_str.split('T')[0]


def assemble_weather_info(weather_data, city_name=""):
    """组装天气信息字符串"""
    result = weather_data['result']
    realtime = result['realtime']
    daily = result['daily']
    life_index = daily['life_index']

    # 实时天气
    skycon_name, skycon_emoji = skycon_desc(realtime['skycon'])
    realtime_temp = realtime['temperature']
    realtime_feel = realtime['apparent_temperature']
    realtime_hum = int(realtime['humidity'] * 100)
    realtime_wind = realtime['wind']['speed']
    realtime_aqi = realtime['air_quality']['aqi']['chn']
    realtime_pm25 = realtime['air_quality']['pm25']
    realtime_aqi_desc = get_air_quality_emoji(realtime_aqi)

    weather_info = (
        f"📍 <b>{city_name}</b>  实时天气：\n"
        f"{skycon_emoji} {skycon_name}  {realtime_temp}°C（体感{realtime_feel}°C）\n"
        f"💧 湿度：{realtime_hum}%  💨 风速：{realtime_wind} km/h\n"
        f"🌫️ 空气质量：{realtime_aqi_desc}（PM2.5: {realtime_pm25}）\n\n"
    )

    # 未来三天
    weather_info += f"📍 <b>{city_name}</b>  近 3 日天气：\n"
    for i in range(3):
        date = format_date(daily['temperature'][i]['date'])
        skycon_code = daily['skycon'][i]['value']
        skycon_name, skycon_emoji = skycon_desc(skycon_code)
        temp_max = daily['temperature'][i]['max']
        temp_min = daily['temperature'][i]['min']
        temp_avg = daily['temperature'][i]['avg']
        hum_avg = int(daily['humidity'][i]['avg'] * 100)
        hum_max = int(daily['humidity'][i]['max'] * 100)
        hum_min = int(daily['humidity'][i]['min'] * 100)
        pm25_avg = daily['air_quality']['pm25'][i]['avg']
        pm25_max = daily['air_quality']['pm25'][i]['max']
        pm25_min = daily['air_quality']['pm25'][i]['min']
        rain_prob = daily['precipitation'][i]['probability']
        wind_avg = daily['wind'][i]['avg']['speed']
        wind_max = daily['wind'][i]['max']['speed']
        wind_min = daily['wind'][i]['min']['speed']
        sunrise = daily['astro'][i]['sunrise']['time']
        sunset = daily['astro'][i]['sunset']['time']
        comfort = life_index['comfort'][i]['desc']
        uv = life_index['ultraviolet'][i]['desc']
        carwash = life_index['carWashing'][i]['desc']
        cold = life_index['coldRisk'][i]['desc']

        weather_info += (
            f"📅 <b>{date}</b>\n"
            f"{skycon_emoji} {skycon_name}\n"
            f"🌧️ 降水概率：{rain_prob}%\n"
            f"🌡️ 最高{temp_max}°C / 最低{temp_min}°C / 平均{temp_avg}°C\n"
            f"💧 湿度：{hum_avg}%（最高{hum_max}% 最低{hum_min}%）\n"
            f"🌫️ PM2.5：{pm25_avg}（最高{pm25_max} 最低{pm25_min}）\n"
            f"💨 风速：{wind_avg} km/h（最大{wind_max} 最小{wind_min}）\n"
            f"🌅 日出：{sunrise}  🌇 日落：{sunset}\n"
            f"😊 舒适度：{comfort}   🧴 紫外线：{uv}\n"
            f"🚗 洗车：{carwash}   🤧 感冒：{cold}\n"
            f"------------------------------\n\n"
        )
    weather_info += (
        f" Copyright © 2025, <b>@Astral Wave</b>.\n"
    )
    return weather_info
