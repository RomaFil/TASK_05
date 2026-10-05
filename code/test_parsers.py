"""Прості перевірки розбору даних. Працюють на будь-якому комп'ютері, без Raspberry Pi: python test_parsers.py"""
import motion_logger_demo as d

# класичний приклад NMEA-рядка зі специфікації, контрольна сума *6A
RMC = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
assert d.nmea_checksum_ok(RMC)
assert not d.nmea_checksum_ok(RMC.replace("123519", "123518"))
r = d.parse_rmc(RMC)
assert r["fix"] and abs(r["lat"] - 48.1173) < 1e-4 and abs(r["lon"] - 11.5167) < 1e-4
assert abs(r["speed_kmh"] - 22.4 * 1.852) < 0.01

# без фіксації (статус V) координат нема
nofix = "$GPRMC,123519,V,,,,,,,230394,,*"
body = nofix[1:-1]
chk = 0
for ch in body:
    chk ^= ord(ch)
assert d.parse_rmc("$" + body + "*%02X" % chk)["fix"] is False

# MPU6050: 1 g по осі Z, 0 °/с, температура 36,53 °C при сирому 0
raw = [0, 0, 0, 0, 0x40, 0x00] + [0, 0] + [0] * 6
accel, temp, gyro = d.mpu6050_convert(raw)
assert accel == (0.0, 0.0, 1.0) and temp == 36.53 and gyro == (0.0, 0.0, 0.0)

# ADXL345: молодший байт першим; 256 відліків ≈ 1 g (0,0039 g/біт)
assert d.adxl345_convert([0x00, 0x01, 0, 0, 0xFF, 0xFF]) == (0.9984, 0.0, -0.0039)
print("усі перевірки пройдено")
