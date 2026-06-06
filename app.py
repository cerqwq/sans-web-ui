"""
Sans Web UI - 现代化语音助手Web界面
基于 open-webui 设计理念，为Sans语音助手提供Web界面
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
import json
import os
import sys
import threading
import time
from datetime import datetime

# 添加Sans路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sans', 'voice-assistant'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sans-web-ui-secret')
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局状态
class SansState:
    def __init__(self):
        self.messages = []
        self.is_listening = False
        self.is_speaking = False
        self.current_model = "ollama"
        self.tools_count = 0
        self.agents_count = 0

state = SansState()

# 尝试导入Sans核心模块
try:
    from config import config
    from core.assistant import VoiceAssistant
    from core.agent import Agent
    from core.tool_registry import create_default_registry

    assistant = VoiceAssistant()
    agent = Agent()
    registry = create_default_registry()
    state.tools_count = len(registry.get_tool_definitions())
    state.agents_count = len(agent.orchestrator.agents)
    SANS_AVAILABLE = True
except Exception as e:
    print(f"Sans模块加载失败: {e}")
    SANS_AVAILABLE = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天消息"""
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({'error': '消息不能为空'}), 400

    # 记录用户消息
    state.messages.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })

    # 流式响应
    def generate():
        full_response = ""

        if SANS_AVAILABLE:
            try:
                for chunk in agent.run_task(message):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as e:
                error_msg = f"处理出错: {str(e)}"
                yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                full_response = error_msg
        else:
            # Sans未加载时的模拟响应
            response = f"收到: {message} (Sans模块未加载)"
            full_response = response
            yield f"data: {json.dumps({'chunk': response})}\n\n"

        # 记录助手回复
        state.messages.append({
            'role': 'assistant',
            'content': full_response,
            'timestamp': datetime.now().isoformat()
        })

        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'sans_available': SANS_AVAILABLE,
        'current_model': state.current_model if SANS_AVAILABLE else 'N/A',
        'tools_count': state.tools_count,
        'agents_count': state.agents_count,
        'messages_count': len(state.messages),
        'is_listening': state.is_listening,
        'is_speaking': state.is_speaking
    })

@app.route('/api/history')
def get_history():
    """获取聊天历史"""
    return jsonify({'messages': state.messages[-50:]})  # 最近50条

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """清空聊天历史"""
    state.messages.clear()
    if SANS_AVAILABLE:
        assistant.reset()
    return jsonify({'status': 'cleared'})

@app.route('/api/tools')
def get_tools():
    """获取可用工具列表"""
    if SANS_AVAILABLE:
        tools = registry.get_tool_definitions()
        return jsonify({'tools': tools})
    return jsonify({'tools': []})

@app.route('/api/agents')
def get_agents():
    """获取可用Agent列表"""
    if SANS_AVAILABLE:
        agents = agent.orchestrator.list_agents()
        return jsonify({'agents': agents})
    return jsonify({'agents': []})

@app.route('/api/models')
def get_models():
    """获取模型信息"""
    if SANS_AVAILABLE:
        return jsonify({
            'ollama': config.ollama_model,
            'mimo': config.mimo_model,
            'current': assistant.current_model
        })
    return jsonify({'error': 'Sans未加载'})

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """TTS接口"""
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': '文本不能为空'}), 400

    # 异步TTS
    def do_tts():
        if SANS_AVAILABLE:
            try:
                from core.tts import TTSEngine
                tts = TTSEngine(voice=config.tts_voice)
                tts.speak(text)
            except Exception as e:
                print(f"TTS错误: {e}")

    threading.Thread(target=do_tts, daemon=True).start()
    return jsonify({'status': 'speaking', 'text': text})

@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    print(f"客户端已连接")

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开"""
    print(f"客户端已断开")

if __name__ == '__main__':
    print("=" * 50)
    print("  Sans Web UI")
    print("  http://localhost:8080")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
