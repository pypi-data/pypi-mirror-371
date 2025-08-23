from machine import Pin, PWM, Timer, ADC, I2C
from micropython import schedule
from time import ticks_ms, ticks_us, sleep, sleep_ms
import dht, neopixel

###############################################################################
# EXCEPTIONS
###############################################################################

class PWMChannelAlreadyInUse(Exception):
    pass

class EventFailedScheduleQueueFull(Exception):
    pass

###############################################################################
# SUPPORTING CLASSES
###############################################################################

def clamp(n, low, high): return max(low, min(n, high))

def pinout(output=True):
    """
    Returns a textual representation of the Raspberry Pi pico pins and functions.

    :param bool output:
        If :data:`True` (the default) the pinout will be "printed".
        
    """
    pins = """        ---usb---
GP0  1  |o     o| -1  VBUS
GP1  2  |o     o| -2  VSYS
GND  3  |o     o| -3  GND
GP2  4  |o     o| -4  3V3_EN
GP3  5  |o     o| -5  3V3(OUT)
GP4  6  |o     o| -6           ADC_VREF
GP5  7  |o     o| -7  GP28     ADC2
GND  8  |o     o| -8  GND      AGND
GP6  9  |o     o| -9  GP27     ADC1
GP7  10 |o     o| -10 GP26     ADC0
GP8  11 |o     o| -11 RUN
GP9  12 |o     o| -12 GP22
GND  13 |o     o| -13 GND
GP10 14 |o     o| -14 GP21
GP11 15 |o     o| -15 GP20
GP12 16 |o     o| -16 GP19
GP13 17 |o     o| -17 GP18
GND  18 |o     o| -18 GND
GP14 19 |o     o| -19 GP17
GP15 20 |o     o| -20 GP16
        ---------"""

    if output:
        print(pins)
    return pins

class PinMixin:
    """
    Mixin used by devices that have a single pin number.
    """

    @property
    def pin(self):
        """
        Returns the pin number used by the device.
        """
        return self._pin_num

    def __str__(self):
        return "{} (pin {})".format(self.__class__.__name__, self._pin_num)

class PinsMixin:
    """
    Mixin used by devices that use multiple pins.
    """

    @property
    def pins(self):
        """
        Returns a tuple of pins used by the device.
        """
        return self._pin_nums

    def __str__(self):
        return "{} (pins - {})".format(self.__class__.__name__, self._pin_nums)
        
class ValueChange:
    """
    Internal class to control the value of an output device. 

    :param OutputDevice output_device:
        The OutputDevice object you wish to change the value of.

    :param generator:
        A generator function that yields a 2d list of
        ((value, seconds), *).
        
        The output_device's value will be set for the number of
        seconds.

    :param int n:
        The number of times to repeat the sequence. If None, the
        sequence will repeat forever. 
    
    :param bool wait:
        If True the ValueChange object will block (wait) until
        the sequence has completed.
    """
    def __init__(self, output_device, generator, n, wait):
        self._output_device = output_device
        self._generator = generator
        self._n = n

        self._gen = self._generator()
        
        self._timer = Timer()
        self._running = True
        self._wait = wait
        
        self._set_value()
            
    def _set_value(self, timer_obj=None):
        if self._wait:
            # wait for the exection to end
            next_seq = self._get_value()
            while next_seq is not None:
                value, seconds = next_seq
                
                self._output_device._write(value)
                sleep(seconds)
                
                next_seq = self._get_value()
                
        else:
            # run the timer
            next_seq = self._get_value()
            if next_seq is not None:
                value, seconds = next_seq
                
                self._output_device._write(value)            
                self._timer.init(period=int(seconds * 1000), mode=Timer.ONE_SHOT, callback=self._set_value)

        if next_seq is None:
            # the sequence has finished, turn the device off
            self._output_device.off()
            self._running = False
                
    def _get_value(self):
        try:
            return next(self._gen)
            
        except StopIteration:
            
            self._n = self._n - 1 if self._n is not None else None
            if self._n == 0:
                # it's the end, return None
                return None
            else:
                # recreate the generator and start again
                self._gen = self._generator()
                return next(self._gen)
        
    def stop(self):
        """
        Stops the ValueChange object running.
        """
        self._running = False
        self._timer.deinit()

###############################################################################
# OUTPUT DEVICES
###############################################################################

class OutputDevice:
    """
    Base class for output devices. 
    """   
    def __init__(self, active_high=True, initial_value=False):
        self.active_high = active_high
        if initial_value is not None:
            self._write(initial_value)
        self._value_changer = None
    
    @property
    def active_high(self):
        """
        Sets or returns the active_high property. If :data:`True`, the 
        :meth:`on` method will set the Pin to HIGH. If :data:`False`, 
        the :meth:`on` method will set the Pin to LOW (the :meth:`off` method 
        always does the opposite).
        """
        return self._active_state

    @active_high.setter
    def active_high(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True
        
    @property
    def value(self):
        """
        Sets or returns a value representing the state of the device: 1 is on, 0 is off.
        """
        return self._read()

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)
        
    def on(self, value=1, t=None, wait=False):
        """
        Turns the device on.

        :param float value:
            The value to set when turning on. Defaults to 1.

        :param float t:
            The time in seconds that the device should be on. If None is 
            specified, the device will stay on. The default is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the device will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        if t is None:
            self.value = value
        else:
            self._start_change(lambda : iter([(value, t), ]), 1, wait)

    def off(self):
        """
        Turns the device off.
        """
        self.value = 0
            
    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is on.
        """
        return bool(self.value)

    def toggle(self):
        """
        If the device is off, turn it on. If it is on, turn it off.
        """
        if self.is_active:
            self.off()
        else:
            self.on()
            
    def blink(self, on_time=1, off_time=None, n=None, wait=False):
        """
        Makes the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds that the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds that the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.

        :param int n:
            The number of times to repeat the blink operation. If None is 
            specified, the device will continue blinking forever. The default
            is None.

        :param bool wait:
           If True, the method will block until the device stops turning on and off. 
           If False, the method will return and the device will turn on and off in
           the background. Defaults to False.        
        """
        off_time = on_time if off_time is None else off_time
        
        self.off()

        # is there anything to change?
        if on_time > 0 or off_time > 0:
            self._start_change(lambda : iter([(1,on_time), (0,off_time)]), n, wait)
            
    def _start_change(self, generator, n, wait):
        self._value_changer = ValueChange(self, generator, n, wait)
    
    def _stop_change(self):
        if self._value_changer is not None:
            self._value_changer.stop()
            self._value_changer = None

    def close(self):
        """
        Turns the device off.
        """
        self.value = 0

class DigitalOutputDevice(OutputDevice, PinMixin):
    """
    Represents a device driven by a digital pin.

    :param int pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the LED will be off initially. If
        :data:`True`, the LED will be switched on initially.
    """
    def __init__(self, pin, active_high=True, initial_value=False):
        self._pin_num = pin
        self._pin = Pin(pin, Pin.OUT)
        super().__init__(active_high, initial_value)
        
    def _value_to_state(self, value):
        return int(self._active_state if value else self._inactive_state)
    
    def _state_to_value(self, state):
        return int(bool(state) == self._active_state)
    
    def _read(self):
        return self._state_to_value(self._pin.value())

    def _write(self, value):
        self._pin.value(self._value_to_state(value))
                
    def close(self):
        """
        Closes the device and turns the device off. Once closed, the device
        can no longer be used.
        """
        super().close()
        self._pin = None

class DigitalLED(DigitalOutputDevice):
    """
    Represents a simple LED, which can be switched on and off.

    :param int pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the LED will be off initially. If
        :data:`True`, the LED will be switched on initially.
    """
    pass

DigitalLED.is_lit = DigitalLED.is_active

class Buzzer(DigitalOutputDevice):
    """
    Represents an active or passive buzzer, which can be turned on or off.

    :param int pin:
        The pin that the device is connected to.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the Buzzer will be off initially. If
        :data:`True`, the Buzzer will be switched on initially.
    """
    pass

Buzzer.beep = Buzzer.blink

