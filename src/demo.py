"""Synthetic input example. No real vehicle, sensor, or network is connected."""
from .parking_controller import Calibration, Controller, Sample


def main():
    controller = Controller()
    print("SYNTHETIC HOST MODEL - not a hardware measurement")
    for now, rear_cm in [(0, 80), (1, 80), (2, 80), (4.5, 80), (7.5, 80), (8, 20), (8.5, 19)]:
        command = controller.tick(now, Sample(35, now), Sample(rear_cm, now))
        encoded = {z: list(v) for z, v in Calibration().payloads(command).items()}
        print(f"t={now:4.1f} state={controller.state.name:16} logical={command} payloads={encoded}")


if __name__ == "__main__":
    main()
