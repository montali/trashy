from selenium import webdriver
from PIL import Image
from datetime import timedelta, datetime
import time
import re
from selenium.webdriver.common.action_chains import ActionChains


def get_current_coordinates(driver):
    groups = None
    while groups is None:
        groups = re.search(
            r'(@\d{2}.\d{7,},\d{2}.\d{7,})', str(driver.current_url))
    coordinates = groups.group(1).strip("@").split(",")
    return float(coordinates[0]), float(coordinates[1])


def move_map(driver, x, y):
    actions = ActionChains(driver)
    maps = driver.find_element_by_class_name("widget-scene-canvas")
    actions.drag_and_drop_by_offset(
        maps, x, y).perform()

def remove_labels(driver):
    actions = ActionChains(driver)
    
    hoverElement = driver.find_element_by_class_name("QNI8Sb-minimap-UDotu-LgbsSe")
    actions.move_to_element(hoverElement).perform()
    time.sleep(2)
    driver.find_element_by_class_name("QotPpe-LJSvSb-cdLCv-mAKE4e-z5C9Gb").click()
    time.sleep(2)
    driver.find_element_by_xpath("//label[contains(@class, 't9hXV-cdLCv-checkbox-V67aGc') and contains(text(), 'Etichette')]").click()
    time.sleep(1)
    driver.find_element_by_class_name("t9hXV-cdLCv-icon-TvD9Pc").click()


driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.get("https://maps.google.com")
print("Everything is set up. Now, please log in with your Google user and do shit that makes captcha trigger")
start = datetime.now()
while datetime.now() < start+timedelta(seconds=5):
    pass

# last_lat = 41.9058809
# last_lon = 12.4392198
# start_lat = 41.9423509
# start_lon = 12.4168289

start_lat = 41.9058809
start_lon = 12.4392198
last_lat = 41.9423509
last_lon = 12.4168289

lat = start_lat
map_url = f"https://www.google.com/maps/@{str(start_lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
time.sleep(3)
driver.get(map_url)
remove_labels(driver)
action = ActionChains(driver)
while lat <= last_lat:
    lon = start_lon
    while lon >= last_lon:
        time.sleep(1)
        move_map(driver, 100, 0)
        lat, lon = get_current_coordinates(driver)
        driver.save_screenshot(f"{lat},{lon}.png")
    move_map(driver, 0, 100)
    time.sleep(2)
    lat, lon = get_current_coordinates(driver)
    map_url = f"https://www.google.com/maps/@{str(lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
    driver.get(map_url)
    remove_labels(driver)
