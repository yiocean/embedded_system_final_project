
import time
from rpi_ws281x import PixelStrip, Color
import argparse

LED_COUNT = 64
LED_PIN = 18

LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

def colorWipe(strip, color, wait_ms=20):
    """一次擦除顯示像素的顏色。"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def light_selected_range(strip, segments, color=Color(255, 0, 0), wait_ms=1000):
    """只亮指定範圍內的燈"""

    # start = segment * 7
    # end = start + 6
    # for i in range(strip.numPixels()):
    #     if start <= i < end:
    #         strip.setPixelColor(i, color)
        # else:
        #     strip.setPixelColor(i, 0)
    # segments = 

    expanded = [x for val in segments for x in [val]*7]
    for i in range(56):
        if expanded[i]:
            strip.setPixelColor(i, color)
        else:
            strip.setPixelColor(i, 0)

    strip.show()
    time.sleep(wait_ms / 1000.0)
    for i in range(56):
        strip.setPixelColor(i, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    lights = [
        [1,1,0,0,1,1,1],  # '1'
        [1,1,1,1,0,0,1],  # '1'
        [0,0,0,0,0,0,0],  # '0'
    ]

    try:
        for light in lights:
            print("Lighting LED 16~18.")
            light_selected_range(strip=strip, segments=light)

        colorWipe(strip, Color(0, 0, 0), 100)

    except:
        colorWipe(strip, Color(0, 0, 0), 100)
