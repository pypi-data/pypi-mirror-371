import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, TypeVar, Union
from pydantic import BaseModel, Field, validator
import httpx
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .logger import get_logger, LogCategory

T = TypeVar('T')

# ===== 配置常量 =====
DEFAULT_CONFIG_FILE = Path(__file__).parent / "app_config.json"
BACKUP_CONFIG_FILE = Path(__file__).parent / "app_config.backup.json"
TEMPLATE_CONFIG_FILE = Path(__file__).parent / "app_config.template.json"

# ================================================================================
# 饥荒联机版DMP QQ机器人 配置文件
# ================================================================================
# 
# 📖 使用说明：
# 1. 首次使用请修改 DMPConfig 中的服务器地址和令牌
# 2. 在 BotConfig 中设置超级用户QQ号
# 3. 其他配置使用默认值即可，高级用户可根据需要调整
# 
# 🔧 配置方式：
# - 方式1：直接编辑生成的 app_config.json 文件
# - 方式2：修改本文件中的默认值后重启机器人
# 
# ⚠️  重要提醒：
# - 请妥善保管您的DMP令牌，不要泄露给他人
# - 确保DMP服务器地址包含正确的端口号
# 
# ================================================================================

class ConfigSection(BaseModel):
    """配置节基类"""
    
    def validate_self(self) -> List[str]:
        """验证配置节，返回错误列表"""
        return []

