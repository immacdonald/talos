from PIL import ImageGrab
import numpy as np
import cv2
from pynput.mouse import Button, Controller
import time
from functools import wraps

BREED_COMPLETE = cv2.imread("./images/breed_complete.png", 0)
PLACE_IN_NURSERY = cv2.imread("./images/place_in_nursery.png", 0)
BREEDING_CAVE = cv2.imread("./images/breeding_cave.png", 0)
BREED_RETRY = cv2.imread("./images/breed_retry.png", 0)
BREED = cv2.imread("./images/breed.png", 0)
NURSERY = cv2.imread("./images/nursery.png", 0)
PLANT_EGG = cv2.imread("./images/plant_egg.png", 0)
SELL_EGG = cv2.imread("./images/sell_egg.png", 0)
CONFIRM_SELL = cv2.imread("./images/confirm_sell.png", 0)

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return wrap

def locate_image(image, region):
    # Capture the screen
    img = ImageGrab.grab()
    img = img.crop(region)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

    w, h = image.shape[::-1] 

    # Perform template matching
    res = cv2.matchTemplate(img_cv, image, cv2.TM_CCOEFF_NORMED)

    # Specify a threshold 
    threshold = 0.7

    # Store the coordinates of matched area in a numpy array 
    loc = np.where(res >= threshold) 

    if len(loc) > 0:
        for pt in zip(*loc[::-1]): 
            #print('Found at', region[0] + pt[0], region[1] + pt[1], region[0] + pt[0] + w, region[1] + pt[1] + h)
            center = (region[0] + pt[0] + w // 2, region[1] + pt[1] + h // 2)
            return center

def locate_or_retry(image, name, region, count = 1):
    location = locate_image(image, region)
    if location:
        #print(f'Found {name} at {location[0]},{location[1]}')
        return {'x': location[0], 'y': location[1]}
    else:
        if count > 4:
            return None 
        else:
            print(f'Retrying {name}')
            return locate_or_retry(image, name, region, count + 1)

def interact_with_image(image, name: str, region = (0, 0, 2000, 1800)):
    location = locate_or_retry(image=image, name=name, region=region)
    if location is None:
        print(f'Unable to locate {name}')
        return False
    
    click_location(x=location['x'], y=location['y'])
    return location


_mouse = Controller()

def click_location(x, y, delay: float = 0.1):
    _mouse.position = (x // 2, y // 2) 
    if delay > 0:
        time.sleep(delay)
    
    _mouse.click(Button.left)


def plant_cycle(delay = 0.5, short_delay = 0.35):
    #@timing
    def breed_complete_sequence():
        breeding_cave = interact_with_image(BREED_COMPLETE, name='breed_complete', region=(580, 680, 680, 780))
        if breeding_cave is False:
            breeding_cave = interact_with_image(BREEDING_CAVE, name='breeding_cave')
            if breeding_cave is False:
                return False
        time.sleep(short_delay)
        if interact_with_image(PLACE_IN_NURSERY, name='place_in_nursery', region=(720, 1300, 1400, 1440)):
            return breeding_cave
        return False        

    #@timing
    def breed_retry_sequence():
        if interact_with_image(BREED_RETRY, name='breed_retry', region=(420, 1440, 720, 1820)):
            time.sleep(short_delay)
            if interact_with_image(BREED, name='breed', region=(700, 1200, 1380, 1540)):
                return True
        return False

    #@timing
    def nursery_sequence(region = (0, 0, 2000, 1800)):
        if interact_with_image(NURSERY, name='nursery', region=region):
            time.sleep(delay)
            if interact_with_image(PLANT_EGG, name='plant_egg', region=(0, 1400, 300, 1800)):
                time.sleep(short_delay)
                if interact_with_image(SELL_EGG, name='sell_egg', region=(1200, 960, 1540, 1340)):
                    return True
        return False
    
    breeding_cave_location = breed_complete_sequence()
    if not breeding_cave_location:
        print('Retrying incubate sequence')
        breeding_cave_location = breed_complete_sequence()
        if not breeding_cave_location:
            return False
    click_location(breeding_cave_location['x'], breeding_cave_location['y'], 0.4)
    time.sleep(delay)

    if not breed_retry_sequence():
        print('Retrying breed sequence')
        if not interact_with_image(BREEDING_CAVE, name='breeding_cave'):
            return False
        if not breed_retry_sequence():
            return False
    time.sleep(short_delay)

    if not nursery_sequence(region=(1320, 880, 1400, 980)):
        # Retry if it fails initially
        print('Retrying sell sequence')
        if not nursery_sequence():
            return False
    time.sleep(short_delay)

    if interact_with_image(CONFIRM_SELL, name='confirm_sell', region=(500, 1300, 1020, 1440)):
        time.sleep(short_delay)
        return True

    return False


def main():
    print('Starting in 3')
    time.sleep(1)
    print('Starting in 2')
    time.sleep(1)
    print('Starting in 1')
    time.sleep(1)
    print('Activating Dragonvale bot')

    for i in range(10000):
        start_cycle = time.perf_counter()
        success = plant_cycle()
        end_cycle = time.perf_counter()
        if success: 
            print(f"Finished cycle {i + 1} in {end_cycle - start_cycle:0.2f} seconds")
        else:
            print(f'Failed cycle {i + 1} in {end_cycle - start_cycle:0.2f} seconds')
            return
    

main()