from collections import deque
import numpy as np
import imutils
import cv2
import time


def CropAndRectangleImage(image):
    angle = -1.5
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)[200:-190, 420:-548]


def WaitForBump(camera):
    redLowerLeft = (0, 70, 50)
    redUpperLeft = (10, 255, 255)

    redLowerRight = (170, 70, 50)
    redUpperRight = (180, 255, 255)
    pts = deque(maxlen=64)
    while True:
        (grabbed, frame) = camera.read()
        frame = CropAndRectangleImage(frame)
        frame = imutils.resize(frame, width=800, height=600)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, redLowerLeft, redUpperLeft)
        mask = cv2.inRange(hsv, redLowerRight, redUpperRight)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if (radius < 500) & (radius > 50):
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # update the points queue
        pts.appendleft(center)
        # loop over the set of tracked points
        for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            # draw the connecting lines
            thickness = int(np.sqrt(64 / float(i + 1)) * 2)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
            # print("x={}, y={}".format(pts[i][0], pts[i][1]))
            if pts[i - 1][1] - pts[i][1] > 10:
                x, y = pts[i - 1][0], pts[i - 1][1]
                # print("bump at ({}, {})".format(x, y))
                hit_time=time.time()
                return (x, y, int(hit_time))
                cv2.circle(frame, pts[i - 1], int(radius), (255, 255, 255), 2)
        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()