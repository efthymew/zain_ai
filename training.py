import ubjson
import os
import slippi
import shutil

import numpy as np

from slippi.id import CSSCharacter

origin = "zain_games"

for root, dirs, files in os.walk(origin):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, "rb") as f:
            try:
                game = slippi.Game(f)
            except:
                continue



        

            print("hi")