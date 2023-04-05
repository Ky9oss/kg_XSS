import concurrent.futures
import textwrap
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
import queue
import contextlib


# global
ifstop = False



# 简易上下文管理器，通过with可以使用该函数,并最终一定执行finanly即关闭等操作。类似with open
@contextlib.contextmanager
def open_url(url, driver):
    driver.get(url)
    try:
        yield
    finally:
        driver.quit()



def xssHackNow(url, xss_code, options):

    try:

        global ifstop
        if ifstop:
            sys.exit()


        driver = webdriver.Chrome(options=options)
        with open_url(url, driver):
            # 找到所有可输入元素
            all_inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')


            #只测试第一个输入栏
            input_element = all_inputs[0]
            input_element.clear()
            input_element.send_keys(xss_code + Keys.RETURN)

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
            except NoAlertPresentException:
                pass
            else:
                print(f"[^_^] {xss_code} SUCCESS!")
                ifstop = True


    except KeyboardInterrupt:
        print("[^_^] Bye~~~")
        ifstop = True



        #if alert_box and "XSS" in alert_box[0].text_content():
        #page_source = driver.page_source
        #soup = html.fromstring(page_source)
        #alert_box = soup.cssselect("div.alert-box")
        #if alert_box:
        #    print(f'{xss_code} success!')
        #    ifstop = True



def main(url, xss_codes_file):

    try:
        print('Start Hacking...')

        # 创建queue
        xss_codes_queue = queue.Queue()
        #counts = queue.Queue()

        # 将chrome浏览器设置成无头模式（headless mode）
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')


        # 读取包含 XSS 代码的文件
        with open(xss_codes_file, "r") as f:
            xss_codes = f.read().splitlines()

        # 填充Queue
        for xss_code in xss_codes:
            #xss_code = xss_code.strip(',').strip('"')
            xss_codes_queue.put(xss_code)

        #for i in range(len(xss_codes)):
        #    counts.put(i) 


        # 创建线程池,最大线程50
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:

            while not xss_codes_queue.empty():

                # 取出queue
                xss_code = xss_codes_queue.get()
                #count = counts.get()
                executor.submit(xssHackNow, url, xss_code, options)
                if ifstop:
                    sys.exit()



        
    except KeyboardInterrupt:
        sys.exit()
    finally:
        print('Done!')


if __name__ == "__main__":
    print(textwrap.dedent(
    '''

    ██╗  ██╗██╗   ██╗ ██████╗  ██████╗ ███████╗███████╗
    ██║ ██╔╝╚██╗ ██╔╝██╔════╝ ██╔═══██╗██╔════╝██╔════╝
    █████╔╝  ╚████╔╝ ██║  ███╗██║   ██║███████╗███████╗
    ██╔═██╗   ╚██╔╝  ██║   ██║██║   ██║╚════██║╚════██║
    ██║  ██╗   ██║   ╚██████╔╝╚██████╔╝███████║███████║
    ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                                                                      
    '''))

    myparser = argparse.ArgumentParser(
        prog='kgXSS', 

        formatter_class=argparse.RawDescriptionHelpFormatter, #表示description和epilog的换行方式完全按照我们的文本的换行方式

        description='A simple tool with XSS automatic injection :)', 

        epilog=textwrap.dedent( #textwrap.dedent表示自动将多行字符串的前面的空白补齐
        '''
        examples:
            python kgXXS.py -u https://xxx.xxx.com
            python kgXXS.py -u https://xxx.xxx.com -f /home/xss/dictionary

        '''
        ))


    myparser.add_argument('-u', '--url', help='the url you want to hack') 
    myparser.add_argument('-f', '--filepath', default="xss_dictionary.txt", help='the XSS dictionary you want to use')
    args = myparser.parse_args() #args是命名空间，这行命令将用户输入的参数去掉双杠后作为命名空间的属性

    url = args.url
    file_path = args.filepath

    if url and file_path :
        main(url, file_path)
    else:
        print('Wrong usage. Please use -h or --help to learn more.')


