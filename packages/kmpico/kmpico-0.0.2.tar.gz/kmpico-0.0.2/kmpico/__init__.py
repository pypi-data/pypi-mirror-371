__name__ = "kmpico"
__package__ = "kmpico"
# 버전과 author 정보는 pyproject.toml에서 관리하는 것이 최신 방식이지만,
# picozero 스타일을 따르기 위해 여기에 명시할 수 있습니다.
__version__ = '0.0.2'  # pyproject.toml의 버전과 일치시키세요.
__author__ = "limtae"

# kmpico.py 파일로부터 사용자가 직접 사용할 클래스들을 가져옵니다.
from .kmpico import (
    # Exceptions
    PWMChannelAlreadyInUse,
    EventFailedScheduleQueueFull,

    # Functions
    pinout,

    # Output Devices
    DigitalOutputDevice,
    DigitalLED,
    Buzzer,
    PWMOutputDevice,
    PWMLED,
    LED,
    pico_led,
    PWMBuzzer,
    Speaker,
    RGBLED,
    Motor,
    Robot,
    Servo,
    Neopixel,
    WaterPump,

    # Input Devices
    DigitalInputDevice,
    Switch,
    Button,
    AnalogInputDevice,
    Potentiometer,
    Pot,
    TemperatureSensor,
    pico_temp_sensor,
    TempSensor,
    Thermistor,
    DistanceSensor,
    DHTSensor,
    WaterLevelSensor,
    SoilMoistureSensor,
    ShockSensor,
    PhotoInterrupter,
    TouchSensor,
    LightSensor,
    
    # Display Devices
    OLED,
    I2C_LCD,
)