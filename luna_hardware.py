import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

# Pin definitions for the LCD screen
# HD44780-combatible LCD in 4-bit mode
# No BL control (yet)
lcd_rs = digitalio.DigitalInOut(board.D21)
lcd_en = digitalio.DigitalInOut(board.D12)
lcd_d7 = digitalio.DigitalInOut(board.D19)
lcd_d6 = digitalio.DigitalInOut(board.D26)
lcd_d5 = digitalio.DigitalInOut(board.D16)
lcd_d4 = digitalio.DigitalInOut(board.D20)
lcd_bl = None

lcd_columns = 16
lcd_rows = 2

# Init the LCD driver
lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_bl)

# Status LED definition (GPS lock)
led = digitalio.DigitalInOut(board.D23)
led.direction = digitalio.Direction.OUTPUT