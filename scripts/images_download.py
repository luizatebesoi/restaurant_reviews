from os.path import dirname

import requests  # to get image from the web
import shutil
import pandas as pd
import os


def bulk_download(links, folder_name):
    for link in links:
        if pd.notna(link) and link != 'nan':

            r = requests.get(link, stream=True)
            if r.status_code == 200:
                filename = link.split("/")[-1]
                path = os.path.join(dirname(dirname(__file__)), os.path.join("{}/{}".format(folder_name, filename)))
                r.raw.decode_content = True
                with open(path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                print(filename)


def download(link, folder_name):
    if pd.notna(link) and link != 'nan':
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            filename = link.split("/")[-1]
            dirname = os.path.dirname
            path = os.path.join(dirname(dirname(__file__)), os.path.join("{}/{}".format(folder_name, filename)))
            r.raw.decode_content = True
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(filename)