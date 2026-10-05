#!/usr/bin/env python3
"""Motion Logger: ДЕМОНСТРАЦІЙНИЙ код для Raspberry Pi 5 (буде змінюватись).

Раз на секунду читає датчики, пише рядок у CSV-лог і показує стан світлодіодом:
  - MPU6050 (модуль GY-87, I2C, адреса 0x68): прискорення, швидкість обертання, температура;
  - ADXL345 (модуль GY-291, SPI0, CE0): прискорення;
  - GPS NEO-6M (UART): координати, швидкість, чи є фіксація;
  - кнопка 1 (GPIO17): пауза / відновлення запису;
  - кнопка 2 (GPIO13): позначка «MARK» у наступному рядку логу;
  - світлодіод: червоний — нема GPS-фіксації, зелений — є, синій блимає при записі.

Піни взято з таблиці підключень плати (altium/, README.md). На реальному залізі НЕ перевірено.
Якщо якийсь датчик або бібліотека недоступні, програма це пише й продовжує без нього.
"""
import csv
import glob
import os
import sys
import time

# ---------------- налаштування (піни за схемою плати) ----------------
LED_R, LED_G, LED_B = 27, 22, 6          # GPIO світлодіодів (через резистори на платі)
BTN1, BTN2 = 17, 13                      # GPIO кнопок
BUTTON_ACTIVE_HIGH = True                # припущення: натиснута кнопка дає 1; перевірити на залізі
I2C_BUS, MPU_ADDR = 1, 0x68              # I2C1 (піни 3 і 5), AD0 на землі
SPI_BUS, SPI_CS = 0, 0                   # SPI0, CE0 (пін 24)
GPS_PORT = os.environ.get("GPS_PORT", "/dev/ttyAMA2")   # uart2 на GPIO4/5; назву overlay не перевірено
GPS_BAUD = 9600
LOG_FILE = os.environ.get("LOG_FILE", "motion_log.csv")
PERIOD_S = 1.0


# ---------------- розбір даних (працює і без заліза, є тести) ----------------
def to_signed16(hi, lo):
    v = (hi << 8) | lo
    return v - 65536 if v & 0x8000 else v


def mpu6050_convert(raw14):
    """14 байт з регістра 0x3B → (accel_g[3], temp_c, gyro_dps[3]); діапазони ±2 g і ±250 °/с."""
    w = [to_signed16(raw14[i], raw14[i + 1]) for i in range(0, 14, 2)]
    accel = tuple(round(v / 16384.0, 4) for v in w[0:3])
    temp = round(w[3] / 340.0 + 36.53, 2)
    gyro = tuple(round(v / 131.0, 3) for v in w[4:7])
    return accel, temp, gyro


def adxl345_convert(raw6):
    """6 байт з регістра 0x32 → прискорення в g (повна роздільність ≈ 3,9 мг/біт)."""
    return tuple(round(to_signed16(raw6[i + 1], raw6[i]) * 0.0039, 4) for i in range(0, 6, 2))


def nmea_checksum_ok(line):
    """Перевірка контрольної суми NMEA: XOR символів між '$' і '*'."""
    if not line.startswith("$") or "*" not in line:
        return False
    body, _, tail = line[1:].partition("*")
    calc = 0
    for ch in body:
        calc ^= ord(ch)
    try:
        return calc == int(tail[:2], 16)
    except ValueError:
        return False


def _deg(value, hemi):
    """ddmm.mmmm → градуси."""
    if not value:
        return None
    dot = value.index(".")
    deg = float(value[:dot - 2]) + float(value[dot - 2:]) / 60.0
    return -deg if hemi in ("S", "W") else deg


def parse_rmc(line):
    """$GPRMC / $GNRMC → dict(fix, lat, lon, speed_kmh) або None, якщо рядок не підходить."""
    if not nmea_checksum_ok(line):
        return None
    f = line.split("*")[0].split(",")
    if f[0][3:] != "RMC" or len(f) < 8:
        return None
    fix = f[2] == "A"
    return {
        "fix": fix,
        "lat": _deg(f[3], f[4]) if fix else None,
        "lon": _deg(f[5], f[6]) if fix else None,
        "speed_kmh": round(float(f[7]) * 1.852, 2) if fix and f[7] else None,
    }


# ---------------- робота із залізом ----------------
class Leds:
    """Світлодіоди й кнопки через libgpiod 2.x (пакет python3-libgpiod)."""

    def __init__(self):
        self.req = None
        try:
            import gpiod
            from gpiod.line import Bias, Direction, Value
            self.Value = Value
            path = self._find_chip(gpiod)
            out = gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
            inp = gpiod.LineSettings(direction=Direction.INPUT,
                                     bias=Bias.PULL_DOWN if BUTTON_ACTIVE_HIGH else Bias.PULL_UP)
            self.req = gpiod.request_lines(path, consumer="motion-logger", config={
                LED_R: out, LED_G: out, LED_B: out, BTN1: inp, BTN2: inp})
            print("GPIO: чип", path)
        except Exception as e:
            print("GPIO недоступний:", e)

    @staticmethod
    def _find_chip(gpiod):
        # На Pi 5 піни гребінки належать мікросхемі RP1; номер gpiochip залежить від ядра.
        for path in sorted(glob.glob("/dev/gpiochip*")):
            try:
                if "rp1" in gpiod.Chip(path).get_info().label.lower():
                    return path
            except Exception:
                pass
        return "/dev/gpiochip0"

    def set(self, r=False, g=False, b=False):
        if self.req:
            V = self.Value
            self.req.set_values({LED_R: V.ACTIVE if r else V.INACTIVE,
                                 LED_G: V.ACTIVE if g else V.INACTIVE,
                                 LED_B: V.ACTIVE if b else V.INACTIVE})

    def pressed(self, pin):
        if not self.req:
            return False
        active = self.req.get_value(pin) == self.Value.ACTIVE
        return active if BUTTON_ACTIVE_HIGH else not active


