import os
import toml

# 读取默认配置
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default.toml")
config = {}
if os.path.exists(DEFAULT_CONFIG_PATH):
    with open(DEFAULT_CONFIG_PATH, "r") as f:
        config = toml.load(f)

# 支持环境变量覆盖
def get(key, default=None):
    return os.getenv(key, config.get(key, default))
