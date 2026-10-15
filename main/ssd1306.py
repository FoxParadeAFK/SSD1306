from machine import I2C, Pin
from math import ceil
from micropython import const

# reference: https://www.reddit.com/r/PixelArt/comments/ppcd19/smallest_legible_pixel_fonts/
# 3x3 microfont
MICRO_FONT: dict[str, list[int]] = {
    'a': [0x6, 0x7, 0x7, 0x0],
    'b': [0x7, 0x6, 0x6, 0x0],
    'c': [0x7, 0x5, 0x5, 0x0],
    'd': [0x6, 0x6, 0x7, 0x0],
    'e': [0x7, 0x7, 0x5, 0x0],
    'f': [0x7, 0x3, 0x1, 0x0],
    'g': [0x7, 0x7, 0x6, 0x0],
    'h': [0x7, 0x2, 0x7, 0x0],
    'i': [0x5, 0x7, 0x5, 0x0],
    'j': [0x5, 0x7, 0x1, 0x0],
    'k': [0x7, 0x2, 0x5, 0x0],
    'l': [0x7, 0x4, 0x4, 0x0],
    'm': [0x7, 0x3, 0x7, 0x0],
    'n': [0x7, 0x1, 0x7, 0x0],
    'o': [0x7, 0x5, 0x7, 0x0],
    'p': [0x7, 0x3, 0x3, 0x0],
    'q': [0x3, 0x3, 0x7, 0x0],
    'r': [0x7, 0x3, 0x5, 0x0],
    's': [0x4, 0x7, 0x1, 0x0],
    't': [0x1, 0x7, 0x1, 0x0],
    'u': [0x7, 0x4, 0x7, 0x0],
    'v': [0x3, 0x4, 0x3, 0x0],
    'w': [0x7, 0x6, 0x7, 0x0],
    'x': [0x5, 0x2, 0x5, 0x0],
    'y': [0x3, 0x6, 0x3, 0x0],
    'z': [0x1, 0x7, 0x4, 0x0],
    '1': [0x1, 0x7, 0x0, 0x0],
    '2': [0x1, 0x7, 0x4, 0x0],
    '3': [0x5, 0x7, 0x7, 0x0],
    '4': [0x3, 0x2, 0x7, 0x0],
    '5': [0x4, 0x7, 0x1, 0x0],
    '6': [0x7, 0x6, 0x6, 0x0],
    '7': [0x1, 0x3, 0x7, 0x0],
    '8': [0x7, 0x7, 0x7, 0x0],
    '9': [0x3, 0x3, 0x7, 0x0],
    '0': [0x7, 0x5, 0x7, 0x0],
    '\'': [0x0, 0x1, 0x0, 0x0],
    '\"': [0x1, 0x0, 0x1, 0x0],
    '^': [0x2, 0x1, 0x2, 0x0],
    '-': [0x2, 0x2, 0x2, 0x0],
    '=': [0x5, 0x5, 0x5, 0x0],
    '_': [0x4, 0x4, 0x4, 0x0],
    '+': [0x2, 0x7, 0x2, 0x0],
    '[': [0x7, 0x5, 0x0, 0x0],
    ']': [0x0, 0x5, 0x7, 0x0],
    '{': [0x2, 0x7, 0x5, 0x0],
    '}': [0x5, 0x7, 0x2, 0x0],
    '<': [0x2, 0x5, 0x0, 0x0],
    '>': [0x0, 0x5, 0x2, 0x0],
    '\\': [0x1, 0x2, 0x4, 0x0],
    '/': [0x4, 0x2, 0x1, 0x0],
    '|': [0x0, 0x7, 0x0, 0x0],
    ':': [0x0, 0x5, 0x0, 0x0],
    '.': [0x0, 0x4, 0x0, 0x0],
    ' ': [0x0, 0x0, 0x0, 0x0],
}

BINARY_FONT: dict[str, list[int]] = {
    '0': [0x00],
    '1': [0x01],
}

