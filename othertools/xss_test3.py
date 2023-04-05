import requests
from lxml import html
import asyncio
from pyppeteer import launch




def send_request():

    # 发送包含 XSS 代码的 POST 请求
    data = {'name': '<script>alert(1)</script>'}
    url='http://127.0.0.1/DVWA/vulnerabilities/xss_r/'
    response = requests.post(url, data=data, timeout=30)
    print(response.text)


    # 判断是否触发了alert
    soup = html.fromstring(response.text)
    alert_box = soup.cssselect("div.alert-box")
    if alert_box and 'XSS' in alert_box[0].text_content():
        print(f"Vulnerable input element found: {data.keys()} with XSS code: {data.values()}")
    else:
        print(f"Vulnerable input element NOT found: {data.keys()} with XSS code: {data.values()}")



async def check_alert(url):
    browser = await launch(headless=True) # 创建一个 Headless Chrome 浏览器
    page = await browser.newPage() # 打开一个新页面
    await page.goto(url) # 访问指定的网址
    
    # 监听 'dialog' 事件，以便捕获弹出窗口
    def dialog_handler(dialog):
        asyncio.ensure_future(dialog.dismiss()) # 关闭弹出窗口
    
    page.on('dialog', dialog_handler)
    
    # 在页面中执行一些 JavaScript 代码，可能会导致弹出窗口
    await page.evaluate("alert('Hello, World!')")
    
    # 等待一段时间，以确保所有弹出窗口都已关闭
    await asyncio.sleep(1)
    
    # 检查页面是否还有未关闭的弹出窗口
    dialogs = await page.browserContext().dialogs()
    has_alert = any(dialog.type == 'alert' for dialog in dialogs) # 判断是否存在 alert 类型的弹出窗口
    print(f"Has alert: {has_alert}")
    
    await browser.close() # 关闭浏览器

asyncio.get_event_loop().run_until_complete(check_alert('http://127.0.0.1/DVWA/vulnerabilities/xss_r/'))


