"""元素操作关键字

提供元素点击、输入、选择等交互操作关键字。
充分利用Playwright的智能等待机制。
"""

import logging
import time
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

logger = logging.getLogger(__name__)


def _get_current_locator() -> ElementLocator:
    """获取当前页面的元素定位器"""
    page = browser_manager.get_current_page()
    return ElementLocator(page)


@keyword_manager.register('点击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
    {'name': '强制点击', 'mapping': 'force', 
     'description': '是否强制点击（忽略元素状态检查）', 'default': False},
    {'name': '索引', 'mapping': 'index', 
     'description': '元素索引（当有多个匹配元素时）'},
    {'name': '可见性', 'mapping': 'visible_only', 
     'description': '是否只点击可见元素', 'default': False},
], category='UI/交互', tags=['点击', '交互'])
def click_element(**kwargs):
    """点击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间
        force: 是否强制点击
        index: 元素索引（当有多个匹配元素时）
        visible_only: 是否只点击可见元素

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')
    force = kwargs.get('force', False)
    index = kwargs.get('index')
    visible_only = kwargs.get('visible_only', False)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"点击元素: {selector}"):
        try:
            locator = _get_current_locator()

            # 根据参数选择合适的定位方式
            if visible_only:
                element = locator.locate_by_visible(selector)
            else:
                element = locator.locate(selector)

            # 如果指定了索引，使用nth定位
            if index is not None:
                element = element.nth(index)

            # 使用Playwright的智能等待机制
            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.click(force=force, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"强制点击: {force}\n"
                f"索引: {index if index is not None else '无'}\n"
                f"仅可见元素: {visible_only}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"元素点击成功: {selector} "
                f"(索引: {index}, 可见性: {visible_only})"
            )

            # 直接返回成功状态
            return True

        except Exception as e:
            error_msg = f"元素点击失败: {str(e)}"
            if "timeout" in str(e).lower():
                error_msg += (f"\n可能原因: 1) 元素不存在或不可见 "
                              f"2) 页面加载缓慢 3) 定位器 '{selector}' 不正确")
            elif "detached" in str(e).lower():
                error_msg += "\n可能原因: 页面结构发生变化，元素已被移除"
            
            logger.error(error_msg)
            allure.attach(
                f"错误信息: {error_msg}",
                name="元素点击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise Exception(error_msg)


@keyword_manager.register('双击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['双击', '交互'])
def double_click_element(**kwargs):
    """双击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"双击元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.dblclick(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素双击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素双击成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素双击失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素双击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('右键点击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['右键', '交互'])
