import asyncio
import functools
import hashlib
import hmac
import inspect
import json
import logging
import mimetypes
import os
import re
import sqlite3
import threading
import time
import traceback
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from urllib.parse import parse_qs, unquote, urlparse
import smtplib
import socketserver
import weakref
import redis
import aiohttp
from aiohttp import web
import jwt
import base64
from dataclasses import dataclass

__version__ = "2.0.0"
__author__ = "iliya"


# ============================================================================
# Configuration System
# ============================================================================

class Config:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self):
        self._config = {
            'DEBUG': False,
            'SECRET_KEY': os.urandom(32).hex(),
            'DATABASE': 'app.db',
            'TEMPLATE_DIR': 'templates',
            'STATIC_DIR': 'static',
            'REDIS_URL': 'redis://localhost:6379/0',
            'SMTP_SERVER': None,
            'SMTP_PORT': 587,
            'SMTP_USERNAME': None,
            'SMTP_PASSWORD': None,
        }
    
    def load_from_file(self, config_file: str):
        """بارگذاری تنظیمات از فایل JSON"""
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                self._config.update(config_data)
    
    def load_from_env(self):
        """بارگذاری تنظیمات از متغیرهای محیطی"""
        for key in self._config:
            env_value = os.getenv(f"KHAFAN_{key}")
            if env_value:
                self._config[key] = env_value
    
    def __getitem__(self, key):
        return self._config.get(key)
    
    def __setitem__(self, key, value):
        self._config[key] = value


# ============================================================================
# Advanced Logging
# ============================================================================

class KhafanLogger:
    """سیستم لاگینگ پیشرفته"""
    
    def __init__(self, log_file: str = "khafan.log"):
        self.logger = logging.getLogger('KhafanFlask')
        self.logger.setLevel(logging.DEBUG)
        
        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)


# ============================================================================
# Improved Template Engine
# ============================================================================

