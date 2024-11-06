from PIL import Image
import numpy as np
import cv2
from pynput.mouse import Button, Controller
from time import sleep
from mss import mss

from Quartz import CGDisplayBounds, CGMainDisplayID

class Talos:
    def __init__(self, images, use_global_region=False, threshold=0.9):
        # Read the image data in upon initialization
        self.images = {
            name: {
                "image": cv2.imread(details["path"], 0),
                # Region is stored in "top, left, bottom, right"
                "region": tuple(map(int, details["region"].split(','))) if "region" in details else None
            }
            for name, details in images.items()
        }

        self.use_global_region = use_global_region
        self.threshold = threshold
        self.mouse = Controller()
        self.mouse_delay = 0.1
        self.retry_delay = 0.2
        self.scale_factor = self.get_display_scale()[0]

    def get_display_scale(self) -> tuple[float, float]:
        main_display = CGMainDisplayID()
        bounds = CGDisplayBounds(main_display)
        logical_width: int = bounds.size.width
        logical_height: int = bounds.size.height

        # Use screencapture for baseline of functional dimensions
        with mss() as sct:
            display = sct.monitors[1]
            sct_img = sct.grab(display)
            scaled_width: int = sct_img.width
            scaled_height: int = sct_img.height
        
        # Calculate scale difference between logical and functional dimensions
        scale_x: float = scaled_width / logical_width
        scale_y: float = scaled_height / logical_height

        #print(f"Scale factors are {scale_x}, {scale_y}")
        return scale_x, scale_y

    # Capture the entire screen or a specific region (given in logical dimensions)
    def capture_screen(self, region=None):
        with mss() as sct:
            display = {"top": region[0], "left": region[1], "width": (region[3]-region[1]), "height": (region[2]-region[0])} if region else sct.monitors[1]

            sct_img = sct.grab(display)
            return np.array(sct_img)[:, :, :3]
            #return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def locate_image(self, image, region):   
        img = self.capture_screen(region=region)
        img = cv2.resize(img, (int(img.shape[1] // self.scale_factor), int(img.shape[0] // self.scale_factor)))

        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        #cv2.imshow('Talos Debug Image', img_cv)
        #cv2.waitKey(0)

        image = cv2.resize(image, None, fx=0.5, fy=0.5)
        w, h = image.shape[::-1]

        all_matches = cv2.matchTemplate(img_cv, image, cv2.TM_CCOEFF_NORMED)

        matches = np.where(all_matches >= self.threshold)
        if matches[0].size > 0:
            location = next(zip(*matches[::-1]))
            base_region = (region[0] if region else 0, region[1] if region else 1)

            #print(f"Found image at {location[1] // self.scale_factor}, {location[0] // self.scale_factor}, {(location[1] + h) // self.scale_factor}, {(location[0] + w) // self.scale_factor}" )

            #center = base_region[1] + (location[0] + w // 2) // self.scale_factor, base_region[0] + (location[1] + h // 2) // self.scale_factor
            center = base_region[1] + (location[0] + w // 2), base_region[0] + (location[1] + h // 2)
            return center
        
        return None

    def locate_or_retry(self, image_name, use_global_region, retries, count=1):
        image_details = self.images.get(image_name)
        if not image_details:
            raise ValueError(f"Image '{image_name}' not found.")
        
        image, region = image_details["image"], image_details["region"]

        if use_global_region or self.use_global_region:
            region = None

        location = self.locate_image(image, region)

        if location:
            #print(f'Found {image_name} at {location[0]}, {location[1]}')
            return location
        elif count <= retries:
            #print(f"Retrying {image_name}")
            sleep(self.retry_delay)
            return self.locate_or_retry(image_name, use_global_region, retries, count + 1)
        else:
            print(f"Unable to locate {image_name}, retrying or ending program.")
            return None

    def click_location(self, x, y):
        #print(f'Attempting to click {x}, {y}')
        self.mouse.position = (x), (y)
        sleep(self.mouse_delay)
        self.mouse.click(Button.left)

    def interact_with_image(self, image_name, use_global_region, retries=4):
        location = self.locate_or_retry(image_name, use_global_region, retries)

        if location:
            self.click_location(location[0], location[1])
            return True
        
        return False