class PWMOutputDevice(OutputDevice, PinMixin):
    """
    Represents a device driven by a PWM pin.

    :param int pin:
        The pin that the device is connected to.

    :param int freq:
        The frequency of the PWM signal in hertz. Defaults to 100.

    :param int duty_factor:
        The duty factor of the PWM signal. This is a value between 0 and 65535.
        Defaults to 65535.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the LED will be off initially. If
        :data:`True`, the LED will be switched on initially.
    """
    
    PIN_TO_PWM_CHANNEL = ["0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B","7A","7B","0A","0B","1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    _channels_used = {}
    
    def __init__(self, pin, freq=100, duty_factor=65535, active_high=True, initial_value=False):
        self._check_pwm_channel(pin)
        self._pin_num = pin
        self._duty_factor = duty_factor
        self._pwm = PWM(Pin(pin))
        self._pwm.freq(freq)
        super().__init__(active_high, initial_value)
        
    def _check_pwm_channel(self, pin_num):
        channel = PWMOutputDevice.PIN_TO_PWM_CHANNEL[pin_num]
        if channel in PWMOutputDevice._channels_used.keys():
            raise PWMChannelAlreadyInUse(
                "PWM channel {} is already in use by {}. Use a different pin".format(
                    channel,
                    str(PWMOutputDevice._channels_used[channel])
                    )
                )
        else:
            PWMOutputDevice._channels_used[channel] = self
        
    def _state_to_value(self, state):
        return (state if self.active_high else self._duty_factor - state) / self._duty_factor

    def _value_to_state(self, value):
        return int(self._duty_factor * (value if self.active_high else 1 - value))
    
    def _read(self):
        return self._state_to_value(self._pwm.duty_u16())
    
    def _write(self, value):
        self._pwm.duty_u16(self._value_to_state(value))
        
    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is on.
        """
        return self.value != 0

    @property
    def freq(self):
        """
        Returns the current frequency of the device.
        """
        return self._pwm.freq()
    
    @freq.setter
    def freq(self, freq):
        """
        Sets the frequency of the device.
        """
        self._pwm.freq(freq)

    def blink(self, on_time=1, off_time=None, n=None, wait=False, fade_in_time=0, fade_out_time=None, fps=25):
        """
        Makes the device turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.

        :param int n:
            The number of times to repeat the blink operation. If `None`, the 
            device will continue blinking forever. The default is `None`.

        :param bool wait:
           If True, the method will block until the LED stops blinking. If False,
           the method will return and the LED will blink in the background.
           Defaults to False.

        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.

        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self.off()
        
        off_time = on_time if off_time is None else off_time
        fade_out_time = fade_in_time if fade_out_time is None else fade_out_time
        
        def blink_generator():
            if fade_in_time > 0:
                for s in [
                    (i * (1 / fps) / fade_in_time, 1 / fps)
                    for i in range(int(fps * fade_in_time))
                    ]:
                    yield s
            
            if on_time > 0:
                yield (1, on_time)

            if fade_out_time > 0:
                for s in [
                    (1 - (i * (1 / fps) / fade_out_time), 1 / fps)
                    for i in range(int(fps * fade_out_time))
                    ]:
                    yield s
            
            if off_time > 0:
                yield (0, off_time)
        
        # is there anything to change?
        if on_time > 0 or off_time > 0 or fade_in_time > 0 or fade_out_time > 0:
            self._start_change(blink_generator, n, wait)

    def pulse(self, fade_in_time=1, fade_out_time=None, n=None, wait=False, fps=25):
        """
        Makes the device pulse on and off repeatedly.
        
        :param float fade_in_time:
            The length of time in seconds that the device will take to turn on.
            Defaults to 1.

        :param float fade_out_time:
           The length of time in seconds that the device will take to turn off.
           Defaults to 1.
           
        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states. Defaults to 25.
           
        :param int n:
           The number of times to pulse the LED. If None, the LED will pulse
           forever. Defaults to None.
    
        :param bool wait:
           If True, the method will block until the LED stops pulsing. If False,
           the method will return and the LED will pulse in the background.
           Defaults to False.
        """
        self.blink(on_time=0, off_time=0, fade_in_time=fade_in_time, fade_out_time=fade_out_time, n=n, wait=wait, fps=fps)

    def close(self):
        """
        Closes the device and turns the device off. Once closed, the device
        can no longer be used.
        """
        super().close()
        del PWMOutputDevice._channels_used[
            PWMOutputDevice.PIN_TO_PWM_CHANNEL[self._pin_num]
            ]
        self._pwm.deinit()
        self._pwm = None
    
class PWMLED(PWMOutputDevice):
    """
    Represents an LED driven by a PWM pin; the brightness of the LED can be changed.

    :param int pin:
        The pin that the device is connected to.

    :param int freq:
        The frequency of the PWM signal in hertz. Defaults to 100.

    :param int duty_factor:
        The duty factor of the PWM signal. This is a value between 0 and 65535.
        Defaults to 65535.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the LED will be off initially. If
        :data:`True`, the LED will be switched on initially.
    """
PWMLED.brightness = PWMLED.value

def LED(pin, pwm=True, active_high=True, initial_value=False):
    """
    Returns an instance of :class:`DigitalLED` or :class:`PWMLED` depending on
    the value of the `pwm` parameter. 

    ::

        from picozero import LED

        my_pwm_led = LED(1)

        my_digital_led = LED(2, pwm=False)

    :param int pin:
        The pin that the device is connected to.

    :param int pin:
        If `pwm` is :data:`True` (the default), a :class:`PWMLED` will be
        returned. If `pwm` is :data:`False`, a :class:`DigitalLED` will be
        returned. A :class:`PWMLED` can control the brightness of the LED but
        uses 1 PWM channel.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the device will be off initially. If
        :data:`True`, the device will be switched on initially.
    """
    if pwm:
        return PWMLED(
            pin=pin,
            active_high=active_high,
            initial_value=initial_value)
    else:
        return DigitalLED(
            pin=pin,
            active_high=active_high,
            initial_value=initial_value)

try:
    pico_led = LED("LED", pwm=False)
except TypeError:
    # older version of micropython before "LED" was supported
    pico_led = LED(25, pwm=False)

class PWMBuzzer(PWMOutputDevice):
    """
    Represents a passive buzzer driven by a PWM pin; the volume of the buzzer can be changed.

    :param int pin:
        The pin that the buzzer is connected to.

    :param int freq:
        The frequency of the PWM signal in hertz. Defaults to 440.

    :param int duty_factor:
        The duty factor of the PWM signal. This is a value between 0 and 65535.
        Defaults to 1023.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If :data:`False` (the default), the buzzer will be off initially.  If
        :data:`True`, the buzzer will be switched on initially.
    """    
    def __init__(self, pin, freq=440, duty_factor=1023, active_high=True, initial_value=False):
        super().__init__(pin, freq, duty_factor, active_high, initial_value)

PWMBuzzer.volume = PWMBuzzer.value
PWMBuzzer.beep = PWMBuzzer.blink

class Speaker(OutputDevice, PinMixin):
    """
    Represents a speaker driven by a PWM pin.

    :param int pin:
        The pin that the speaker is connected to.

    :param int initial_freq:
        The initial frequency of the PWM signal in hertz. Defaults to 440.
    
    :param int initial_volume:
        The initial volume of the PWM signal. This is a value between 0 and
        1. Defaults to 0.

    :param int duty_factor:
        The duty factor of the PWM signal. This is a value between 0 and 65535.
        Defaults to 1023.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the Pin
        to HIGH. If :data:`False`, the :meth:`on` method will set the Pin to
        LOW (the :meth:`off` method always does the opposite).
    """    
    NOTES = {
        'b0': 31, 'c1': 33, 'c#1': 35, 'd1': 37, 'd#1': 39, 'e1': 41, 'f1': 44, 'f#1': 46, 'g1': 49,'g#1': 52, 'a1': 55,
        'a#1': 58, 'b1': 62, 'c2': 65, 'c#2': 69, 'd2': 73, 'd#2': 78,
        'e2': 82, 'f2': 87, 'f#2': 93, 'g2': 98, 'g#2': 104, 'a2': 110, 'a#2': 117, 'b2': 123,
        'c3': 131, 'c#3': 139, 'd3': 147, 'd#3': 156, 'e3': 165, 'f3': 175, 'f#3': 185, 'g3': 196, 'g#3': 208, 'a3': 220, 'a#3': 233, 'b3': 247,
        'c4': 262, 'c#4': 277, 'd4': 294, 'd#4': 311, 'e4': 330, 'f4': 349, 'f#4': 370, 'g4': 392, 'g#4': 415, 'a4': 440, 'a#4': 466, 'b4': 494,
        'c5': 523, 'c#5': 554, 'd5': 587, 'd#5': 622, 'e5': 659, 'f5': 698, 'f#5': 740, 'g5': 784, 'g#5': 831, 'a5': 880, 'a#5': 932, 'b5': 988,
        'c6': 1047, 'c#6': 1109, 'd6': 1175, 'd#6': 1245, 'e6': 1319, 'f6': 1397, 'f#6': 1480, 'g6': 1568, 'g#6': 1661, 'a6': 1760, 'a#6': 1865, 'b6': 1976,
        'c7': 2093, 'c#7': 2217, 'd7': 2349, 'd#7': 2489,
        'e7': 2637, 'f7': 2794, 'f#7': 2960, 'g7': 3136, 'g#7': 3322, 'a7': 3520, 'a#7': 3729, 'b7': 3951,
        'c8': 4186, 'c#8': 4435, 'd8': 4699, 'd#8': 4978 
        }
    
    def __init__(self, pin, initial_freq=440, initial_volume=0, duty_factor=1023, active_high=True):
        
        self._pin_num = pin
        self._pwm_buzzer = PWMBuzzer(
            pin,
            freq=initial_freq,
            duty_factor=duty_factor,
            active_high=active_high,
            initial_value=None,
            )
        
        super().__init__(active_high, None)
        self.volume = initial_volume
        
    def on(self, volume=1):
        self.volume = volume
        
    def off(self):
        self.volume = 0

    @property
    def value(self):
        """
        Sets or returns the value of the speaker. The value is a tuple of (freq, volume).
        """
        return tuple(self.freq, self.volume)

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)

    @property
    def volume(self):
        """
        Sets or returns the volume of the speaker: 1 for maximum volume, 0 for off.
        """
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        self.value = (self.freq, self.volume)
        
    @property
    def freq(self):
        """
        Sets or returns the current frequency of the speaker.
        """
        return self._pwm_buzzer.freq
    
    @freq.setter
    def freq(self, freq):
        self.value = (freq, self.volume)
        
    def _write(self, value):
        # set the frequency
        if value[0] is not None:
            self._pwm_buzzer.freq = value[0]
        
        # write the volume value
        if value[1] is not None:
            self._pwm_buzzer.volume = value[1]

    def _to_freq(self, freq):
        if freq is not None and freq != '' and freq != 0: 
            if type(freq) is str:
                return int(self.NOTES[freq])
            elif freq <= 128 and freq > 0: # MIDI
                midi_factor = 2**(1/12)
                return int(440 * midi_factor ** (freq - 69))
            else:
                return freq
        else:
            return None

    def beep(self, on_time=1, off_time=None, n=None, wait=False, fade_in_time=0, fade_out_time=None, fps=25):
        """
        Makes the buzzer turn on and off repeatedly.
        
        :param float on_time:
            The length of time in seconds that the device will be on. Defaults to 1.

        :param float off_time:
            The length of time in seconds that the device will be off. If `None`, 
            it will be the same as ``on_time``. Defaults to `None`.

        :param int n:
            The number of times to repeat the beep operation. If `None`, the 
            device will continue beeping forever. The default is `None`.

        :param bool wait:
           If True, the method will block until the buzzer stops beeping. If False,
           the method will return and the buzzer will beep in the background.
           Defaults to False.

        :param float fade_in_time:
            The length of time in seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            The length of time in seconds to spend fading out. If `None`,
            it will be the same as ``fade_in_time``. Defaults to `None`.

        :param int fps:
           The frames per second that will be used to calculate the number of
           steps between off/on states when fading. Defaults to 25.
        """
        self._pwm_buzzer.blink(on_time, off_time, n, wait, fade_in_time, fade_out_time, fps)

    def play(self, tune=440, duration=1, volume=1, n=1, wait=True):
        """
        Plays a tune for a given duration. 

        :param int tune:

            The tune to play can be specified as:

                + a single "note", represented as:
                  + a frequency in Hz e.g. `440`
                  + a midi note e.g. `60`
                  + a note name as a string e.g. `"E4"`
                + a list of notes and duration e.g. `[440, 1]` or `["E4", 2]`
                + a list of two value tuples of (note, duration) e.g. `[(440,1), (60, 2), ("e4", 3)]`

            Defaults to `440`.
        
        :param int volume:
            The volume of the tune; 1 is maximum volume, 0 is mute. Defaults to 1.

        :param float duration:
            The duration of each note in seconds. Defaults to 1.

        :param int n:
           The number of times to play the tune. If None, the tune will play
           forever. Defaults to 1.
    
        :param bool wait:
           If True, the method will block until the tune has finished. If False,
           the method will return and the tune will play in the background.
           Defaults to True.
        """

        self.off()

        # tune isn't a list, so it must be a single frequency or note
        if not isinstance(tune, (list, tuple)):
            tune = [(tune, duration)]
        # if the first element isn't a list, then it must be list of a single note and duration
        elif not isinstance(tune[0], (list, tuple)):
            tune = [tune]

        def tune_generator():
            for note in tune:
                
                # note isn't a list or tuple, it must be a single frequency or note
                if not isinstance(note, (list, tuple)):
                    # make it into a tuple
                    note = (note, duration)

                # turn the notes into frequencies
                freq = self._to_freq(note[0])
                freq_duration = note[1]
                freq_volume = volume if freq is not None else 0
                
                # if this is a tune of greater than 1 note, add gaps between notes
                if len(tune) == 1:
                    yield ((freq, freq_volume), freq_duration)
                else:
                    yield ((freq, freq_volume), freq_duration * 0.9)
                    yield ((freq, 0), freq_duration * 0.1)
                    
        self._start_change(tune_generator, n, wait)

    def close(self):
        self._pwm_buzzer.close()

