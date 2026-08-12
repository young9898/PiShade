# PiShade

A motorized roller shade driven by a Raspberry Pi and a stepper motor, so a
cheap pull-down shade opens and closes on solar time instead of on somebody
remembering to pull the cord.

Built in January 2019 for a room with houseplants and an aquarium that wanted a
consistent daily light cycle. Nothing in it is specific to that room — it is a
stepper turning a roller a fixed number of steps, twice a day. It picked up the
name PiShade in 2021, when this repository was created.

> **Note on the code:** the original scripts were never committed. What is here
> is a **reconstruction** written in 2026 from the original build notes. The step
> counts, the mechanism, and the cron schedule are the real ones. The code is
> new, written against the documented library API rather than recovered.

## How it works

A NEMA 17 stepper turns the shade's roller through an Adafruit Motor HAT on
the Pi's GPIO header. Two cron jobs run the shade to its limit in each
direction. There are no limit switches and no encoder — the travel is a step
count that was calibrated once and has not needed to change.

## The calibration, and why it is 3200

A NEMA 17 is 1.8° per step, so 200 full steps per revolution. The Adafruit
library's `INTERLEAVE` style doubles the resolution to **400 steps per
revolution**; `MICROSTEP` at the library's default of 8 gives 1600.

The original calibration was done by taping a mark on the roller, stepping the
motor, and counting until the mark came back around. That produced "about 428
steps per rotation" — 7% over the true 400, which is exactly what counting to a
visual mark with a little slop in the drive looks like.

Full travel was then set at **3200 steps**, picked because it was a tidy round
number. It happens to land on **exactly 8.0 revolutions**, and at the measured
~1.6 inches of shade per revolution that is roughly **12.8 inches** of travel.
A separate note in the build log — 4000 microsteps ≈ 4 inches — is the same
geometry seen through the 1600-steps/rev microstep mode, and agrees.

The lesson worth keeping: the sloppy hand calibration was 7% wrong, and it did
not matter, because the number that got used was rounded to something the
mechanism could absorb. Shades are forgiving. Do not build an encoder for this.

### Interleave vs. microstep

`INTERLEAVE` was chosen over `MICROSTEP` deliberately. Microstepping buys
smoothness and resolution that a window shade has no use for, at the cost of
4× the steps for the same travel and less torque per step. Interleave has
enough torque to overcome the shade's static friction on startup, which is the
only hard moment in the cycle.

## Scheduling

The original schedule was plain fixed-time cron:

```cron
0 17 * * * /usr/bin/python3 /home/pi/PiShade/motor_down.py
0  8 * * * /usr/bin/python3 /home/pi/PiShade/motor_up.py
```

Fixed times drift badly against the actual sun across a year. The better
version uses [`sunwait`](https://github.com/risacher/sunwait), which blocks
until sunrise or sunset at a given latitude/longitude:

```cron
# Substitute your own coordinates. Two decimal places is plenty — the sun does
# not care, and six decimals pins a residence to the centimetre.
0 4 * * * sunwait wait rise 00.00N 000.00W && /usr/bin/python3 /home/pi/PiShade/motor_up.py
0 15 * * * sunwait wait set 00.00N 000.00W && /usr/bin/python3 /home/pi/PiShade/motor_down.py
```

Check `sunwait`'s own docs for the exact argument form on your build; it also
supports civil-twilight offsets, which are usually what you actually want for a
shade rather than true sunrise.

## Parts

| Part | Notes |
|---|---|
| Raspberry Pi | Any model with the 40-pin header |
| Adafruit Motor HAT (or DC+Stepper HAT) | Stepper terminal 1 |
| STEPPERONLINE NEMA 17 stepper | 26 N·cm (36.8 oz-in), 12 V, 0.4 A/phase |
| 12 V supply for the HAT | Separate from the Pi's own supply |
| Roller shade | An inexpensive hardware-store pull-down |
| 3D printed parts | Motor mount and a coupler to the roller tube |

The 26 N·cm motor is generously sized for this. Shade torque is dominated by
static friction at startup, not by the weight of the fabric.

## Printed parts

The three parts that were actually installed, in `models/`. These are the
as-printed 2019 STLs, not a re-modelled set — there is no CAD source, only the
mesh.

| File | Size | Notes |
|---|---|---|
| `models/roller_hub.stl` | Ø31.3 × 21.8 mm | Drives the roller tube. Ø31.3 is a slip fit into a nominal 1¼ in (31.75 mm) tube; check yours with calipers, tubes vary. |
| `models/motor_bracket.stl` | 66.4 × 57.5 × 55.2 mm | Carries the NEMA 17 at the driven end. |
| `models/end_bracket.stl` | 81.4 × 61.8 × 45.4 mm | Idler end, opposite the motor. |

The hub took four revisions to fit — Ø46.5, then 33.3, then 31.3 — which is the
usual story of measuring a tube's inside diameter by eye and then by caliper.
Printed in PLA at 0.2 mm layers, 20% infill; the hub was run at 0.08 mm and 80%
because it is the part that transmits all the torque.

Dimensions above were measured off the original toolpaths, not read from a
model tree. Print one, check it against your own hardware before committing to
the pair.

## Running it

```bash
pip3 install adafruit-circuitpython-motorkit
python3 shade.py up --dry-run     # prints the move, touches no hardware
python3 shade.py down             # full travel
python3 shade.py up 400           # one revolution, for calibration
```

`shade.py` imports the Adafruit stack lazily, so `--dry-run` works on a laptop.
The motor is released after every move — a stepper held at standstill draws
full rated current and gets hot for no benefit, and friction holds the shade
fine.

## Attribution

The 2019 original was adapted from the `StepperTest.py` example in
[adafruit/Adafruit-Motor-HAT-Python-Library](https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library).
That repository is archived and carries **no license file**, so none of its
code is reproduced here — this implementation was written fresh against the
API. Credit for the original approach belongs to Adafruit.

For anything new, use Adafruit's modern MIT-licensed replacement,
[`adafruit-circuitpython-motorkit`](https://github.com/adafruit/Adafruit_CircuitPython_MotorKit),
which is what the code here targets.

## License

MIT — see [LICENSE](LICENSE). Relicensed from GPL-3.0 in 2026; copies
distributed under the earlier license remain under it.
No strings beyond the license file, and no policing. If this saves you an
afternoon, that is the whole point. Credit is appreciated and never demanded; if
you build something better on top of it, that is the best outcome available.

## Contact

github@youngnetwork.org