def right_click_element(**kwargs):
    """右键点击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"右键点击元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.click(button="right", timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素右键点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素右键点击成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素右键点击失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素右键点击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('输入文本', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '文本', 'mapping': 'text', 'description': '要输入的文本内容'},
    {'name': '清空输入框', 'mapping': 'clear', 
     'description': '输入前是否清空输入框', 'default': True},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['输入', '文本'])
def input_text(**kwargs):
    """输入文本

    Args:
        selector: 元素定位器
        text: 要输入的文本
        clear: 是否清空输入框
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    text = kwargs.get('text', '')
    clear = kwargs.get('clear', True)
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"输入文本: {selector} -> {text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000

            if clear:
                # 使用fill方法，它会自动清空并填入内容
                element.fill(text, timeout=timeout_ms)
            else:
                # 不清空的情况下，先点击获得焦点，然后输入
                element.click(timeout=timeout_ms)
                element.type(text, delay=50, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"输入文本: {text}\n"
                f"清空输入框: {clear}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本输入信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本输入成功: {selector} -> {text}")

            # 直接返回输入的文本
            return text

        except Exception as e:
            logger.error(f"文本输入失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本输入失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('清空文本', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['清空', '文本'])
def clear_text(**kwargs):
    """清空文本

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"清空文本: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.clear(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本清空信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本清空成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"文本清空失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本清空失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('勾选复选框', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '复选框元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['复选框', '勾选'])
def check_checkbox(**kwargs):
    """勾选复选框

    Args:
        selector: 复选框定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"勾选复选框: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.check(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="复选框勾选信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"复选框勾选成功: {selector}")

            # 直接返回成功状态
            return True
        except Exception as e:
            logger.error(f"复选框勾选失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="复选框勾选失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('取消勾选复选框', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '复选框元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['复选框', '取消'])
def uncheck_checkbox(**kwargs):
    """取消勾选复选框

    Args:
        selector: 复选框定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"取消勾选复选框: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.uncheck(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="复选框取消勾选信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"复选框取消勾选成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"复选框取消勾选失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="复选框取消勾选失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('设置复选框状态', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '复选框元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '选中状态', 'mapping': 'checked', 
     'description': '是否选中复选框', 'default': True},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['复选框', '设置'])
def set_checkbox(**kwargs):
    """设置复选框状态

    Args:
        selector: 复选框定位器
        checked: 是否选中
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    checked = kwargs.get('checked', True)
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"设置复选框状态: {selector} -> {checked}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.set_checked(checked, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"选中状态: {checked}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="复选框状态设置信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"复选框状态设置成功: {selector} -> {checked}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"复选框状态设置失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="复选框状态设置失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('选择单选框', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '单选框元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['单选框', '选择'])
def select_radio(**kwargs):
    """选择单选框

    Args:
        selector: 单选框定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"选择单选框: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.check(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="单选框选择信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"单选框选择成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"单选框选择失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="单选框选择失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('选择下拉选项', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '下拉框元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '选项值', 'mapping': 'value', 
     'description': '要选择的选项值'},
    {'name': '选项标签', 'mapping': 'label', 
     'description': '要选择的选项标签文本'},
    {'name': '选项索引', 'mapping': 'index', 
     'description': '要选择的选项索引（从0开始）'},
    {'name': '多选', 'mapping': 'multiple', 
     'description': '是否多选（值用逗号分隔）', 'default': False},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['下拉框', '选择'])
def select_option(**kwargs):
    """选择下拉框选项

    Args:
        selector: 下拉框定位器
        value: 选项值
        label: 选项标签
        index: 选项索引
        multiple: 是否多选
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    value = kwargs.get('value')
    label = kwargs.get('label')
    index = kwargs.get('index')
    multiple = kwargs.get('multiple', False)
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    if not any([value, label, index is not None]):
        raise ValueError("必须提供选项值、标签或索引中的一个")

    with allure.step(f"选择下拉选项: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000

            # 根据提供的参数选择选项
            if value is not None:
                if multiple and isinstance(value, str):
                    # 多选情况，将逗号分隔的字符串转换为列表
                    values = [v.strip() for v in value.split(',')]
                    element.select_option(values, timeout=timeout_ms)
                else:
                    element.select_option(value, timeout=timeout_ms)
            elif label is not None:
                if multiple and isinstance(label, str):
                    # 多选情况，将逗号分隔的字符串转换为列表
                    labels = [
                        label_item.strip() 
                        for label_item in label.split(',')
                    ]
                    element.select_option(label=labels, timeout=timeout_ms)
                else:
                    element.select_option(label=label, timeout=timeout_ms)
            elif index is not None:
                element.select_option(index=index, timeout=timeout_ms)

            selection_info = []
            if value:
                selection_info.append(f"选项值: {value}")
            if label:
                selection_info.append(f"选项标签: {label}")
            if index is not None:
                selection_info.append(f"选项索引: {index}")

            allure.attach(
                f"定位器: {selector}\n"
                f"{'; '.join(selection_info)}\n"
                f"多选: {multiple}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="下拉选项选择信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"下拉选项选择成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"下拉选项选择失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="下拉选项选择失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('逐字符输入', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '文本', 'mapping': 'text', 'description': '要输入的文本内容'},
    {'name': '延迟', 'mapping': 'delay', 
     'description': '字符间延迟时间（毫秒）', 'default': 100},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['输入', '逐字符'])
def type_text(**kwargs):
    """逐字符输入文本（适用于有特殊键盘处理的情况）

    Args:
        selector: 元素定位器
        text: 要输入的文本
        delay: 字符间延迟
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    text = kwargs.get('text', '')
    delay = kwargs.get('delay', 100)
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"逐字符输入: {selector} -> {text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.press_sequentially(text, delay=delay, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"输入文本: {text}\n"
                f"字符延迟: {delay}毫秒\n"
                f"超时时间: {timeout or '默认'}秒",
                name="逐字符输入信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"逐字符输入成功: {selector} -> {text}")

            # 直接返回输入的文本
            return text

        except Exception as e:
            logger.error(f"逐字符输入失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="逐字符输入失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('按键操作', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '按键', 'mapping': 'key', 
     'description': '按键名称或组合键（如Enter、Ctrl+A等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['按键', '键盘'])
def press_key(**kwargs):
    """按键操作

    Args:
        selector: 元素定位器
        key: 按键名称或组合键
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    key = kwargs.get('key')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not key:
        raise ValueError("按键参数不能为空")

    with allure.step(f"按键操作: {selector} -> {key}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.press(key, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"按键: {key}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="按键操作信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"按键操作成功: {selector} -> {key}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"按键操作失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="按键操作失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('悬停元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['悬停', '鼠标'])
def hover_element(**kwargs):
    """悬停在元素上

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"悬停元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.hover(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素悬停信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素悬停成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素悬停失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素悬停失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('拖拽元素', [
    {'name': '源定位器', 'mapping': 'source_selector', 
     'description': '要拖拽的源元素定位器'},
    {'name': '目标定位器', 'mapping': 'target_selector', 
     'description': '拖拽目标元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['拖拽', '鼠标'])
def drag_element(**kwargs):
    """拖拽元素到另一个元素

    Args:
        source_selector: 源元素定位器
        target_selector: 目标元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    source_selector = kwargs.get('source_selector')
    target_selector = kwargs.get('target_selector')
    timeout = kwargs.get('timeout')

    if not source_selector:
        raise ValueError("源定位器参数不能为空")
    if not target_selector:
        raise ValueError("目标定位器参数不能为空")

    with allure.step(f"拖拽元素: {source_selector} -> {target_selector}"):
        try:
            locator = _get_current_locator()
            source_element = locator.locate(source_selector)
            target_element = locator.locate(target_selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            source_element.drag_to(target_element, timeout=timeout_ms)

            allure.attach(
                f"源定位器: {source_selector}\n"
                f"目标定位器: {target_selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素拖拽信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素拖拽成功: {source_selector} -> {target_selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素拖拽失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素拖拽失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('聚焦元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['聚焦'])
def focus_element(**kwargs):
    """聚焦元素

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"聚焦元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.focus(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素聚焦信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素聚焦成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素聚焦失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素聚焦失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('滚动元素到视野', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
    {'name': '滚动容器', 'mapping': 'scroll_container', 
     'description': '可选，指定滚动容器的定位器'},
    {'name': '像素数', 'mapping': 'scroll_step', 
     'description': '可选，每次滚动的像素数', 'default': 10},
    {'name': '最大滚动次数', 'mapping': 'max_attempts', 
     'description': '可选，最大滚动次数', 'default': 20},
], category='UI/交互', tags=['滚动', '视野'])
def scroll_into_view(**kwargs):
    """滚动元素到视野中

    Args:
        selector (str): 元素定位器（必填）
        timeout (int): 超时时间（秒）
        scroll_container (str): 可选，滚动容器的定位器
        scroll_step (int): 每次滚动的像素数
        max_attempts (int): 最大滚动次数

    Returns:
        bool: 是否滚动成功

    Raises:
        ValueError: 当必要参数缺失时
        Exception: 当滚动操作失败时
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    scroll_container = kwargs.get('scroll_container')
    scroll_step = kwargs.get('scroll_step', 10)
    max_attempts = kwargs.get('max_attempts', 20)

    with allure.step(f"滚动元素到视野: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            page = browser_manager.get_current_page()

            if scroll_container:
                # 容器内滚动模式
                scroll_container_element = locator.locate(scroll_container)
                
                for attempt in range(1, max_attempts + 1):
                    if element.is_visible():
                        logger.info(f"元素已在视野中(第{attempt}次检查)")
                        return True
                    
                    # 滚动容器
                    scroll_container_element.hover(timeout=timeout_ms)
                    page.mouse.wheel(0, scroll_step)
                    logger.debug(f"滚动容器[{scroll_container}] 第{attempt}次滚动")
                    time.sleep(0.5)
                
                # 达到最大尝试次数仍未找到
                raise TimeoutError(f"经过{max_attempts}次滚动后元素仍未可见")
            else:
                # 直接滚动到元素
                element.scroll_into_view_if_needed(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素滚动信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素滚动成功: {selector}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"元素滚动失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素滚动失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('上传文件', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '文件输入框元素定位器'},
    {'name': '文件路径', 'mapping': 'file_paths', 
     'description': '要上传的文件路径（单个文件或多个文件用逗号分隔）'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/交互', tags=['上传', '文件'])
def upload_files(**kwargs):
    """上传文件

    Args:
        selector: 文件输入框定位器
        file_paths: 文件路径（单个或多个，用逗号分隔）
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    file_paths = kwargs.get('file_paths')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not file_paths:
        raise ValueError("文件路径参数不能为空")

    # 处理文件路径，支持单个文件或多个文件
    if isinstance(file_paths, str):
        if ',' in file_paths:
            paths = [path.strip() for path in file_paths.split(',')]
        else:
            paths = [file_paths]
    else:
        paths = file_paths

    with allure.step(f"上传文件: {selector} -> {paths}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.set_input_files(paths, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"文件路径: {', '.join(paths)}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文件上传信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文件上传成功: {selector} -> {paths}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文件上传失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

@keyword_manager.register('检查导航栏是否为空', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '容器定位器（CSS选择器、XPath等）'},
    {'name': '内容类型', 'mapping': 'content_type', 
     'description': '内容类型：auto-自动检测，menu-菜单，page_tree-页面树', 'default': 'auto'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/检查', tags=['导航栏', '空检查', '菜单', '页面树'])
def check_navigation_empty(**kwargs):
    """检查导航栏是否为空（支持菜单和页面树）

    Args:
        selector: 容器定位器
        content_type: 内容类型（auto/menu/page_tree）
        timeout: 超时时间

    Returns:
        bool: 如果导航栏为空返回True，否则返回False
    """
    selector = kwargs.get('selector')
    content_type = kwargs.get('content_type', 'auto')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    if content_type not in ['auto', 'menu', 'page_tree']:
        raise ValueError("内容类型必须是 'auto', 'menu' 或 'page_tree'")

    with allure.step(f"检查导航栏是否为空: {selector}"):
        try:
            # 调试日志：函数开始执行
            logger.debug(f"[导航栏检查] 开始执行函数，参数: selector={selector}, content_type={content_type}, timeout={timeout}")
            
            locator = _get_current_locator()
            container = locator.locate(selector)
            
            # 调试日志：容器定位成功
            logger.debug(f"[导航栏检查] 成功定位容器: {selector}")

            timeout_ms = int(timeout * 1000) if timeout else 30000
            
            # 等待容器可见
            logger.debug(f"[导航栏检查] 等待容器可见，超时: {timeout_ms}ms")
            container.wait_for(state='visible', timeout=timeout_ms)
            logger.debug(f"[导航栏检查] 容器可见")
            
            # 自动检测内容类型
            if content_type == 'auto':
                logger.debug(f"[导航栏检查] 自动检测内容类型")
                
                # 检查是否包含菜单项
                menu_items = container.locator('.ix-menu-item[aria-label]')
                menu_count = menu_items.count()
                logger.debug(f"[导航栏检查] 检测到菜单项数量: {menu_count}")
                
                # 检查是否包含页面树节点
                page_nodes = container.locator('.plugin_pagetree_children_span a')
                page_count = page_nodes.count()
                logger.debug(f"[导航栏检查] 检测到页面树节点数量: {page_count}")
                
                # 根据元素数量决定类型
                if menu_count > 0 and menu_count >= page_count:
                    content_type = 'menu'
                    logger.info(f"[导航栏检查] 自动检测结果：菜单类型，元素数量: {menu_count}")
                elif page_count > 0:
                    content_type = 'page_tree'
                    logger.info(f"[导航栏检查] 自动检测结果：页面树类型，元素数量: {page_count}")
                else:
                    logger.warning(f"[导航栏检查] 自动检测失败：未找到菜单项或页面树节点")
                    # 如果没有找到任何元素，默认使用菜单类型
                    content_type = 'menu'
                    logger.info(f"[导航栏检查] 默认使用菜单类型进行空检查")
            
            # 根据内容类型获取元素和容器
            if content_type == 'menu':
                logger.debug(f"[导航栏检查] 使用菜单容器选择器: .ix-menu-inline")
                submenu_container = container.locator('.ix-menu-inline')
                items = submenu_container.locator('.ix-menu-item[aria-label]')
                content_name = '菜单'
            else:  # page_tree
                logger.debug(f"[导航栏检查] 使用页面树容器选择器")
                submenu_container = container  # 页面树直接使用主容器
                items = container.locator('.plugin_pagetree_children_span a')
                content_name = '页面树'
            
            # 获取元素数量
            item_count = items.count()
            logger.info(f"[导航栏检查] 找到 {item_count} 个{content_name}项")
            
            # 检查容器内容
            inner_html = submenu_container.inner_html()
            
            # 综合判断是否为空
            is_empty = item_count == 0 or not inner_html.strip()
            
            # 创建详细的输出信息
            output_info = f"导航栏检查结果:\n"
            output_info += f"定位器: {selector}\n"
            output_info += f"内容类型: {content_name}\n"
            output_info += f"超时时间: {timeout or '默认'}秒\n"
            output_info += f"元素数量: {item_count}\n"
            output_info += f"容器HTML内容: {inner_html[:100]}{'...' if len(inner_html) > 100 else ''}\n"
            output_info += f"是否为空: {is_empty}\n"
            
            # 添加调试信息
            output_info += f"\n调试信息:\n"
            output_info += f"使用的容器选择器: {'.ix-menu-inline' if content_type == 'menu' else '主容器'}\n"
            output_info += f"使用的项选择器: {'.ix-menu-item[aria-label]' if content_type == 'menu' else '.plugin_pagetree_children_span a'}\n"

            allure.attach(
                output_info,
                name=f"{content_name}空检查结果",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"{content_name}空检查完成: {selector}, 是否为空: {is_empty}")

            # 返回检查结果
            return is_empty

        except Exception as e:
            logger.error(f"导航栏检查失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="导航栏检查失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
@keyword_manager.register('输出导航栏内容', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '容器定位器（CSS选择器、XPath等）'},
    {'name': '内容类型', 'mapping': 'content_type', 
     'description': '内容类型：auto-自动检测，menu-菜单，page_tree-页面树', 'default': 'auto'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '超时时间（秒）', 'default': 30},
], category='UI/检查', tags=['导航栏', '内容输出', '菜单', '页面树'])
def output_navigation_content(**kwargs):
    """输出导航栏内容（支持菜单和页面树）

    Args:
        selector: 容器定位器
        content_type: 内容类型（auto/menu/page_tree）
        timeout: 超时时间

    Returns:
        list: 导航栏列表
    """
    selector = kwargs.get('selector')
    content_type = kwargs.get('content_type', 'auto')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    if content_type not in ['auto', 'menu', 'page_tree']:
        raise ValueError("内容类型必须是 'auto', 'menu' 或 'page_tree'")

    with allure.step(f"输出导航栏内容: {selector}"):
        try:
            # 调试日志：函数开始执行
            logger.debug(f"[导航栏内容输出] 开始执行函数，参数: selector={selector}, content_type={content_type}, timeout={timeout}")
            
            locator = _get_current_locator()
            container = locator.locate(selector)
            
            # 调试日志：容器定位成功
            logger.debug(f"[导航栏内容输出] 成功定位容器: {selector}")

            timeout_ms = int(timeout * 1000) if timeout else 30000
            
            # 等待容器可见
            logger.debug(f"[导航栏内容输出] 等待容器可见，超时: {timeout_ms}ms")
            container.wait_for(state='visible', timeout=timeout_ms)
            logger.debug(f"[导航栏内容输出] 容器可见")
            
            # 自动检测内容类型
            if content_type == 'auto':
                logger.debug(f"[导航栏内容输出] 自动检测内容类型")
                
                # 检查是否包含菜单项
                menu_items = container.locator('.ix-menu-item[aria-label]')
                menu_count = menu_items.count()
                logger.debug(f"[导航栏内容输出] 检测到菜单项数量: {menu_count}")
                
                # 检查是否包含页面树节点
                page_nodes = container.locator('.plugin_pagetree_children_span a')
                page_count = page_nodes.count()
                logger.debug(f"[导航栏内容输出] 检测到页面树节点数量: {page_count}")
                
                # 根据元素数量决定类型
                if menu_count > 0 and menu_count >= page_count:
                    content_type = 'menu'
                    logger.info(f"[导航栏内容输出] 自动检测结果：菜单类型，元素数量: {menu_count}")
                elif page_count > 0:
                    content_type = 'page_tree'
                    logger.info(f"[导航栏内容输出] 自动检测结果：页面树类型，元素数量: {page_count}")
                else:
                    logger.warning(f"[导航栏内容输出] 自动检测失败：未找到菜单项或页面树节点")
                    raise Exception("无法自动检测内容类型，请手动指定")
            
            # 根据内容类型获取元素
            if content_type == 'menu':
                logger.debug(f"[导航栏内容输出] 使用菜单选择器: .ix-menu-item[aria-label]")
                items = container.locator('.ix-menu-item[aria-label]')
                attr_name = 'aria-label'
                content_name = '菜单'
            else:  # page_tree
                logger.debug(f"[导航栏内容输出] 使用页面树选择器: .plugin_pagetree_children_span a")
                items = container.locator('.plugin_pagetree_children_span a')
                attr_name = 'text'  # 页面树使用文本内容
                content_name = '页面树'
            
            # 获取元素数量
            count = items.count()
            logger.info(f"[导航栏内容输出] 找到 {count} 个{content_name}项")
            
            # 收集内容
            content_list = []
            for i in range(count):
                logger.debug(f"[导航栏内容输出] 处理第 {i+1}/{count} 个{content_name}项")
                item = items.nth(i)
                
                try:
                    if attr_name == 'aria-label':
                        # 菜单项：获取 aria-label 属性
                        item_value = item.get_attribute(attr_name)
                    else:
                        # 页面树：获取文本内容
                        item_value = item.inner_text().strip()
                    
                    if item_value:
                        content_list.append(item_value)
                        logger.debug(f"[导航栏内容输出] {content_name}项 {i}: {item_value}")
                    else:
                        logger.warning(f"[导航栏内容输出] {content_name}项 {i}: 值为空")
                        
                except Exception as e:
                    logger.error(f"[导航栏内容输出] 处理{content_name}项 {i} 失败: {str(e)}")
                    continue
            
            # 创建详细的输出信息
            output_info = f"导航栏内容输出结果:\n"
            output_info += f"定位器: {selector}\n"
            output_info += f"内容类型: {content_name}\n"
            output_info += f"超时时间: {timeout or '默认'}秒\n"
            output_info += f"元素数量: {count}\n"
            output_info += f"有效内容数量: {len(content_list)}\n"
            output_info += f"内容列表:\n"
            
            for i, item in enumerate(content_list):
                output_info += f"  {i+1}. {item}\n"
            
            # 添加调试信息
            output_info += f"\n调试信息:\n"
            output_info += f"选择的属性/内容: {attr_name}\n"
            output_info += f"检测到的选择器: {'.ix-menu-item[aria-label]' if content_type == 'menu' else '.plugin_pagetree_children_span a'}\n"

            allure.attach(
                output_info,
                name=f"{content_name}内容输出结果",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"{content_name}内容输出完成: {selector}, 元素数量: {len(content_list)}")

            # 返回内容列表
            return content_list

        except Exception as e:
            logger.error(f"导航栏内容输出失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="导航栏内容输出失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise