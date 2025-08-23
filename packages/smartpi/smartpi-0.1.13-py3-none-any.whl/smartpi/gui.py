import socket
import json
import sys
import threading
import queue
import atexit

# 连接对象（模块级单例）
_connection = None
# 命令队列
_command_queue = queue.Queue(maxsize=1000)
# 后台发送线程
_sender_thread = None
# 线程停止标志
_stop_event = threading.Event()

def init(host="127.0.0.1", port=65167):
    """初始化GUI连接"""
    global _connection, _sender_thread, _stop_event
    if _connection is None:
        try:
            _connection = socket.create_connection((host, port))
            _connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except ConnectionRefusedError:
            print(f"无法连接到GUI服务器 {host}:{port}", file=sys.stderr)
            return
        
        # 启动后台发送线程
        _stop_event.clear()
        _sender_thread = threading.Thread(target=_send_worker, daemon=True)
        _sender_thread.start()
        _send({"type": "clear"})

def _send_worker():
    """后台发送线程的工作函数"""
    while not _stop_event.is_set():
        try:
            # 从队列中获取命令，最多等待0.01秒
            cmd = _command_queue.get(timeout=0.01)
            
            if _connection:
                data = json.dumps(cmd) + "\n"
                _connection.sendall(data.encode())
            
            # 标记任务完成
            _command_queue.task_done()
        except queue.Empty:
            continue
        except (BrokenPipeError, ConnectionResetError):
            # 连接断开，尝试重新连接
            _reconnect()
        except Exception as e:
            print(f"发送错误: {e}", file=sys.stderr)
            time.sleep(0.1)

def _reconnect():
    """尝试重新连接服务器"""
    global _connection
    if _connection:
        try:
            _connection.close()
        except:
            pass
        _connection = None
    
    # 尝试重新连接
    try:
        _connection = socket.create_connection(("127.0.0.1", 65167))
        _connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        _send({"type": "clear"})
    except Exception as e:
        print(f"重新连接失败: {e}", file=sys.stderr)

def _send(cmd):
    """发送命令到服务器（线程安全）"""
    # 如果没有连接，直接返回
    if _connection is None and "pytest" not in sys.modules:
        return
    
    # 将命令放入队列由后台线程发送
    try:
        _command_queue.put(cmd, block=False)
    except queue.Full:
        # 队列满时丢弃最旧的一条命令
        try:
            _command_queue.get_nowait()
        except queue.Empty:
            pass
        _command_queue.put(cmd, block=False)

def show_text(x, y, text, color="black", size=16):
    _send({"type": "text", "x": x, "y": y, "text": text, "color": color, "size": size})

def print(text):
    _send({"type": "print", "text": text})

def println(text):
    _send({"type": "println", "text": text})

def show_image(x, y, path, width, height):
    _send({"type": "image", "x": x, "y": y, "path": path, "width": width, "height": height})

def draw_line(x1, y1, x2, y2, color="black", width=1):
    _send({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "width": width})

def fill_rect(x, y, w, h, color="black"):
    _send({"type": "fill_rect", "x": x, "y": y, "w": w, "h": h, "color": color})
    
def draw_rect(x, y, w, h, width, color="black"):
    _send({"type": "draw_rect", "x": x, "y": y, "w": w, "h": h, "width": width, "color": color})

def fill_circle(cx, cy, r, color="black"):
    _send({"type": "fill_circle", "cx": cx, "cy": cy, "r": r, "color": color})

def draw_circle(cx, cy, r, width, color="black"):
    _send({"type": "draw_circle", "cx": cx, "cy": cy, "r": r, "width": width, "color": color})

def clear():
    _send({"type": "clear"})

def close():
    """关闭GUI连接"""
    global _connection, _sender_thread, _stop_event
    # 设置停止事件
    _stop_event.set()
    if _sender_thread:
        # 等待发送线程退出
        _sender_thread.join(timeout=0.5)
    if _connection:
        try:
            _connection.close()
        except:
            pass
        _connection = None

# 注册程序退出时自动关闭连接
atexit.register(close)