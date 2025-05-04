import os
import toml

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default.toml")
config = {}
if os.path.exists(DEFAULT_CONFIG_PATH):
    with open(DEFAULT_CONFIG_PATH, "r") as f:
        config = toml.load(f)


def get(key, default=None):
    # 查询 key，不支持 「 . 」，使用 「 _ 」
    env_key = key.replace('.', '_').upper()
    env_val = os.getenv(env_key)
    if env_val is not None:
        return env_val

    # 支持多级key：bot.nick_name
    keys = key.split('.')
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value