class RGBLED(OutputDevice, PinsMixin):
    """
    Extends :class:`OutputDevice` and represents a full colour LED component (composed
    of red, green, and blue LEDs).
    Connect the common cathode (longest leg) to a ground pin; connect each of
    the other legs (representing the red, green, and blue anodes) to any GP
    pins. You should use three limiting resistors (one per anode).
    The following code will make the LED yellow::

        from picozero import RGBLED
        rgb = RGBLED(1, 2, 3)
        rgb.color = (1, 1, 0)

    0–255 colours are also supported::

        rgb.color = (255, 255, 0)

    :type red: int
    :param red:
        The GP pin that controls the red component of the RGB LED. 
    :type green: int
    :param green:
        The GP pin that controls the green component of the RGB LED.
    :type blue: int
    :param blue:
        The GP pin that controls the blue component of the RGB LED.
    :param bool active_high:
        Set to :data:`True` (the default) for common cathode RGB LEDs. If you
        are using a common anode RGB LED, set this to :data:`False`.
    :type initial_value: ~colorzero.Color or tuple
    :param initial_value:
        The initial color for the RGB LED. Defaults to black ``(0, 0, 0)``.
    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMLED` instances for
        each component of the RGBLED. If :data:`False`, construct 
        :class:`DigitalLED` instances.
    
    """
    def __init__(self, red=None, green=None, blue=None, active_high=True,
                 initial_value=(0, 0, 0), pwm=True):
        self._pin_nums = (red, green, blue)
        self._leds = ()
        self._last = initial_value
        LEDClass = PWMLED if pwm else DigitalLED
        self._leds = tuple(
            LEDClass(pin, active_high=active_high)
            for pin in (red, green, blue))
        super().__init__(active_high, initial_value)
        
    def _write(self, value):
        if type(value) is not tuple:
            value = (value, ) * 3       
        for led, v in zip(self._leds, value):
            led.value = v
        
    @property
    def value(self):
        """
        Represents the colour of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 1 if *pwm* was :data:`True`
        when the class was constructed (but only takes values of 0 or 1 otherwise).
        For example, red would be ``(1, 0, 0)`` and yellow would be ``(1, 1,
        0)``, whereas orange would be ``(1, 0.5, 0)``.
        """
        return tuple(led.value for led in self._leds)

    @value.setter
    def value(self, value):
        self._stop_change()
        self._write(value)

    @property
    def is_active(self):
        """
        Returns :data:`True` if the LED is currently active (not black) and
        :data:`False` otherwise.
        """
        return self.value != (0, 0, 0)

    is_lit = is_active

    def _to_255(self, value):
        return round(value * 255)
    
    def _from_255(self, value):
        return 0 if value == 0 else value / 255
    
    @property
    def color(self):
        """
        Represents the colour of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (but only takes values of 0 or 255 otherwise).
        For example, red would be ``(255, 0, 0)`` and yellow would be ``(255, 255,
        0)``, whereas orange would be ``(255, 127, 0)``.
        """
        return tuple(self._to_255(v) for v in self.value)

    @color.setter
    def color(self, value):
        self.value = tuple(self._from_255(v) for v in value)

    @property
    def red(self):
        """
        Represents the red component of the LED as a value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (but only takes values of 0 or 255 otherwise).
        """
        return self._to_255(self.value[0])

    @red.setter
    def red(self, value):
        r, g, b = self.value
        self.value = self._from_255(value), g, b

    @property
    def green(self):
        """
        Represents the green component of the LED as a value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (but only takes values of 0 or 255 otherwise).
        """
        return self._to_255(self.value[1])

    @green.setter
    def green(self, value):
        r, g, b = self.value
        self.value = r, self._from_255(value), b

    @property
    def blue(self):
        """
        Represents the blue component of the LED as a value between 0 and 255 if *pwm* was :data:`True`
        when the class was constructed (but only takes values of 0 or 255 otherwise).
        """
        return self._to_255(self.value[2])

    @blue.setter
    def blue(self, value):
        r, g, b = self.value
        self.value = r, g, self._from_255(value)

    def on(self):
        """
        Turns the LED on. This is equivalent to setting the LED color to white, e.g.
        ``(1, 1, 1)``.
        """
        self.value = (1, 1, 1)

    def invert(self):
        """
        Inverts the state of the device. If the device is currently off
        (:attr:`value` is ``(0, 0, 0)``), this changes it to "fully" on
        (:attr:`value` is ``(1, 1, 1)``). If the device has a specific colour,
        this method inverts the colour.
        """
        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)
        
    def toggle(self):
        """
        Toggles the state of the device. If the device has a specific colour, then that colour is saved and the device is turned off. 
        If the device is off, it will be changed to the last colour it had when it was on or, if none, to fully on (:attr:`value` is ``(1, 1, 1)``).
        """
        if self.value == (0, 0, 0):
            self.value = self._last or (1, 1, 1)
        else:
            self._last = self.value 
            self.value = (0, 0, 0)
            
    def blink(self, on_times=1, fade_times=0, colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Makes the device blink between colours repeatedly.

        :param float on_times:
            Single value or tuple of numbers of seconds to stay on each colour. Defaults to 1 second. 
        :param float fade_times:
            Single value or tuple of times to fade between each colour. Must be 0 if
            *pwm* was :data:`False` when the class was constructed.
        :type colors: tuple
            Tuple of colours to blink between, use ``(0, 0, 0)`` for off.
        :param colors:
            The colours to blink between. Defaults to red, green, blue.
        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.
        :param bool wait:
            If :data:`False` (the default), use a Timer to manage blinking,
            continue blinking, and return immediately. If :data:`False`, only
            return when the blinking is finished (warning: the default value of
            *n* will result in this method never returning).
        """    
        self.off()
        
        if type(on_times) is not tuple:
            on_times = (on_times, ) * len(colors)
        if type(fade_times) is not tuple:
            fade_times = (fade_times, ) * len(colors)
        # If any value is above zero then treat all as 0-255 values
        if any(v > 1 for v in sum(colors, ())):
            colors = tuple(tuple(self._from_255(v) for v in t) for t in colors)
        
        def blink_generator():
        
            # Define a linear interpolation between
            # off_color and on_color
            
            lerp = lambda t, fade_in, color1, color2: tuple(
                (1 - t) * off + t * on
                if fade_in else
                (1 - t) * on + t * off
                for off, on in zip(color2, color1)
                )
            
            for c in range(len(colors)):
                if on_times[c] > 0:
                    yield (colors[c], on_times[c])
                    
                if fade_times[c] > 0:
                    for i in range(int(fps * fade_times[c])):
                        v = lerp(i * (1 / fps) / fade_times[c], True, colors[(c + 1) % len(colors)], colors[c])
                        t = 1 / fps       
                        yield (v, t)
    
        self._start_change(blink_generator, n, wait)
            
    def pulse(self, fade_times=1, colors=((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Makes the device fade between colours repeatedly.

        :param float fade_times:
            Single value or tuple of numbers of seconds to spend fading. Defaults to 1.
        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.
        :type colors: tuple
        :param on_color:
            Tuple of colours to pulse between in order. Defaults to red, off, green, off, blue, off. 
        :type off_color: ~colorzero.Color or tuple
        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)
        
    def cycle(self, fade_times=1, colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), n=None, wait=False, fps=25):
        """
        Makes the device fade in and out repeatedly.

        :param float fade_times:
            Single value or tuple of numbers of seconds to spend fading between colours. Defaults to 1.
        :param float fade_times:
            Number of seconds to spend fading out. Defaults to 1.
        :type colors: tuple
        :param on_color:
            Tuple of colours to cycle between. Defaults to red, green, blue. 
        :type n: int or None
        :param n:
            Number of times to cycle; :data:`None` (the default) means forever.
        """
        on_times = 0
        self.blink(on_times, fade_times, colors, n, wait, fps)

    def close(self):
        super().close()
        for led in self._leds:
            led.close()
        self._leds = None
    
RGBLED.colour = RGBLED.color

class Motor(PinsMixin):
    """
    Represents a motor connected to a motor controller that has a two-pin
    input. One pin drives the motor "forward", the other drives the motor
    "backward".

    :type forward: int
    :param forward:
        The GP pin that controls the "forward" motion of the motor. 
    
    :type backward: int
    :param backward:
        The GP pin that controls the "backward" motion of the motor. 
    
    :param bool pwm:
        If :data:`True` (the default), PWM pins are used to drive the motor. 
        When using PWM pins, values between 0 and 1 can be used to set the 
        speed.
    
    """
    def __init__(self, forward, backward, pwm=True):
        self._pin_nums = (forward, backward)
        self._forward = PWMOutputDevice(forward) if pwm else DigitalOutputDevice(forward)
        self._backward = PWMOutputDevice(backward) if pwm else DigitalOutputDevice(backward)
        
    def on(self, speed=1, t=None, wait=False):
        """
        Turns the motor on and makes it turn.

        :param float speed:
            The speed as a value between -1 and 1: 1 turns the motor at
            full speed in one direction, -1 turns the motor at full speed in
            the opposite direction. Defaults to 1.

        :param float t:
            The time in seconds that the motor should run for. If None is 
            specified, the motor will stay on. The default is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        if speed > 0:
            self._backward.off()
            self._forward.on(speed, t, wait)
            
        elif speed < 0:
            self._forward.off()
            self._backward.on(-speed, t, wait)
        
        else:
            self.off()

    def off(self):
        """
        Stops the motor turning.
        """
        self._backward.off()
        self._forward.off()

    @property
    def value(self):
        """
        Sets or returns the motor speed as a value between -1 and 1: -1 is full
        speed "backward", 1 is full speed "forward", 0 is stopped.
        """
        return self._forward.value + (-self._backward.value)

    @value.setter
    def value(self, value):
        if value != 0:
            self.on(value)
        else:
            self.stop()

    def forward(self, speed=1, t=None, wait=False):
        """
        Makes the motor turn "forward".

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the motor should turn for. If None is 
            specified, the motor will stay on. The default is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self.on(speed, t, wait)

    def backward(self, speed=1, t=None, wait=False):
        """
        Makes the motor turn "backward".

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the motor should turn for. If None is 
            specified, the motor will stay on. The default is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self.on(-speed, t, wait)

    def close(self):
        """
        Closes the device and releases any resources. Once closed, the device
        can no longer be used.
        """
        self._forward.close()
        self._backward.close()

Motor.start = Motor.on
Motor.stop = Motor.off

class Robot:
    """
    Represents a generic dual-motor robot / rover / buggy.

    Alias for :class:`Rover`.

    This class is constructed with two tuples representing the forward and
    backward pins of the left and right controllers. For example,
    if the left motor's controller is connected to pins 12 and 13, while the
    right motor's controller is connected to pins 14 and 15, then the following
    example will drive the robot forward::

        from picozero import Robot

        robot = Robot(left=(12, 13), right=(14, 15))
        robot.forward()

    :param tuple left:
        A tuple of two pins representing the forward and backward inputs of the 
        left motor's controller.

    :param tuple right:
        A tuple of two pins representing the forward and backward inputs of the 
        right motor's controller.

    :param bool pwm:
        If :data:`True` (the default), pwm pins will be used, allowing variable 
        speed control. 

    """
    def __init__(self, left, right, pwm=True):
        self._left = Motor(left[0], left[1], pwm)
        self._right = Motor(right[0], right[1], pwm)

    @property
    def left_motor(self):
        """
        Returns the left :class:`Motor`.
        """
        return self._left

    @property
    def right_motor(self):
        """
        Returns the right :class:`Motor`.
        """
        return self._right

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return (self._left.value, self._right.value)

    @value.setter
    def value(self, value):
        self._left.value, self._right.value = value
        
    def forward(self, speed=1, t=None, wait=False):
        """
        Makes the robot move "forward".

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the robot should move for. If None is 
            specified, the robot will continue to move until stopped. The default 
            is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self._left.forward(speed, t, False)
        self._right.forward(speed, t, wait)
        
    def backward(self, speed=1, t=None, wait=False):
        """
        Makes the robot move "backward".

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the robot should move for. If None is 
            specified, the robot will continue to move until stopped. The default 
            is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self._left.backward(speed, t, False)
        self._right.backward(speed, t, wait)
        
    def left(self, speed=1, t=None, wait=False):
        """
        Makes the robot turn "left" by turning the left motor backward and the 
        right motor forward.

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the robot should turn for. If None is 
            specified, the robot will continue to turn until stopped. The default 
            is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self._left.backward(speed, t, False)
        self._right.forward(speed, t, wait)
    
    def right(self, speed=1, t=None, wait=False):
        """
        Makes the robot turn "right" by turning the left motor forward and the 
        right motor backward.

        :param float speed:
            The speed as a value between 0 and 1: 1 is full speed, 0 is stop. Defaults to 1.

        :param float t:
            The time in seconds that the robot should turn for. If None is 
            specified, the robot will continue to turn until stopped. The default 
            is None.

        :param bool wait:
           If True, the method will block until the time `t` has expired. 
           If False, the method will return and the motor will turn on in
           the background. Defaults to False. Only effective if `t` is not
           None.
        """
        self._left.forward(speed, t, False)
        self._right.backward(speed, t, wait)
        
    def stop(self):
        """
        Stops the robot.
        """
        self._left.stop()
        self._right.stop()

    def close(self):
        """
        Closes the device and releases any resources. Once closed, the device
        can no longer be used.
        """
        self._left.close()
        self._right.close()
    
Rover = Robot
'''
class Servo(PWMOutputDevice):
    """
    Represents a PWM-controlled servo motor.

    Setting the `value` to 0 will move the servo to its minimum position,
    1 will move the servo to its maximum position. Setting the `value` to
    :data:`None` will turn the servo "off" (i.e. no signal is sent).

    :type pin: int
    :param pin:
        The pin the servo motor is connected to. 

    :param bool initial_value:
        If :data:`0`, the servo will be set to its minimum position.  If
        :data:`1`, the servo will set to its maximum position. If :data:`None`
        (the default), the position of the servo will not change.

    :param float min_pulse_width:
        The pulse width corresponding to the servo's minimum position. This
        defaults to 1ms.

    :param float max_pulse_width:
        The pulse width corresponding to the servo's maximum position. This
        defaults to 2ms.

    :param float frame_width:
        The length of time between servo control pulses measured in seconds.
        This defaults to 20ms which is a common value for servos.

    :param int duty_factor:
        The duty factor of the PWM signal. This is a value between 0 and 65535.
        Defaults to 65535.    
    """
    def __init__(self, pin, initial_value=None, min_pulse_width=1/1000, max_pulse_width=2/1000, frame_width=20/1000, duty_factor=65535):
        self._min_duty = int((min_pulse_width / frame_width) * duty_factor)
        self._max_duty = int((max_pulse_width / frame_width) * duty_factor)
        
        super().__init__(pin, freq=int(1 / frame_width), duty_factor=duty_factor, initial_value=initial_value)
        
    def _state_to_value(self, state):
        return None if state == 0 else clamp((state - self._min_duty) / (self._max_duty - self._min_duty), 0, 1)
        
    def _value_to_state(self, value):
        return 0 if value is None else int(self._min_duty + ((self._max_duty - self._min_duty) * value))
    
    def min(self):
        """
        Set the servo to its minimum position.
        """
        self.value = 0
    
    def mid(self):
        """
        Set the servo to its mid-point position.
        """
        self.value = 0.5
        
    def max(self):
        """
        Set the servo to its maximum position.
        """
        self.value = 1

    def off(self):
        """
        Turn the servo "off" by setting the value to `None`.
        """
        self.value = None
'''
###############################################################################
# INPUT DEVICES
###############################################################################

class InputDevice:
    """
    Base class for input devices.
    """
    def __init__(self, active_state=None):
        self._active_state = active_state

    @property
    def active_state(self):
        """
        Sets or returns the active state of the device. If :data:`None` (the default),
        the device will return the value that the pin is set to. If
        :data:`True`, the device will return :data:`True` if the pin is
        HIGH. If :data:`False`, the device will return :data:`False` if the
        pin is LOW.
        """
        return self._active_state

    @active_state.setter
    def active_state(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True
        
    @property
    def value(self):
        """
        Returns the current value of the device. This is either :data:`True` 
        or :data:`False` depending on the value of :attr:`active_state`.
        """
        return self._read()

class DigitalInputDevice(InputDevice, PinMixin):
    """
    Represents a generic input device with digital functionality e.g. buttons 
    that can be either active or inactive.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True`, the device will be pulled up to HIGH. If
        :data:`False` (the default), the device will be pulled down to LOW.

    :param bool active_state:
        If :data:`True` (the default), the device will return :data:`True`
        if the pin is HIGH. If :data:`False`, the device will return
        :data:`False` if the pin is LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses. The default is 
        :data:`None`.
    """
    def __init__(self, pin, pull_up=False, active_state=None, bounce_time=None):
        super().__init__(active_state)
        self._pin_num = pin
        self._pin = Pin(
            pin,
            mode=Pin.IN,
            pull=Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self._bounce_time = bounce_time
        
        if active_state is None:
            self._active_state = False if pull_up else True
        else:
            self._active_state = active_state
        
        self._state = self._pin.value()
        
        self._when_activated = None
        self._when_deactivated = None
        
        # setup interupt
        self._pin.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
    def _state_to_value(self, state):
        return int(bool(state) == self._active_state)
    
    def _read(self):
        return self._state_to_value(self._state)

    def _pin_change(self, p):
        # turn off the interupt
        p.irq(handler=None)
        
        last_state = p.value()
        
        if self._bounce_time is not None:
            # wait for stability
            stop = ticks_ms() + (self._bounce_time * 1000)
            while ticks_ms() < stop:
                # keep checking, reset the stop if the value changes
                if p.value() != last_state:
                    stop = ticks_ms() + (self._bounce_time * 1000)
                    last_state = p.value()
        
        # re-enable the interupt
        p.irq(self._pin_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        
        # did the value actually change? 
        if self._state != last_state:
            # set the state
            self._state = self._pin.value()
            
            # manage call backs
            callback_to_run = None
            if self.value and self._when_activated is not None:
                callback_to_run = self._when_activated
                    
            elif not self.value and self._when_deactivated is not None:
                callback_to_run = self._when_deactivated
            
            if callback_to_run is not None:
                
                def schedule_callback(callback):
                    callback()
            
                try:
                    schedule(schedule_callback, callback_to_run)
                    
                except RuntimeError as e:
                    if str(e) == "schedule queue full":
                        raise EventFailedScheduleQueueFull(
                            "{} - {} not run due to the micropython schedule being full".format(
                                str(self), callback_to_run.__name__))
                    else:
                        raise e

    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is active.
        """
        return bool(self.value)

    @property
    def is_inactive(self):
        """
        Returns :data:`True` if the device is inactive.
        """
        return not bool(self.value)
    
    @property
    def when_activated(self):
        """
        Returns a :samp:`callback` that will be called when the device is activated.
        """
        return self._when_activated
    
    @when_activated.setter
    def when_activated(self, value):
        self._when_activated = value
        
    @property
    def when_deactivated(self):
        """
        Returns a :samp:`callback` that will be called when the device is deactivated.
        """
        return self._when_deactivated
    
    @when_deactivated.setter
    def when_deactivated(self, value):
        self._when_deactivated = value
    
    def close(self):
        """
        Closes the device and releases any resources. Once closed, the device
        can no longer be used.
        """
        self._pin.irq(handler=None)
        self._pin = None

class Switch(DigitalInputDevice):
    """
    Represents a toggle switch, which is either open or closed.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True` (the default), the device will be pulled up to
        HIGH. If :data:`False`, the device will be pulled down to LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses. Defaults to 0.02 
        seconds.
    """
    def __init__(self, pin, pull_up=True, bounce_time=0.02): 
        super().__init__(pin=pin, pull_up=pull_up, bounce_time=bounce_time)

Switch.is_closed = Switch.is_active
Switch.is_open = Switch.is_inactive
Switch.when_closed = Switch.when_activated
Switch.when_opened = Switch.when_deactivated

class Button(Switch):
    """
    Represents a push button, which can be either pressed or released.

    :param int pin:
        The pin that the device is connected to.

    :param bool pull_up:
        If :data:`True` (the default), the device will be pulled up to
        HIGH. If :data:`False`, the device will be pulled down to LOW.

    :param float bounce_time:
        The bounce time for the device. If set, the device will ignore
        any button presses that happen within the bounce time after a
        button release. This is useful to prevent accidental button
        presses from registering as multiple presses. Defaults to 0.02 
        seconds.
    """
    pass

Button.is_pressed = Button.is_active
Button.is_released = Button.is_inactive
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated 

class AnalogInputDevice(InputDevice, PinMixin):
    """
    Represents a generic input device with analogue functionality, e.g. 
    a potentiometer.

    :param int pin:
        The pin that the device is connected to.
        
    :param active_state:
        The active state of the device. If :data:`True` (the default),
        the :class:`AnalogInputDevice` will assume that the device is
        active when the pin is high and above the threshold. If 
        ``active_state`` is ``False``, the device will be active when 
        the pin is low and below the threshold. 

    :param float threshold:
        The threshold that the device must be above or below to be
        considered active. The default is 0.5.

    """
    def __init__(self, pin, active_state=True, threshold=0.5):
        self._pin_num = pin
        super().__init__(active_state)
        self._adc = ADC(pin)
        self._threshold = float(threshold)
        
    def _state_to_value(self, state):
        return (state if self.active_state else 65535 - state) / 65535

    def _value_to_state(self, value):
        return int(65535 * (value if self.active_state else 1 - value))
    
    def _read(self):
        return self._state_to_value(self._adc.read_u16())
        
    @property
    def threshold(self):
        """
        The threshold that the device must be above or below to be
        considered active. The default is 0.5.
        """
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = float(value)

    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is active.
        """
        return self.value > self.threshold

    @property
    def voltage(self):
        """
        Returns the voltage of the analogue device.
        """
        return self.value * 3.3

    def close(self):
        self._adc = None

class Potentiometer(AnalogInputDevice):
    """
    Represents a potentiometer, which outputs a variable voltage
    between 0 and 3.3V.

    Alias for :class:`Pot`.

    :param int pin:
        The pin that the device is connected to.
        
    :param active_state:
        The active state of the device. If :data:`True` (the default),
        the :class:`AnalogInputDevice` will assume that the device is
        active when the pin is high and above the threshold. If 
        ``active_state`` is ``False``, the device will be active when 
        the pin is low and below the threshold. 

    :param float threshold:
        The threshold that the device must be above or below to be
        considered active. The default is 0.5.

    """
    pass

Pot = Potentiometer

def pico_temp_conversion(voltage):
    # Formula for calculating temp from voltage for the onboard temperature sensor
    return 27 - (voltage - 0.706)/0.001721

class TemperatureSensor(AnalogInputDevice):
    """
    Represents a TemperatureSensor, which outputs a variable voltage. The voltage 
    can be converted to a temperature using a `conversion` function passed as a 
    parameter.

    Alias for :class:`Thermistor` and :class:`TempSensor`.

    :param int pin:
        The pin that the device is connected to.
        
    :param active_state:
        The active state of the device. If :data:`True` (the default),
        the :class:`AnalogInputDevice` will assume that the device is
        active when the pin is high and above the threshold. If 
        ``active_state`` is ``False``, the device will be active when 
        the pin is low and below the threshold. 

    :param float threshold:
        The threshold that the device must be above or below to be
        considered active. The default is 0.5.

    :param float conversion:
        A function that takes a voltage and returns a temperature. 

        e.g. The internal temperature sensor has a voltage range of 0.706V to 0.716V 
        and would use the follow conversion function::
        
            def temp_conversion(voltage):
                return 27 - (voltage - 0.706)/0.001721

            temp_sensor = TemperatureSensor(pin, conversion=temp_conversion)

        If :data:`None` (the default), the ``temp`` property will return :data:`None`.

    """
    def __init__(self, pin, active_state=True, threshold=0.5, conversion=None):
         self._conversion = conversion
         super().__init__(pin, active_state, threshold)
        
    @property
    def temp(self):
        """
        Returns the temperature of the device. If the conversion function is not
        set, this will return :data:`None`.
        """
        if self._conversion is not None:
            return self._conversion(self.voltage)
        else:
            return None

    @property
    def conversion(self):
        """
        Sets or returns the conversion function for the device.
        """
        return self._conversion

    @conversion.setter
    def conversion(self, value):
        self._conversion = value
       
pico_temp_sensor = TemperatureSensor(4, True, 0.5, pico_temp_conversion)
TempSensor = TemperatureSensor
Thermistor = TemperatureSensor

class DistanceSensor(PinsMixin):
    """
    Represents a HC-SR04 ultrasonic distance sensor.

    :param int echo:
        The pin that the ECHO pin is connected to.

    :param int trigger:
        The pin that the TRIG pin is connected to. 

    :param float max_distance:
        The :attr:`value` attribute reports a normalized value between 0 (too
        close to measure) and 1 (maximum distance). This parameter specifies
        the maximum distance expected in meters. This defaults to 1.
    """
    def __init__(self, echo, trigger, max_distance=1):
        self._pin_nums = (echo, trigger)
        self._max_distance = max_distance
        self._echo = Pin(echo, mode=Pin.IN, pull=Pin.PULL_DOWN)
        self._trigger = Pin(trigger, mode=Pin.OUT, value=0)
        
    def _read(self):
        echo_on = None
        echo_off = None
        timed_out = False
        
        self._trigger.off()
        sleep(0.000005)
        self._trigger.on()
        sleep(0.00001)
        self._trigger.off()

        # If an echo isn't measured in 100 milliseconds, it should
        # be considered out of range. The maximum length of the
        # echo is 38 milliseconds but it's not known how long the
        # transmission takes after the trigger
        stop = ticks_ms() + 100
        while echo_off is None and not timed_out:
            if self._echo.value() == 1 and echo_on is None:
                echo_on = ticks_us()
            if echo_on is not None and self._echo.value() == 0:
                echo_off = ticks_us()
            if ticks_ms() > stop:
                timed_out = True
            
        if echo_off is None or timed_out:
            return None
        else:
            distance = ((echo_off - echo_on) * 0.000343) / 2
            distance = min(distance, self._max_distance)
            return distance
    
    @property
    def value(self):
        """
        Returns a value between 0, indicating the reflector is either touching 
        the sensor or is sufficiently near that the sensor can’t tell the 
        difference, and 1, indicating the reflector is at or beyond the 
        specified max_distance. A return value of None indicates that the
        echo was not received before the timeout.
        """
        distance = self.distance
        return distance / self._max_distance if distance is not None else None
    
    @property
    def distance(self):
        """
        Returns the current distance measured by the sensor in meters. Note 
        that this property will have a value between 0 and max_distance.
        """
        return self._read()

    @property
    def max_distance(self):
        """
        Returns the maximum distance that the sensor will measure in metres.
        """
        return self._max_distance

#===========================================================================================================#
#추가한 부분
class DHTSensor(DigitalInputDevice): #온습도 센서
    def __init__(self, pin, model='DHT11'):
        super().__init__(pin)
        self._model = model.upper()
        if self._model == 'DHT11':
            self._sensor = dht.DHT11(Pin(self._pin_num))
        elif self._model == 'DHT22':
            self._sensor = dht.DHT22(Pin(self._pin_num))
        else:
            raise ValueError("Unsupported DHT sensor model: {}".format(self._model))
    
    def read(self):
        self._sensor.measure()
        self._temperature = self._sensor.temperature()
        self._humidity = self._sensor.humidity()
    
    @property
    def temperature(self):
        self.read()
        return self._temperature
    
    @property
    def humidity(self):
        self.read()
        return self._humidity
    
    def __str__(self):
        self.read()
        return "Temperature: {}C, Humidity: {}%".format(self._temperature, self._humidity)
#===========================================================================================================#
# OLED 클래스 추가 128x64 디스플레이사용한다고 가정
class OLED(PinsMixin):
    def __init__(self, scl, sda, width=128, height=64, i2c_id=0, freq=400000):
        # OLED 클래스 초기화 메서드. SCL, SDA 핀 번호와 디스플레이의 너비와 높이를 설정
        self._pin_nums = (scl, sda)
        # I2C 통신 설정을 위해 I2C 객체를 생성
        self._i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=freq)
        # SSD1306 OLED 드라이버 객체를 생성
        self._display = ssd1306.SSD1306_I2C(width, height, self._i2c)
    
    def text(self, message, x, y):
        # 지정된 위치에 텍스트 메시지를 출력
        self._display.text(message, x, y)
        self._display.show()
        
    def fill(self, color):
        # 디스플레이 전체를 지정된 색상으로 채우기.
        self._display.fill(color)
        self._display.show()

    def show(self):
        # 디스플레이에 변경사항을 반영.
        self._display.show()

    def clear(self):
        # 디스플레이를 지우기 (전체를 검은색으로 채우기).
        self._display.fill(0)
        self._display.show()
        
    def invert(self, invert):
        # 디스플레이의 색상을 반전
        self._display.invert(invert)
        self._display.show()

    def pixel(self, x, y, color):
        # 지정된 위치의 픽셀을 설정
        self._display.pixel(x, y, color)
        self._display.show()

    def line(self, x0, y0, x1, y1, color):
        # 지정된 두 점 사이에 선 그리기
        self._display.line(x0, y0, x1, y1, color)
        self._display.show()

    def rect(self, x, y, width, height, color):
        # 지정된 위치에 직사각형을 그리기
        self._display.rect(x, y, width, height, color)
        self._display.show()

    def fill_rect(self, x, y, width, height, color):
        # 지정된 위치에 채워진 직사각형을 그리기
        self._display.fill_rect(x, y, width, height, color)
        self._display.show()

