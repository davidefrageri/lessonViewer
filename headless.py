import time
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import request

def find_course_url(browser: webdriver.Chrome, course_name: str) -> str:
    courses_a = find_elements_timeout(browser, By.CSS_SELECTOR, "#my_courses > div > a", 30)

    for course_a in courses_a:
        if (course_a.text.rfind(course_name) != -1):
            return course_a.get_property("href")
        
def find_element_timeout(driver: WebDriver, locator_by: By, locator_str: str, timeout: int) -> WebElement:
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((locator_by, locator_str)))
    return driver.find_element(locator_by, locator_str)

def find_elements_timeout(driver: WebDriver, locator_by: By, locator_str: str, timeout: int) -> List[WebElement]:
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((locator_by, locator_str)))
    return driver.find_elements(locator_by, locator_str)

# GET cookie session
def create_login_cookies():
    browser = webdriver.Chrome()

    browser.get('https://training.mulesoft.com/login')
    # time.sleep(4) # TODO: await page loading
    login_title = browser.title

    cookies_accept_button = find_element_timeout(browser,By.ID, "onetrust-accept-btn-handler", 10)
    cookies_accept_button.click()

    user_input = find_element_timeout(browser, By.NAME, "username", 10)
    user_input.send_keys("")

    password_input = find_element_timeout(browser, By.NAME, "password", 10)
    password_input.send_keys("")

    submit_button = find_element_timeout(browser, By.TAG_NAME, "button", 10)
    submit_button.click()

    # TODO: maybe remove
    while(browser.title == login_title):
        time.sleep(2)

    course_url = find_course_url(browser, "Anypoint Platform Development: Fundamentals")

    browser.get(course_url)

    transcript_url = find_element_timeout(browser, By.ID, "eb-cp-btn-transcript", 30).get_property("href")

    browser.get(transcript_url)

    page_buttons = find_elements_timeout(browser, By.CSS_SELECTOR, "div.input-group-btn > a.btn.btn-default", 10)

    page_counter = int(page_buttons[-1].get_property("href").replace("javascript:gotoPage(","").split(",")[0])
    
    resources_ids = []
    browser.execute_script(f"gotoPage(0)")
    for p in range(1,page_counter+2):
        time.sleep(1)

        trs = find_elements_timeout(browser, By.CSS_SELECTOR, "#divLessonsStats > div > div.panel-body > table > tbody > tr.lessonStatRow", 10)
        resources_a = find_elements_timeout(browser, By.CSS_SELECTOR, "#divLessonsStats > div > div.panel-body > table > tbody > tr.lessonStatRow > td:nth-child(2) > a", 10)
        times_td = find_elements_timeout(browser, By.CSS_SELECTOR, "td.inlHelp.hidden-xs", 10)

        for i in range(len(trs)):
            try:
                trs[i].find_element(By.CSS_SELECTOR, "i.fa.fa-check.txt-color-checked")
            except:
                if (resources_a[i].text.rfind("Walkthrough") != -1):
                    res_url = resources_a[i].get_property("href")
                    print(res_url)
                    n_minutes_actual = 0
                    if len(times_td[i].text.split("min")) > 2:
                        n_minutes_actual = int(times_td[i].text.replace(" ","").split("min")[0])
                    n_minutes_expected = int(times_td[i].text.replace(" ","").split("/")[-1].split("min")[0])
                    n_seconds_remaining = (n_minutes_expected-n_minutes_actual)*60
                    resources_ids.append((res_url.split("courseItemDocumentId=")[-1],n_seconds_remaining))
        
        browser.execute_script(f"gotoPage({p})")

    print(resources_ids)

    browser.get(course_url)

    # awaiter page loaded
    find_element_timeout(browser, By.ID, "eb-cp-btn-transcript", 30).get_property("href")

    time.sleep(5)

    for resource_id in resources_ids:
        browser.execute_script(f"ebObj.getObject('eb_obj_0').launchLessonById('{resource_id[0]}', '', 'NATURE_FILE')")

        time.sleep(resource_id[1])

        span = find_element_timeout(browser,By.ID,"eb-cp-pgnum",10)
        pages = span.text.replace("&nbsp;","").replace("Page","").split("of")

        while len(pages)==2 and int(pages[0])<=int(pages[1]):
            browser.execute_script(f"ebObj.getObject('eb_obj_0').next()")
            time.sleep(1)
            span = find_element_timeout(browser,By.ID,"eb-cp-pgnum",10)
            pages = span.text.replace("&nbsp;","").replace("Page","").split("of")
        
        time.sleep(10)


    browser.quit()


def main():
    create_login_cookies()


if __name__ == "__main__":
    main()