from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from selenium.webdriver.support.ui import Select

# 设置你的chromedriver路径
chromedriver_path = 'C:/Program Files/Google/Chrome/Application/chromedriver'

# 初始化webdriver
driver = webdriver.Chrome(chromedriver_path)
print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - WebDriver initialized.")

# 在访问页面前，将navigator.webdriver设置为undefined
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# 访问目标网站
driver.get('https://www.ipe.org.cn/MapLowCarbon/LowCarbon.html?q=5')
print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Page loaded: {driver.current_url}")
wait = WebDriverWait(driver, 10)

try:  # 开始try块
    # 打开输出文件
    with open('output.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入标题头
        writer.writerow(['排名', '城市', '年份', '指标', '数值'])

        # 遍历2010年到2020年
        for year in range(2010, 2021):
            # 定位年份下拉菜单并选择年份
            select_year = Select(wait.until(EC.element_to_be_clickable((By.ID, 'yearList'))))
            select_year.select_by_value(str(year))
            # 定位城市下拉菜单
            select_element = Select(driver.find_element(By.ID, "citytype"))
            # 选择城市（value="0"对应“城市”）
            select_element.select_by_value("0")
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Year selected: {year}")
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - City selected as '城市'.")
            # 找到筛选按钮
            filter_button = driver.find_element(By.ID, 'filter_btn')
            # 点击筛选按钮
            filter_button.click()

            # 等待页面加载完成
            wait.until(EC.presence_of_element_located((By.ID, 'idpage')))
            # 获取下一页按钮
            next_page = driver.find_element(By.CSS_SELECTOR, 'i.icon-arrow-right-active')

            # 翻页操作开始之前保存屏幕截图
            driver.save_screenshot(f'screenshot_before_paging_{year}.png')

            # 页码初始值
            page_number = 1
            while True:  # 改为无限循环，直到没有下一页为止
                # 等待新页面的表格加载
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-list > tbody > tr')))
                rows = driver.find_elements(By.CSS_SELECTOR, 'table.table-list > tbody > tr')
                for row in rows:
                    try:
                        # 尝试获取行的数据
                        rank = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)').text
                        city = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
                        year = row.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text
                        indicator = row.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
                        value = row.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text
                        writer.writerow([rank, city, year, indicator, value])
                    except StaleElementReferenceException as e:
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Exception: {e}. Re-acquiring the row.")
                        # 可以在这里添加代码重新定位元素或者刷新页面等恢复操作

                try:
                    #重新定位下一页按钮
                    next_page = driver.find_element(By.CSS_SELECTOR, 'i.icon-arrow-right-active')
                    # 检查是否含有'disabled'类
                    if 'disabled' in next_page.get_attribute('class'):
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Last page reached. Year: {year}")
                        break
                    else:
                        # 点击下一页之前保存屏幕截图
                        driver.save_screenshot(f'screenshot_before_clicking_next_{page_number}.png')
                        # 点击下一页
                        next_page.click()
                        # 翻页后保存屏幕截图
                        driver.save_screenshot(f'screenshot_after_clicking_next_{page_number}.png')
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Moved to the next page: {page_number + 1}.")
                        page_number += 1
                        # 重新获取“下一页”按钮以确保它不是一个陈旧的元素引用
                        next_page = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.icon-arrow-right-active')))
                except ElementClickInterceptedException as e:
                    # 如果点击被拦截，使用JavaScript尝试点击
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Click intercepted: {e}. Retrying with JavaScript.")
                    driver.execute_script("arguments[0].click();", next_page)
                except NoSuchElementException as e:
                    # 如果没有找到元素，可能是最后一页，打印信息并退出循环
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No next page button found: {e}. Ending pagination.")
                    break
                except Exception as e:
                    # 其他未预料的异常
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - An unexpected error occurred: {e}.")
                    break

            # 保存在完成年份循环后的屏幕截图
            driver.save_screenshot(f'screenshot_after_year_{year}.png')
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Completed data extraction for the year: {year}.")

    # 完成所有年份的数据提取后，打印完成的消息
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Data extraction completed for all years.")
finally:
    # 最后不管发生什么都关闭WebDriver
    driver.quit()
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - WebDriver closed.")
