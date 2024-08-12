""" this file will be the script that runs embedded in dolphin it should:
    tally frames each frame drawn and store in a buffer until on the 11th frame then send
    the past 10 frames through a model and gather the next 10 frames of actions and store them in a buffer
    that the engine pulls from and sends to dolphin over the course of the next 10 frames, then repeat
"""