#===========================================================================================================#
# LCD 클래스 추가 2x16 디스플레이사용한다고 가정 I2clcd와 LcdApi는 lcd를 제어하기 위한 기본 클래스임.
# 통신 속도가 느리면 조절 가능(자세한 건 부품별 코드에서 LCD코드 주석확인하기)
class LcdApi:
    # Implements the API for talking with HD44780 compatible character LCDs.
    LCD_CLR = 0x01
    LCD_RET_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01
    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04
    LCD_FUNCTION = 0x20
    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_10DOTS = 0x04
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80
    LCD_RS_CMD = 0
    LCD_RS_DATA = 1
    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True

    def init_display(self):
        self.write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        time.sleep_ms(5)
        self.write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        time.sleep_ms(1)
        self.write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        time.sleep_ms(1)
        self.write_init_nibble(self.LCD_FUNCTION)
        time.sleep_ms(1)
        self.write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        self.write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.write_command(self.LCD_CLR)
        self.write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)

    def clear(self):
        self.write_command(self.LCD_CLR)
        self.write_command(self.LCD_RET_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        self.write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def hide_cursor(self):
        self.write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        self.write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR | self.LCD_ON_BLINK)

    def blink_cursor_off(self):
        self.write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)
    '''
    #------4행16열 LCD를 쓸 때 사용해야하는 move_to 함수------
    #단, 함수를 바꾸면 그 다음에 아래에 존재하는 I2C_LCD클래스에서 rows파라미터를 4로 값을 변경해줘야함!!
    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        # DDRAM 주소는 4라인 LCD 기준으로 설정
        line_offsets = [0x00, 0x40, 0x14, 0x54]  # 4-line LCD용 DDRAM 주소 오프셋
        if cursor_y >= len(line_offsets):
            cursor_y = 0  # 잘못된 줄이면 첫 줄로
        addr = line_offsets[cursor_y] + cursor_x
        self.write_command(self.LCD_DDRAM | addr)
    #-------------------------------------------------------
    '''
    #------2행16열 LCD를 쓸 때 사용해야하는 move_to 함수------
    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3f
        if cursor_y == 1:
            addr += 0x40  # 2nd line offset
        self.write_command(self.LCD_DDRAM | addr)
    #-------------------------------------------------------
    def putchar(self, char):
        if char == '\n':
            if self.implied_newline:
                return
            self.cursor_x = self.num_columns
        else:
            self.write_data(ord(char))
            self.cursor_x += 1
        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = (char != '\n')
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        location &= 0x7
        self.write_command(self.LCD_CGRAM | (location << 3))
        self.write_data(charmap)

    def hal_backlight_on(self):
        raise NotImplementedError

    def hal_backlight_off(self):
        raise NotImplementedError

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError

    def hal_write_init_nibble(self, nibble):
        raise NotImplementedError

    def write_command(self, cmd):
        self.hal_write_command(cmd)

    def write_data(self, data):
        self.hal_write_data(data)

    def write_init_nibble(self, nibble):
        self.hal_write_init_nibble(nibble)

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        self.hal_backlight = True
        self.hal_write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        sleep_ms(5)
        self.hal_write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION | self.LCD_FUNCTION_8BIT)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        sleep_ms(1)
        LcdApi.__init__(self, num_lines, num_columns)
        self.hal_write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.hal_write_command(self.LCD_CLR)
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)

    def hal_backlight_on(self):
        self.hal_backlight = True
        self.i2c.writeto(self.i2c_addr, bytearray([0x08]))

    def hal_backlight_off(self):
        self.hal_backlight = False
        self.i2c.writeto(self.i2c_addr, bytearray([0x00]))

    def hal_write_command(self, cmd):
        byte = (cmd & 0xF0) | self.LCD_RS_CMD
        # 백라이트 제어 플래그를 추가하여 항상 켜도록 설정
        byte |= 0x08  # 백라이트 비트 추가
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))

        byte = (cmd << 4) & 0xF0 | self.LCD_RS_CMD
        byte |= 0x08  # 백라이트 비트 추가
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))

    def hal_write_data(self, data):
        byte = (data & 0xF0) | self.LCD_RS_DATA
        # 백라이트 제어 플래그를 추가하여 항상 켜도록 설정
        byte |= 0x08  # 백라이트 비트 추가
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))

        byte = (data << 4) & 0xF0 | self.LCD_RS_DATA
        byte |= 0x08  # 백라이트 비트 추가
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))

    def hal_write_init_nibble(self, nibble):
        byte = nibble & 0xF0
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.LCD_RW_WRITE]))

