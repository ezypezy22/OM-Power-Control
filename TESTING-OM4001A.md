# OM Power Control 0.1.35 prerelease 3 (build 43)

Apple Silicon. This preview uses separate station settings from the normal release. Settings from the local PR11 test builds are reused. Enter the amplifier address manually when first using the preview; Auto Discovery is currently available in KPA1500 Control, not OM Power Control.

Close other amplifier clients before connecting. Choose the correct model and confirm the reported amplifier model/firmware and readings. OM4001A operating controls and Auto Tune are enabled based on operator-reported hardware testing. The experimental session opt-in has been removed. OM2501A remains monitoring only.

For OM4001A, click Auto-tune and confirm; an Unlock tuning dialog requests the amplifier admin password unless one is already saved. OM3501A does not require this password. Remember saves only after the amplifier accepts it; a wrong typed password does not erase a good saved one. Storage is a private file, not encrypted. Settings provides Forget saved admin password. Passwords are excluded from snapshots and redacted in traces.

The operator supplies and stops RF and sets drive under manufacturer instructions. This app never keys the radio or adjusts drive. Stop sends one request; stop RF manually. Exit waits for RF-off and amplifier confirmation. Do not infer successful tuning from a stopped or interrupted tune. Fault, freshness, countdown, command-confirmation and no-retry protections remain.

Check prominent SWR, full/compact layout, callsign wrapping, steady LIVE/Operate borders, pulsing LIVE LED, themes, and About amplifier click-outside dismissal. Fan-setting commands and abnormal hardware paths need further operator validation. Portable/simulation tests are not hardware certification.

After exiting an unused tune, confirm the waiting banner/window dismisses after amplifier confirmation and later normal transmission stays silent. A successful/aborted current tune with RF still on must retain its stop-transmitting alert until fresh RF-off confirmation.
