"""PiShade — drive a roller shade from a Raspberry Pi stepper motor.

SUBJECT: motion control for a roller-shade roller driven by a NEMA 17 stepper
through an Adafruit Motor HAT; travel constants below were calibrated by
counting steps against a mark on the roller, not by CAD.

Reconstruction (2026) of a 2021 script that was not kept under version
control. The step counts and the cron schedule are from the original notes;
the code itself is new, written against the documented MotorKit API.
"""

import atexit
import sys

# --- Calibration -----------------------------------------------------------
# A NEMA 17 is 1.8 deg/step -> 200 full steps per revolution.
# INTERLEAVE doubles that to 400 steps/rev; MICROSTEP (8x) gives 1600.
STEPS_PER_REV_FULL = 200
STEPS_PER_REV_INTERLEAVE = STEPS_PER_REV_FULL * 2

# Full travel, measured on the installed shade: 8 revolutions of the roller.
TRAVEL_STEPS = 3200                      # = 8.0 rev in INTERLEAVE
INCHES_PER_REV = 1.6                     # roller circumference, measured
TRAVEL_INCHES = TRAVEL_STEPS / STEPS_PER_REV_INTERLEAVE * INCHES_PER_REV

STEPPER_PORT = 1                         # Motor HAT stepper terminal 1/2
STEP_DELAY_S = 0.005                     # ~200 steps/s; slow enough not to stall


def _hardware():
    """Import the Adafruit stack lazily so the module is importable off-Pi."""
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper

    kit = MotorKit()
    motor = kit.stepper1 if STEPPER_PORT == 1 else kit.stepper2
    atexit.register(motor.release)
    return motor, stepper


def move(direction, steps=TRAVEL_STEPS, dry_run=False):
    """Run the roller `steps` interleaved steps in 'up' or 'down'.

    The motor is always released on exit. A stepper left energised at a
    standstill draws its full rated current and gets hot; nothing about a
    shade needs holding torque, gravity and friction hold it fine.
    """
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")

    revs = steps / STEPS_PER_REV_INTERLEAVE
    print(f"{direction}: {steps} steps = {revs:.2f} rev "
          f"= {revs * INCHES_PER_REV:.1f} in")
    if dry_run:
        return

    import time

    motor, stepper = _hardware()
    sense = stepper.FORWARD if direction == "up" else stepper.BACKWARD
    try:
        for _ in range(steps):
            motor.onestep(direction=sense, style=stepper.INTERLEAVE)
            time.sleep(STEP_DELAY_S)
    finally:
        motor.release()


def main(argv):
    if len(argv) < 2 or argv[1] not in ("up", "down"):
        print("usage: shade.py {up|down} [steps] [--dry-run]", file=sys.stderr)
        return 2
    steps = TRAVEL_STEPS
    for arg in argv[2:]:
        if arg != "--dry-run":
            steps = int(arg)
    move(argv[1], steps, dry_run="--dry-run" in argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
