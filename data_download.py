"""
Script to download satellite imagery from GMaps
"""
import csv
import re
import requests
import shutil
import random
from selenium import webdriver
from datetime import timedelta, datetime
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
from wand.image import Image
# Require wand's API library and basic ctypes
from wand.api import library
from ctypes import c_void_p, c_size_t

# Tell Python's wand library about the MagickWand Compression Quality (not Image's Compression Quality)
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]


class SatDownloader():
    def __init__(self, key, csv_file, driver, ratio=0.5):
        self.key = key
        self.csv_file = csv_file
        self.ratio = ratio
        self.driver = driver

    def read_csv(self):
        """
        Reads in a csv file and returns a list of dictionaries
        """
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def get_coordinates(self, url):
        """
        Splits a GMaps url to get the coordinates
        """
        return re.search(r'(\d{2}.\d{7},\d{2}.\d{7})', url).group(1)

    def download_image(self, coordinates, size, folder):
        """
        Gets a trash image given its coordinates and its size
        """
        zoom = 20 if int(size) > 2 else 25
        api_endpoint = f"https://maps.googleapis.com/maps/api/staticmap?center={coordinates}&zoom={zoom}&&size=1000x1000&maptype=satellite&key={self.key}"
        r = requests.get(api_endpoint, stream=True)
        if r.status_code == 200:
            with open(f"{folder}/{coordinates}.png", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    def download_image_illegally(self, coordinates, size, folder):
        url = f"https://www.google.com/maps/@{str(coordinates)},43m/data=!3m1!1e3!5m1!1e4"
        self.driver.get(url)
        time.sleep(2)
        self.remove_labels()
        self.driver.save_screenshot(f"{coordinates}.png")
        with Image(filename=f"{coordinates}.png") as img:
            img.resize(width=1280, height=811)
            # Set the optimization level through the linked resources of
            # the image instance. (i.e. `wand.image.Image.wand`)
            library.MagickSetCompressionQuality(img.wand, 40)
            img.save(filename=f"{folder}/{coordinates}.jpg")
        os.remove(f"{coordinates}.png")

    def get_random_coordinates(self, url, trash=False):
        original_coordinates = re.search(
            r'(\d{2}.\d{7},\d{2}.\d{7})', url).group(1)
        lat, lon = original_coordinates.split(',')
        lat = float(lat)
        lon = float(lon)
        if trash:
            lat += random.uniform(0.00001, 0.0001)
            lon += random.uniform(0.00001, 0.0001)
        else:
            lat += random.uniform(0.1, 1)
            lon += random.uniform(0.1, 1)
        return f"{round(lat,7)},{round(lon,7)}"

    def get_trash(self):
        self.read_csv()
        for row in self.read_csv():
            # Get images for trash and non-trash, according to the +/- ratio
            for i in range(int(self.ratio*10)):
                try:
                    self.download_image_illegally(self.get_random_coordinates(
                        row["Link"], trash=True), row["Size"], "data/images/newtrash")
                except AttributeError:
                    pass
            for j in range(int((1-self.ratio)*10)):
                try:
                    self.download_image_illegally(self.get_random_coordinates(
                        row["Link"], trash=False), row["Size"], "data/images/newnontrash")
                except AttributeError:
                    break

    def remove_labels(self):
        try:
            self.driver.execute_script(
                'st=document.createElement("style");st.type="text/css";st.appendChild(document.createTextNode("\\#omnibox-container, #minimap, .app-viewcard-strip,#vasquette,.scene-footer-container {display:none;}"));document.getElementsByTagName("head")[0].appendChild(st)')
        except Exception as e:
            print(e)


if __name__ == "__main__":
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get("https://maps.google.com")
    print("Everything is set up. Accept the cookies pls.")
    start = datetime.now()
    while datetime.now() < start+timedelta(seconds=5):
        pass

    s = SatDownloader(
        "AIzaSyCcRQrdVbgdfwFdH81Mhg1pGrnKTZtrUeM", "data/trash_data.csv", driver)
    s.get_trash()
