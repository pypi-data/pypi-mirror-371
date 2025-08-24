import smbus
import time

class VanTurtle_Fan:
	FAN_ONE = 1
	FAN_TWO = 2

	REG_INPUT_PORT_0 = 0x00
	REG_INPUT_PORT_1 = 0x01

	REG_OUTPUT_PORT_0 = 0x02
	REG_OUTPUT_PORT_1 = 0x03

	REG_CONFIG_PORT_0 = 0x06
	REG_CONFIG_PORT_1 = 0x07

	BUTTON_PRESS_DURATION = 0.15

	def __init__(self, bus=1, address=0x27, no_blink=False):
		"""
		Initialize the VanTurtle Fan controller.

		:param bus: The I2C bus number (default is 1 on pi5).
		:param address: The I2C address of the fan controller, modifiable with the A0, A1 and A2 switches (default is 0x27).
		:param no_blink: If True, do not blink the LEDs on startup (default is False).
		"""

		# Connect to the I2C bus and set the address
		self._bus = smbus.SMBus(bus)
		self._address = address

		# Verify connection to the chip
		try:
			self._bus.read_byte_data(self._address, self.REG_CONFIG_PORT_0)
		except Exception as e:
			raise ConnectionError(f"Failed to connect to I2C device at address {hex(self._address)}, did you set the correct address?") from e

		# Set all pins to OUTPUT, except for P00 and P10, which are INPUTs for the hold LEDs (00000001)
		self._bus.write_byte_data(self._address, self.REG_CONFIG_PORT_0, 0x01)
		self._bus.write_byte_data(self._address, self.REG_CONFIG_PORT_1, 0x01)

		# Set all output pins to LOW (00000000)
		self._bus.write_byte_data(self._address, self.REG_OUTPUT_PORT_0, 0x00)
		self._bus.write_byte_data(self._address, self.REG_OUTPUT_PORT_1, 0x00)

		# Blink the LEDs indicate the controller is connected
		if not no_blink:
			self.led(self.FAN_ONE, True)
			self.led(self.FAN_TWO, True)
			time.sleep(self.BUTTON_PRESS_DURATION)
			self.led(self.FAN_ONE, False)
			self.led(self.FAN_TWO, False)

	def _getreg(self, fan):
		"""
		Returns the register for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: The register address for the specified fan.
		"""

		if fan not in (self.FAN_ONE, self.FAN_TWO):
			raise ValueError("Invalid fan number. Use FAN_ONE or FAN_TWO.")

		return self.REG_OUTPUT_PORT_0 if fan == 1 else self.REG_OUTPUT_PORT_1

	def _setpin(self, fan, pin, state):
		"""
		Sets the state of a specific pin for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:param pin: The pin number to set (1-7).
		:param state: True to set the pin HIGH, False to set it LOW.
		:return: Pin number if the operation was successful.
		"""

		reg = self._getreg(fan)
		# Read the current output state
		output = self._bus.read_byte_data(self._address, reg)

		# Set pin P01 or P11 to 0 or 1
		if state:
			output |= 1 << pin
		else:
			output &= ~(1 << pin)

		# Overwrite the state
		self._bus.write_byte_data(self._address, reg, output)

		return pin

	def press(self, fan, pin, length=False):
		"""
		Simulates a button press for the specified fan and pin.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:param pin: The pin number to press (1-7).
		:param length: Optional duration to hold the button down in seconds. If omitted, uses BUTTON_PRESS_DURATION.
		:return: Pin number if the operation was successful.
		"""

		# Default length is the time to hold the button down
		if length == False: length = self.BUTTON_PRESS_DURATION

		# Always turn on the LED to indicate activity
		# Do this first to that if the script crashes, the LED will still be on
		self.led(fan, True)
		# Set the pin to HIGH to simulate a button press
		self._setpin(fan, pin, True)

		# Wait for the specified length of time, the fan only polls once every +/- 100ms
		time.sleep(length)

		# Release the button by setting the pin to LOW and turn off the LED
		self._setpin(fan, pin, False)
		self.led(fan, False)

		return pin

	def get_autohold(self, fan):
		"""
		Returns the state of the Auto ("hold to set") LED for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: True if the Auto LED is on, False if it is off.
		"""

		if fan not in (self.FAN_ONE, self.FAN_TWO):
			raise ValueError("Invalid fan number. Use FAN_ONE or FAN_TWO.")

		# Get INPUT registers, not OUTPUT
		reg = self.REG_INPUT_PORT_0 if fan == 1 else self.REG_INPUT_PORT_1

		# Read all input states
		input_state = self._bus.read_byte_data(self._address, reg)

		# Get P00 or P10 from the least significant bit
		# Because the fan pulls low when the LED is on, we need to invert the result
		return not bool(input_state & 0x01)

	# Set the LED state for the specified fan
	def led(self, fan=False, state=True):
		"""
		Sets the LED state for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:param state: True to turn the LED on, False to turn it off.
		:return: Pin number if the operation was successful.
		"""
		return self._setpin(fan, 1, state)

	# Shorthand functions for specific button presses
	def auto(self, fan=False):
		"""
		Turn Auto on or off on the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		return self.press(fan, 2)

	def reverse(self, fan=False):
		"""
		Reverse airflow direction for the specified fan, button is labeled "In/Out".

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		return self.press(fan, 3)

	def faster(self, fan=False):
		"""
		Increase airflow speed for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		return self.press(fan, 5)

	def slower(self, fan=False):
		"""
		Lower airflow speed for the specified fan.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		return self.press(fan, 6)

	def beep(self, fan=False):
		"""
		Makes the specified fan beep with no change to its configuration.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		return self.press(fan, 7)


	# On off has some special handling
	def onoff(self, fan=False, beep=True):
		"""
		Turn on or off the specified fan, depending on its previous state.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful.
		"""
		# Without beeping first it will not react 100% of the time, so i guess we beep
		if beep:
			self.beep(fan)
			time.sleep(0.2)
			self.beep(fan)

		return self.press(fan, 4, self.BUTTON_PRESS_DURATION * 5)

	# Turning on auto will make the fan turn on when off, and stay on when already on
	# Therefore, if we turn on auto and then turn the fan off we know for sure it is off
	def reset(self, fan=False):
		"""
		Ensures the fan is off by pressing the Auto button followed by the On/Off button.

		:param fan: 1 for FAN_ONE, 2 for FAN_TWO
		:return: Pin number if the operation was successful
		"""
		self.auto(fan)
		time.sleep(self.BUTTON_PRESS_DURATION)
		return self.onoff(fan)