class DMPConfig(ConfigSection):
    """
    DMP API配置 - 这是最重要的配置，必须正确设置才能使用
    
    🔧 快速设置指南：
    1. 修改 base_url 为您的DMP服务器地址（例如：https://your-server.com:8080）
    2. 修改 token 为您的DMP API令牌（在DMP管理面板中生成）
    3. 集群配置现在支持动态获取，无需手动设置
    
    ⚠️  注意：请确保DMP服务器地址包含端口号，且令牌具有足够的权限
    """
    
    # 🌐 DMP服务器连接配置（必须设置）
    base_url: str = Field(default="https://your-dmp-server.com", description="DMP服务器地址（包含端口，如：https://192.168.1.100:8080）")
    token: str = Field(default="your_dmp_token_here", description="DMP API访问令牌（在DMP管理面板中生成）")
    
    # ⚙️ 高级配置（一般无需修改）
    timeout: float = Field(default=10.0, description="请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: float = Field(default=1.0, description="重试延迟（秒）")
    
    # 🔄 动态集群管理配置
    auto_discover_clusters: bool = Field(default=True, description="是否自动发现和管理集群")
    cluster_cache_ttl: int = Field(default=300, description="集群信息缓存时间（秒）")
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v or v == "https://your-dmp-server.com":
            raise ValueError("请设置正确的DMP服务器地址")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("DMP服务器地址必须以http://或https://开头")
        return v.rstrip('/')
    
    @validator('token')
    def validate_token(cls, v):
        if not v or v == "your_dmp_token_here":
            raise ValueError("请设置正确的DMP API令牌")
        if len(v) < 10:
            raise ValueError("DMP API令牌长度不能少于10个字符")
        return v
    

    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0 or v > 300:
            raise ValueError("超时时间必须在0-300秒之间")
        return v
    
    @validator('max_retries')
    def validate_max_retries(cls, v):
        if v < 0 or v > 10:
            raise ValueError("重试次数必须在0-10之间")
        return v
    
    def validate_self(self) -> List[str]:
        """额外的配置验证"""
        errors = []
        
        # 检查服务器连通性（异步，这里先记录需要检查）
        if self.base_url and self.token:
            # 这个验证会在配置加载后异步执行
            pass
            
        return errors

class BotConfig(ConfigSection):
    """
    QQ机器人配置 - 控制机器人的权限和行为
    
    🔧 快速设置指南：
    1. 在 superusers 中添加管理员QQ号（如：["123456789", "987654321"]）
    2. 根据需要设置允许使用的群组（空表示所有群组都可用）
    3. 可以修改命令前缀（默认为"/"）
    """
    
    # 👥 用户权限配置（重要）
    superusers: List[str] = Field(default_factory=list, description="超级用户QQ号列表（如：['123456789']）")
    admin_groups: List[str] = Field(default_factory=list, description="管理员群组列表（群号）")
    allowed_groups: List[str] = Field(default_factory=list, description="允许使用的群组列表（空表示不限制）")
    
    # 🤖 机器人行为配置
    command_prefix: str = Field(default="/", description="命令前缀")
    enable_private_chat: bool = Field(default=True, description="是否启用私聊功能")
    enable_group_chat: bool = Field(default=True, description="是否启用群聊功能")
    
    @validator('superusers')
    def validate_superusers(cls, v):
        if not v:
            raise ValueError("至少需要设置一个超级用户")
        for user_id in v:
            if not user_id.isdigit():
                raise ValueError(f"无效的用户ID: {user_id}")
        return v

# ================================================================================
# 系统内部类和高级配置区域 - 以下配置一般情况下无需修改
# ================================================================================

class ConfigValidationError(Exception):
    """配置验证错误"""
    pass

class ConfigReloadError(Exception):
    """配置重载错误"""
    pass

class ConfigChangeHandler(FileSystemEventHandler):
    """配置文件变更监听器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.logger = get_logger(__name__)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('app_config.json'):
            self.logger.info(f"检测到配置文件变更: {event.src_path}", category=LogCategory.SYSTEM)
            # 延迟重载，避免文件正在写入时读取
            threading.Timer(1.0, self.config_manager._reload_config).start()

class CacheConfig(ConfigSection):
    """缓存配置"""
    
    # 内存缓存配置
    memory_max_size: int = Field(default=1000, description="内存缓存最大条目数")
    memory_default_ttl: int = Field(default=300, description="内存缓存默认TTL（秒）")
    
    # 文件缓存配置
    file_cache_dir: str = Field(default="./cache", description="文件缓存目录")
    file_max_size: int = Field(default=10000, description="文件缓存最大条目数")
    file_default_ttl: int = Field(default=1800, description="文件缓存默认TTL（秒）")
    
    # 清理配置
    cleanup_interval: int = Field(default=3600, description="缓存清理间隔（秒）")
    auto_cleanup: bool = Field(default=True, description="是否启用自动清理")

class MessageConfig(ConfigSection):
    """
    消息互通配置 - 支持群聊和私聊双模式
    
    🔧 功能特性：
    - 支持群聊/私聊自由切换
    - 智能消息去重和过滤
    - 灵活的消息格式模板
    - 多集群/世界支持
    """
    
    # 🚀 核心功能配置
    enable_message_bridge: bool = Field(default=True, description="是否启用消息互通功能")
    sync_interval: float = Field(default=3.0, description="消息同步间隔（秒，建议3-10秒）")
    max_message_length: int = Field(default=200, description="单条消息最大长度限制")
    
    # 📱 聊天模式配置
    default_chat_mode: str = Field(default="private", description="默认聊天模式（private: 私聊, group: 群聊）")
    allow_group_chat: bool = Field(default=True, description="是否允许群聊消息互通")
    allow_private_chat: bool = Field(default=True, description="是否允许私聊消息互通")
    
    # 🎯 目标服务器配置
    default_target_cluster: str = Field(default="", description="默认目标集群（空值自动选择第一个）")
    default_target_world: str = Field(default="", description="默认目标世界（空值自动选择）")
    auto_select_world: bool = Field(default=True, description="是否自动选择合适的世界")
    
    # 🔍 消息过滤配置
    filter_system_messages: bool = Field(default=True, description="是否过滤系统消息")
    filter_qq_messages: bool = Field(default=True, description="是否过滤来自QQ的消息（避免循环）")
    blocked_words: List[str] = Field(default_factory=list, description="屏蔽词列表")
    blocked_players: List[str] = Field(default_factory=list, description="屏蔽玩家列表")
    
    # 📝 消息格式配置
    qq_to_game_template: str = Field(default="[QQ] {username}: {message}", description="QQ到游戏的消息模板")
    game_to_qq_template: str = Field(default="🎮 [{cluster}] {player}: {message}", description="游戏到QQ的消息模板")
    system_message_template: str = Field(default="📢 [{cluster}] 系统: {message}", description="系统消息模板")
    
    # ⚡ 性能优化配置
    enable_message_cache: bool = Field(default=True, description="是否启用消息缓存")
    cache_duration: int = Field(default=300, description="消息缓存持续时间（秒）")
    max_batch_size: int = Field(default=5, description="批量消息处理大小")
    dedupe_window: int = Field(default=60, description="消息去重时间窗口（秒）")
    
    # 🔔 通知配置
    notify_connection_status: bool = Field(default=True, description="是否通知连接状态变化")
    notify_new_users: bool = Field(default=True, description="是否通知新用户加入互通")
    show_player_join_leave: bool = Field(default=False, description="是否显示玩家进出服务器消息")
    
    @validator('default_chat_mode')
    def validate_chat_mode(cls, v):
        if v not in ['private', 'group']:
            raise ValueError("聊天模式必须是 'private' 或 'group'")
        return v
    
    @validator('sync_interval')
    def validate_sync_interval(cls, v):
        if v < 1.0 or v > 60.0:
            raise ValueError("同步间隔必须在1-60秒之间")
        return v
    
    def validate_self(self) -> List[str]:
        """验证消息配置"""
        errors = []
        
        if not self.allow_group_chat and not self.allow_private_chat:
            errors.append("至少需要启用一种聊天模式（群聊或私聊）")
        
        if self.max_message_length < 10:
            errors.append("消息长度限制不能少于10个字符")
        
        if self.cache_duration < 60:
            errors.append("缓存持续时间建议不少于60秒")
        
        return errors

class LoggingConfig(ConfigSection):
    """日志配置"""
    
    # 基础配置
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="text", description="日志格式 (text/json)")
    
    # 文件配置
    log_to_file: bool = Field(default=True, description="是否记录到文件")
    log_file_path: str = Field(default="./logs/app.log", description="日志文件路径")
    max_file_size: int = Field(default=10485760, description="日志文件最大大小（字节）")
    backup_count: int = Field(default=5, description="日志文件备份数量")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ['text', 'json']:
            raise ValueError("日志格式必须是: text 或 json")
        return v

class Config(BaseModel):
    """
    主配置类
    
    配置文件会自动生成为 app_config.json，您可以直接编辑该文件或通过代码修改配置
    """
    
    # 📋 主要配置（需要用户设置）
    dmp: DMPConfig = Field(default_factory=DMPConfig, description="DMP API配置")
    bot: BotConfig = Field(default_factory=BotConfig, description="机器人配置")
    
    # 🔧 功能配置（可选设置）
    message: MessageConfig = Field(default_factory=MessageConfig, description="消息互通配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="缓存配置")
    
    # 📊 系统信息（自动管理）
    version: str = Field(default="1.0.0", description="配置版本")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="最后更新时间")
    
    # 兼容性属性（保持向后兼容）
    @property
    def dmp_base_url(self) -> str:
        return self.dmp.base_url
    
    @property
    def dmp_token(self) -> str:
        return self.dmp.token
    
    @property
    def default_cluster(self) -> str:
        # 兼容性：返回空字符串，实际使用中由集群管理器动态获取
        return ""
    
    def validate_all(self) -> Dict[str, List[str]]:
        """验证所有配置节"""
        errors = {}
        
        sections = {
            'dmp': self.dmp,
            'bot': self.bot,
            'cache': self.cache,
            'message': self.message,
            'logging': self.logging
        }
        
        for section_name, section in sections.items():
            section_errors = section.validate_self()
            if section_errors:
                errors[section_name] = section_errors
        
        return errors
    
    async def get_first_cluster(self) -> str:
        """获取第一个可用的集群名称（兼容性方法）"""
        try:
            headers = {
                "Authorization": self.dmp.token,
                "X-I18n-Lang": "zh"
            }
            
            async with httpx.AsyncClient(timeout=self.dmp.timeout) as client:
                response = await client.get(f"{self.dmp.base_url}/setting/clusters", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") == 200:
                    clusters = data.get("data", [])
                    if clusters:
                        return clusters[0].get("clusterName", "Master")
                
                return "Master"
        except Exception:
            return "Master"

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.backup_file = BACKUP_CONFIG_FILE
        self.logger = get_logger(__name__)
        
        self._config: Optional[Config] = None
        self._observers: List[Callable[[Config], None]] = []
        self._file_observer: Optional[Observer] = None
        self._lock = threading.Lock()
        
        # 初始化配置
        self._load_config()
        
        # 启动文件监听
        self._start_file_watcher()
    
    def _start_file_watcher(self):
        """启动配置文件监听器"""
        try:
            self._file_observer = Observer()
            event_handler = ConfigChangeHandler(self)
            self._file_observer.schedule(
                event_handler, 
                str(self.config_file.parent), 
                recursive=False
            )
            self._file_observer.start()
            self.logger.info("配置文件监听器启动成功", category=LogCategory.SYSTEM)
        except Exception as e:
            self.logger.error(f"启动配置文件监听器失败: {e}", category=LogCategory.SYSTEM)
    
    def _load_config(self):
        """加载配置"""
        with self._lock:
            try:
                if self.config_file.exists():
                    # 从文件加载
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._config = Config(**data)
                    self.logger.info(f"从文件加载配置成功: {self.config_file}", category=LogCategory.SYSTEM)
                else:
                    # 尝试从模板创建配置文件
                    if self._create_config_from_template():
                        # 重新加载刚创建的配置
                        with open(self.config_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        self._config = Config(**data)
                        self.logger.info(f"从模板创建配置文件成功: {self.config_file}", category=LogCategory.SYSTEM)
                    else:
                        # 创建默认配置
                        self._config = Config()
                        self._save_config()
                        self.logger.info("创建默认配置文件", category=LogCategory.SYSTEM)
                
                # 验证配置
                errors = self._config.validate_all()
                if errors:
                    error_msg = "配置验证失败:\n"
                    for section, section_errors in errors.items():
                        error_msg += f"  {section}: {', '.join(section_errors)}\n"
                    self.logger.warning(error_msg, category=LogCategory.SYSTEM)
                
            except Exception as e:
                self.logger.error(f"加载配置失败: {e}", category=LogCategory.SYSTEM)
                if self.backup_file.exists():
                    try:
                        # 尝试从备份恢复
                        with open(self.backup_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        self._config = Config(**data)
                        self.logger.info("从备份配置恢复成功", category=LogCategory.SYSTEM)
                    except Exception as backup_error:
                        self.logger.error(f"从备份恢复失败: {backup_error}", category=LogCategory.SYSTEM)
                        self._config = Config()
                else:
                    self._config = Config()
    
    def _create_config_from_template(self) -> bool:
        """从模板创建配置文件"""
        try:
            if TEMPLATE_CONFIG_FILE.exists():
                # 复制模板文件到配置文件
                import shutil
                shutil.copy2(TEMPLATE_CONFIG_FILE, self.config_file)
                
                # 显示配置指南
                print("\n" + "="*60)
                print("🎉 配置文件已生成！")
                print("="*60)
                print(f"📁 配置文件位置: {self.config_file}")
                print("\n📋 接下来请按照以下步骤配置：")
                print("1. 停止机器人 (Ctrl+C)")
                print("2. 编辑配置文件，修改必要设置：")
                print("   - dmp.base_url: 您的DMP服务器地址")
                print("   - dmp.token: 您的DMP访问令牌")
                print("   - bot.superusers: 您的QQ号")
                print("3. 保存文件并重新启动机器人")
                print("\n💡 提示：配置支持热重载，保存后1秒内自动生效")
                print("="*60)
                
                return True
            else:
                self.logger.warning("配置模板文件不存在", category=LogCategory.SYSTEM)
                return False
        except Exception as e:
            self.logger.error(f"从模板创建配置文件失败: {e}", category=LogCategory.SYSTEM)
            return False
    
    def _save_config(self):
        """保存配置"""
        try:
            # 创建备份
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, self.backup_file)
            
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 更新时间戳
            self._config.last_updated = datetime.now().isoformat()
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config.dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info("配置保存成功", category=LogCategory.SYSTEM)
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}", category=LogCategory.SYSTEM)
            raise ConfigReloadError(f"保存配置失败: {e}")
    
    def _reload_config(self):
        """重载配置"""
        try:
            old_config = self._config
            self._load_config()
            
            # 通知观察者
            for observer in self._observers:
                try:
                    observer(self._config)
                except Exception as e:
                    self.logger.error(f"配置变更通知失败: {e}", category=LogCategory.SYSTEM)
            
            self.logger.info("配置热重载成功", category=LogCategory.SYSTEM)
            
        except Exception as e:
            self.logger.error(f"配置热重载失败: {e}", category=LogCategory.SYSTEM)
    
    def get_config(self) -> Config:
        """获取当前配置"""
        if self._config is None:
            self._load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            with self._lock:
                # 创建新配置实例
                current_data = self._config.dict()
                
                # 递归更新配置
                def update_dict(target: dict, source: dict):
                    for key, value in source.items():
                        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                            update_dict(target[key], value)
                        else:
                            target[key] = value
                
                update_dict(current_data, updates)
                
                # 验证新配置
                new_config = Config(**current_data)
                errors = new_config.validate_all()
                if errors:
                    error_msg = "配置验证失败: " + str(errors)
                    raise ConfigValidationError(error_msg)
                
                # 应用新配置
                self._config = new_config
                self._save_config()
                
                # 通知观察者
                for observer in self._observers:
                    try:
                        observer(self._config)
                    except Exception as e:
                        self.logger.error(f"配置变更通知失败: {e}", category=LogCategory.SYSTEM)
                
                self.logger.info("配置更新成功", category=LogCategory.SYSTEM)
                return True
                
        except Exception as e:
            self.logger.error(f"配置更新失败: {e}", category=LogCategory.SYSTEM)
            return False
    
    def add_observer(self, observer: Callable[[Config], None]):
        """添加配置变更观察者"""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable[[Config], None]):
        """移除配置变更观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def validate_config(self) -> Dict[str, List[str]]:
        """验证当前配置"""
        return self._config.validate_all() if self._config else {}
    
    async def test_dmp_connection(self) -> bool:
        """测试DMP连接"""
        try:
            config = self.get_config()
            headers = {
                "Authorization": config.dmp.token,
                "X-I18n-Lang": "zh"
            }
            
            async with httpx.AsyncClient(timeout=config.dmp.timeout) as client:
                response = await client.get(f"{config.dmp.base_url}/setting/clusters", headers=headers)
                response.raise_for_status()
                return True
                
        except Exception as e:
            self.logger.error(f"DMP连接测试失败: {e}", category=LogCategory.SYSTEM)
            return False
    
    def shutdown(self):
        """关闭配置管理器"""
        if self._file_observer:
            self._file_observer.stop()
            self._file_observer.join()
        self.logger.info("配置管理器已关闭", category=LogCategory.SYSTEM)

# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> Config:
    """获取当前配置（兼容性函数）"""
    return get_config_manager().get_config()

# 兼容性函数
def get_plugin_config(config_class):
    """兼容NoneBot的get_plugin_config"""
    return get_config()