"""
Script to download satellite imagery from GMaps
"""
import csv
import re
import requests
import shutil

class SatDownloader():
    def __init__(self, true_false_split, key, csv_file):
        self.true_false_split = true_false_split
        self.key = key
        self.csv_file = csv_file
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
    def download_image(self,coordinates, size):
        """
        Gets a trash image given its coordinates and its size
        """
        zoom = 20 if int(size) > 2 else 25
        api_endpoint = f"https://maps.googleapis.com/maps/api/staticmap?center={coordinates}&zoom={zoom}&&size=1000x1000&maptype=satellite&key={self.key}"
        r = requests.get(api_endpoint, stream=True)
        if r.status_code == 200:
            with open(coordinates+".png", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)      

    def get_trash(self):
        self.read_csv()
        for row in self.read_csv():
            try:
                self.download_image(self.get_coordinates(row["Link"]), row["Size"])
            except AttributeError:
                pass
        
if __name__ == "__main__":
    s = SatDownloader(1, "AIzaSyCcRQrdVbgdfwFdH81Mhg1pGrnKTZtrUeM", "data/trash_data.csv")
    s.get_trash()