class I2C_LCD(PinsMixin):
    def __init__(self, scl, sda, i2c_id=0, i2c_addr=0x27, rows=2, cols=16, freq=400000):
        # I2C_LCD 클래스 초기화 메서드입니다. SCL, SDA 핀 번호와 I2C 주소, 디스플레이의 행과 열을 설정합니다.
        self._pin_nums = (scl, sda)
        # I2C 통신 설정을 위해 I2C 객체를 생성합니다.
        self._i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=freq)
        # I2C LCD 드라이버 객체를 생성합니다.
        self._lcd = I2cLcd(self._i2c, i2c_addr, rows, cols)
    
    def clear(self):
        # LCD 화면을 지웁니다.
        self._lcd.clear()
        
    def putstr(self, message, col=0, row=0):
        # 지정된 위치에 텍스트 메시지를 출력합니다.
        self._lcd.move_to(col, row)
        self._lcd.putstr(message)
    
    def backlight_on(self):
        # LCD 백라이트를 켭니다.
        self._lcd.hal_backlight_on()
    
    def backlight_off(self):
        # LCD 백라이트를 끕니다.
        self._lcd.hal_backlight_off()

#===========================================================================================================#
#수위감지센서
class WaterLevelSensor:
    def __init__(self, pin, threshold=0.5):
        """
        WaterLevelSensor 클래스 초기화 메서드.
        
        :param pin: 수위 감지 센서가 연결된 아날로그 핀 번호.
        :param threshold: 수위 임계값으로, 기본값은 0.5로 설정됨.
        """
        self.adc = ADC(Pin(pin))  # 아날로그 핀을 ADC로 설정
        self.threshold = threshold  # 수위 임계값 설정

    def read_value(self):
        """
        현재 수위 값을 읽어오는 메서드.
        
        :return: 0.0에서 1.0 사이의 값을 반환하여, 센서의 아날로그 값을 정규화된 값으로 반환.
        """
        # ADC 값을 0.0에서 1.0 사이의 값으로 변환하여 반환
        return self.adc.read_u16() / 65535

    def is_water_level_high(self):
        """
        현재 수위가 임계값을 초과하는지 확인하는 메서드.
        
        :return: 수위가 임계값보다 높으면 True, 그렇지 않으면 False를 반환.
        """
        # 읽어온 수위 값이 임계값을 초과하는지 여부를 확인
        return self.read_value() > self.threshold

    def set_threshold(self, threshold):
        """
        수위 임계값을 설정하는 메서드.
        
        :param threshold: 새로 설정할 수위 임계값.
        """
        # 새로운 임계값 설정
        self.threshold = threshold
