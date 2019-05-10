"""
`dasdeployer.rgb`
====================================================

Helper class for the ring of RGB LED's that surround the big button
which are part of the same addressable matrix with the 8 RGB LED ring
inside the button.

* Author(s): Martin Woodward

**Hardware:**

"* `112mm 32 WS2812B 5050 RGB LED Ring (Adafruit Neopixel compatible) <https://amzn.to/2V5ClD0>`_"
"* `32mm 8 WS2812B 5050 RGB LED Ring (Adafruit Neopixel compatible) <https://amzn.to/2KKgZqD>`_"

**Software and Dependencies:**

* Adafruit_CircuitPython_NeoPixel https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel

"""

import time
import neopixel
import board
import threading, queue

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/martinwoodward/DasDeployer.git"

_PIXEL_PIN = board.D21 # NeoPixels must be connected to 10, 12, 18 or 21 to work.
_RING_PIXELS = 32
_BUTTON_PIXELS = 8
_NUM_PIXELS = _RING_PIXELS + _BUTTON_PIXELS
_ORDER = neopixel.GRB # The ones I purchased have red and green reversed

class Color:
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)

class RGBButton():
    def __init__(self, brightness=0.2, fps=25):
        self.brightness = brightness
        self.delay = 1/fps
        self.pixels = neopixel.NeoPixel(
            _PIXEL_PIN, _NUM_PIXELS, brightness=self.brightness, auto_write=False, pixel_order=_ORDER)
        self._animate_thread = None

    def off(self):
        self._animate_stop()
        self.pixels.fill((0,0,0))
        self.pixels.show()

    def fill(self, color):
        self._animate_stop()
        self.pixels.fill(color)
        self.pixels.show()

    def _animate_stop(self):
        if getattr(self, '_animate_thread', None):
            self._animate_thread.stop()
        self._animate_thread = None        
    
    def _animate_start(self):
        self._animate_stop()
        self._animate_thread = AnimateThread(self.pixels,0.5)
        self._animate_thread.start()

    def pulse(self, color=Color.WHITE):
        self._animate_start()

class AnimateThread(threading.Thread):
    def __init__(self, pixels, delay):
        super(AnimateThread, self).__init__()
        self.daemon = True
        self.stoprequest = threading.Event()
        self.pixels = pixels
        self.delay = delay

    def start(self):
        self.stoprequest.clear()
        super(AnimateThread, self).start()

    def stop(self, timeout=10):
        self.stoprequest.set()
        self.join(timeout)

    def join(self, timeout=None):
        super(AnimateThread, self).join(timeout)
        if self.is_alive():
            assert timeout is not None
            raise RuntimeError(
                "Thread failed to die within %d seconds" % timeout)
    
    def run(self):
        while True:
            self.pixels.fill(Color.RED)
            self.pixels.show()
            if self.stoprequest.wait(self.delay):
                break
            self.pixels.fill(Color.GREEN)
            self.pixels.show()
            if self.stoprequest.wait(self.delay):
                break
            self.pixels.fill(Color.BLUE)
            self.pixels.show()
            if self.stoprequest.wait(self.delay):
                break
    