class SimpleJin:
    """موتور تمپلیت پیشرفته با پشتیبانی از وراثت و فیلترها"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.cache = {}
        self.filters = {
            'upper': str.upper,
            'lower': str.lower,
            'trim': str.strip,
            'capitalize': str.capitalize,
            'length': len,
        }
    
    def add_filter(self, name: str, func: Callable):
        """اضافه کردن فیلتر جدید"""
        self.filters[name] = func
    
    def render(self, template_name: str, **context) -> str:
        """رندر کردن تمپلیت با کانتکست"""
        template_path = self.template_dir / template_name
        
        if template_name in self.cache:
            template = self.cache[template_name]
        else:
            if not template_path.exists():
                raise FileNotFoundError(f"Template '{template_name}' not found")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            self.cache[template_name] = template
        
        return self._process_template(template, context)
    
    def _process_template(self, template: str, context: Dict) -> str:
        """پردازش تمپلیت با syntax پیشرفته"""
        
        # پردازش وراثت تمپلیت
        template = self._process_extends(template, context)
        
        # پردازش متغیرها با فیلترها {{ var | filter }}
        def replace_var(match):
            var_part = match.group(1).strip()
            parts = var_part.split('|')
            var_name = parts[0].strip()
            applied_filters = [f.strip() for f in parts[1:]] if len(parts) > 1 else []
            
            try:
                if '.' in var_name:
                    parts = var_name.split('.')
                    value = context
                    for part in parts:
                        value = value[part]
                else:
                    value = context.get(var_name, '')
                
                # اعمال فیلترها
                for filter_name in applied_filters:
                    if filter_name in self.filters:
                        value = self.filters[filter_name](value)
                
                if isinstance(value, str):
                    return escape(str(value))
                return str(value)
            except (KeyError, TypeError):
                return ''
        
        template = re.sub(r'\{\{\s*(.+?)\s*\}\}', replace_var, template)
        
        # پردازش حلقه‌ها {% for item in items %}
        def process_for_loop(match):
            loop_var = match.group(1).strip()
            list_var = match.group(2).strip()
            loop_content = match.group(3)
            
            if list_var not in context:
                return ''
                
            result = []
            items = context[list_var]
            if not isinstance(items, (list, tuple)):
                items = [items]
                
            for index, item in enumerate(items):
                loop_context = context.copy()
                loop_context[loop_var] = item
                loop_context['loop'] = {
                    'index': index + 1,
                    'index0': index,
                    'first': index == 0,
                    'last': index == len(items) - 1
                }
                result.append(self._process_template(loop_content, loop_context))
            
            return ''.join(result)
        
        template = re.sub(
            r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}',
            process_for_loop,
            template,
            flags=re.DOTALL
        )
        
        # پردازش شرطی‌ها {% if condition %}
        def process_if(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            else_content = match.group(4) if match.group(4) else ''
            
            try:
                if '.' in condition:
                    parts = condition.split('.')
                    value = context
                    for part in parts:
                        value = value[part]
                else:
                    value = context.get(condition, False)
                
                if value:
                    return self._process_template(if_content, context)
                return self._process_template(else_content, context)
            except:
                return self._process_template(else_content, context)
        
        template = re.sub(
            r'\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}',
            process_if,
            template,
            flags=re.DOTALL
        )
        
        # پردازش include
        def process_include(match):
            included_template = match.group(1).strip()
            try:
                return self.render(included_template, **context)
            except FileNotFoundError:
                return ''
        
        template = re.sub(
            r'\{%\s*include\s+[\'"](.+?)[\'"]\s*%\}',
            process_include,
            template,
            flags=re.DOTALL
        )
        
        return template
    
    def _process_extends(self, template: str, context: Dict) -> str:
        """پردازش وراثت تمپلیت"""
        extends_match = re.match(r'\{%\s*extends\s+[\'"](.+?)[\'"]\s*%\}(.*?)$', template, re.DOTALL)
        if not extends_match:
            return template
        
        parent_template = extends_match.group(1)
        blocks = {}
        
        # پیدا کردن تمام بلاک‌ها
        block_matches = re.finditer(r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}', template, re.DOTALL)
        for match in block_matches:
            blocks[match.group(1)] = match.group(2)
        
        # لود کردن قالب والد
        parent_path = self.template_dir / parent_template
        if not parent_path.exists():
            raise FileNotFoundError(f"Parent template '{parent_template}' not found")
        
        with open(parent_path, 'r', encoding='utf-8') as f:
            parent_content = f.read()
        
        # جایگزینی بلاک‌ها
        def replace_block(match):
            block_name = match.group(1)
            return blocks.get(block_name, match.group(2))
        
        return re.sub(
            r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}',
            replace_block,
            parent_content,
            flags=re.DOTALL
        )


# ============================================================================
# Improved Database ORM
# ============================================================================

class Migration:
    """مدیریت migrations دیتابیس"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_migration_table()
    
    def _create_migration_table(self):
        """ایجاد جدول migrations"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def apply(self, migration_name: str, sql: str):
        """اعمال یک migration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # بررسی اینکه migration قبلاً اعمال نشده
        cursor.execute("SELECT COUNT(*) FROM migrations WHERE name = ?", (migration_name,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        try:
            cursor.executescript(sql)
            cursor.execute("INSERT INTO migrations (name) VALUES (?)", (migration_name,))
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()


@dataclass
class Relationship:
    type: str  # 'one-to-many' or 'many-to-many'
    related_table: str
    foreign_key: Optional[str] = None
    junction_table: Optional[str] = None


class SimpleORM:
    """ORM پیشرفته با پشتیبانی از روابط و تراکنش‌ها"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.migration = Migration(db_path)
        self.relationships = defaultdict(list)
        self.init_db()
    
    def init_db(self):
        """مقداردهی اولیه دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()
    
    def add_relationship(self, table: str, relationship: Relationship):
        """اضافه کردن رابطه به جدول"""
        self.relationships[table].append(relationship)
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """اجرای کوئری و برگرداندن نتایج"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        finally:
            conn.close()
    
    def transaction(self, queries: List[Tuple[str, tuple]]):
        """اجرای تراکنش"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            for query, params in queries:
                cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_table(self, table_name: str, **columns):
        """ساخت جدول آسان"""
        cols = []
        for name, col_type in columns.items():
            cols.append(f"{name} {col_type}")
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(cols)})"
        self.execute(query)
    
    def insert(self, table: str, **data) -> int:
        """درج رکورد جدید"""
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        self.execute(query, tuple(data.values()))
        return self.execute("SELECT last_insert_rowid()")[0]['last_insert_rowid()']
    
    def select(self, table: str, where: str = "", **params) -> List[Dict]:
        """انتخاب رکوردها با پشتیبانی از روابط"""
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        results = self.execute(query, tuple(params.values()) if params else ())
        
        # بارگذاری روابط
        for relationship in self.relationships[table]:
            if relationship.type == 'one-to-many':
                for record in results:
                    related_data = self.execute(
                        f"SELECT * FROM {relationship.related_table} WHERE {relationship.foreign_key} = ?",
                        (record['id'],)
                    )
                    record[relationship.related_table] = related_data
            elif relationship.type == 'many-to-many':
                for record in results:
                    related_data = self.execute(
                        f"""
                        SELECT {relationship.related_table}.* 
                        FROM {relationship.related_table}
                        JOIN {relationship.junction_table} ON 
                            {relationship.junction_table}.related_id = {relationship.related_table}.id
                        WHERE {relationship.junction_table}.main_id = ?
                        """,
                        (record['id'],)
                    )
                    record[relationship.related_table] = related_data
        
        return results
    
    def update(self, table: str, where: str, **data) -> int:
        """آپدیت رکوردها"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.execute(query, tuple(data.values()))
    
    def delete(self, table: str, where: str, **params) -> int:
        """حذف رکوردها"""
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(query, tuple(params.values()) if params else ())


# ============================================================================
# Improved Cache System
# ============================================================================

class SimpleCache:
    """سیستم کش پیشرفته با پشتیبانی از Redis"""
    
    def __init__(self, default_timeout: int = 300, redis_url: Optional[str] = None):
        self.default_timeout = default_timeout
        self.redis = None
        self.local_cache = {}
        self.timeouts = {}
        
        if redis_url:
            try:
                self.redis = redis.from_url(redis_url)
            except:
                pass
    
    def get(self, key: str) -> Any:
        """دریافت مقدار از کش"""
        if self.redis:
            try:
                value = self.redis.get(key)
                return json.loads(value) if value else None
            except:
                pass
        
        if key in self.local_cache:
            if key in self.timeouts and time.time() > self.timeouts[key]:
                del self.local_cache[key]
                del self.timeouts[key]
                return None
            return self.local_cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """تنظیم مقدار در کش"""
        if self.redis:
            try:
                self.redis.setex(key, timeout or self.default_timeout, json.dumps(value))
                return
            except:
                pass
        
        self.local_cache[key] = value
        if timeout is None:
            timeout = self.default_timeout
        if timeout > 0:
            self.timeouts[key] = time.time() + timeout
    
    def delete(self, key: str) -> None:
        """حذف از کش"""
        if self.redis:
            try:
                self.redis.delete(key)
            except:
                pass
        
        if key in self.local_cache:
            del self.local_cache[key]
        if key in self.timeouts:
            del self.timeouts[key]
    
    def clear(self) -> None:
        """پاک کردن کامل کش"""
        if self.redis:
            try:
                self.redis.flushdb()
            except:
                pass
        
        self.local_cache.clear()
        self.timeouts.clear()
    
    def invalidate_pattern(self, pattern: str):
        """حذف کش‌های مطابق با الگو"""
        if self.redis:
            try:
                for key in self.redis.scan_iter(pattern):
                    self.redis.delete(key)
            except:
                pass
        
        keys_to_delete = [k for k in self.local_cache if re.match(pattern, k)]
        for key in keys_to_delete:
            self.delete(key)


# ============================================================================
# Request/Response Classes
# ============================================================================

class Request:
    """کلاس درخواست با امکانات کامل"""
    
    def __init__(self, method: str, path: str, headers: Dict, body: bytes, query_params: Dict):
        self.method = method.upper()
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params
        self._json = None
        self._form = None
        self._files = None
        self.session = {}
        self.user = None
    
    @property
    def json(self) -> Dict:
        """دریافت JSON از body"""
        if self._json is None:
            try:
                self._json = json.loads(self.body.decode('utf-8'))
            except:
                self._json = {}
        return self._json
    
    @property
    def form(self) -> Dict:
        """دریافت فرم data"""
        if self._form is None:
            self._form = {}
            if self.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
                try:
                    form_data = self.body.decode('utf-8')
                    self._form = parse_qs(form_data, keep_blank_values=True)
                    self._form = {k: v[0] if len(v) == 1 else v for k, v in self._form.items()}
                except:
                    pass
        return self._form
    
    @property
    def files(self) -> Dict:
        """دریافت فایل‌های آپلود شده"""
        if self._files is None:
            self._files = {}
            if self.headers.get('content-type', '').startswith('multipart/form-data'):
                try:
                    # TODO: پیاده‌سازی پارس multipart
                    pass
                except:
                    pass
        return self._files
    
    def get_header(self, name: str, default: str = "") -> str:
        """دریافت header"""
        return self.headers.get(name.lower(), default)


class Response:
    """کلاس پاسخ با امکانات کامل"""
    
    def __init__(self, content: Any = "", status: int = 200, headers: Optional[Dict] = None):
        self.status = status
        self.headers = headers or {}
        
        if isinstance(content, dict):
            self.content = json.dumps(content, ensure_ascii=False)
            self.headers.setdefault('Content-Type', 'application/json; charset=utf-8')
        elif isinstance(content, bytes):
            self.content = content
            self.headers.setdefault('Content-Type', 'application/octet-stream')
        else:
            self.content = str(content)
            self.headers.setdefault('Content-Type', 'text/html; charset=utf-8')
    
    def set_cookie(self, name: str, value: str, max_age: int = 86400, path: str = "/"):
        """تنظیم کوکی"""
        cookie = f"{name}={value}; Max-Age={max_age}; Path={path}"
        self.headers['Set-Cookie'] = cookie


# ============================================================================
# Improved Authentication & Security
# ============================================================================

class SessionManager:
    """مدیریت سشن‌ها"""
    
    def __init__(self, cache: SimpleCache):
        self.cache = cache
    
    def create_session(self, user_id: int) -> str:
        """ایجاد سشن جدید"""
        session_id = str(uuid.uuid4())
        self.cache.set(f"session:{session_id}", user_id, timeout=86400)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[int]:
        """دریافت اطلاعات سشن"""
        return self.cache.get(f"session:{session_id}")
    
    def destroy_session(self, session_id: str):
        """حذف سشن"""
        self.cache.delete(f"session:{session_id}")


class JWTAuth:
    """سیستم احراز هویت JWT پیشرفته"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def encode_jwt(self, payload: Dict, exp_hours: int = 24) -> str:
        """ساخت JWT token"""
        header = {"alg": "HS256", "typ": "JWT"}
        payload['exp'] = int(time.time()) + (exp_hours * 3600)
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def decode_jwt(self, token: str) -> Optional[Dict]:
        """رمزگشایی JWT token"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except:
            return None
    
    async def oauth2_token(self, provider: str, code: str, redirect_uri: str) -> Optional[Dict]:
        """دریافت توکن از OAuth2 provider"""
        providers = {
            'google': {
                'token_url': 'https://oauth2.googleapis.com/token',
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')
            }
        }
        
        if provider not in providers:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.post(providers[provider]['token_url'], data={
                'code': code,
                'client_id': providers[provider]['client_id'],
                'client_secret': providers[provider]['client_secret'],
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }) as response:
                return await response.json()


class PasswordManager:
    """مدیر رمزعبور با امنیت بالا"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """هش کردن رمزعبور"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + key.hex()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """تایید رمزعبور"""
        try:
            salt = bytes.fromhex(hashed[:64])
            key = bytes.fromhex(hashed[64:])
            test_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return key == test_key
        except:
            return False


# ============================================================================
# Event System
# ============================================================================

class EventManager:
    """مدیریت رویدادها"""
    
    def __init__(self):
        self.listeners = defaultdict(list)
    
    def on(self, event_name: str):
        """دکوراتور برای ثبت listener"""
        def decorator(func):
            self.listeners[event_name].append(func)
            return func
        return decorator
    
    def emit(self, event_name: str, *args, **kwargs):
        """ارسال رویداد"""
        for listener in self.listeners[event_name]:
            try:
                if asyncio.iscoroutinefunction(listener):
                    asyncio.create_task(listener(*args, **kwargs))
                else:
                    listener(*args, **kwargs)
            except:
                pass


# ============================================================================
# Background Tasks
# ============================================================================

class TaskManager:
    """مدیر تسک‌های پس‌زمینه"""
    
    def __init__(self):
        self.tasks = []
        self.running = False
        self.thread = None
    
    def add_task(self, func: Callable, *args, **kwargs):
        """اضافه کردن تسک جدید"""
        task = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'created': time.time()
        }
        self.tasks.append(task)
    
    def start(self):
        """شروع اجرای تسک‌ها"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_tasks, daemon=True)
            self.thread.start()
    
    def stop(self):
        """توقف اجرای تسک‌ها"""
        self.running = False
    
    def _run_tasks(self):
        """اجرای تسک‌ها در پس‌زمینه"""
        while self.running:
            if self.tasks:
                task = self.tasks.pop(0)
                try:
                    if asyncio.iscoroutinefunction(task['func']):
                        asyncio.run(task['func'](*task['args'], **task['kwargs']))
                    else:
                        task['func'](*task['args'], **task['kwargs'])
                except Exception as e:
                    print(f"Task error: {e}")
            time.sleep(0.1)


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """سیستم Rate Limiting"""
    
    def __init__(self):
        self.clients = defaultdict(lambda: deque())
    
    def is_allowed(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """بررسی اجازه درخواست"""
        now = time.time()
        client_requests = self.clients[client_id]
        
        while client_requests and client_requests[0] < now - window_seconds:
            client_requests.popleft()
        
        if len(client_requests) >= max_requests:
            return False
        
        client_requests.append(now)
        return True


# ============================================================================
# WebSocket Support
# ============================================================================

class WebSocketManager:
    """مدیر WebSocket connections"""
    
    def __init__(self):
        self.connections = weakref.WeakSet()
    
    def add_connection(self, ws):
        """اضافه کردن connection جدید"""
        self.connections.add(ws)
    
    async def broadcast(self, message: str):
        """ارسال پیام به همه connections"""
        for ws in list(self.connections):
            try:
                await ws.send_str(message)
            except:
                pass


# ============================================================================
# Testing Framework
# ============================================================================

class TestClient:
    """کلاینت تست برای تست APIها"""
    
    def __init__(self, app):
        self.app = app
    
    async def request(self, method: str, path: str, headers: Dict = None, body: Any = None) -> Response:
        """ارسال درخواست تست"""
        headers = headers or {}
        body = body if isinstance(body, bytes) else json.dumps(body).encode() if body else b''
        
        request = Request(
            method=method,
            path=path,
            headers=headers,
            body=body,
            query_params=parse_qs(urlparse(path).query)
        )
        
        return await asyncio.get_event_loop().run_in_executor(None, self.app.handle_request, request)


# ============================================================================
# Main App Class
# ============================================================================

class KhafanHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler برای KhafanFlask"""
    
    def log_message(self, format, *args):
        """غیرفعال کردن لاگ‌های پیش‌فرض"""
        if hasattr(self.server, 'app') and self.server.app.debug:
            super().log_message(format, *args)
    
    def do_GET(self):
        self._handle_request('GET')
    
    def do_POST(self):
        self._handle_request('POST')
    
    def do_PUT(self):
        self._handle_request('PUT')
    
    def do_DELETE(self):
        self._handle_request('DELETE')
    
    def do_PATCH(self):
        self._handle_request('PATCH')
    
    def do_OPTIONS(self):
        self._handle_request('OPTIONS')
    
    def _handle_request(self, method: str):
        """پردازش درخواست"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
            
            request = Request(
                method=method,
                path=parsed_url.path,
                headers=dict(self.headers),
                body=body,
                query_params=query_params
            )
            
            response = self.server.app.handle_request(request)
            
            self.send_response(response.status)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            
            if isinstance(response.content, str):
                self.wfile.write(response.content.encode('utf-8'))
            else:
                self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            if hasattr(self.server, 'app') and self.server.app.debug:
                error_html = f"""
                <h1>خطای سرور داخلی</h1>
                <pre>{traceback.format_exc()}</pre>
                """
            else:
                error_html = "<h1>خطای سرور داخلی</h1>"
            
            self.wfile.write(error_html.encode('utf-8'))


class App:
    """
    کلاس اصلی KhafanFlask - نسخه پیشرفته
    
    مثال ساده:
    ```python
    app = App()
    
    @app.route('/')
    async def home():
        return "سلام دنیا! 🚀"
    
    app.run()
    ```
    """
    
    def __init__(self, 
                 secret_key: Optional[str] = None,
                 debug: bool = False,
                 template_dir: str = "templates",
                 static_dir: str = "static",
                 db_path: str = "app.db",
                 config_file: Optional[str] = None):
        
        self.config = Config()
        if config_file:
            self.config.load_from_file(config_file)
        self.config.load_from_env()
        
        self.secret_key = secret_key or self.config['SECRET_KEY']
        self.debug = debug or self.config['DEBUG']
        self.template_dir = template_dir or self.config['TEMPLATE_DIR']
        self.static_dir = static_dir or self.config['STATIC_DIR']
        
        self.routes = {}
        self.before_request_handlers = []
        self.after_request_handlers = []
        self.error_handlers = {}
        self.middlewares = []
        
        self.logger = KhafanLogger()
        self.template_engine = SimpleJin(self.template_dir)
        self.cache = SimpleCache(redis_url=self.config['REDIS_URL'])
        self.db = SimpleORM(db_path or self.config['DATABASE'])
        self.jwt = JWTAuth(self.secret_key)
        self.session = SessionManager(self.cache)
        self.task_manager = TaskManager()
        self.rate_limiter = RateLimiter()
        self.websocket_manager = WebSocketManager()
        self.event_manager = EventManager()
        self.test_client = TestClient(self)
        
        self._setup_default_routes()
        self._setup_user_system()
        
        if self.config['SMTP_SERVER']:
            self.setup_mail(
                self.config['SMTP_SERVER'],
                self.config['SMTP_PORT'],
                self.config['SMTP_USERNAME'],
                self.config['SMTP_PASSWORD']
            )
        
        self.logger.info("🚀 KhafanFlask initialized successfully!")
        if self.debug:
            self.logger.debug("🔧 Debug mode is ON")
    
    def _setup_default_routes(self):
        """راه‌اندازی routeهای پیش‌فرض"""
        self.route(f'/{self.static_dir}/<path:filename>')(self._serve_static)
        self.route('/favicon.ico')(lambda: self._serve_static('favicon.ico'))
        self.route('/api/docs')(self._api_docs)
        self.websocket_route('/ws')(self._handle_websocket)
    
    def _setup_user_system(self):
        """راه‌اندازی سیستم کاربری"""
        self.db.create_table('users',
            id='INTEGER PRIMARY KEY AUTOINCREMENT',
            username='TEXT UNIQUE NOT NULL',
            email='TEXT UNIQUE NOT NULL',
            password_hash='TEXT NOT NULL',
            created_at='TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            is_active='BOOLEAN DEFAULT 1'
        )
        
        self.db.create_table('roles',
            id='INTEGER PRIMARY KEY AUTOINCREMENT',
            name='TEXT UNIQUE NOT NULL',
            permissions='TEXT'
        )
        
        self.db.create_table('user_roles',
            user_id='INTEGER',
            role_id='INTEGER',
            FOREIGN_KEY_user_id='FOREIGN KEY(user_id) REFERENCES users(id)',
            FOREIGN_KEY_role_id='FOREIGN KEY(role_id) REFERENCES roles(id)'
        )
    
    def route(self, path: str, methods: Optional[List[str]] = None, **options):
        """دکوراتور route پیشرفته"""
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        def decorator(func):
            regex_path = path
            param_types = {}
            
            def process_param(match):
                param_name = match.group(2)
                param_type = match.group(1) or 'string'
                param_types[param_name] = param_type
                
                if param_type == 'int':
                    return rf'(?P<{param_name}>\d+)'
                elif param_type == 'path':
                    return rf'(?P<{param_name}>[^/]+(?:/[^/]+)*)'
                else:
                    return rf'(?P<{param_name}>[^/]+)'
            
            regex_path = re.sub(r'<(\w+:)?(\w+)>', process_param, path)
            regex_path = f'^{regex_path}$'
            
            route_info = {
                'func': func,
                'methods': [m.upper() for m in methods],
                'regex': re.compile(regex_path),
                'options': options,
                'original_path': path,
                'param_types': param_types
            }
            
            if hasattr(func, '_cache_timeout'):
                route_info['options']['cache'] = func._cache_timeout
            
            if hasattr(func, '_rate_limit'):
                route_info['options']['rate_limit'] = func._rate_limit
            
            self.routes[path] = route_info
            
            return func
        
        return decorator
    
    def websocket_route(self, path: str):
        """دکوراتور برای WebSocket routes"""
        def decorator(func):
            self.routes[path] = {
                'func': func,
                'methods': ['WEBSOCKET'],
                'regex': re.compile(f'^{path}$'),
                'options': {},
                'original_path': path,
                'param_types': {}
            }
            return func
        return decorator
    
    def before_request(self, func):
        """دکوراتور before request"""
        self.before_request_handlers.append(func)
        return func
    
    def after_request(self, func):
        """دکوراتور after request"""
        self.after_request_handlers.append(func)
        return func
    
    def errorhandler(self, code: int):
        """دکوراتور مدیریت خطا"""
        def decorator(func):
            self.error_handlers[code] = func
            return func
        return decorator
    
    def middleware(self, func):
        """دکوراتور middleware"""
        self.middlewares.append(func)
        return func
    
    async def handle_request(self, request: Request) -> Response:
        """پردازش اصلی درخواست"""
        try:
            # بررسی سشن
            session_id = request.get_header('X-Session-ID')
            if session_id:
                user_id = self.session.get_session(session_id)
                if user_id:
                    user = self.db.select('users', 'id = ?', id=user_id)
                    if user:
                        request.user = user[0]
            
            for middleware in self.middlewares:
                result = middleware(request)
                if asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, Response):
                    return result
            
            for handler in self.before_request_handlers:
                result = handler(request)
                if asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, Response):
                    return result
            
            route_info, params = self._find_route(request.path, request.method)
            
            if not route_info:
                return self._handle_error(404, request)
            
            if 'rate_limit' in route_info['options']:
                client_id = request.headers.get('x-real-ip', request.headers.get('remote-addr', 'unknown'))
                if not self.rate_limiter.is_allowed(client_id, **route_info['options']['rate_limit']):
                    return Response("Rate limit exceeded", 429)
            
            cache_key = f"{request.method}:{request.path}"
            cached_response = self.cache.get(cache_key)
            if cached_response and 'cache' in route_info['options']:
                return Response(cached_response)
            
            try:
                if params:
                    for param_name, param_value in params.items():
                        param_type = route_info['param_types'].get(param_name, 'string')
                        if param_type == 'int':
                            params[param_name] = int(param_value)
                
                sig = inspect.signature(route_info['func'])
                if len(sig.parameters) > 0:
                    result = route_info['func'](request, **params)
                else:
                    result = route_info['func']()
                
                if asyncio.iscoroutine(result):
                    result = await result
                
                if isinstance(result, Response):
                    response = result
                else:
                    response = Response(result)
                
                if 'cache' in route_info['options']:
                    self.cache.set(cache_key, response.content, route_info['options']['cache'])
                
                for handler in self.after_request_handlers:
                    handler_result = handler(request, response)
                    if asyncio.iscoroutine(handler_result):
                        handler_result = await handler_result
                    response = handler_result or response
                
                self.event_manager.emit('request_processed', request, response)
                return response
                
            except Exception as e:
                self.logger.error(f"Handler error: {str(e)}")
                if self.debug:
                    raise
                return self._handle_error(500, request, str(e))
                
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return self._handle_error(500, request, str(e))
    
    def _find_route(self, path: str, method: str) -> Tuple[Optional[Dict], Dict]:
        """یافتن route مناسب"""
        for route_path, route_info in self.routes.items():
            if method.upper() not in route_info['methods']:
                continue
                
            match = route_info['regex'].match(path)
            if match:
                return route_info, match.groupdict()
        
        return None, {}
    
    def _handle_error(self, code: int, request: Request, message: str = "") -> Response:
        """مدیریت خطاها"""
        self.logger.error(f"Error {code}: {message}")
        
        if code in self.error_handlers:
            try:
                return Response(self.error_handlers[code](request, message))
            except:
                pass
        
        error_messages = {
            404: "صفحه مورد نظر یافت نشد 😕",
            405: "متد درخواست مجاز نیست",
            429: "تعداد درخواست‌ها زیاد است، لطفا کمی صبر کنید",
            500: "خطای داخلی سرور رخ داده است"
        }
        
        error_message = error_messages.get(code, f"خطای {code}")
        if message and self.debug:
            error_message += f"\n\n{message}"
        
        return Response(f"<h1>{error_message}</h1>", code)
    
    async def _handle_websocket(self, request):
        """مدیریت درخواست‌های WebSocket"""
        ws_app = web.Application()
        ws_app.router.add_get(request.path, self._websocket_handler)
        return await ws_app.handle(request)
    
    async def _websocket_handler(self, request):
        """هندلر WebSocket"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_manager.add_connection(ws)
        
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.websocket_manager.broadcast(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                self.logger.error(f"WebSocket error: {ws.exception()}")
        
        return ws
    
    def _serve_static(self, filename: str = "") -> Response:
        """سرو فایل‌های static"""
        try:
            static_path = Path(self.static_dir) / filename
            if not static_path.exists():
                return self._handle_error(404, None)
            
            with open(static_path, 'rb') as f:
                content = f.read()
            
            mime_type, _ = mimetypes.guess_type(str(static_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            return Response(content, headers={'Content-Type': mime_type})
            
        except Exception as e:
            return self._handle_error(500, None, str(e))
    
    def _api_docs(self) -> Response:
        """تولید مستندات API خودکار"""
        docs = {
            "title": "KhafanFlask API Documentation",
            "version": __version__,
            "routes": []
        }
        
        for path, info in self.routes.items():
            if not path.startswith('/api'):
                continue
                
            route_doc = {
                "path": path,
                "methods": info['methods'],
                "description": info['func'].__doc__ or "No description",
                "parameters": list(info['param_types'].keys())
            }
            docs["routes"].append(route_doc)
        
        return Response(docs)
    
    def render_template(self, template_name: str, **context) -> str:
        """رندر کردن تمپلیت"""
        return self.template_engine.render(template_name, **context)
    
    def redirect(self, url: str, code: int = 302) -> Response:
        """ریدایرکت"""
        response = Response("", code)
        response.headers['Location'] = url
        return response
    
    def send_file(self, file_path: str) -> Response:
        """ارسال فایل"""
        return self._serve_static(file_path)
    
    def flash(self, message: str, category: str = "info"):
        """پیام‌های flash"""
        session_id = str(uuid.uuid4())
        self.cache.set(f"flash:{session_id}", {'message': message, 'category': category}, timeout=60)
        return session_id
    
    def get_flash_messages(self, session_id: str) -> List[Dict]:
        """دریافت پیام‌های flash"""
        messages = self.cache.get(f"flash:{session_id}") or []
        self.cache.delete(f"flash:{session_id}")
        return messages if isinstance(messages, list) else [messages]
    
    def add_background_task(self, func: Callable, *args, **kwargs):
        """اضافه کردن تسک پس‌زمینه"""
        self.task_manager.add_task(func, *args, **kwargs)
    
    def create_user(self, username: str, email: str, password: str, roles: List[str] = None) -> Optional[int]:
        """ساخت کاربر جدید"""
        try:
            password_hash = PasswordManager.hash_password(password)
            user_id = self.db.insert('users', 
                username=username,
                email=email, 
                password_hash=password_hash
            )
            
            if roles:
                for role in roles:
                    role_id = self.db.select('roles', 'name = ?', name=role)
                    if role_id:
                        self.db.insert('user_roles', user_id=user_id, role_id=role_id[0]['id'])
            
            return user_id
        except:
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """احراز هویت کاربر"""
        users = self.db.select('users', 'username = ? AND is_active = 1', username=username)
        if not users:
            return None
        
        user = users[0]
        if PasswordManager.verify_password(password, user['password_hash']):
            user_dict = dict(user)
            del user_dict['password_hash']
            
            # بارگذاری نقش‌ها
            roles = self.db.execute("""
                SELECT r.name 
                FROM roles r 
                JOIN user_roles ur ON r.id = ur.role_id 
                WHERE ur.user_id = ?
            """, (user['id'],))
            user_dict['roles'] = [r['name'] for r in roles]
            
            return user_dict
        return None
    
    def generate_token(self, user_data: Dict, exp_hours: int = 24) -> str:
        """تولید JWT token"""
        return self.jwt.encode_jwt(user_data, exp_hours)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """تایید JWT token"""
        return self.jwt.decode_jwt(token)
    
    def require_auth(self, roles: Optional[List[str]] = None):
        """دکوراتور برای routes که نیاز به احراز هویت دارند"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(request, *args, **kwargs):
                auth_header = request.get_header('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return Response({"error": "Token required"}, 401)
                
                token = auth_header[7:]
                user_data = self.verify_token(token)
                
                if not user_data:
                    return Response({"error": "Invalid token"}, 401)
                
                if roles:
                    user_roles = user_data.get('roles', [])
                    if not any(role in user_roles for role in roles):
                        return Response({"error": "Insufficient permissions"}, 403)
                
                request.user = user_data
                return await func(request, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def api_route(self, path: str, methods: Optional[List[str]] = None, version: str = "v1"):
        """دکوراتور برای API routes با پشتیبانی از versioning"""
        def decorator(func):
            @self.route(f'/api/{version}{path}', methods)
            @functools.wraps(func)
            async def wrapper(request, *args, **kwargs):
                try:
                    result = func(request, *args, **kwargs)
                    if asyncio.iscoroutine(result):
                        result = await result
                    if isinstance(result, Response):
                        return result
                    return Response({"success": True, "data": result, "version": version})
                except Exception as e:
                    error_msg = str(e) if self.debug else "Internal server error"
                    return Response({"success": False, "error": error_msg, "version": version}, 500)
            
            return wrapper
        return decorator
    
    def paginate(self, query_result: List[Dict], page: int = 1, per_page: int = 20) -> Dict:
        """صفحه‌بندی نتایج"""
        total = len(query_result)
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            "items": query_result[start:end],
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    
    def setup_mail(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """تنظیم سیستم ایمیل"""
        self.mail_config = {
            'server': smtp_server,
            'port': smtp_port,
            'username': username,
            'password': password
        }
    
    def send_email(self, to: str, subject: str, body: str, is_html: bool = False):
        """ارسال ایمیل"""
        if not hasattr(self, 'mail_config'):
            raise Exception("Mail not configured. Use setup_mail() first.")
        
        def send_async():
            try:
                msg = MIMEMultipart()
                msg['From'] = self.mail_config['username']
                msg['To'] = to
                msg['Subject'] = subject
                
                msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
                
                server = smtplib.SMTP(self.mail_config['server'], self.mail_config['port'])
                server.starttls()
                server.login(self.mail_config['username'], self.mail_config['password'])
                server.send_message(msg)
                server.quit()
                
            except Exception as e:
                self.logger.error(f"Email send error: {e}")
        
        self.add_background_task(send_async)
    
    def generate_model(self, model_name: str, **fields):
        """تولید مدل دیتابیس"""
        table_name = f"{model_name.lower()}s"
        
        self.db.create_table(table_name, **fields)
        
        model_code = f'''
class {model_name}Model:
    """مدل {model_name} - تولید خودکار KhafanFlask"""
    
    def __init__(self, app):
        self.app = app
        self.table = "{table_name}"
    
    def create(self, **data):
        return self.app.db.insert(self.table, **data)
    
    def get_all(self):
        return self.app.db.select(self.table)
    
    def get_by_id(self, id):
        result = self.app.db.select(self.table, "id = ?", id=id)
        return result[0] if result else None
    
    def update(self, id, **data):
        return self.app.db.update(self.table, "id = ?", id=id, **data)
    
    def delete(self, id):
        return self.app.db.delete(self.table, "id = ?", id=id)

# استفاده:
# {model_name.lower()}_model = {model_name}Model(app)
        '''
        
        self.logger.info(f"✅ Model {model_name} created!")
        print("📋 Generated code:")
        print(model_code)
    
    def generate_crud_routes(self, model_name: str):
        """تولید routeهای CRUD خودکار"""
        name_lower = model_name.lower()
        name_plural = f"{name_lower}s"
        
        crud_code = f'''
# CRUD Routes برای {model_name} - تولید خودکار KhafanFlask

@app.api_route('/{name_plural}', ['GET'])
async def get_{name_plural}(request):
    """دریافت لیست {model_name}"""
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 20))
    
    items = app.db.select('{name_plural}')
    return app.paginate(items, page, per_page)

@app.api_route('/{name_plural}/<int:id>', ['GET'])
async def get_{name_lower}(request, id):
    """دریافت {model_name} با ID"""
    item = app.db.select('{name_plural}', 'id = ?', id=id)
    if not item:
        return Response({{"error": "{model_name} not found"}}, 404)
    return item[0]

@app.api_route('/{name_plural}', ['POST'])
@validate_json('title', 'content')
async def create_{name_lower}(request):
    """ساخت {model_name} جدید"""
    data = request.json
    item_id = app.db.insert('{name_plural}', **data)
    app.event_manager.emit('create_{name_lower}', item_id, data)
    return {{"id": item_id, "message": "{model_name} created successfully"}}

@app.api_route('/{name_plural}/<int:id>', ['PUT'])
@validate_json('title', 'content')
async def update_{name_lower}(request, id):
    """آپدیت {model_name}"""
    data = request.json
    updated = app.db.update('{name_plural}', 'id = ?', **data)
    if not updated:
        return Response({{"error": "{model_name} not found"}}, 404)
    app.event_manager.emit('update_{name_lower}', id, data)
    return {{"message": "{model_name} updated successfully"}}

@app.api_route('/{name_plural}/<int:id>', ['DELETE'])
async def delete_{name_lower}(request, id):
    """حذف {model_name}"""
    deleted = app.db.delete('{name_plural}', 'id = ?', id=id)
    if not deleted:
        return Response({{"error": "{model_name} not found"}}, 404)
    app.event_manager.emit('delete_{name_lower}', id)
    return {{"message": "{model_name} deleted successfully"}}
        '''
        
        self.logger.info(f"✅ CRUD routes for {model_name} generated!")
        print("📋 Generated code:")
        print(crud_code)
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: Optional[bool] = None):
        """اجرای سرور"""
        if debug is not None:
            self.debug = debug
        
        self.task_manager.start()
        
        class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
            daemon_threads = True
        
        server = ThreadedHTTPServer((host, port), KhafanHTTPRequestHandler)
        server.app = self
        
        self.logger.info(f"""
🚀 KhafanFlask Server Starting...
📍 Running on: http://{host}:{port}
🔧 Debug mode: {'ON' if self.debug else 'OFF'}
📊 Routes loaded: {len(self.routes)}
🛠️ Static files: /{self.static_dir}/
📝 Templates: {self.template_dir}/
📚 API docs: http://{host}:{port}/api/docs
        """)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Server stopping...")
            self.task_manager.stop()
            server.shutdown()
            self.logger.info("✅ Server stopped successfully!")


# ============================================================================
# Decorators & Utilities
# ============================================================================

def cache(timeout: int = 300):
    """دکوراتور کش کردن"""
    def decorator(func):
        func._cache_timeout = timeout
        return func
    return decorator

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """دکوراتور محدود کردن نرخ"""
    def decorator(func):
        func._rate_limit = {'max_requests': max_requests, 'window_seconds': window_seconds}
        return func
    return decorator

def validate_json(*required_fields):
    """دکوراتور اعتبارسنجی JSON"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            if not request.json:
                return Response({"error": "JSON data required"}, 400)
            
            missing_fields = []
            for field in required_fields:
                if field not in request.json:
                    missing_fields.append(field)
            
            if missing_fields:
                return Response({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }, 400)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles):
    """دکوراتور برای بررسی نقش‌ها"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return Response({"error": "Authentication required"}, 401)
            
            user_roles = request.user.get('roles', [])
            if not any(role in user_roles for role in roles):
                return Response({"error": "Insufficient permissions"}, 403)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Quick Start Templates
# ============================================================================

def create_blog_app() -> App:
    """ساخت اپ بلاگ آماده"""
    app = App(debug=True)
    
    app.db.create_table('posts',
        id='INTEGER PRIMARY KEY AUTOINCREMENT',
        title='TEXT NOT NULL',
        content='TEXT NOT NULL',
        author_id='INTEGER',
        created_at='TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        published='BOOLEAN DEFAULT 0'
    )
    
    app.db.add_relationship('posts', Relationship(
        type='one-to-many',
        related_table='users',
        foreign_key='author_id'
    ))
    
    @app.route('/')
    async def home(request):
        posts = app.db.select('posts', 'published = 1 ORDER BY created_at DESC LIMIT 10')
        return app.render_template('blog_home.html', posts=posts)
    
    @app.api_route('/posts')
    async def get_posts(request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        posts = app.db.select('posts', 'published = 1 ORDER BY created_at DESC')
        return app.paginate(posts, page, per_page)
    
    @app.api_route('/posts', ['POST'])
    @app.require_auth(['user'])
    @validate_json('title', 'content')
    async def create_post(request):
        data = request.json
        data['author_id'] = request.user['id']
        post_id = app.db.insert('posts', **data)
        app.event_manager.emit('post_created', post_id, data)
        return {"id": post_id, "message": "Post created successfully"}
    
    @app.event_manager.on('post_created')
    def on_post_created(post_id, data):
        app.logger.info(f"New post created: {post_id}")
    
    app.logger.info("📝 Blog app created! Don't forget to create templates/blog_home.html")
    return app

def create_api_server() -> App:
    """ساخت API server آماده"""
    app = App(debug=True)
    
    @app.middleware
    async def cors_middleware(request):
        def add_cors_headers(request, response):
            response.headers.update({
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            })
            return response
        
        app.after_request(add_cors_headers)
    
    @app.api_route('/health')
    async def health_check(request):
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": __version__
        }
    
    @app.api_route('/auth/register', ['POST'])
    @validate_json('username', 'email', 'password')
    async def register(request):
        data = request.json
        user_id = app.create_user(data['username'], data['email'], data['password'], roles=['user'])
        if not user_id:
            return Response({"error": "Username or email already exists"}, 400)
        
        session_id = app.session.create_session(user_id)
        token = app.generate_token({"user_id": user_id, "username": data['username'], "roles": ['user']})
        app.event_manager.emit('user_registered', user_id, data['username'])
        return {"token": token, "user_id": user_id, "session_id": session_id}
    
    @app.api_route('/auth/login', ['POST'])
    @validate_json('username', 'password')
    async def login(request):
        data = request.json
        user = app.authenticate_user(data['username'], data['password'])
        if not user:
            return Response({"error": "Invalid credentials"}, 401)
        
        session_id = app.session.create_session(user['id'])
        token = app.generate_token({"user_id": user['id'], "username": user['username'], "roles": user['roles']})
        app.event_manager.emit('user_login', user['id'], user['username'])
        return {"token": token, "user": user, "session_id": session_id}
    
    @app.api_route('/auth/oauth/<provider>', ['GET'])
    async def oauth_login(request, provider):
        code = request.query_params.get('code')
        redirect_uri = request.query_params.get('redirect_uri')
        if not code or not redirect_uri:
            return Response({"error": "Missing code or redirect_uri"}, 400)
        
        token_data = await app.jwt.oauth2_token(provider, code, redirect_uri)
        if not token_data:
            return Response({"error": "OAuth authentication failed"}, 400)
        
        return {"token": token_data}
    
    @app.event_manager.on('user_registered')
    def on_user_registered(user_id, username):
        app.logger.info(f"New user registered: {username} (ID: {user_id})")
    
    app.logger.info("🔐 API Server created with auth endpoints!")
    return app


# ============================================================================
# Main Export
# ============================================================================

__all__ = [
    'App', 'Request', 'Response', 'SimpleJin', 'SimpleORM', 'SimpleCache',
    'JWTAuth', 'PasswordManager', 'TaskManager', 'RateLimiter', 'WebSocketManager',
    'Config', 'KhafanLogger', 'SessionManager', 'EventManager', 'TestClient',
    'cache', 'rate_limit', 'validate_json', 'require_role',
    'create_blog_app', 'create_api_server'
]


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    app = create_api_server()
    
    # تعریف یک فیلتر جدید
    app.template_engine.add_filter('reverse', lambda s: s[::-1])
    
    # تعریف یک مدل جدید
    app.generate_model('Product', 
        id='INTEGER PRIMARY KEY AUTOINCREMENT',
        name='TEXT NOT NULL',
        price='REAL NOT NULL',
        stock='INTEGER DEFAULT 0'
    )
    
    # تولید CRUD routes
    app.generate_crud_routes('Product')
    
    # تعریف یک migration
    app.db.migration.apply('add_category_to_products', '''
        ALTER TABLE products ADD COLUMN category_id INTEGER;
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    
    # اجرای سرور
    app.run(debug=True)