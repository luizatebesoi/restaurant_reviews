import os
from os.path import dirname

import data_processing_functions_final as dpf
import images_download as dwn
import pandas as pd


def image_titles1(links):
    results = []
    for link in links:
        if pd.notna(link):
            filename = link.split("/")[-1]
            file = os.path.join(os.path.join(dirname(dirname(__file__)), "media/restaurants/images/"), filename)
            file = file.replace("\\","/")
            results.append(file)
        else:
            results.append(None)
    print(file)

image_titles1(["https://images.deliveryhero.io/image/fd-ro/LH/v3gk-listing.jpg"])