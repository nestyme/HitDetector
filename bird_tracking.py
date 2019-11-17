from utils import *
import requests
from flask import Flask

def main():
    s = requests.Session()
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FPS, 150)
    while True:
        response = WaitForBump(camera)
        api_endpoint = "https://arngry.herokuapp.com/hit/{}/{}/{}".format(response[0],
                                                                          response[1], response[2])
        print(response)
        s.get(api_endpoint)
        time.sleep(1)


if __name__ == '__main__':
    main()
