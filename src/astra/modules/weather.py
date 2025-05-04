import csv
import os

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

    def resolve(self, query):
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