#===========================================================================================================#
#토양수분센서
#퍼센트변환버젼
class SoilMoistureSensor:
    def __init__(self, pin, min_value=20000, max_value=50000):
        self.adc = ADC(Pin(pin))  # 아날로그 핀 설정
        self.min_value = min_value  # 최소 센서 값 (건조한 상태)
        self.max_value = max_value  # 최대 센서 값 (습한 상태)

    def read_raw_value(self):
        # ADC 값을 읽어옴
        return self.adc.read_u16()

    def read_percentage(self):
        # 센서 값을 퍼센트(%)로 변환
        raw_value = self.read_raw_value()
        # 퍼센트로 변환하여 반환 (0% - 100%)
        percentage = (raw_value - self.min_value) / (self.max_value - self.min_value) * 100
        return max(0, min(100, percentage))  # 0%에서 100% 범위로 제한

#===========================================================================================================#
#네오픽셀 제어
class Neopixel:
    def __init__(self, pin, num_leds):
        """
        NeoPixel 클래스 초기화 메서드
        :param pin: 네오픽셀이 연결된 핀 번호 (GPIO 핀 번호)
        :param num_leds: 제어할 NeoPixel LED의 개수
        """
        # Pin을 사용하여 해당 핀을 디지털 출력 핀으로 설정
        self.pin = Pin(pin, Pin.OUT)
        
        # 제어할 LED 개수를 설정
        self.num_leds = num_leds
        
        # NeoPixel 객체 초기화: 지정한 핀과 LED 개수를 사용하여 네오픽셀 제어 준비
        self.np = neopixel.NeoPixel(self.pin, self.num_leds)

    def set_pixel(self, n, color):
        """
        특정 LED에 색상을 설정하는 메서드
        :param n: 색상을 설정할 LED 번호 (0부터 시작하는 인덱스)
        :param color: (R, G, B) 형태의 색상 값, 각각 0~255 범위
        """
        if n < self.num_leds:
            # 선택한 LED에 (R, G, B) 값으로 색상을 설정
            self.np[n] = color
            
            # 변경 사항을 네오픽셀에 전송하여 실제로 색상이 적용되도록 함
            self.np.write()

    def fill(self, color):
        """
        모든 LED에 동일한 색상을 설정하는 메서드
        :param color: (R, G, B) 형태의 색상 값, 각각 0~255 범위
        """
        for i in range(self.num_leds):
            # 모든 LED에 지정된 색상을 설정
            self.set_pixel(i, color)

    def clear(self):
        """
        모든 LED를 끄는 메서드 (검정색으로 설정)
        """
        # 모든 LED를 (0, 0, 0) 즉, 검정색으로 설정하여 끔
        self.fill((0, 0, 0))

    def show(self):
        """
        현재 설정된 LED 색상을 적용하는 메서드 (write 명령어를 전송)
        """
        # 모든 변경 사항을 네오픽셀로 전송하여 실제로 표시되게 함
        self.np.write()
