import asyncio
from playwright.async_api import async_playwright
from html2text import html2text
import pyperclip
from tenacity import sleep
from os import system


async def url2md(url: str, cdp_endpoint: str, re_md=True, timeout=10000) -> str:
    """
    通过已运行的 Chrome 浏览器获取指定 URL 页面并转换为 Markdown 字符串（异步版本）

    参数:
        url (str): 要获取的目标网页 URL
        cdp_endpoint (str): Chrome DevTools Protocol 端点，默认是 http://127.0.0.1:9222
        re_md (bool): 是否返回 Markdown 格式，为 False 时返回原始 HTML
        proxy (str): 可选参数，代理服务器地址，如 "http://proxy.example.com:8080"
        timeout (int): 页面加载超时时间（毫秒），默认10000ms

    返回:
        str: 转换后的 Markdown 格式字符串或原始 HTML
    """
    content = ""

    # 使用 Playwright 的异步 API
    async with async_playwright() as p:
        # 连接到已运行的 Chrome 浏览器实例
        browser = await p.chromium.connect_over_cdp(cdp_endpoint)
        # 获取或创建浏览器上下文
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()

        # 创建新页面
        page = await context.new_page()
        try:
            # 导航到目标 URL，设置超时时间
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            # sleep(120)
            try:
                # 等待页面基本内容加载
                await page.wait_for_load_state("networkidle", timeout=timeout)
            except Exception as e:
                print(f"网络空闲等待超时，返回已加载内容: {e}")
            # 获取页面 HTML 内容
            html_content = await page.content()
            # 根据参数决定返回格式
            content = html2text(html_content) if re_md else html_content
        except Exception as e:
            print(f"处理页面时出错: {e}")
            # 出错时尝试获取已加载的部分内容
            try:
                html_content = await page.content()
                content = html2text(html_content) if re_md else html_content
            except Exception as fallback_e:
                print(f"获取已加载内容失败: {fallback_e}")
                content = f"页面加载出错: {str(e)}"
        finally:
            # 关闭页面和浏览器连接
            try:
                await page.close()
                await browser.close()
            except:
                pass
    return content


# 示例用法
# if __name__ == "__main__":
#     cdp_endpoint_proxy = 9224
#     cdp_endpoint_direct = "http://127.0.0.1:9225"
#     proxy = "http://127.0.0.1:1080"
#     cmd = 'google-chrome --remote-debugging-port="' + str(cdp_endpoint_proxy) + '" --proxy-server="' + str(
#         proxy) + '" --user-data-dir=/tmp/chrome-profile &'
#     cmd2 = 'google-chrome --remote-debugging-port="' + str(
#         cdp_endpoint_direct) + '" --user-data-dir=/tmp/chrome-profile &'
#     system(cmd)
#     sleep(1)
#     # 确保 Chrome 已以调试模式启动，例如：
#     # google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile
#     target_url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=high+Q+organic+laser"
#     # target_url = "https://scijournals.onlinelibrary.wiley.com/doi/full/10.1002/pi.3173"
#
#
#     markdown_with_proxy = asyncio.run(url2md(
#         target_url,
#         cdp_endpoint="http://127.0.0.1:9224",
#         re_md=True
#     ))
#
#     print(markdown_with_proxy)
#     pyperclip.copy(markdown_with_proxy)