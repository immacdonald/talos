import pyautogui
import time

def locateOrRetry(image: str, region, count = 1):
    try:
        located_image = pyautogui.locateCenterOnScreen(image, minSearchTime=0.7, grayscale=True, confidence=0.4, region=region)
        #location_data = pyautogui.locateOnScreen(image, minSearchTime=1, grayscale=True, confidence=0.8, region=region)
        #print(f'Found {image} at region: {location_data}')
        #print(f'Located {image}')
        return located_image
    except:
        if count > 3:
            print(f'Unable to successfully find {image}, aborting program')
            return None 
        else:
            print(f'Retrying {image}')
            return locateOrRetry(image, region, count + 1)

def interactWithImage(image: str, region = (0, 50 * 2, 1100 * 2, 800 * 2)):
    start_search = time.perf_counter()
    location = locateOrRetry(f'images/{image}.png', region)
    end_search = time.perf_counter()
    print(f"Finished search for {image} in {end_search - start_search:0.2f} seconds")
    #print(f' {image} is at {location}')
    if location is None:
        print(f'Failed to find {image}')
        return False
    
    clickLocation(location=location)
    end_interact = time.perf_counter()
    print(f"Finished interaction of {image} in {end_interact - end_search:0.2f} seconds")
    return location


def clickLocation(location):
    pyautogui.leftClick(location.x // 2, location.y // 2) 

def clickXYLocation(x, y, delay: float = 0):
    if delay > 0:
        time.sleep(delay)
    pyautogui.leftClick(x // 2, y // 2) 


def plant_cycle():
    breeding_cave = interactWithImage('breed_complete', region=(480, 680, 100, 80))
    if breeding_cave is False:
        return False
    if interactWithImage('place_in_nursery', region=(720, 1320, 650, 100)) is False:
        return False
    clickXYLocation(x=breeding_cave.x, y=breeding_cave.y + 12, delay=0.2)
    if interactWithImage('breed_retry', region=(400, 1400, 300, 300)) is False:
        return False
    if interactWithImage('breed', region=(830, 1300, 440, 140)) is False:
        return False
    if interactWithImage('nursery', region=(1420, 850, 80, 140)) is False:
        return False
    if interactWithImage('plant_egg', region=(40, 1430, 200, 200)) is False:
        return False
    if interactWithImage('sell_egg', region=(1280, 980, 240, 320)) is False:
        # Retry clicking the nursery, plant egg, and sell egg steps if needed
        if interactWithImage('nursery') is False:
            return False
        if interactWithImage('plant_egg', region=(40, 1430, 200, 200)) is False:
            return False
        if interactWithImage('sell_egg', region=(1280, 980, 240, 320)) is False:
            return False
    if interactWithImage('confirm_sell', region=(510, 1310, 500, 130)) is False:
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
        print(f"Finished cycle {i + 1} in {end_cycle - start_cycle:0.2f} seconds")
        time.sleep(0.25)
        if success == False:
            print(f'Failed cycle {i + 1}')
            return
    

main()