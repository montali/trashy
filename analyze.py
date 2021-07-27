from selenium import webdriver
from PIL import Image
from datetime import timedelta, datetime
import time
import re
import os
from selenium.webdriver.common.action_chains import ActionChains
from wand.image import Image
# Require wand's API library and basic ctypes
from wand.api import library
from ctypes import c_void_p, c_size_t
import keras
import tensorflow as tf

# Tell Python's wand library about the MagickWand Compression Quality (not Image's Compression Quality)
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]
model = tf.keras.models.load_model('saved_model/nn')


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


def get_image_trashiness(image_path):
    test_image = keras.preprocessing.image.load_img(image_path)
    img_array = keras.preprocessing.image.img_to_array(test_image)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    return tf.nn.softmax(model.predict(img_array))


driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.get("https://maps.google.com")
print("Everything is set up. Accept the cookies pls.")
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
        if get_image_trashiness(f"{lat},{lon}.png") > 0.8:
            print(f"Found trash at {lat},{lon}")
        else:
            os.remove(f"{lat},{lon}.png")
    move_map(driver, 0, 100)
    time.sleep(2)
    lat, lon = get_current_coordinates(driver)
    map_url = f"https://www.google.com/maps/@{str(lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
    driver.get(map_url)