#===========================================================================================================#
#워터펌프 제어
class WaterPump:
    def __init__(self, pin1, pin2):
        """
        워터펌프 클래스 초기화 메서드
        :param pin1: 모터 드라이버의 IN1 또는 A+ 핀에 연결된 GPIO 핀
        :param pin2: 모터 드라이버의 IN2 또는 A- 핀에 연결된 GPIO 핀
        """
        self.motor_pin1 = DigitalOutputDevice(pin1)  # IN1 (A+) 핀 제어
        self.motor_pin2 = DigitalOutputDevice(pin2)  # IN2 (A-) 핀 제어

    def turn_on(self, direction=True):
        """
        워터펌프를 켜는 메서드
        :param direction: True이면 정방향, False이면 역방향
        """
        if direction:
            self.motor_pin1.on()
            self.motor_pin2.off()
        else:
            self.motor_pin1.off()
            self.motor_pin2.on()

    def turn_off(self):
        """
        워터펌프를 끄는 메서드
        """
        self.motor_pin1.off()
        self.motor_pin2.off()

    def run_for(self, duration, direction=True):
        """
        워터펌프를 일정 시간 동안 동작시키는 메서드
        :param duration: 워터펌프를 동작시킬 시간(초)
        :param direction: True이면 정방향, False이면 역방향
        """
        self.turn_on(direction)
        sleep(duration)
        self.turn_off()

