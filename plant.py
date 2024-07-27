from PIL import Image, ImageFile
import pyautogui
import time

BREED_COMPLETE: ImageFile.ImageFile = Image.open("./images/breed_complete.png")
PLACE_IN_NURSERY: ImageFile.ImageFile = Image.open("./images/place_in_nursery.png")
BREED_RETRY: ImageFile.ImageFile = Image.open("./images/breed_retry.png")
BREED: ImageFile.ImageFile = Image.open("./images/breed.png")
NURSERY: ImageFile.ImageFile = Image.open("./images/nursery.png")
PLANT_EGG: ImageFile.ImageFile = Image.open("./images/plant_egg.png")
SELL_EGG: ImageFile.ImageFile = Image.open("./images/sell_egg.png")
CONFIRM_SELL: ImageFile.ImageFile = Image.open("./images/confirm_sell.png")

def locateOrRetry(image: ImageFile.ImageFile, region, count = 1):
    try:
        located_image = pyautogui.locateCenterOnScreen(image, minSearchTime=0.7, grayscale=True, confidence=0.4, region=region)
        #location_data = pyautogui.locateOnScreen(image, minSearchTime=1, grayscale=True, confidence=0.8, region=region)
        #print(f'Found {image} at region: {location_data}')
        #print(f'Located {image}')
        return located_image
    except:
        if count > 3:
            print(f'Unable to successfully find {image.filename}, aborting program')
            return None 
        else:
            print(f'Retrying {image.filename}')
            return locateOrRetry(image, region, count + 1)

def interactWithImage(image, region = (0, 50 * 2, 1100 * 2, 800 * 2)):
    start_search = time.perf_counter()
    location = locateOrRetry(image, region)
    end_search = time.perf_counter()
    print(f"Finished search for {image.filename} in {end_search - start_search:0.2f} seconds")
    #print(f' {image} is at {location}')
    if location is None:
        print(f'Failed to find {image.filename}')
        return False
    
    clickLocation(location=location)
    #end_interact = time.perf_counter()
    #print(f"Finished interaction of {image.filename} in {end_interact - end_search:0.2f} seconds")
    return location

from pynput.mouse import Button, Controller
_mouse = Controller()

def clickLocation(location):
    _mouse.position = (location.x // 2, location.y // 2) 
    time.sleep(0.1)
    _mouse.click(Button.left)

def clickXYLocation(x, y, delay: float = 0):
    _mouse.position = (x // 2, y // 2) 
    if delay > 0:
        time.sleep(delay)
    
    _mouse.click(Button.left)


def plant_cycle():
    breeding_cave = interactWithImage(BREED_COMPLETE, region=(480, 680, 100, 80))
    if breeding_cave is False:
        return False
    if interactWithImage(PLACE_IN_NURSERY, region=(720, 1320, 650, 100)) is False:
        return False
    clickXYLocation(x=breeding_cave.x, y=breeding_cave.y + 24, delay=0.4)
    if interactWithImage(BREED_RETRY, region=(400, 1400, 300, 300)) is False:
        return False
    if interactWithImage(BREED, region=(830, 1300, 440, 140)) is False:
        return False
    if interactWithImage(NURSERY, region=(1420, 850, 80, 140)) is False:
        return False
    if interactWithImage(PLANT_EGG, region=(40, 1430, 200, 200)) is False:
        return False
    if interactWithImage(SELL_EGG, region=(1280, 980, 240, 320)) is False:
        # Retry clicking the nursery, plant egg, and sell egg steps if needed
        if interactWithImage(NURSERY) is False:
            return False
        if interactWithImage(PLANT_EGG, region=(40, 1430, 200, 200)) is False:
            return False
        if interactWithImage(SELL_EGG, region=(1280, 980, 240, 320)) is False:
            return False
    if interactWithImage(CONFIRM_SELL, region=(510, 1310, 500, 130)) is False:
        return False
    return True


def main():
    print('Starting in 3')
    time.sleep(1)
    print('Starting in 2')
    time.sleep(1)
    print('Starting in 1')
    time.sleep(1)
    print('Activating Dragonvale bot')

    pyautogui.FAILSAFE = True

    for i in range(5000):
        start_cycle = time.perf_counter()
        success = plant_cycle()
        end_cycle = time.perf_counter()
        if success: 
            print(f"Finished cycle {i + 1} in {end_cycle - start_cycle:0.2f} seconds")
            time.sleep(0.25)
        elif success == False:
            print(f'Failed cycle {i + 1} in {end_cycle - start_cycle:0.2f} seconds')
            return
    

main()