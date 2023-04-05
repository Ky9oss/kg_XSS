import logging
import requests
from lxml import html
import linecache
import concurrent.futures
from urllib.parse import urlparse
from multiprocessing import Pool, cpu_count




def send_request(logger, url, input_name, xss_code):

    # 发送包含 XSS 代码的 POST 请求
    data = {input_name: xss_code}

    try:
        response = requests.post(url, data=data, timeout=30)

        # 判断是否触发了alert
        soup = html.fromstring(response.text)
        alert_box = soup.cssselect("div.alert-box")
        if alert_box and 'XSS' in alert_box[0].text_content():
            message = f"Vulnerable input element found: {input_name} with XSS code: {xss_code}"
            logger.info(message)
            return True


    except Exception as e:
        logger.warning(f"Error occurred while sending request to {url}: {str(e)}")
    return False



def test_xss(url):


    # 初始化日志记录器
    domain_name = urlparse(url).netloc.split(':')[0]
    log_file = "log.log"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(domain_name)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)



    # 获取所有可输入元素
    response = requests.get(url, timeout=30)
    tree = html.fromstring(response.content)
    inputs = tree.xpath('//input[@type="text"] | //textarea')


    logger.info("-" * 50)
    logger.info(f"Starting XSS test on {url}")
    logger.info(f"Number of input elements found: {len(inputs)}")


    # 逐行读取包含 XSS 代码的文件，并去掉前后的双引号和逗号
    xss_codes_file = "xss_dictionary.txt"
    xss_codes = []
    for n in range(1, len(open(xss_codes_file).readlines())+1):
        line = linecache.getline(xss_codes_file, n)
        xss_code = line.strip(',').strip('"')
        xss_codes.append(xss_code)


    # 使用线程池，动态调整最大并发数量
    max_workers = min(50, len(inputs)*len(xss_codes), cpu_count()*4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 为每个输入框创建一个线程，并尝试该输入框与 XSS 代码文件中的每一行组合成的一组键值对
        futures = []
        for input_element in inputs:
            for xss_code in xss_codes:
                # 提交任务到线程池
                future = executor.submit(send_request, logger, url, input_element.name, xss_code)
                futures.append(future)

        # 统计失败次数
        failed_count = sum([1 for future in futures if not future.result()])


    if failed_count:
        logger.info(f"{failed_count} injections failed out of {len(inputs)*len(xss_codes)} total injections")
    else:
        logger.info("No vulnerabilities found")
    logger.info("-" * 50)
    # 在日志文件中添加一个额外的分隔线，以将其与下一个页面的测试结果分开
    logger.info("")

    logger.removeHandler(fh)
    fh.close()



def main():
    # 读取targets.txt文件
    targets_file = "targets.txt"
    with open(targets_file, 'r') as f:
        targets = [line.strip() for line in f]

    # 使用多进程，每个网站一个进程
    pool = Pool(processes=len(targets))
    pool.map(test_xss, targets)
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