#===========================================================================================================#
#기존 Servo클래스에서 제어하기 쉽게 하기 위한 클래스 재정의

class Servo:
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        self._angle = 0  # 현재 각도 저장
        self._is_on = True

    def _angle_to_duty(self, angle):
        pulse_us = self.min_us + (angle / 180) * (self.max_us - self.min_us)
        period_us = 1000000 / self.freq
        duty = int((pulse_us / period_us) * 65535)
        return duty

    @property
    def value(self):
        return self._angle

    @value.setter
    def value(self, angle):
        angle = max(0, min(180, int(angle)))
        self._angle = angle
        if self._is_on:
            self.pwm.duty_u16(self._angle_to_duty(angle))

    def off(self):
        self._is_on = False
        self.pwm.duty_u16(0)

    def on(self):
        self._is_on = True
        self.value = self._angle  # 현재 각도 다시 적용

    def min(self):
        self.value = 0  # 0도

    def mid(self):
        self.value = 90  # 90도

    def max(self):
        self.value = 180  # 180도

    def pulse(self, start=0, end=180, delay=0.01):
        """서보를 start~end 각도까지 서서히 이동"""
        step = 1 if start < end else -1
        for angle in range(start, end + step, step):
            self.value = angle
            sleep(delay)
            
#===========================================================================================================#
#충격감지센서 클래스
class ShockSensor(DigitalInputDevice):
    """
    피지컬 컴퓨팅용 충격 센서 클래스
    디지털 충격 센서를 제어할 수 있도록 picozero 스타일로 구성됨
    """

    def __init__(self, pin):
        super().__init__(pin)
    
    def is_shocked(self):
        """
        충격이 감지되었는지 확인
        (센서가 HIGH 상태이면 충격 감지로 간주)
        """
        return self.value == 1
        
#===========================================================================================================#
#포토인터럽터 클래스

class PhotoInterrupter(DigitalInputDevice):
    """
    포토인터럽터 센서를 제어하기 위한 클래스
    슬롯 사이에 물체가 감지되면 출력이 바뀜
    """

    def __init__(self, pin):
        super().__init__(pin)
    
    def is_blocked(self):
        """
        빛이 차단되어 감지되었는지 여부 (슬롯이 막혔는지)
        """
        return self.value == 1  # 슬롯이 막히면 물체 인지 
        #사용하는 포토인터럽터 센서의 출력이 반대일 수도 있음
        #위 예제는 물체가 있을 때 감지하는 코드
        #만약 센서가 반대로 인식한다면 value 값을 0으로 바꿀 것
    
#===========================================================================================================#
#터치센서 클래스
class TouchSensor(DigitalInputDevice):
    """
    터치 감지 센서를 위한 클래스
    터치되면 출력값이 바뀜
    """

    def __init__(self, pin):
        super().__init__(pin)

    def is_touched(self):
        """
        센서가 터치되었는지 여부
        일반적으로 터치되면 HIGH 출력
        """
        return self.value == 1
        #센서의 출력이 반대일 수도 있음
        #위 예제는 물체가 있을 때 감지하는 코드
        #만약 센서가 반대로 인식한다면 value 값을 0으로 바꿀 것

#===========================================================================================================#
#조도센서 클래스
class LightSensor:
    """
    아날로그 조도 센서 클래스 (예: CDS 센서)
    밝기 값은 0~100의 비율로 반환됨
    """
    def __init__(self, pin):
        self.adc = ADC(pin)

    def read_value(self):
        """
        원시 ADC 값을 0~65535 범위로 반환
        """
        return self.adc.read_u16()

    def brightness(self):
        """
        밝기 비율(0~100%)로 반환
        CDS는 밝을수록 값이 낮아짐 → 반전하여 % 계산
        """
        raw = self.read_value()
        percentage = (65535 - raw) * 100 // 65535
        return percentage

    def is_dark(self, threshold=60):
        """
        어두운 상태인지 판단 (기본 임계값: 60%)
        """
        return self.brightness() > threshold
    
    

