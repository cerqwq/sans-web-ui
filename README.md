# 🌐 Sans Web UI

Sans语音助手的现代化Web界面，基于open-webui设计理念。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Flask-Web-green?logo=flask" />
  <img src="https://img.shields.io/badge/WebSocket-实时-purple" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

## ✨ 特性

- 🎨 现代化深色主题UI
- 💬 流式对话响应
- 📊 实时系统状态显示
- 🔧 工具和Agent状态查看
- 🗣️ TTS语音合成接口
- 📱 响应式设计

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install flask flask-socketio

# 2. 确保Sans语音助手已配置
# 路径: E:/sans/voice-assistant/

# 3. 启动Web UI
python app.py

# 4. 打开浏览器
# http://localhost:8080
```

## 📁 项目结构

```
sans-web-ui/
├── app.py           # Flask应用
├── templates/
│   └── index.html   # Web界面
└── README.md
```

## 🔌 API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 发送消息（流式响应） |
| `/api/status` | GET | 获取系统状态 |
| `/api/history` | GET | 获取聊天历史 |
| `/api/clear` | POST | 清空聊天历史 |
| `/api/tools` | GET | 获取可用工具 |
| `/api/agents` | GET | 获取可用Agent |
| `/api/models` | GET | 获取模型信息 |
| `/api/speak` | POST | TTS语音合成 |

## 🎨 界面预览

- 深色渐变背景
- 流式打字效果
- 实时状态栏
- 侧边栏系统信息

## 📄 许可证

MIT License
