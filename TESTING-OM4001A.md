# OM4001A experimental hardware test

Use this prerelease only for deliberate operator-supervised testing under the amplifier manufacturer’s instructions and station limits. Quit other OM Power app copies first. The app shares your existing settings. Apple Silicon and macOS 14 or newer are required.

1. With RF off, select the amplifier address and model, connect, and confirm About amplifier reports OM4001A and the actual firmware (3.16 or newer). Check the upper-left heading reads OM4001A Control and readings match the amplifier.
2. In Settings, enable experimental OM4001A testing and confirm the warning. Permission applies only to this connection. Verify basic Operate/Standby and normal power/cooling behavior first. The app blocks commands during warm-up and cooling.
3. Proceed to Auto Tune only when basic controls and telemetry are confirmed and the station is configured under the manufacturer’s instructions. Select Operate and Start Auto Tune. Wait for the amplifier’s confirmed waiting state before manually supplying the prescribed RF/drive. The app does not key or adjust the radio.
4. Observe tuning and confirmed completion. Stop RF manually as required by the manufacturer. Check the amplifier’s own display and settings; an app message alone is not hardware validation. Test waiting-state Exit and active-tuning Stop only within the manufacturer’s permitted procedure. Unexpected replies or unconfirmed commands require operator review; do not repeatedly click or retry.
5. Reconnect and confirm experimental controls have returned to disabled. Verify saving unrelated settings does not change the DX Caliber shared measurement.

Report amplifier model, firmware, macOS version, prerelease version, which steps were completed, expected versus observed results, and relevant timestamped protocol responses. Do not post station credentials, private network details or unrelated captures publicly. No intentionally induced faults, RF transmission into an unsuitable load, or protection bypass is required.

Simulation tests validate the app’s state handling only; they do not certify OM4001A hardware behavior.
