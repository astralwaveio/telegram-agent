import threading

from src.astra.plugins.weather import run_listen_weather, listen_weather


def start_background_tasks(application):
    """
    启动所有需要后台运行的线程任务。
    后续如有更多任务，直接在这里添加即可。
    """
    # 启动天气预警监听线程
    weather_thread = threading.Thread(
        target=run_listen_weather,
        args=(listen_weather, application.bot),
        daemon=True
    )
    weather_thread.start()

    # 你可以在这里继续添加其他后台线程任务
    # 例如：
    # other_thread = threading.Thread(target=other_func, args=(...), daemon=True)
    # other_thread.start()
