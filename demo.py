from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
from selenium.webdriver.common.action_chains import ActionChains


debug = True

def log(text):
    if debug:
        print(text)
    else:
        pass

if __name__ == '__main__':
    url = 'https://passport.zhihuishu.com/login?service=https://onlineservice.zhihuishu.com/login/gologin'
    course = "" #课程名称
    university = "" #学校名称
    student_code = "" #学号
    passport = "" #密码
    count = 2 #要看的集数

    browser = webdriver.Chrome()

    wait = WebDriverWait(browser, 10)
    browser.get(url)

    #添加cookie减少弹窗数量
    browser.add_cookie({'name' : 'cookieServer', 'value' : '1', 'domain' : '.zhihuishu.com'})
    browser.add_cookie({'name' : 'warningTip', 'value' : '1', 'domain' : '.zhihuishu.com'})

    #登录操作
    log('开始登录')
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, '学号'))).click()
    wait.until(EC.presence_of_element_located((By.ID, 'quickSearch'))).send_keys(university) 
    wait.until(EC.presence_of_element_located((By.ID, 'clCode'))).send_keys(student_code) 
    wait.until(EC.presence_of_element_located((By.ID, 'clPassword'))).send_keys(passport) 
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#schoolListCode > li > b > font'))).click()
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'wall-sub-btn'))).click()
    
    #进入对应课程
    log('进入课程')
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'courseName')))
    course_list = browser.find_elements_by_class_name('courseName')
    flag = -1
    for index,item in enumerate(course_list):
        if item.text == course:
            flag = index
            break
    if flag != -1:
        course_list[index].click()
    else:
        log("未找到对应课程")
        exit()
    
    #关闭成绩提醒(可能会被弹题窗口挡住，要处理这种情况)
    try:
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'popboxes_close'))).click()
    except ElementClickInterceptedException:
        pop_chapter = browser.find_element_by_class_name('tanti_popchapter')
        ActionChains(browser).move_to_element(pop_chapter).click().perform()
        browser.find_element_by_link_text('关闭').click()
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'popboxes_close'))).click()

    new_episode = True
    while count > 0:
        time.sleep(5)
        #模拟鼠标划入播放窗口的操作，唤起底部控制栏
        video_area = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'videoArea')))
        #识别当前状态（播放、暂停、播放完、问题弹出）
        try:
            playButton = browser.find_element_by_class_name('playButton')
        except NoSuchElementException:
            if new_episode:
                #调至1.5倍速
                ActionChains(browser).move_to_element(video_area).perform()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'speedBox'))).click()
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'speedTab15'))).click()
                log('设置1.5倍速')
                #调静音
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'volumeBox'))).click()
                log('设置静音')
                #设置标志位
                new_episode=False
        else:
            #判断是否有弹窗弹出或是播放完
            try:
                pop_chapter = browser.find_element_by_class_name('tanti_popchapter')
            except NoSuchElementException:
                pass_time = browser.find_element_by_class_name('passTime')
                ActionChains(browser).move_to_element(video_area).perform()
                if pass_time.get_attribute('style') == 'width: 100%;':
                    count = count - 1
                    if count != 0:
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'nextButton'))).click()
                        new_episode=True
                        log('播放下一集')
                else:
                    log('继续播放')
                    playButton.click()
            else:
                ActionChains(browser).move_to_element(pop_chapter).click().perform()
                browser.find_element_by_link_text('关闭').click()
                log('关闭弹窗')
    print('已经看完目标集数，程序退出')
  