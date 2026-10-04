from machine import I2C, Pin
from micropython import const

_SLAVE_ADDRESS: int = const(0x3C)
_CONTROL_BYTE: int = const(0x00)

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