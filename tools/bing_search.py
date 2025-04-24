import requests
import tomli

def load_config(filepath="config.toml"):
    """加载 TOML 配置文件."""
    try:
        with open(filepath, "rb") as f:  # 使用 "rb" 模式以字节形式读取
            config = tomli.load(f)
            return config
    except FileNotFoundError:
        print(f"Error: 配置文件 '{filepath}' 未找到.")
        return None
    except tomli.TOMLDecodeError as e:
        print(f"Error: TOML 解析错误: {e}")
        return None

config = load_config()
BING_API_KEY = config["bing"]["BING_API_KEY"]

def get_bing_search(query):
    headers = {
        'Ocp-Apim-Subscription-Key': BING_API_KEY,
    }
    params = {
        'q': query,
        'count': 5,
        'mkt': 'zh-CN'
    }
    response = requests.get(
        'https://api.bing.microsoft.com/v7.0/search',
        headers=headers,
        params=params
    )
    return response.json()