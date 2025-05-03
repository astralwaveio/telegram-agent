# 简单缓存服务
_cache = {}

def set_cache(key, value):
    _cache[key] = value

def get_cache(key, default=None):
    return _cache.get(key, default)
