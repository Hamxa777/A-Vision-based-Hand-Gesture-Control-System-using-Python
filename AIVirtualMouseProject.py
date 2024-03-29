import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui


wCam, hCam = 640, 480
frameR = 120    # frame reduction
smoothening = 2

pTime = 0
plocX, plocY = 0,0
clocX, clocY = 0,0

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
print(wScr,hScr)


while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. Get tip of index & middle finger
    if len(lmList) != 0:
        x1,y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        print(fingers)

        try:
            # 4. Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 0:

                # 5. Convert Coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # 6. Smoothen Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move Mouse
                autopy.mouse.move(x3,y3)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # 8. Both Index & Last fingers are up, Clicking Mode
            if fingers[1] == 1 and fingers[2] == 1 and fingers[4] == 0:
                length , img, lineInfo = detector.findDistance(8,12,img)
                if length < 100:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    #autopy.mouse.click()
                    pyautogui.doubleClick()
                    #pyautogui.rightClick()
                    print('index & middle is up')

                    plocX, plocY = clocX, clocY

            # 9. Both Index & Last fingers are up, Right Clicking Mode
            if fingers[1] == 1 and fingers[4] == 1:
                length, img, lineInfo = detector.findDistance(8, 20, img)
                if length < 500:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.rightClick()
                    print('index & last is up')

                    plocX, plocY = clocX, clocY
        except:
            print("Error")

    # 11. Frame Rate
    cTime = time.time()
    fps = 1/((cTime)-(pTime))
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)