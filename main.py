from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

import os
import time
import sys

from collections import Counter
from typing import Any

from helpers import convert_str_to_number
from logger import logger as get_logger

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SUBDOMAIN = os.getenv("SUBDOMAIN")
AUTH_USER = os.getenv("AUTH_USER")
AUTH_PASS = os.getenv("AUTH_PASS")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASS = os.getenv("LOGIN_PASS")

logger = get_logger(file=f"{BASE_DIR}/main.log")


def login_to_platform(form: Any = None) -> None:
    """Handle authentication."""

    login_email = form.find_element(By.ID, "inputEmail").send_keys(LOGIN_EMAIL)
    login_password = form.find_element(By.ID, "inputPassword").send_keys(LOGIN_PASS)
    login_btn = form.find_element(By.TAG_NAME, "button").click()

    return None


def get_highest_echarts_value(driver) -> int:
    """Retrieve highest value from echarts graph."""

    script = """
        // create `script` element
        var scriptTag = document.createElement('script');
        scriptTag.setAttribute('src', 'https://cdn.jsdelivr.net/npm/echarts@5.2.1/dist/echarts.min.js');

        setTimeout(getHighestValue, 3000);

        function getHighestValue() {
            var echarts = echarts();
            var canvas = document.querySelector('#web-graph > div > canvas');
            var echartsInstance = echarts.getInstanceByDom(canvas);
            console.log(echartsInstance);
            return echartsInstance
        }

        return getHighestValue();
    """
    driver.set_script_timeout(3000)
    echarts_instance = driver.execute_async_script(script)
    print(echarts_instance)


def run_test_case_1(driver: Any) -> dict:
    """Check numerical values of Similarity, Articles & Twitter. Valid range > 0."""

    logger.info("Running test case 1...")

    test_result = {
        "similarities": False,
        "articles": False,
        "twitter": {"post": False, "retweets": False, "likes": False},
    }

    # get first row in table
    tbody = driver.find_element(By.TAG_NAME, "tbody")
    trow = tbody.find_elements(By.TAG_NAME, "tr")[0]

    # retrieve values
    similarity = convert_str_to_number(
        trow.find_element(By.CLASS_NAME, "alert-warning").text
    )
    articles = convert_str_to_number(
        trow.find_element(By.CLASS_NAME, "alert-info").text
    )
    twitter_post = convert_str_to_number(
        trow.find_element(By.CLASS_NAME, "tw_posts").text
    )
    twitter_retweet = convert_str_to_number(
        trow.find_element(By.CLASS_NAME, "tw_retweet").text
    )
    twitter_likes = convert_str_to_number(
        trow.find_element(By.CLASS_NAME, "tw_likes").text
    )

    # check validity of values
    if similarity > 0:
        test_result["similarities"] = True
    if articles > 0:
        test_result["articles"] = True
    if twitter_post > 0:
        test_result["twitter"]["post"] = True
    if twitter_retweet > 0:
        test_result["twitter"]["retweets"] = True
    if twitter_likes > 0:
        test_result["twitter"]["likes"] = True

    return dict(test_result)


def run_test_case_2(driver: Any) -> dict:
    """Check values of Web, TV, Twitter, Search, Web sections. Valid range > 0."""

    logger.info("Running test case 2...")

    test_result = {
        "total_section": {
            "web": False,
            "tv": False,
            "twitter": False,
            "search": False,
        },
        "web_section": {"web": False, "highest_echarts_value": None},
    }

    # navigate to first keyword reports page
    keyword = driver.find_elements(By.CLASS_NAME, "__keywords")[0]
    report_page = keyword.find_element(By.TAG_NAME, "a")
    report_page.click()
    driver.implicitly_wait(40)

    script = """
        var result = new Object()
        var t = setInterval(delayScrape, 5000)
        var span = document.querySelector('.p-content-word__total #totalTvCountup')
        sessionStorage.setItem('count', span.innerHTML)

        var count = 0;

        function delayScrape() {
            count += 1
            var prevCount = sessionStorage.getItem('count')
            if (prevCount === span.innerHTML) {
                if (count === 6){
                    stopInterval()
                }
            } else {
                var curCount = sessionStorage.setItem('count', span.innerHTML)
            }
        }

        delayScrape();

        function stopInterval() {
            clearInterval(t)
            returnCallback()
        }

        var done = arguments[0]; // pass callback function to variable

        function returnCallback() {
            // total section elements
            var web = document.querySelector('.p-content-word__total #totalNewsCountup').innerHTML;
            var tv = document.querySelector('.p-content-word__total #totalTvCountup').innerHTML;
            var twitter = document.querySelector('.p-content-word__total #totalTwitterCountup').innerHTML;
            var search = document.querySelector('.p-content-word__total #totalSearchCountup').innerHTML;

            // web section elements
            var webInfo = document.querySelector('.p-content-word__web #webInfoTotalNewsCountup').innerHTML;

            result.web = parseInt(web.replace(/,/g,''))
            result.tv = parseInt(tv.replace(/,/g,''))
            result.twitter = parseInt(twitter.replace(/,/g,''))
            result.search = parseInt(search.replace(/,/g,''))
            result.webInfo = parseInt(webInfo.replace(/,/g,''))

            return done(result)
        }
    """
    driver.set_script_timeout(3000)
    script_result = driver.execute_async_script(script)

    # check validity of values
    if script_result["web"] > 0:
        test_result["total_section"]["web"] = True
    if script_result["tv"] > 0:
        test_result["total_section"]["tv"] = True
    if script_result["twitter"] > 0:
        test_result["total_section"]["twitter"] = True
    if script_result["search"] > 0:
        test_result["total_section"]["search"] = True
    if script_result["webInfo"] > 0:
        test_result["web_section"]["web"] = True

    # retrieve highest echarts value
    # highest_echarts_value = get_highest_echarts_value(driver)
    # test_result["web_section"]["highest_echarts_value"] = highest_echarts_value

    return dict(test_result)


