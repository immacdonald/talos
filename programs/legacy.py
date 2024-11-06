from PIL import ImageGrab
import numpy as np
import cv2
from pynput.mouse import Button, Controller
from time import sleep, time, perf_counter

# Load images once
IMAGES = {
    "BREED_COMPLETE": cv2.imread("./images/breed_complete.png", 0),
    "PLACE_IN_NURSERY": cv2.imread("./images/place_in_nursery.png", 0),
    "BREEDING_CAVE": cv2.imread("./images/breeding_cave.png", 0),
    "BREED_RETRY": cv2.imread("./images/breed_retry.png", 0),
    "BREED": cv2.imread("./images/breed.png", 0),
    "NURSERY": cv2.imread("./images/nursery_small.png", 0),
    "PLANT_EGG": cv2.imread("./images/plant_egg.png", 0),
    "SELL_EGG": cv2.imread("./images/sell_egg.png", 0),
    "CONFIRM_SELL": cv2.imread("./images/confirm_sell.png", 0),
}


def locate_image(image, region):
    img = ImageGrab.grab(bbox=region)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

    image = cv2.resize(image, None, fx=0.5, fy=0.5)
    w, h = image.shape[::-1]

    res = cv2.matchTemplate(img_cv, image, cv2.TM_CCOEFF_NORMED)

    threshold = 0.9
    loc = np.where(res >= threshold)
    if loc[0].size > 0:
        for pt in zip(*loc[::-1]):
            # print('Found at', (region[0] + pt[0]) * 2, (region[1] + pt[1]) * 2, (region[0] + pt[0] + w) * 2, (region[1] + pt[1] + h) * 2)
            center = (
                (region[0] + pt[0] + w // 2) * 2,
                (region[1] + pt[1] + h // 2) * 2,
            )
            return center


def locate_or_retry(image, name, region, retries, count=1):
    location = locate_image(image, region)
    if location:
        # print(f'Found {name} at {location[0]}, {location[1]}')
        return {"x": location[0], "y": location[1]}
    else:
        if count > retries:
            return None
        else:
            print(f"Retrying {name}")
            sleep(0.3)
            return locate_or_retry(image, name, region, retries, count + 1)


def interact_with_image(image, name: str, region=(0, 0, 2000, 1800), retries=4):
    location = locate_or_retry(
        image=image,
        name=name,
        region=(region[0] // 2, region[1] // 2, region[2] // 2, region[3] // 2),
        retries=retries,
    )
    if location is None:
        print(f"Unable to locate {name}")
        return False
    click_location(x=location["x"], y=location["y"])
    return location


_mouse = Controller()


def click_location(x, y, delay: float = 0.1):
    _mouse.position = (x // 2, y // 2)
    if delay > 0:
        sleep(delay)
    _mouse.click(Button.left)


def plant_cycle(delay=0.7, short_delay=0.4):
    def breed_complete_sequence(complete_region=(540, 600, 700, 900)):
        breeding_cave = interact_with_image(
            IMAGES["BREED_COMPLETE"],
            name="breed_complete",
            region=complete_region,
            retries=30,
        )
        if breeding_cave is False:
            return False
        sleep(delay)
        if interact_with_image(
            IMAGES["PLACE_IN_NURSERY"],
            name="place_in_nursery",
            region=(720, 1300, 1400, 1440),
        ):
            return breeding_cave
        return False

    def breed_retry_sequence(cave_region=(600, 700, 850, 950)):
        if interact_with_image(
            IMAGES["BREEDING_CAVE"], name="breeding_cave", region=cave_region
        ):
            sleep(delay)
            if interact_with_image(
                IMAGES["BREED_RETRY"], name="breed_retry"
            ):
                sleep(short_delay)
                if interact_with_image(
                    IMAGES["BREED"], name="breed", region=(700, 1200, 1380, 1540)
                ):
                    return True
        return False

    def nursery_sequence(nursery_region=(1320, 880, 1600, 1280)):
        if interact_with_image(
            IMAGES["NURSERY"], name="nursery", region=nursery_region, retries=15
        ):
            sleep(1)
            if interact_with_image(
                IMAGES["PLANT_EGG"], name="plant_egg", region=(0, 1400, 500, 1900)
            ):
                sleep(short_delay)
                if interact_with_image(
                    IMAGES["SELL_EGG"], name="sell_egg", region=(1100, 960, 1740, 1340)
                ):
                    return True
        return False

    global_region = (0, 0, 2000, 1800)

    if not breed_complete_sequence():
        print("Retrying incubate sequence")
        if not breed_complete_sequence(complete_region=global_region):
            return False
    sleep(delay)

    if not breed_retry_sequence():
        print("Retrying breed sequence")
        if not breed_retry_sequence(cave_region=global_region):
            return False
    sleep(short_delay)

    if not nursery_sequence():
        print("Retrying sell sequence")
        if not nursery_sequence(nursery_region=global_region):
            return False
    sleep(short_delay)

    if interact_with_image(
        IMAGES["CONFIRM_SELL"], name="confirm_sell", region=(500, 1300, 1020, 1440)
    ):
        sleep(short_delay)
        return True

    return False


def format_time(elapsed):
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = elapsed % 60

    return f"{hours:02}:{minutes:02}:{seconds:04.1f}"


def main():
    print("Starting in 3")
    sleep(1) 
    print("Starting in 2")
    sleep(1)
    print("Starting in 1")
    sleep(1)
    print("Activating Dragonvale Plant Cycler v1.0")

    double_day = True
    double_value = 2 if double_day else 1
    currency = 'candy corn'

    start_time = time()

    for i in range(10000):
        start_cycle = perf_counter()
        success = plant_cycle()
        end_cycle = perf_counter()
        ec_count = (i + 1) * 3 * double_value
        if success:
            print(
                f"Cycle {i + 1} in {end_cycle - start_cycle:0.2f}s, total of {ec_count} {currency} over {format_time(time() - start_time)}"
            )
        else:
            print(
                f"Terminated at cycle {i + 1} for a total of {ec_count} {currency} over {format_time(time() - start_time)}"
            )
            return


if __name__ == "__main__":
    main()
