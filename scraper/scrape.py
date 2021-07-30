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
import tensorflow as tf
from tensorflow import keras
# Tell Python's wand library about the MagickWand Compression Quality (not Image's Compression Quality)
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]


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
    try:
        driver.execute_script(
            'st=document.createElement("style");st.type="text/css";st.appendChild(document.createTextNode("\\#omnibox-container, #minimap, .app-viewcard-strip,#vasquette,.scene-footer-container {display:none;}"));document.getElementsByTagName("head")[0].appendChild(st)')
    except Exception as e:
        print(e)


driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.get("https://maps.google.com")
print("Everything is set up. Accept the cookies pls.")
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
model = tf.keras.models.load_model('../saved_model/nn')
while lat <= last_lat:
    lon = start_lon
    while lon >= last_lon:
        time.sleep(1)
        move_map(driver, 100, 0)
        lat, lon = get_current_coordinates(driver)
        driver.save_screenshot(f"{lat},{lon}.png")
        with Image(filename=f"{lat},{lon}.png") as img:
            img.resize(width=1280, height=811)
            # Set the optimization level through the linked resources of
            # the image instance. (i.e. `wand.image.Image.wand`)
            library.MagickSetCompressionQuality(img.wand, 40)
            img.save(filename=f"{lat},{lon}.jpg")
            os.remove(f"{lat},{lon}.png")
            test_image = keras.preprocessing.image.load_img(f"{lat},{lon}.jpg")
            img_array = keras.preprocessing.image.img_to_array(test_image)
            img_array = tf.expand_dims(img_array, 0)  # Create a batch
            trashiness = tf.nn.softmax(model.predict(img_array))
            print(
                f"Place {lat},{lon} is {trashiness[0][1]*100}% trashy")
            os.remove(f"{lat},{lon}.jpg")
    move_map(driver, 0, 100)
    time.sleep(2)
    lat, lon = get_current_coordinates(driver)
    map_url = f"https://www.google.com/maps/@{str(lat)},{str(start_lon)},43m/data=!3m1!1e3!5m1!1e4"
    driver.get(map_url)
    remove_labels(driver)