class Mpu6050:
    def __init__(self):
        self.bus = None
        try:
            from smbus2 import SMBus
            self.bus = SMBus(I2C_BUS)
            self.bus.write_byte_data(MPU_ADDR, 0x6B, 0x00)   # вийти зі сну
            print("MPU6050: ок")
        except Exception as e:
            print("MPU6050 недоступний:", e)
            self.bus = None

    def read(self):
        if not self.bus:
            return None
        try:
            return mpu6050_convert(self.bus.read_i2c_block_data(MPU_ADDR, 0x3B, 14))
        except Exception:
            return None


class Adxl345:
    def __init__(self):
        self.spi = None
        try:
            import spidev
            self.spi = spidev.SpiDev()
            self.spi.open(SPI_BUS, SPI_CS)
            self.spi.max_speed_hz = 1_000_000
            self.spi.mode = 0b11                              # ADXL345 працює в режимі SPI 3
            devid = self.spi.xfer2([0x80 | 0x00, 0x00])[1]   # регістр DEVID, має бути 0xE5
            if devid != 0xE5:
                raise RuntimeError("DEVID=0x%02X, очікувалось 0xE5" % devid)
            self.spi.xfer2([0x2D, 0x08])                      # POWER_CTL: режим вимірювання
            self.spi.xfer2([0x31, 0x08])                      # DATA_FORMAT: повна роздільність, ±2 g
            print("ADXL345: ок")
        except Exception as e:
            print("ADXL345 недоступний:", e)
            self.spi = None

    def read(self):
        if not self.spi:
            return None
        try:
            return adxl345_convert(self.spi.xfer2([0xC0 | 0x32] + [0] * 6)[1:])
        except Exception:
            return None


class Gps:
    def __init__(self):
        self.ser = None
        self.last = {"fix": False, "lat": None, "lon": None, "speed_kmh": None}
        try:
            import serial
            self.ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=0.2)
            print("GPS: порт", GPS_PORT)
        except Exception as e:
            print("GPS недоступний:", e)

    def poll(self):
        """Зчитує все, що накопичилось у порту, і оновлює останнє значення з $xxRMC."""
        if not self.ser:
            return self.last
        try:
            for raw in self.ser.read(self.ser.in_waiting or 1).decode("ascii", "ignore").splitlines():
                data = parse_rmc(raw.strip())
                if data:
                    self.last = data
        except Exception:
            pass
        return self.last


# ---------------- головний цикл ----------------
def main():
    leds, mpu, adxl, gps = Leds(), Mpu6050(), Adxl345(), Gps()
    new_file = not os.path.exists(LOG_FILE)
    log = open(LOG_FILE, "a", newline="", encoding="utf-8")
    out = csv.writer(log)
    if new_file:
        out.writerow(["time", "mark", "mpu_ax_g", "mpu_ay_g", "mpu_az_g", "mpu_temp_c",
                      "gyro_x_dps", "gyro_y_dps", "gyro_z_dps",
                      "adxl_x_g", "adxl_y_g", "adxl_z_g", "gps_fix", "lat", "lon", "speed_kmh"])
    paused, mark, was_pressed1, was_pressed2 = False, False, False, False
    print("Запис у", LOG_FILE, "(Ctrl+C — вихід; кнопка 1 — пауза, кнопка 2 — позначка)")
    try:
        while True:
            t0 = time.time()
            p1, p2 = leds.pressed(BTN1), leds.pressed(BTN2)
            if p1 and not was_pressed1:
                paused = not paused
                print("пауза" if paused else "запис відновлено")
            if p2 and not was_pressed2:
                mark = True
            was_pressed1, was_pressed2 = p1, p2

            fix = gps.poll()
            if not paused:
                m, a = mpu.read(), adxl.read()
                accel, temp, gyro = m if m else ((None,) * 3, None, (None,) * 3)
                row = [time.strftime("%Y-%m-%d %H:%M:%S"), "MARK" if mark else "", *accel, temp, *gyro,
                       *(a if a else (None,) * 3), int(fix["fix"]), fix["lat"], fix["lon"], fix["speed_kmh"]]
                out.writerow(row)
                log.flush()
                print(row)
                mark = False
                leds.set(r=not fix["fix"], g=fix["fix"], b=True)   # синій блимає разом із записом
                time.sleep(0.1)
            leds.set(r=not fix["fix"] and not paused, g=fix["fix"] and not paused, b=False)
            time.sleep(max(0.0, PERIOD_S - (time.time() - t0)))
    except KeyboardInterrupt:
        print("\nвихід")
    finally:
        leds.set()
        log.close()


if __name__ == "__main__":
    sys.exit(main())
