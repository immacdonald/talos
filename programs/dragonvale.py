from os import path
from itertools import count
from time import sleep, time, perf_counter

from talos import Talos

format_time = lambda elapsed: f"{int(elapsed // 3600):02}:{int((elapsed % 3600) // 60):02}:{elapsed % 60:04.1f}"

def plant_cycle(talos: Talos, delay=0.6, short_delay=0.3):
    # Define sequences
    def breed_complete_sequence(global_region = False):
        if talos.interact_with_image("BREED_COMPLETE", global_region, retries=30):
            sleep(delay)
            return talos.interact_with_image("PLACE_IN_NURSERY", global_region)

    def breed_retry_sequence(global_region = False):
        if talos.interact_with_image("BREEDING_CAVE", global_region):
            sleep(delay)
            if talos.interact_with_image("BREED_RETRY", global_region):
                sleep(short_delay)
                return talos.interact_with_image("BREED", global_region)

    def nursery_sequence(global_region = False):
        if talos.interact_with_image("NURSERY", global_region):
            sleep(delay)
            if talos.interact_with_image("PLANT_EGG", global_region):
                sleep(short_delay)
                return talos.interact_with_image("SELL_EGG", global_region)

    if not breed_complete_sequence():
        print("Retrying incubate sequence")
        if not breed_complete_sequence(True):
            return False

    # Execute sequences
    if not breed_retry_sequence():
        print("Retrying breed sequence")
        if not breed_retry_sequence(True):
            return False
    sleep(short_delay)

    if not nursery_sequence():
        print("Retrying sell sequence")
        if not nursery_sequence(True):
            return False
    sleep(short_delay)

    if talos.interact_with_image("CONFIRM_SELL", False):
        sleep(short_delay)
        return True

    return False

# Main function
def main():
    images = {
        "BREED_COMPLETE": {
            "path": "images/breed_complete.png",
            "region": "340, 290, 400, 350"
        },
        "PLACE_IN_NURSERY": {
            "path": "images/place_in_nursery.png",
            "region": "640, 340, 730, 710"
        },
        "BREEDING_CAVE": {
            "path": "images/breeding_cave.png",
            "region": "400, 290, 460, 360"
        },
        "BREED_RETRY": {
            "path": "images/breed_retry.png",
            "region": "710, 270, 810, 390"
        },
        "BREED": {
            "path": "images/breed.png",
            "region": "640, 400, 730, 650"
        },
        "NURSERY": {
            "path": "images/nursery_small.png",
            "region": "500, 700, 550, 770"
        },
        "PLANT_EGG": {
            "path": "images/plant_egg.png",
            "region": "750, 100, 840, 200"
        },
        "SELL_EGG": {
            "path": "images/sell_egg.png",
            "region": "480, 540, 660, 690"
        },
        "CONFIRM_SELL": {
            "path": "images/confirm_sell.png",
            "region": "640, 240, 740, 520"
        }
    }

    dir = path.dirname(__file__)

    for details in images.values():
        details['path'] = path.join(dir, details['path'])


    talos = Talos(images, True)
    
    print("Starting in 3")
    sleep(1) 
    print("Starting in 2")
    sleep(1)
    print("Starting in 1")
    sleep(1)
    print("Activating Dragonvale Plant Cycler v1.0")
    
    start_time = time()
    double_day = True
    double_value = 2 if double_day else 1
    currency = 'candy corn'
    ec_count = 0

    for i in count():
        start_cycle = perf_counter()
        success = plant_cycle(talos)
        end_cycle = perf_counter()

        if success:
            ec_count += 3 * double_value
            print(f"Cycle {i + 1} in {end_cycle - start_cycle:0.2f}s, total of {ec_count} {currency} over {format_time(time() - start_time)}")
        else:
            print(f"Terminated at cycle {i} for a total of {ec_count} {currency} over {format_time(time() - start_time)}")
            return

if __name__ == "__main__":
    main()