def run_test_case_3(driver) -> dict:
    """Display list of topics and number duplicate domains."""

    duplicate_domains = {}

    logger.info("Running test case 3...")

    script = """
        scrollTo(0, 500)

        var domains = new Array()
        var done = arguments[0];
        var t = setInterval(findTopicSection, 3000)

        function findTopicSection() {
            var section = document.querySelector('.p-content-word__web #collapse-cluster-web .p-article-archives.p-article-country');
            if (section !== null) {
                stopInterval()
                findDomains(section)
            }
        }

        findTopicSection()

        function findDomains(topicSection) {
            var i;
            var articles = topicSection.getElementsByTagName('article')

            for (i = 0; i < articles.length; i++) {
                var domain = articles[i].querySelector('div > div > span > span:nth-last-child(1) > a')
                domains.push(domain.textContent.trim())
            }

            returnCallback()
        }

        function stopInterval() {
            clearInterval(t)
        }

        function returnCallback() {
            return done(domains)
        }
    """
    driver.set_script_timeout(3000)
    domains = driver.execute_async_script(script)

    # count domains
    domains_count = dict(Counter(domains))

    # record duplicates
    for key in domains_count.keys():
        if domains_count[key] >= 2:
            duplicate_domains[key] = domains_count[key]

    return dict(duplicate_domains)


def run_test_case_4(driver) -> dict:
    """
    Goto articles page and scroll through the pages to collect the number
    of domains for a given word for a time period (e.g. monthly).
    """

    web_section = driver.find_element(By.CSS_SELECTOR, "#collapse-cluster-web")
    ActionChains(driver).move_to_element(web_section)

    articles_hyperlink = web_section.find_element(
        By.CSS_SELECTOR,
        "div:nth-last-child(1) > div:nth-last-child(2) > div:nth-last-child(1) > a",
    )
    articles_hyperlink.click()


def main() -> dict:
    """
    Start web driver.
    -------
    :return: Dictionary containing test results.
    """

    url = f"http://{AUTH_USER}:{AUTH_PASS}@{SUBDOMAIN}"
    has_args = True if len(sys.argv) > 1 else False
    search_by = sys.argv[1] if has_args else "week"

    s = Service(ChromeDriverManager().install())

    with webdriver.Chrome(service=s) as driver:
        logger.info("========== Start driver ==========")

        driver.maximize_window()

        # call url
        driver.get(url)
        driver.implicitly_wait(10)

        # login to platform
        login_form = driver.find_element(By.TAG_NAME, "form")
        login_to_platform(form=login_form)
        driver.implicitly_wait(20)

        # browse webpage based on period
        period_input_group_element = driver.find_element(
            By.CLASS_NAME, "p-period-settings__change"
        )
        if search_by == "day":
            change_period_btn = period_input_group_element.find_elements(
                By.TAG_NAME, "button"
            )[0]
        elif search_by == "week":
            change_period_btn = period_input_group_element.find_elements(
                By.TAG_NAME, "button"
            )[1]
        elif search_by == "month":
            change_period_btn = period_input_group_element.find_elements(
                By.TAG_NAME, "button"
            )[2]
        change_period_btn.click()

        # run test cases
        logger.info("Running test cases...")

        test_result_1 = run_test_case_1(driver)
        logger.info("Test case 1 complete")

        test_result_2 = run_test_case_2(driver)
        logger.info("Test case 2 complete")

        test_result_3 = run_test_case_3(driver)
        logger.info("Test case 3 complete")

        test_result_4 = run_test_case_4(driver)
        logger.info("Test case 4 complete")

    return {
        "test_case_1": test_result_1,
        "test_case_2": test_result_2,
        "test_case_3": test_result_3,
        "test_case_4": test_result_4,
    }


def clean_test_results(data: dict) -> dict:
    """Clean test results.
    -------
    :param data: Uncleaned test results data.

    :return: Dictionary containing cleaned results.
    """

    logger.info("Cleaning test results...")

    cleaned_results = {
        "test_case_1": True,
        "test_case_2": True,
        "test_case_3": True,
        "test_case_4": True,
    }

    for key in data.keys():
        if key == "test_case_1":
            for k1, v1 in data[key].items():
                if k1 == "twitter":
                    for k2, v2 in data[key][k1].items():
                        if v2 == False:
                            data["test_case_1"] = False
                if v1 == False:
                    data["test_case_1"] = False

        if key == "test_case_2":
            for k1, v1 in data[key].items():
                if k1 == "total_section":
                    for k2, v2 in data[key][k1].items():
                        if v2 == False:
                            data["test_case_2"] = False
                if k1 == "web_section":
                    data[key][k1].pop("highest_echarts_value")  # skip check for key
                    for k3, v4 in data[key][k1].items():
                        if v4 == False:
                            data["test_case_2"] = False

    return dict(cleaned_results)


if __name__ == "__main__":
    passed, failed = int(), int()

    start_time = time.time()
    test_results = main()
    end_time = time.time()

    total_time = format(end_time - start_time, ".2f")

    logger.info("Retrieving test results...")
    cleaned_results = clean_test_results(test_results)

    for key in cleaned_results.keys():
        if cleaned_results[key] == True:
            passed += 1
            logger.info(f"{key}:: PASSED")
        else:
            failed += 1
            logger.error(f"{key}:: FAILED")

    logger.info(
        f"========== {failed} failed, {passed} passed in {total_time} =========="
    )
