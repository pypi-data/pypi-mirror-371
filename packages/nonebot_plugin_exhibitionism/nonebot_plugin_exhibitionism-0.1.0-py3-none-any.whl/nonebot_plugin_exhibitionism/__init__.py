import inspect
import asyncio
from typing import List, Optional
from typing_extensions import TypedDict, NotRequired

from arclet.alconna import Alconna, Args, CommandMeta, AllParam
from nonebot import require, logger
from nonebot.matcher import Matcher, matchers, current_bot, current_event
from nonebot.adapters import Bot, Event
from nonebot.message import _check_matcher
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.exception import FinishedException
require("nonebot_plugin_alconna")   # noqa
from nonebot_plugin_alconna import AlconnaMatch, Match, on_alconna, AlconnaMatcher, command_manager, UniMessage


from .draw import code_to_jpeg


class HandlerInfo(TypedDict):
    """Handler执行信息结构

    Attributes:
        source: Handler函数的完整源码字符串
    """
    source: NotRequired[Optional[str]]


class SimulationResult(TypedDict):
    """Matcher执行模拟结果

    Attributes:
        executable_handlers: 实际会被执行的Handler信息列表
        error: 模拟过程中的错误信息
    """
    executable_handlers: List[HandlerInfo]
    error: NotRequired[str]


__version__ = "0.1.0"
__author__ = "hlfzsi"

__plugin_meta__ = PluginMetadata(
    name="让我看看！！",
    description="赛博露阴癖, 将你的代码展示到群聊",
    usage="/see [目标指令]",
    type="application",
    homepage="https://github.com/hlfzsi/nonebot-plugin-exhibitionism",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),

    extra={
        "version": __version__,
        "author": __author__,
    }
)


async def simulate_matcher_execution(matcher_class: type[Matcher], bot: Bot, event: Event) -> SimulationResult:
    """
    模拟Matcher的完整执行流程，预测实际会被执行的handler

    Args:
        matcher_class: 要模拟的Matcher类
        bot: Bot实例
        event: Event实例

    Returns:
        包含执行分析结果的字典
    """
    result: SimulationResult = {
        'executable_handlers': []
    }

    handlers = getattr(matcher_class, 'handlers', [])
    if not handlers:
        return result

    try:
        current_handler = handlers[0]
        handler_info: HandlerInfo = {}

        if hasattr(current_handler, 'call'):
            func = current_handler.call
        else:
            func = current_handler

        try:
            if inspect.isfunction(func) or inspect.ismethod(func):
                handler_info['source'] = inspect.getsource(func)
            elif hasattr(func, '__func__'):
                actual_func = func.__func__
                handler_info['source'] = inspect.getsource(actual_func)
        except (OSError, TypeError) as e:
            handler_info['source'] = f"# 无法获取源码: {e}"

        result['executable_handlers'].append(handler_info)

    except Exception as e:
        result['error'] = f"分析错误: {e}"

    return result


async def find_matched_matchers(bot: Bot, event: Event, command: str) -> List[type[Matcher]]:
    matched_list: List[type[Matcher]] = []
    processed_matchers: set[type[Matcher]] = set()

    for alc in command_manager.get_commands():
        try:
            parse_result = alc.parse(command)
            if parse_result.matched:
                if matcher_ref := alc.meta.extra.get("matcher"):
                    if matcher_class := matcher_ref():
                        if matcher_class not in processed_matchers:
                            logger.debug(
                                f"命令 '{command}' [通过 Alconna 解析] 成功匹配到 Matcher: "
                                f"{matcher_class.plugin_name}:{matcher_class.module_name}"
                            )
                            matched_list.append(matcher_class)
                            processed_matchers.add(matcher_class)
        except Exception as e:
            logger.trace(f"Alconna 解析命令 '{command}' 时出错: {e}")

    try:
        ConcreteMessage = event.get_message().__class__
        new_message = ConcreteMessage(command)
        update_fields = {"message": new_message,
                         "raw_message": str(new_message)}
        new_event = event.model_copy(update=update_fields)
    except Exception:
        return matched_list

    for priority in sorted(matchers.keys()):
        for matcher_class in matchers[priority]:
            if matcher_class in processed_matchers or issubclass(matcher_class, AlconnaMatcher):
                continue

            state = {}
            bot_token = current_bot.set(bot)
            event_token = current_event.set(new_event)
            is_match = False
            try:
                is_match = await _check_matcher(
                    Matcher=matcher_class, bot=bot, event=new_event, state=state,
                    stack=None, dependency_cache={}
                )
            except Exception as e:
                logger.trace(
                    f"模拟检查 Matcher '{matcher_class.plugin_name}:{matcher_class.module_name}' 时出错: {e}")
            finally:
                current_bot.reset(bot_token)
                current_event.reset(event_token)

            if is_match:
                logger.debug(
                    f"命令 '{command}' [通过模拟检查] 成功匹配到 Matcher: "
                    f"{matcher_class.plugin_name}:{matcher_class.module_name}"
                )
                if matcher_class not in processed_matchers:
                    matched_list.append(matcher_class)
                    processed_matchers.add(matcher_class)

    return matched_list


see_see = on_alconna(
    Alconna(
        "/see",
        Args["target_cmd", AllParam],
        meta=CommandMeta(description="让我看看")
    ),
)


@see_see.handle()
async def see(bot: Bot, event: Event, target_cmd: Match[tuple] = AlconnaMatch("target_cmd")):
    target_cmd_tuple = target_cmd.result or ()
    target_cmd_str = " ".join(map(str, target_cmd_tuple)).strip()
    found_matchers = await find_matched_matchers(bot, event, target_cmd_str)
    target_matcher = found_matchers[0] if found_matchers else None
    if not target_matcher:
        await see_see.finish("没有找到对应的处理器，请检查输入。")

    simulation_result = await simulate_matcher_execution(target_matcher, bot, event)

    if 'error' in simulation_result:
        await see_see.finish(f"分析处理器时出错: {simulation_result['error']}")

    if simulation_result['executable_handlers']:
        first_handler = simulation_result['executable_handlers'][0]

        if first_handler.get('source'):
            source = first_handler.get('source')
            if isinstance(source, str) and not source.startswith('#'):
                try:
                    image_data = await asyncio.to_thread(code_to_jpeg, source)

                    await see_see.finish(UniMessage().image(raw=image_data))

                except FinishedException:
                    raise
                except Exception as e:
                    await see_see.finish(f"生成源码图片失败: {e}")
            else:
                await see_see.finish("无法获取有效源码")
        else:
            await see_see.finish("找不到源码")
    else:
        await see_see.finish("没有找到会执行的handler")
