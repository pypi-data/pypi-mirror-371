"""
缓存管理命令

提供缓存查看、清除、统计等管理功能的QQ命令
"""

from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.log import logger
from .cache_manager import cache_manager


# 创建缓存管理命令
cache_status_cmd = on_command("缓存状态", permission=SUPERUSER, priority=1, block=True)
cache_clear_cmd = on_command("清理缓存", permission=SUPERUSER, priority=1, block=True)
cache_stats_cmd = on_command("缓存统计", permission=SUPERUSER, priority=1, block=True)


@cache_status_cmd.handle()
async def handle_cache_status(bot: Bot, event: Event):
    """查看缓存状态"""
    try:
        stats = cache_manager.get_stats()
        
        response = "📊 缓存系统状态:\n"
        response += f"🧠 内存缓存大小: {stats['memory_cache_size']}\n"
        response += f"📈 总请求数: {stats['total_requests']}\n"
        response += f"🎯 总命中率: {stats['hit_rate']:.2%}\n"
        response += f"🧠 内存命中率: {stats['memory_hit_rate']:.2%}\n"
        response += f"📄 文件命中率: {stats['file_hit_rate']:.2%}\n"
        response += f"❌ 未命中数: {stats['misses']}\n\n"
        
        # 显示当前缓存的键
        if stats['memory_cache_keys']:
            response += f"🔑 内存缓存键 (前10个):\n"
            for key in stats['memory_cache_keys'][:10]:
                response += f"  • {key[:50]}...\n"
        else:
            response += "🔑 内存缓存为空\n"
        
        await bot.send(event, response)
        
    except Exception as e:
        error_msg = f"❌ 获取缓存状态失败: {str(e)}"
        logger.error(error_msg)
        await bot.send(event, error_msg)


@cache_clear_cmd.handle()
async def handle_cache_clear(bot: Bot, event: Event):
    """清理缓存命令"""
    try:
        # 获取清理前统计
        old_stats = cache_manager.get_stats()
        old_memory_size = old_stats['memory_cache_size']
        
        # 清理所有缓存
        await cache_manager.clear()
        
        response = "🗑️ 缓存清理完成!\n"
        response += f"清理前内存缓存大小: {old_memory_size}\n"
        response += f"清理后内存缓存大小: 0\n"
        response += "📄 所有文件缓存已清空\n"
        response += "🔄 缓存统计已重置\n"
        
        await bot.send(event, response)
        logger.info("🗑️ 管理员清理了所有缓存")
        
    except Exception as e:
        error_msg = f"❌ 清理缓存失败: {str(e)}"
        logger.error(error_msg)
        await bot.send(event, error_msg)


@cache_stats_cmd.handle() 
async def handle_cache_stats(bot: Bot, event: Event):
    """查看详细缓存统计"""
    try:
        stats = cache_manager.get_stats()
        
        response = "📈 详细缓存统计:\n\n"
        
        # 性能指标
        response += "🎯 性能指标:\n"
        response += f"  总请求数: {stats['total_requests']}\n"
        response += f"  内存命中: {stats['memory_hits']}\n"
        response += f"  文件命中: {stats['file_hits']}\n"
        response += f"  缓存未命中: {stats['misses']}\n\n"
        
        # 命中率分析
        if stats['total_requests'] > 0:
            total_hits = stats['memory_hits'] + stats['file_hits']
            response += "📊 命中率分析:\n"
            response += f"  总命中率: {stats['hit_rate']:.2%}\n"
            response += f"  内存命中率: {stats['memory_hit_rate']:.2%}\n"
            response += f"  文件命中率: {stats['file_hit_rate']:.2%}\n"
            response += f"  缓存效率: {total_hits/stats['total_requests']:.2%}\n\n"
        
        # 缓存容量
        response += "💾 缓存容量:\n"
        response += f"  内存缓存: {stats['memory_cache_size']} 项\n"
        response += f"  内存缓存键: {len(stats['memory_cache_keys'])}\n\n"
        
        # 性能建议
        if stats['total_requests'] > 10:
            if stats['hit_rate'] < 0.3:
                response += "⚠️ 建议: 命中率较低，考虑调整TTL设置\n"
            elif stats['hit_rate'] > 0.8:
                response += "✅ 优秀: 缓存命中率很高，性能良好\n"
            else:
                response += "👍 良好: 缓存命中率正常\n"
        
        await bot.send(event, response)
        
    except Exception as e:
        error_msg = f"❌ 获取缓存统计失败: {str(e)}"
        logger.error(error_msg)
        await bot.send(event, error_msg)


# 缓存类型清理命令
api_cache_clear_cmd = on_command("清理API缓存", permission=SUPERUSER, priority=1, block=True)
db_cache_clear_cmd = on_command("清理数据库缓存", permission=SUPERUSER, priority=1, block=True) 
config_cache_clear_cmd = on_command("清理配置缓存", permission=SUPERUSER, priority=1, block=True)


@api_cache_clear_cmd.handle()
async def handle_api_cache_clear(bot: Bot, event: Event):
    """清理API缓存"""
    try:
        await cache_manager.clear("api")
        await bot.send(event, "🗑️ API缓存已清理完成")
        logger.info("🗑️ 管理员清理了API缓存")
    except Exception as e:
        await bot.send(event, f"❌ 清理API缓存失败: {str(e)}")


@db_cache_clear_cmd.handle()
async def handle_db_cache_clear(bot: Bot, event: Event):
    """清理数据库缓存"""
    try:
        await cache_manager.clear("db")
        await bot.send(event, "🗑️ 数据库缓存已清理完成")
        logger.info("🗑️ 管理员清理了数据库缓存")
    except Exception as e:
        await bot.send(event, f"❌ 清理数据库缓存失败: {str(e)}")


@config_cache_clear_cmd.handle()
async def handle_config_cache_clear(bot: Bot, event: Event):
    """清理配置缓存"""
    try:
        await cache_manager.clear("config")
        await bot.send(event, "🗑️ 配置缓存已清理完成")
        logger.info("🗑️ 管理员清理了配置缓存")
    except Exception as e:
        await bot.send(event, f"❌ 清理配置缓存失败: {str(e)}")


# 帮助命令
cache_help_cmd = on_command("缓存帮助", permission=SUPERUSER, priority=1, block=True)


@cache_help_cmd.handle()
async def handle_cache_help(bot: Bot, event: Event):
    """缓存管理帮助"""
    help_text = """📚 缓存管理命令帮助

🔍 查看命令:
• @bot 缓存状态 - 查看当前缓存状态
• @bot 缓存统计 - 查看详细统计信息

🗑️ 清理命令:
• @bot 清理缓存 - 清理所有缓存
• @bot 清理API缓存 - 只清理API调用缓存
• @bot 清理数据库缓存 - 只清理数据库查询缓存
• @bot 清理配置缓存 - 只清理配置相关缓存

ℹ️ 说明:
• 缓存采用三级存储: 内存 → 文件 → 源数据
• API缓存TTL较短，适合实时数据
• 配置缓存TTL较长，适合稳定配置
• 数据库缓存介于两者之间

⚠️ 注意: 这些命令只有超级用户可以使用"""

    await bot.send(event, help_text)
