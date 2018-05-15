import sys
import time
import subprocess
import os, signal
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import platform
import logging
import inspect



implicit_wait_time = 3
specific_wait_time = 15

# TODO: Que dandole sea capaz de sacar una "lista de elementos" hacia tabla mediante un tag


global aux_display_selenium_helpers

# now Firefox will run in a virtual display.
# you will not see the browser.

def get_browser(development = 0, with_visual_browser = 0, browser_size_x = 1500, browser_size_y = 1200, PROXY = ""):

    options = Options()
    path = os.path.dirname(os.path.realpath(__file__))
    geckodriver_file = os.path.join(path, "resources/geckodriver_ubuntu")
    if sys.platform == "linux2":
        if platform.dist()[0] == "Ubuntu":
            geckodriver_file = os.path.join(path, "resources/geckodriver_ubuntu")
        else:
            geckodriver_file = os.path.join(path, "resources/geckodriver")
    else:
        geckodriver_file = os.path.join(path, "resources/geckodriver.exe")

    if development:
        logging.basicConfig(level=logging.INFO)
        try:
            import pydevd
        except:
            pass
    else:

        if not with_visual_browser:
            try:
                from pyvirtualdisplay import Display
                aux_display_selenium_helpers = Display(visible=with_visual_browser, size=(browser_size_x, browser_size_y))
                aux_display_selenium_helpers.start()
            except:
                logging.info("[------- INFO] Cant use pyvirtualdisplay, using systems default instead.")

    if not with_visual_browser:
        os.environ['MOZ_HEADLESS'] = '1'
        options.add_argument("--headless")

    logging.info("[************** START] Starting browser...")



    if PROXY:
        profile = webdriver.FirefoxProfile()
        proxy_ip, proxy_port = PROXY.split(":")
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy_ip)
        profile.set_preference("network.proxy.http_port", int(proxy_port))
        profile.update_preferences()
        browser = webdriver.Firefox(executable_path=os.path.abspath(geckodriver_file), firefox_profile=profile)
    else:
        browser = webdriver.Firefox(executable_path=os.path.abspath(geckodriver_file))

    browser.implicitly_wait(implicit_wait_time)
    # browser.set_window_position(100,100) # No logro conseguir que maximice en ubuntu la ventana.
    try:
        browser.set_window_size(browser_size_x, browser_size_y)
    except:
        logging.info("FAILED TO RESIZE THE BROWSER PROPERLY")

    logging.info("[END] Browser launched")

    return browser


## Final interactions

def fill_form(element, text_to_fill):
    if element:
        element.clear()
        element.send_keys(text_to_fill)
        time.sleep(implicit_wait_time)
        logging.info("[END] " + inspect.stack()[0][3] + ".")
        return True
    return False


def click_element(result, position_in_list):
    if result and position_in_list > -1:
        logging.info("[END] Clicking found element.")
        result.click()
        time.sleep(specific_wait_time)
        return True
    elif position_in_list < 0:
        logging.info("[END] Returning element list.")
        return result
    else:
        return False


## Getters

def get_element_parent(element):
    logging.info("\t\t START - END; " + inspect.stack()[0][3] + ": "+str(element))
    return element.find_element_by_xpath("..")


def click_when_exists_by_xpath(browser, identifier, position_in_list = -1, max_retries=20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))

    result = do_func(browser.find_elements_by_xpath, identifier, position_in_list, max_retries=max_retries)
    logging.info("[END] " + inspect.stack()[0][3])
    return click_element(result, position_in_list)


def click_when_exists_by_class(browser, identifier, position_in_list = -1, max_retries = 20):
    logging.info("[************** START] "+ inspect.stack()[0][3] +": " + identifier + ", Position: " + str(position_in_list))
    result = find_element_by_class(browser, identifier, position_in_list, max_retries=max_retries)
    return click_element(result, position_in_list)



def click_when_exists_by_id(browser, identifier, position_in_list = -1, max_retries = 20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))
    result = do_func(browser.find_elements_by_id, identifier, position_in_list, max_retries=max_retries)
    return click_element(result, position_in_list)


def click_when_exists_by_css(browser, identifier, position_in_list = -1, max_retries = 20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))
    result = do_func(browser.find_elements_by_css_selector, identifier, position_in_list, max_retries=max_retries)
    return click_element(result, position_in_list)




def find_element_by_id(browser, identifier, position_in_list = -1, max_retries = 20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))
    return do_func(browser.find_elements_by_id, identifier, position_in_list, max_retries=max_retries)


def find_element_by_tag(browser, identifier, position_in_list = -1, max_retries = 20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))
    return do_func(browser.find_elements_by_tag_name, identifier, position_in_list, max_retries=max_retries)


