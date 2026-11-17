OM Power Control 0.1.35 prerelease 4 (build 46)

Build 46: tuning window now shows frequency in the header and numeric SWR using the main meter’s green/brown/red scale. Removes the band label. Adds the Screen Current (Iscreen) meter between Load Position and Output Power for OM3501A only; other reported models omit it. Stale/disconnected readings remain unavailable.

- Integrates PR #11: redesigned full/compact views, prominent SWR and fixed reflected/input meters, auxiliary fan controls, selectable colour themes and an OM2501A monitoring-only profile.
- Enables OM4001A operating controls and password-unlocked automatic tuning based on operator-reported firmware 3.42 testing. Unknown models remain monitoring only; warm-up/cooling, transmission, fault, freshness and command-confirmation guards remain enforced.
- Remembers a typed admin password only after the amplifier accepts it. A rejected typed password does not replace/delete a working saved password. Saved passwords use a private, unencrypted local file; Settings offers Forget. Passwords are excluded from snapshots and redacted in traces.
- Adds a dedicated automatic-tuning window with Tune/Load positions, tuning offset, power/input feedback and current-tune RF-stop alerts. Confirmed RF-off settles the alert so later normal transmission stays silent.
- Confirms Exit from the amplifier's tuning-status flag when no explicit exit acknowledgment is supplied. Stop/Exit wait longer for confirmation and accept bounded late replies; uncertain results are not retried.
- Clears stale “Automatic tuning ready” feedback when the amplifier leaves the waiting phase, including successful tuning and result dismissal. Preserves readiness for a new waiting tune and preserves pending/uncertain command warnings.
- Preserves the DX Caliber shared measurement when saving unrelated settings. Normal app identity/settings are retained; preview-specific identities and folders are not used.

Local candidate validation: 344 Python tests, 340 passed and four expected skips (two optional private captures and two Windows-only named-object checks); all eleven JavaScript suites passed, including the actual UI readiness regression. Swift typecheck and Mac build/signature verification passed. No live amplifier operations were executed.

Validation and limits: see TESTING-OM4001A.md for operator evidence and remaining fan-setting, native-theme and status-confirmed Exit checks. Manufacturer guidance on Stop while RF remains applied is outstanding; the automatic Stop-then-Exit workaround stays disabled. No manual-tuning controls are included. The operator supplies/stops RF and sets drive; the app never keys the radio.

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
