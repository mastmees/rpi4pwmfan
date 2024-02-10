import time
import subprocess
import os.path

# first configure the system by adding
# dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
# into /boot/firmware/config.txt and rebooting
#


class Temperature:

    def __init__(self):
        self._reading = 100.0  # fake high temp at startup to test-start fan

    def _get_raw(self):
        try:
            return (
                int(open("/sys/class/thermal/thermal_zone0/temp", "r").readline())
                / 1000.0
            )
        except (PermissionError, OSError, FileNotFoundError):
            return 100.0

    @property
    def temperature(self):
        self._reading = self._reading * 0.9 + self._get_raw() * 0.1
        return round(self._reading, 3)


class Fan:

    def __init__(self):
        self._initialized = False
        self.cache = {}

    def _init(self):
        # see if pwm device 0 has been enabled, and enable
        # it if not. it takes some time for the
        # /pwm0/ directory to appear and be populated
        if not self._initialized and not os.path.exists("/sys/class/pwm/pwmchip0/pwm0"):
            try:
                with open("/sys/class/pwm/pwmchip0/export", "w") as f:
                    f.write("0\n")
                self._initialized = True
            except (PermissionError, OSError, FileNotFoundError):
                pass
        else:
            self._initialized = True

    def _get(self, name):
        if name in self.cache:
            return int(self.cache.get(name, 0))
        try:
            value = int(open("/sys/class/pwm/pwmchip0/pwm0/" + name, "r").readline())
            self.cache[name] = value
        except (OSError, FileNotFoundError):
            value = 0
            self._init()
        return value

    def _set(self, name, value):
        try:
            with open("/sys/class/pwm/pwmchip0/pwm0/" + name, "w") as f:
                f.write("%d\n" % value)
            self.cache[name] = value
        except (OSError, FileNotFoundError):
            self._init()

    @property
    def speed(self):
        duty = self._get("duty_cycle")
        return int(duty / 40000 * 100)

    @speed.setter
    def speed(self, value):
        current = self.speed
        value /= 100.0
        value = int(value * 40000)
        if value:
            if not self._get("enable"):
                self._set("period", 40000)
                self._set("duty_cycle", 40000)
                self._set("enable", 1)
            else:
                self._set("duty_cycle", value)
        elif self._get("enable"):
            self._set("enable", 0)
            self._set("duty_cycle", 0)


temp = Temperature()
fan = Fan()
statusupdate = time.monotonic()

subprocess.run(["systemd-notify", "--ready"])

while True:
    t = temp.temperature
    threshold = 50 if fan.speed else 55
    speed = 100 if t > 85 else min(int(t - 25.0), 100)
    if t < threshold:
        fan.speed = 0
    else:
        if not fan.speed:
            fan.speed = 100
        else:
            fan.speed = speed
    if time.monotonic() > (statusupdate + 10):
        subprocess.run(
            [
                "systemd-notify",
                f"--status=temperature: {t:.1f} degC, fan speed {fan.speed}%",
            ]
        )
        statusupdate = time.monotonic()
    time.sleep(1)
