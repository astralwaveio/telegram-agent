# 凌云曦 (Astra)

Astra（凌云曦）是一个基于 Telegram Bot 的多 AI 智能体，支持 ChatGPT、Claude、DeepSeek、阿里QWen 等主流大模型，支持灵活扩展和多模型配置。

- 项目主页: https://astra.eoysky.com
- API 域名: https://astra-api.eoysky.com

## 快速开始

- 安装依赖
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- 配置 .env 文件

- 启动

```bash
python -m src.astra
```

## 目录结构

```
src/
  astra/
    main.py
    ...
```

## Docker 支持

见 Dockerfile 和 docker-compose.yml

## License

MIT
