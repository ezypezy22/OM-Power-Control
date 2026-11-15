OM Power Control 0.1.35-om4001a.1 — experimental prerelease

Based on PR #11 and released 0.1.34. Compact/horizontal display redesign. Upper-left amplifier headings omit the hyphen and prefer the actual reported model.

Explicit per-connection opt-in for unverified OM4001A basic controls and Auto Tune. Requires identified OM4001A firmware 3.16+, fresh confirmed idle, fault-free data, and operator acknowledgement. Off by default and resets on reconnect/restart. No experimental controls through DX Caliber.

Review fixes preserve countdown inhibition and saved companion measurement. Existing transmit/fault/model/freshness checks, acknowledgement handling, Stop behavior and no-retry policy remain. No radio keying, drive changes or fault reset.

Hardware validation pending. See TESTING-OM4001A.md.

OM Power Control 0.1.34 for Mac

- Adds amplifier-reported model, serial number, firmware and operating time; compact electrical readings; Load/Tune position percentages; cooling temperature; warning/fault displays.
- Adds monitoring-only OM4001A display profiles and simulator; OM3501A operating controls remain supported.
- Retries initial TCP connection failures for up to 60 seconds; operating commands and ended sessions are never automatically retried.
- PTT-on status revokes older idle evidence, including during tuning. Idle-looking status alone cannot release the transmit latch.
- Unsupported reported models remain monitoring-only regardless of saved label. Hard/high-voltage faults remain latched until reconnect after amplifier recovery; no automatic fault reset.
- Auto-tune Start/Exit reflect fault and identification-wait restrictions. The separately permitted fault-time Stop action remains available.

Validation: final PR revision: 295 Python tests (291 passed, four expected private-capture/Windows skips), all 7 JavaScript suites passed. User reports testing the OM3501A build and that it looks good; this is not exhaustive fault or full-range hardware validation. OM4001A operating controls remain blocked. Operator supplies/stops RF and sets drive power; the app never keys the radio.

Apple Silicon, macOS 14 or later. Close the previous app before replacing it; one client owns the amplifier connection. Existing station settings are retained.

OM Power Control 0.1.31 beta

- Adds Dismiss to completed auto-tune exit banners, including restored defaults and stopped-tune outcomes. Dismissal survives monitoring updates; a new tune shows its result again.

OM Power Control 0.1.30 beta

Apple Silicon · macOS 14 or later · by NY6C

New since 0.1.26:
- Automatic tuning on the verified OM-3501A: confirmed entry/readiness, live readings, Stop, and Exit.
- Operator supplies and controls RF; the app does not key the radio or adjust drive power.
- Green SUCCESSFUL AUTOTUNE banner with amplifier-reported automatic saving. The banner remains until Dismiss; each new successful tune shows it again.
- Clear distinction between successful tuning, defaults restored after RF interruption, and settings saved after Stop. Interrupted/stopped tuning is never reported as successful.
- Unexpected replies, delayed tuning status, connection loss and unanswered commands display warnings without automatic retries.
- Clear instruction: “Stop transmitting before clicking Exit auto-tune.”

Includes the existing configurable measurements, antenna display, compact/stay-on-top view, About menu, callsign badge and optional DX Caliber sharing through one amplifier connection. DXC’s embedded panel continues to provide its existing readings and power/mode controls; auto-tune controls are in the standalone app.

Validation: live operator checks of successful tune/save, entry/Exit, RF interruption/default recovery, and Stop/Exit acknowledgment. All six local auto-tune captures replayed in regression tests; 72 Python tests completed (70 passed, two unrelated optional capture tests skipped), plus JavaScript presentation and actual UI-handler checks.

Compatibility is established only for the tested OM-3501A. Other models remain monitoring only. Some abnormal amplifier responses and firmware behaviors remain unverified. An unanswered Stop/Exit sequence observed in the Windows client is handled as uncertain rather than automatically retried.

The app and DMG are Developer ID signed, Apple-notarized and stapled. No Python installation is required. Close other amplifier clients before connecting; one client owns the amplifier connection.
