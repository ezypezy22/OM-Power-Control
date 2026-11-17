# Auto-tune minimum input power by band (OM-4001A)

The amplifier waits in **Waiting for input power** until the drive on the band is high enough, then moves to
**Auto-tune in progress**. The minimum differs by band. It is **not** in the manufacturer's rev.4 communication
protocol document (checked: the PDF is plain text and has no tuning-power table), so it is being measured on
real hardware here. Check the OM-4001A user manual too; if it publishes a table, record it below and note the source.

This page is an operator measurement log, not a manufacturer drive-power specification. The current profile contains the single-measurement figures below as advisory fallback text only; they have not met a repeated-measurement validation threshold. Repeat measurements or confirm against the manual before treating them as established thresholds. The amplifier’s live prompt takes precedence; all drive remains subject to manufacturer limits.

## How to measure

1. Use a resonant antenna with a low SWR (note the SWR below) and a clear frequency. The app never keys the radio;
   you control RF and must identify as your licence requires.
2. Connect, select **Operate**, press **Auto-tune**, and enter the admin password when asked.
3. In the **Auto-tune** popup, wait for *Waiting for input power*. The popup shows the **band**, the **input now**,
   the **highest** input seen and the input **when the tune began**.
4. Start with the lowest drive your radio gives and **raise it slowly** in small steps, pausing a second between
   steps. Stop raising the moment the popup changes to *Auto-tune in progress*.
5. Record **Tune began at** (the input when the amplifier started) and **Highest**. Both are whole watts, as reported
   by the amplifier, and the page refreshes about once a second, so a fast ramp can under-read. Raise the drive
   slowly for a trustworthy number.
6. Let the tune finish (or **Stop** / **Exit**), then stop RF yourself.

## Safety

- Keep to the drive level the manual prescribes as the maximum. Do not raise drive to find a limit.
- Stop RF immediately on any alert, a rising reflected power or SWR, or an unexpected message.
- If the tune does not start at a drive you are comfortable with, stop and record "no start at N W".

## The amplifier states the minimum itself

When the drive is too low the amplifier keeps waiting and sends `AUTO:INCREASE INPUT POWER ABOVE 8.0W!` (seen on 40 m, 2026-11-16).
The app shows that figure in the popup ("Increase input to 8 W") and treats it as authoritative; the table below is only a
fallback shown before the amplifier has said anything. The measured 40 m value (8 W) matches. Note the wording is
*above* 8.0 W, and the amplifier reports whole watts, so the real threshold may sit just over the figure.

## Results

| Band | Date | Firmware | Antenna / SWR | Tune began at (W) | Highest (W) | Result | Notes |
|------|------|----------|---------------|-------------------|-------------|--------|-------|
| 160 m | | | | | | Not tested | No antenna available |
| 80 m | | | | | | Not tested | No antenna available |
| 60 m |  |  |  |  |  |  |  |
| 40 m | 2026-11-16 | 3.42 | resonant antenna | 8 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 30 m | | | | | | Not tested | No antenna available |
| 20 m | 2026-11-16 | 3.42 | resonant antenna | 8 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 17 m | 2026-11-16 | 3.42 | resonant antenna | 6 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 15 m | 2026-11-16 | 3.42 | resonant antenna, SWR 1.2:1 | 4 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 12 m | 2026-11-16 | 3.42 | resonant antenna | 11 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 10 m | 2026-11-16 | 3.42 | resonant antenna | 7 | | Tune started | Minimum input for auto-tune to start (operator-reported, single measurement) |
| 6 m |  |  |  |  |  |  |  |

The first measurements (2026-11-16, OM-4001A, firmware 3.42) were reported by the operator as the minimum input at which
auto-tune started. Each is a single measurement, so repeat before relying on them. 60 m and 6 m have not been tried.
The 15 m figure (4 W) differs from the 5 W the operator first gave as an illustrative example, which was never a measurement.

The minimum does not rise steadily with frequency (40 m and 20 m both 8 W, 12 m 11 W, 10 m 7 W), so a per-band table
is needed rather than a formula.

## Other things worth recording

- Whether the minimum changes with SWR, or on a second tune on the same band.
- The OT (tuning offset) value shown at the end of the tune, which should settle near 0 dB.
- Anything the amplifier says that the app did not expect.
