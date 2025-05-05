import csv
import os
from collections import defaultdict

import requests
from rapidfuzz import process, fuzz


class CaiyunWeatherClient:
    """
    彩云天气API通用客户端，支持v2.6和v3版本。
    支持 client = CaiyunWeatherClient()  # 默认v2.6
    支持 client = CaiyunWeatherClient(3) # v3
    """

    BASE_URL = "https://api.caiyunapp.com"

    API_PATHS = {
        "weather": "/{version}/{token}/{lng},{lat}/weather?alert=true&dailysteps=3&hourlysteps=24",
        "realtime": "/{version}/{token}/{lng},{lat}/realtime?alert=true",
        # "air_quality": "/{version}/{token}/{lng},{lat}/air_quality",
        # "historical": "/{version}/{token}/{lng},{lat}/historical",
        # "radar": "/{version}/{token}/{lng},{lat}/radar",
        # 可扩展更多API类型
    }

    def __init__(self, version=None):
        """
        :param version: 可选，API版本。None或未传为v2.6，传3为v3
        """
        self.token = os.getenv("CAIYUN_TOKEN")
        if not self.token:
            raise ValueError("请设置CAIYUN_TOKEN环境变量或传入token参数")
        # 兼容 client = CaiyunWeatherClient(3) 这种写法
        if isinstance(version, int) or (isinstance(version, str) and version == "3"):
            self.version = "v3"
        elif version is None:
            self.version = "v2.6"
        else:
            self.version = str(version)

    def query(self, api_type, location, params=None):
        if api_type not in self.API_PATHS:
            raise ValueError(f"不支持的API类型: {api_type}")
        lng, lat = location
        path = self.API_PATHS[api_type].format(
            version=self.version,
            token=self.token,
            lng=lng,
            lat=lat
        )
        url = self.BASE_URL + path
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class LocationService:
    def __init__(self):
        self.entries = []
        self.name_to_entries = defaultdict(set)  # 用 set 自动去重
        self.all_names = set()
        self._load()

    def _load(self):
        csv_path = os.path.join(os.path.dirname(__file__), "data", "weather_location.csv")
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    code, name, lng, lat = row[:4]
                    if code == "adcode":
                        continue
                    try:
                        lng, lat = float(lng), float(lat)
                    except ValueError:
                        continue
                    levels = name.replace('，', ',').replace(' ', '').split(',')
                    levels = [x for x in levels if x]
                    sub_names = []
                    for i in range(len(levels)):
                        sub_names.append(''.join(levels[i:]))
                    sub_names.append(name)
                    entry = {
                        'code': code,
                        'name': name,
                        'lng': lng,
                        'lat': lat,
                        'levels': levels,
                        'sub_names': sub_names
                    }
                    self.entries.append(entry)
                    for n in sub_names:
                        self.name_to_entries[n].add(id(entry))  # 用id唯一标识
                        self.all_names.add(n)
                    for n in sub_names:
                        short = n.replace('省', '').replace('市', '').replace('区', '').replace('县', '').replace('镇',
                                                                                                                  '').replace(
                            '旗', '')
                        if short != n:
                            self.name_to_entries[short].add(id(entry))
                            self.all_names.add(short)
        # 还原为entry对象
        for k in self.name_to_entries:
            ids = self.name_to_entries[k]
            self.name_to_entries[k] = [e for e in self.entries if id(e) in ids]

    def search_location(self, query, threshold=85):
        query = query.strip().replace(' ', '')
        # 1. 全匹配
        if query in self.name_to_entries:
            entries = self.name_to_entries[query]
            if len(entries) == 1:
                return entries[0], None
            else:
                # 对name去重，随机取一个
                name_map = {}
                for e in entries:
                    if e['name'] not in name_map:
                        name_map[e['name']] = e
                # 如果有多个相同name，只保留一个（随机取一个）
                unique_names = list(name_map.keys())
                return None, unique_names

        # 2. 模糊匹配
        choices = list(self.all_names)
        matches = process.extract(query, choices, scorer=fuzz.partial_ratio, limit=5)
        matches = [m for m in matches if m[1] >= threshold]
        if not matches:
            return None, None
        candidates = []
        for name, score, _ in matches:
            candidates.extend(self.name_to_entries[name])
        unique_candidates = {}
        for c in candidates:
            unique_candidates[c['code']] = c
        candidates = list(unique_candidates.values())
        if len(candidates) == 1:
            return candidates[0], None
        else:
            # 对name去重，随机取一个
            name_map = {}
            for c in candidates:
                if c['name'] not in name_map:
                    name_map[c['name']] = c
            unique_names = list(name_map.keys())
            return None, unique_names
