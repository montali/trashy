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
            r'(@\d{2}.\d{5,},\d{2}.\d{5,})', str(driver.current_url))
    coordinates = groups.group(1).strip("@").split(",")
    return float(coordinates[0]), float(coordinates[1])


def move_map(driver, x, y):
    actions = ActionChains(driver)
    maps = driver.find_element_by_class_name("widget-scene-canvas")
    actions.drag_and_drop_by_offset(
        maps, x, y).perform()


driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.get("https://maps.google.com")
print("Everything is set up. Now, please log in with your Google user and do shit that makes captcha trigger")
start = datetime.now()
while datetime.now() < start+timedelta(seconds=5):
    pass

start_lat = 44.7938947
start_lon = 10.2889675
last_lat = 44.793421
last_lon = 10.2879979
lat = start_lat
map_url = f"https://www.google.com/maps/@{str(start_lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
time.sleep(3)
driver.get(map_url)
action = ActionChains(driver)
while lat > last_lat:
    lon = start_lon
    while lon > last_lon:
        time.sleep(1)
        move_map(driver, 100, 0)
        lat, lon = get_current_coordinates(driver)
        driver.save_screenshot(f"{lat},{lon}.png")
    move_map(driver, 0, 100)
    time.sleep(2)
    lat, lon = get_current_coordinates(driver)
    map_url = f"https://www.google.com/maps/@{str(lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
    driver.get(map_url)
