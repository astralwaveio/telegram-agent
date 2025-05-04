import csv
import os

import httpx
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.astra.constants import WEATHER_INPUT, MAIN_KEYBOARD
from src.astra.modules.errors import CityNotFoundError, CityAmbiguousError

WEATHER_CITYS_PATH = os.path.join(os.path.dirname(__file__), "data", "weather_citys.csv")


class WeatherCityResolver:
    def __init__(self):
        self.city_data = []
        self.name_to_codes = {}
        self._load_csv(WEATHER_CITYS_PATH)

    def _load_csv(self, csv_path):
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                code, full_cn, short_cn, en = row
                levels = full_cn.replace('省', '').replace('市', '').replace('区', '').replace('县', '').replace(
                    '自治县', '').replace('自治州', '').replace('盟', '').replace('旗', '').split('/')
                levels = [x for x in levels if x]
                self.city_data.append({
                    'code': code,
                    'full_cn': full_cn,
                    'short_cn': short_cn,
                    'en': en,
                    'levels': levels
                })
                names = set()
                # 顶级地区
                if len(levels) == 1:
                    names.add(levels[0])
                    for part in short_cn.split('/'):
                        names.add(
                            part.replace('市', '').replace('区', '').replace('县', '').replace('自治县', '').replace(
                                '自治州', '').replace('盟', '').replace('旗', ''))
                    names.add(
                        full_cn.replace('/', '').replace('省', '').replace('市', '').replace('区', '').replace('县',
                                                                                                               '').replace(
                            '自治县', '').replace('自治州', '').replace('盟', '').replace('旗', ''))
                # 其他组合
                for i in range(len(levels)):
                    if i > 0:
                        names.add(''.join(levels[i:]))
                        names.add(''.join(levels[:i + 1]))
                # 拼音支持
                names.add(en.lower())
                names.add(en)  # 保留原始拼音（兼容极端情况）
                # 上级+本级
                if len(levels) >= 2:
                    names.add(levels[-2] + levels[-1])
                # 原始短名
                names.add(short_cn.replace('/', '').replace('省', '').replace('市', '').replace('区', '').replace('县',
                                                                                                                  '').replace(
                    '自治县', '').replace('自治州', '').replace('盟', '').replace('旗', ''))
                # 去重并注册
                for name in names:
                    key = name.strip().lower()
                    if not key:
                        continue
                    self.name_to_codes.setdefault(key, set()).add(code)

    def weather_resolve(self, query):
        """解析地区名，返回唯一编码。支持拼音（不区分大小写）"""
        q = query.strip().replace(' ', '').replace('省', '').replace('市', '').replace('区', '').replace('县',
                                                                                                         '').replace(
            '自治县', '').replace('自治州', '').replace('盟', '').replace('旗', '').lower()
        if not q:
            raise CityNotFoundError()
        # 1. 精确匹配
        codes = self.name_to_codes.get(q)
        if codes:
            if len(codes) == 1:
                return list(codes)[0]
            else:
                raise CityAmbiguousError(codes)
        # 2. 模糊匹配（包含关系）
        fuzzy = []
        for name, codeset in self.name_to_codes.items():
            if q in name:
                for code in codeset:
                    fuzzy.append(code)
        fuzzy = list(set(fuzzy))
        if len(fuzzy) == 1:
            return fuzzy[0]
        elif len(fuzzy) > 1:
            raise CityAmbiguousError(fuzzy)
        else:
            raise CityNotFoundError()


# 处理按钮点击
async def weather_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data.replace("weather_", "")
    # 修改原有按钮消息，提示正在查询
    await query.edit_message_text(f"正在查询 {city} 的天气...")

    # 查询天气
    weather_info = f"{city} 今天天气晴"  # 示例

    # 直接给用户发一条新消息
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=weather_info
    )
    return ConversationHandler.END


# 处理手动输入

async def weather_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_code = update.message.text.strip()
    try:
        city_code = WeatherCityResolver().weather_resolve(city_code)
    except (CityNotFoundError, CityAmbiguousError) as e:
        await update.message.reply_text(f'{e.message}')
        return WEATHER_INPUT
    city_code_prefixes = (
        "WX", "WW", "WQ", "WR", "Y8", "YB", "Y9", "WP", "WZ", "YC", "WT", "WS", "WM", "WK", "WE",
        "W7", "W6", "W9", "WD", "WJ", "WH", "W5", "TV", "TU", "TY", "WN", "TZ", "VB", "TX", "TW", "Y0"
    )
    if not city_code.startswith(city_code_prefixes):
        await update.message.reply_text("暂不支持该城市，请重新输入。")
        return WEATHER_INPUT
    # 构造请求URL
    base_url = "https://api.seniverse.com/v3/weather/"
    async with httpx.AsyncClient() as client:
        private_key = os.getenv("XINZHI_PRI_KEY")
        # 查询实时天气
        now_response = await client.get(
            f"{base_url}now.json",
            params={
                "key": private_key,
                "location": city_code,
                "language": "zh-Hans",
                "unit": "c"
            }
        )
        # 查询未来三天天气
        forecast_response = await client.get(
            f"{base_url}daily.json",
            params={
                "key": private_key,
                "location": city_code,
                "language": "zh-Hans",
                "unit": "c",
                "start": 0,
                "days": 3
            }
        )
    # 检查响应状态码
    if now_response.status_code != 200 or forecast_response.status_code != 200:
        await update.message.reply_text("无法获取天气数据，请稍后再试。")
        return ConversationHandler.END
    now_data = now_response.json()["results"][0]["now"]
    forecast_data = forecast_response.json()["results"][0]["daily"]
    # 构建回复内容
    reply_text = (
        f"🌤️ {update.message.text.strip()} 实时天气：\n"
        f"温度：{now_data['temperature']}°C\n"
        f"天气：{now_data['text_day']}\n"
        f"湿度：{now_data['humidity']}%\n"
        f"风速：{now_data['wind_scale']}级 风力：{now_data['wind_direction']}\n\n"
        f"📅 未来三天天气预报：\n"
        f"1. {forecast_data[0]['date']}：{forecast_data[0]['text_day']} / {forecast_data[0]['text_night']}，"
        f"{forecast_data[0]['low']}°C ~ {forecast_data[0]['high']}°C\n"
        f"2. {forecast_data[1]['date']}：{forecast_data[1]['text_day']} / {forecast_data[1]['text_night']}，"
        f"{forecast_data[1]['low']}°C ~ {forecast_data[1]['high']}°C\n"
        f"3. {forecast_data[2]['date']}：{forecast_data[2]['text_day']} / {forecast_data[2]['text_night']}，"
        f"{forecast_data[2]['low']}°C ~ {forecast_data[2]['high']}°C\n"
    )
    await update.message.reply_text(reply_text, reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END


# 取消命令
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("已取消天气查询。")
    return ConversationHandler.END
