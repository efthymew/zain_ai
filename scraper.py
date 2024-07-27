import ubjson
import os
import slippi
import shutil

from slippi.id import CSSCharacter

origin = "Summit-11"

for root, dirs, files in os.walk(origin):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, "rb") as f:
            try:
                game = slippi.Game(f)
            except:
                continue
        # check to see players to find red marth
        for p in game.start.players:
            if not p:
                continue
            if p.character == CSSCharacter.MARTH and p.costume == 1 and p.type == 0:
                shutil.copyfile(file_path, f"zain_games/{file}")

print("hi")