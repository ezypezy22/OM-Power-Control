# OM Power Control 0.1.35 prerelease 4 (build 46) — hardware validation status

This prerelease uses the normal app identity and settings, unlike prerelease 3’s separate Preview identity. Quit the Preview and normal app before opening this build; check its saved address and auto-connect preference. The Mac build requires Apple Silicon and macOS 14 or later and retains the normal app identity and station settings. Earlier PR11 previews used separate settings; those preview settings are not automatically imported. Enter the amplifier address manually if it is not already saved. Auto Discovery is currently available in KPA1500 Control, not OM Power Control.

Close other amplifier clients before connecting. Choose the correct model and confirm the reported amplifier model/firmware and readings. OM4001A operating controls and Auto Tune are enabled based on operator-reported hardware testing. The experimental session opt-in has been removed. OM2501A remains monitoring only.

For OM4001A, click Auto-tune and confirm; an Unlock tuning dialog requests the amplifier admin password unless one is already saved. OM3501A does not require this password. Remember saves only after the amplifier accepts it; a wrong typed password does not erase a good saved one. Storage is a private file, not encrypted. Settings provides Forget saved admin password. Passwords are excluded from snapshots and redacted in traces.

The operator supplies and stops RF and sets drive under manufacturer instructions. This app never keys the radio or adjusts drive. Stop sends one request; stop RF manually. Exit waits for RF-off and amplifier confirmation. Do not infer successful tuning from a stopped or interrupted tune. Fault, freshness, countdown, command-confirmation and no-retry protections remain.

Check prominent SWR, full/compact layout, callsign wrapping, steady LIVE/Operate borders, pulsing LIVE LED, themes, and About amplifier click-outside dismissal. Fan-setting commands and abnormal hardware paths need further operator validation. Portable/simulation tests are not hardware certification.

After exiting an unused tune, confirm the waiting banner/window dismisses after amplifier confirmation and later normal transmission stays silent. A successful/aborted current tune with RF still on must retain its stop-transmitting alert until fresh RF-off confirmation.

## Remaining operator checks

- Confirm the main-page tuning-ready message disappears when tuning starts or completes and remains cleared after dismissing the successful result. Starting a new tune must show readiness again only while waiting for RF.
- On OM4001A, verify Exit with RF off: the amplifier may answer only PTTOFF; the app requests status and waits for the tuning flag to become `-`. PTTOFF alone is not confirmation of leaving tuning mode. An unconfirmed result remains uncertain; do not retry automatically.
- Fan read has operator trace evidence; fan set commands (temperature/PTT/always on) still need deliberate operator confirmation against the amplifier display.
- Check native macOS window appearance when changing each theme. Browser and contrast tests do not establish native-window behavior.
- OM2501A remains monitoring only; this release does not validate operating or tuning controls for it.

Operator OM4001A firmware 3.42 traces report successful tuning/saving, admin unlock, input-power waiting prompts, Stop and PTTOFF after Exit. They are supplied hardware evidence, not independently executed tests by this review. The manufacturer has been asked about relay cycling/re-arming after Stop while RF remains applied; guidance is still outstanding. Stop RF manually. The automatic Stop-then-Exit workaround remains disabled.

Record model, firmware, app version, completed checks, observed versus expected outcomes and relevant timestamped replies. Do not deliberately provoke faults. These open hardware checks do not authorize equipment access by automated review.
