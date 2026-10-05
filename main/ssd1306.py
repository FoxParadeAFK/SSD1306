from machine import I2C, Pin
from micropython import const

# reference: https://www.reddit.com/r/PixelArt/comments/ppcd19/smallest_legible_pixel_fonts/
# 3x3 microfont
FONT: dict[str, list[int]] = {
    'a': [0x6, 0x7, 0x7],
    'b': [0x7, 0x6, 0x6],
    'c': [0x7, 0x5, 0x5],
    'd': [0x6, 0x6, 0x7],
    'e': [0x7, 0x7, 0x5],
    'f': [0x7, 0x3, 0x1],
    'g': [0x7, 0x7, 0x6],
    'h': [0x7, 0x2, 0x7],
    'i': [0x5, 0x7, 0x5],
    'j': [0x5, 0x7, 0x1],
    'k': [0x7, 0x2, 0x5],
    'l': [0x7, 0x4, 0x4],
    'm': [0x7, 0x3, 0x7],
    'n': [0x7, 0x1, 0x7],
    'o': [0x7, 0x5, 0x7],
    'p': [0x7, 0x3, 0x3],
    'q': [0x3, 0x3, 0x7],
    'r': [0x7, 0x3, 0x5],
    's': [0x4, 0x7, 0x1],
    't': [0x1, 0x7, 0x1],
    'u': [0x7, 0x4, 0x7],
    'v': [0x3, 0x4, 0x3],
    'w': [0x7, 0x6, 0x7],
    'x': [0x5, 0x2, 0x5],
    'y': [0x3, 0x6, 0x3],
    'z': [0x1, 0x7, 0x4],
    '1': [0x1, 0x7, 0x0],
    '2': [0x1, 0x7, 0x4],
    '3': [0x5, 0x7, 0x7],
    '4': [0x3, 0x2, 0x7],
    '5': [0x4, 0x7, 0x1],
    '6': [0x7, 0x6, 0x6],
    '7': [0x1, 0x3, 0x7],
    '8': [0x7, 0x7, 0x7],
    '9': [0x3, 0x3, 0x7],
    '0': [0x7, 0x5, 0x7],
    '\'': [0x0, 0x1, 0x0],
    '\"': [0x1, 0x0, 0x1],
    '^': [0x2, 0x1, 0x2],
    '-': [0x2, 0x2, 0x2],
    '=': [0x5, 0x5, 0x5],
    '_': [0x4, 0x4, 0x4],
    '+': [0x2, 0x7, 0x2],
    '[': [0x7, 0x5, 0x0],
    ']': [0x0, 0x5, 0x7],
    '{': [0x2, 0x7, 0x5],
    '}': [0x5, 0x7, 0x2],
    '<': [0x2, 0x5, 0x0],
    '>': [0x0, 0x5, 0x2],
    '\\': [0x1, 0x2, 0x4],
    '/': [0x4, 0x2, 0x1],
    '|': [0x0, 0x7, 0x0],
    ' ': [0x0, 0x0, 0x0],
}

# reference p.20 8.1.5.2
_SLAVE_ADDRESS: int = const(0x3C)
''' __Either addressed to 0x3C or 0x3D__   
    Used to establish transmissions connection
'''
_CONTROL_BYTE: int = const(0x00)
''' __Consist of CO and D/C bits followed by six '0's__   
    `CO`: if logic '0' then the following information is data bytes only   
    `D/C`: if logic '0' the next data byte is a command, else logic '1' defines a GDDRAM data
'''

_MUX_RATIO: int = const(0xA8)
_DISPLAY_OFFSET: int = const(0xD3)
_DISPLAY_START_LINE: int = const(0x40)
_SEGMENT_REMAP: int = const(0xA0)
_COM_OUTPUT_SCAN_DIRECTION: int = const(0xC0)
_COM_PINS_HARDWARE_CONFIGURATION: int = const(0xDA)
_CONTRAST_CONTROL: int = const(0x81)
_MEMORY_ADDRESS_MODE: int = const(0x20)
_COLUMN_ADDRESS: int = const(0x21)
_PAGE_ADDRESS: int = const(0x22)
_ENTIRE_DISPLAY: int = const(0xA4)
_NORMAL_DISPLAY: int = const(0xA6)
_OSCILLATOR_FREQUENCY: int = const(0xD5)
_CHARGE_PUMP: int = const(0x8D)
_DISPLAY: int = const(0xAE)

i2c: I2C = I2C(sda = Pin(16), scl = Pin(17))
buffer: list[int] = []
page_buffer: list[int] = []

i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x00, bytearray([
    _MUX_RATIO, 0x3F,
    _DISPLAY_OFFSET, 0x00,
    _DISPLAY_START_LINE,
    _SEGMENT_REMAP | 0x00,
    _COM_OUTPUT_SCAN_DIRECTION | 0x00,
    _COM_PINS_HARDWARE_CONFIGURATION, 0x12,
    _CONTRAST_CONTROL, 0x7F,
    _MEMORY_ADDRESS_MODE, 0x00,
    _COLUMN_ADDRESS, 0x00, 0x7F,
    _PAGE_ADDRESS, 0x00, 0x07,
    _ENTIRE_DISPLAY | 0x00,
    _NORMAL_DISPLAY | 0x00,
    _OSCILLATOR_FREQUENCY, 0x80,
    _CHARGE_PUMP, 0x14,
    _DISPLAY | 0x01
]))

i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x40, bytearray([0x00] * 1024))

raw: list[int] = open('triangle.bin', 'rb').read()
CURSOR: list[int] = [20, 2]
RAW_WIDTH: int = 13

i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x00, bytearray([
    _COLUMN_ADDRESS, CURSOR[0], CURSOR[0] + RAW_WIDTH - 1,
    _PAGE_ADDRESS, CURSOR[1], 0x07
]))

def translate_raw_intensity(_byte_pos: int) -> int:
    return 0x1 if raw[_byte_pos] > 0 else 0x0

for _byte_pos in range(len(raw)):
    col: int = _byte_pos % RAW_WIDTH
    seg: int = _byte_pos // RAW_WIDTH

    if seg % 8 == 7 and col == RAW_WIDTH - 1: 
        buffer.extend(page_buffer)
        page_buffer.clear()

    elif seg % 8 == 0: 
        page_buffer.append(translate_raw_intensity(_byte_pos))
    else:
        page_seg: int = seg % 8
        col_seg_byte: int = (translate_raw_intensity(_byte_pos)) << page_seg
        page_buffer[col] = page_buffer[col] | col_seg_byte

i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x40, bytearray(buffer)) 