"""
Script to download satellite imagery from GMaps
"""
import csv
import re
import requests
import shutil
import random

class SatDownloader():
    def __init__(self, key, csv_file, ratio=0.5):
        self.key = key
        self.csv_file = csv_file
        self.ratio = ratio
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
    def download_image(self,coordinates, size, folder):
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
    def get_random_coordinates(self, url, trash=False):
        original_coordinates = re.search(r'(\d{2}.\d{7},\d{2}.\d{7})', url).group(1)
        lat,lon = original_coordinates.split(',')
        lat = float(lat)
        lon = float(lon)
        if trash:
            lat += random.uniform(0.00001, 0.0001)
            lon += random.uniform(0.00001, 0.0001)
        else:
            lat += random.uniform(0.0001, 0.001)
            lon += random.uniform(0.0001, 0.001)
        return f"{round(lat,7)},{round(lon,7)}" 

    def get_trash(self):
        self.read_csv()
        for row in self.read_csv():
            # Get images for trash and non-trash, according to the +/- ratio
            for i in range(int(self.ratio*10)):
                try:
                    self.download_image(self.get_random_coordinates(row["Link"], trash=True), row["Size"], "data/images/trash")
                except AttributeError:
                    pass
            for j in range(int((1-self.ratio)*10)):
                try:
                    self.download_image(self.get_random_coordinates(row["Link"], trash=False), row["Size"], "data/images/nontrash")
                except AttributeError:
                    break

        
if __name__ == "__main__":
    s = SatDownloader("AIzaSyCcRQrdVbgdfwFdH81Mhg1pGrnKTZtrUeM", "data/trash_data.csv")
    s.get_trash()