def find_element_by_class(browser, identifier, position_in_list = -1, max_retries = 20):
    """
    Accepts multiple words as class. Filters for the element to have EXACTLY the specified class (several values if so)

    :param identifier: Class name
    :param position_in_list: Position in the result list, -1 for "return all"
    :param max_retries:
    :param browser:
    :return:
    """

    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list))

    aux_identifier = ""
    element_list = list()
    if " " in identifier.strip():
        aux_identifier = identifier.strip()
        identifier = identifier.strip().split(" ")[0]

    element_list = do_func(browser.find_elements_by_class_name, identifier, -1, max_retries=max_retries)

    if not aux_identifier or not element_list:
        if position_in_list < 0:
            logging.info("[END] " + inspect.stack()[0][3] + ": Returning requested list of elements.")
            return element_list
        else:
            logging.info("[END] " + inspect.stack()[0][3] + ": Returning requested element.")
            return [element for element in element_list if element.get_attribute("class").strip() == identifier.strip()][position_in_list]

    result_element_list = list()
    for element in element_list:
        if element.get_attribute("class").strip() == aux_identifier:
            result_element_list.append(element)
    if position_in_list < 0:
        logging.info("[END] " + inspect.stack()[0][3] + ": Returning requested list of elements.")
        return result_element_list
    else:
        try:
            logging.info("[END] " + inspect.stack()[0][3] + ": Returning requested element.")
            return result_element_list[position_in_list]
        except:
            logging.info("[END] " + inspect.stack()[0][3] + ": Element not found.")
            return False


def fill_form_when_exists_by_id(browser, identifier, position_in_list, text_to_fill, max_retries = 20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list) + ", TextToFill: "+text_to_fill)
    result = do_func(browser.find_elements_by_id, identifier, position_in_list, max_retries=max_retries)
    return fill_form(result, text_to_fill)

def fill_form_when_exists_by_name(browser, identifier, position_in_list, text_to_fill, max_retries=20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(position_in_list) + ", TextToFill: "+text_to_fill)
    result = do_func(browser.find_elements_by_name, identifier, position_in_list, max_retries=max_retries)
    return fill_form(result ,text_to_fill)

def fill_form_when_exists_by_class(browser, identifier, position_in_list, text_to_fill, max_retries=20):
    logging.info("[************** START] " + inspect.stack()[0][3] + ": " + identifier + ", Position: " + str(
        position_in_list) + ", TextToFill: " + text_to_fill)
    result = find_element_by_class(browser, identifier, position_in_list, max_retries=max_retries)
    return fill_form(result, text_to_fill)


def do_func(find_func, identifier, position_in_list, max_retries = 20):

    els = find_func(identifier)
    retries = 0
    while len(els) < position_in_list + 1 and retries < max_retries and len(els) < 1:
        retries += 1
        time.sleep(1)
        els = find_func(identifier)
    if position_in_list == -1:
        logging.info("\t\t START - END; FOUND LIST OF ELEMENTS: " + identifier + ", Position: " + str(position_in_list))
        return els
    elif len(els) > position_in_list:
        logging.info(
            "\t\t START - END; FOUND ELEMENT: " + identifier + ", Position: " + str(position_in_list))
        return els[position_in_list]
    else:
        return False


def get_frames(browser):
    return find_element_by_tag(browser, "frame", -1)


def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

def kill_selenium(browser):
    logging.info("[************** START] Killing Selenium...")
    browser.quit()
    try:
        aux_display_selenium_helpers.stop() # Global variable
    except:
        pass

    try:
        check_kill_process("firefox")
        process = subprocess.Popen(["pkill","firefox -marionette"], stdout=subprocess.PIPE)
        output, error = process.communicate()

    except:
        logging.error("Couldnt kill firefox -marionette, are you using windows?")
    logging.info("[END] Killing Selenium...")


def scrape_table(table ):
    # Hay que pasarle un elemento cuyo tag sea "table"

    table_headers = list()
    header_element = find_element_by_tag(table,"thead", position_in_list = 0, max_retries = 20)
    for header_row in find_element_by_tag(header_element, "tr", -1):
        new_header_row = list()
        for header in find_element_by_tag(header_row, "th", -1):
            new_header_row.append(header)
        table_headers.append(new_header_row)


    table_rows = list()
    body_element = find_element_by_tag(table, "tbody", position_in_list=0, max_retries=20)
    for body_row in find_element_by_tag(body_element, "tr", -1):
        new_body_row = list()
        for body in find_element_by_tag(body_row, "td", -1):
            new_body_row.append(body)
        table_rows.append(new_body_row)

    return table_headers, table_rows


def multiframe_find_element_by_class(browser, identifier, position_in_list = -1, max_retries = 20):
    browser.switch_to.default_content()
    frames = get_frames(browser)
    element_list = list()
    for idx, frame in enumerate(frames):
        browser.switch_to.frame(frame)
        element_list.extend((find_element_by_class(browser, identifier, position_in_list, max_retries),idx))
        browser.switch_to.default_content()
    return element_list


if __name__== "__main__":
    pass