# TASK_05: Raspberry Pi 5 sensor HAT and enclosure

> English summary. The full documentation of this repository is in Ukrainian: [README.md](README.md).

A 2-layer 85 x 60.77 mm board that clips onto the Pi 5's 2x20 header and carries GPS, an IMU + magnetometer + barometer, an SPI accelerometer, two buttons and an RGB LED — plus a parametric Fusion 360 enclosure housing the Pi and the board. Manufactured and verified on real hardware.

Design decisions a reviewer can check in the files:
- the board extends about 20 mm past the Pi on the left, so it never covers USB and Ethernet; mounting holes 2.7 mm on a 58 x 49 mm grid match the Pi;
- origin on pin 1 of the connector; custom symbol + footprint libraries kept in the repo;
- DRC clean (0 violations) after two review rounds; Gerbers and drill in mm with the fab house's naming, generated from a verified STEP export;
- enclosure built by a Python script in Fusion 360 (parametric), printable without supports except one bridge, ventilation cells, rounded corners, engraved label.

Problems found on the way: a blocked connector produced false Net Antennae; a "Remove Necks" rule isolated header GND pins; Component Pushing blocked placement; silk thickness fixed by scripts.

Stack: Altium Designer, Fusion 360 (Python API), 3D printing, Gerber/STEP.