MICRO_FONT_GRADIENT: list[list[int]] = [MICRO_FONT[' '], MICRO_FONT['.'], MICRO_FONT[':'], MICRO_FONT['-'], 
                                        MICRO_FONT['1'], MICRO_FONT['|'], MICRO_FONT['+'], MICRO_FONT['x'], 
                                        MICRO_FONT['='], MICRO_FONT['c'], MICRO_FONT['h'], MICRO_FONT['o'], 
                                        MICRO_FONT['a'], MICRO_FONT['w'], MICRO_FONT['m'], MICRO_FONT['8']]

BINARY_FONT_GRADIENT: list[list[int]] = [BINARY_FONT['0'], BINARY_FONT['1']]

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
_NORMAL_DISPLAY: int = const(0xA7)
_OSCILLATOR_FREQUENCY: int = const(0xD5)
_CHARGE_PUMP: int = const(0x8D)
_DISPLAY: int = const(0xAE)

i2c: I2C = I2C(sda = Pin(16), scl = Pin(17))

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

_COMMONS: int = const(0x80)
_SEGMENTS: int = const(0x40)
_BYTE: int = const(0x08)

_RAW_WIDTH: int = const(16)
_RAW_HEIGHT: int = const(16)
RAW: list[int] = open('circle.bin', 'rb').read()
RAW_LENGTH: int = len(RAW) 

_FONT_SIZE: int = const(0x04)
''' __Size N where N represents the font dimensions NxN__
'''
FONT_PAGE_SIZE: int = _BYTE // _FONT_SIZE
''' __Amount a characters a given font size will take per page__  
    Examples with a font size '0x01' indicate 8 and a font size '0x04' indicate 2
'''
FONT: dict[str, list[int]] = MICRO_FONT
GRADIENT: list[list[int]] = MICRO_FONT_GRADIENT
GRADIENT_INCREMENTS: int = 256 // len(GRADIENT)

CURSOR: tuple = (0, 43)

buffer: bytearray = bytearray(_COMMONS * _SEGMENTS // _BYTE)
i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x40, buffer)

for _raw_byte_pointer in range(RAW_LENGTH):
    # raw image information
    raw_colunm_pointer: int = _raw_byte_pointer % _RAW_WIDTH
    raw_row_pointer: int = _raw_byte_pointer // _RAW_WIDTH

    raw_pixel: int = RAW[_raw_byte_pointer]
    raw_pixel_representation: list[int] = GRADIENT[raw_pixel // GRADIENT_INCREMENTS]

    # buffer information
    buffer_commons_pointer: int = raw_colunm_pointer * _FONT_SIZE + CURSOR[0]
    buffer_segments_pointer: int = raw_row_pointer * _FONT_SIZE + CURSOR[1]

    buffer_page_pointer: int = buffer_segments_pointer // _BYTE
    page_offset: int = buffer_segments_pointer % _BYTE

    # if buffer_page_pointer > 4: break

    # print(f"{buffer_segments_pointer:4}", end = " ")

    for _font_byte_pointer in range(_FONT_SIZE):   
        if buffer_commons_pointer + _font_byte_pointer > _COMMONS - 1: break
        if buffer_segments_pointer > _SEGMENTS - 1: break

        raw_pixel_adjusted: int = raw_pixel_representation[_font_byte_pointer] << page_offset
        raw_pixel_overflow: int = raw_pixel_adjusted >> 8

        buffer_overflow_page_pointer: int = buffer_page_pointer + 1

        if raw_pixel_overflow > 0 and buffer_overflow_page_pointer < _BYTE - 1:
            buffer[(buffer_overflow_page_pointer * _COMMONS) + buffer_commons_pointer + _font_byte_pointer] |= raw_pixel_overflow

        buffer[(buffer_page_pointer * _COMMONS) + buffer_commons_pointer + _font_byte_pointer] |= raw_pixel_adjusted
        
i2c.writeto_mem(_SLAVE_ADDRESS, _CONTROL_BYTE | 0x40, bytearray(buffer)) 