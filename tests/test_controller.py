import math
import unittest
from src.parking_controller import Calibration, Command, Config, Controller, Sample, State


def tick(c, now, right=35, rear=80):
    return c.tick(now, Sample(right, now), Sample(rear, now))


def wall_approach():
    c = Controller()
    for t in (0, 1, 2, 4.5, 7.5):
        tick(c, t)
    assert c.state == State.REVERSE_TO_WALL
    return c


class ParkingTests(unittest.TestCase):
    def test_sequence_and_time_boundaries(self):
        c = Controller()
        for t, state, command in [
            (0, State.SCAN_RIGHT, Command(0, 55)),
            (.999, State.SCAN_RIGHT, Command(0, 55)),
            (1, State.FWD_AFTER, Command(0, 50)),
            (1.999, State.FWD_AFTER, Command(0, 50)),
            (2, State.LEFT_FWD, Command(-12, 50)),
            (4.499, State.LEFT_FWD, Command(-12, 50)),
            (4.5, State.RIGHT_REV, Command(12, -45)),
            (7.499, State.RIGHT_REV, Command(12, -45)),
            (7.5, State.REVERSE_TO_WALL, Command(0, -45)),
        ]:
            self.assertEqual(tick(c, t), command)
            self.assertEqual(c.state, state)

    def test_confirmation_resets_when_object_disappears(self):
        c = Controller()
        for t, d in [(0, 35), (.9, 4000), (1, 35), (1.9, 35)]:
            tick(c, t, right=d)
        self.assertEqual(c.state, State.SCAN_RIGHT)
        tick(c, 2, right=35)
        self.assertEqual(c.state, State.FWD_AFTER)

    def test_detection_range_is_inclusive(self):
        for d in (10, 70):
            with self.subTest(distance=d):
                c = Controller(); tick(c, 0, right=d); tick(c, 1, right=d)
                self.assertEqual(c.state, State.FWD_AFTER)

    def test_outside_detection_range_never_confirms(self):
        for d in (9, 71, 4000):
            with self.subTest(distance=d):
                c = Controller(); tick(c, 0, right=d); tick(c, 2, right=d)
                self.assertEqual(c.state, State.SCAN_RIGHT)

    def test_strict_rear_threshold(self):
        c = wall_approach()
        self.assertEqual(tick(c, 8, rear=20), Command(0, -45))
        self.assertEqual(tick(c, 8.5, rear=19), Command())
        self.assertEqual(c.state, State.DONE)

    def test_zero_missing_or_invalid_rear_never_means_done(self):
        for d in (0, None, -1, 1, 351, math.nan, math.inf):
            with self.subTest(distance=d):
                c = wall_approach()
                self.assertEqual(tick(c, 8, rear=d), Command())
                self.assertEqual(c.state, State.STOP)

    def test_no_echo_waits_then_times_out(self):
        c = wall_approach()
        tick(c, 17.499, rear=4000)
        self.assertEqual(c.state, State.REVERSE_TO_WALL)
        self.assertEqual(tick(c, 17.5, rear=4000), Command())
        self.assertEqual(c.reason, "rear-timeout")

    def test_timeout_has_priority_at_deadline(self):
        c = wall_approach(); tick(c, 17.5, rear=19)
        self.assertEqual(c.state, State.STOP)
        self.assertEqual(c.reason, "rear-timeout")

    def test_rear_is_checked_on_entry(self):
        c = Controller()
        for t in (0, 1, 2, 4.5): tick(c, t)
        self.assertEqual(tick(c, 7.5, rear=0), Command())
        self.assertEqual(c.state, State.STOP)

    def test_stale_right_stops(self):
        c = Controller()
        self.assertEqual(c.tick(1, Sample(35, .49), Sample(80, 1)), Command())
        self.assertEqual(c.reason, "right-sensor-stale-or-future")

    def test_stale_rear_stops(self):
        c = wall_approach()
        self.assertEqual(c.tick(8, Sample(35, 8), Sample(19, 7.49)), Command())
        self.assertEqual(c.state, State.STOP)

    def test_future_sensor_stops(self):
        c = Controller(); c.tick(0, Sample(35, 1), Sample(80, 0))
        self.assertEqual(c.state, State.STOP)

    def test_freshness_boundary(self):
        c = Controller(); c.tick(1, Sample(35, .5), Sample(80, 1))
        self.assertEqual(c.state, State.SCAN_RIGHT)

    def test_invalid_right_stops(self):
        for d in (0, None, -1, 351, math.nan):
            c = Controller(); tick(c, 0, right=d)
            self.assertEqual(c.state, State.STOP)

    def test_scan_timeout_stops(self):
        c = Controller(); tick(c, 0, right=4000); tick(c, 30, right=4000)
        self.assertEqual(c.reason, "scan-timeout")

    def test_operator_stop_latches(self):
        for start in (Controller, wall_approach):
            c = start(); self.assertEqual(c.stop(), Command())
            tick(c, 100, rear=19)
            self.assertEqual(c.state, State.STOP)

    def test_completion_latches_zero_output(self):
        c = wall_approach(); tick(c, 8, rear=19)
        self.assertEqual(tick(c, 9, rear=80), Command())
        self.assertEqual(c.state, State.DONE)

    def test_clock_reversal_stops(self):
        c = Controller(); tick(c, 1); self.assertEqual(tick(c, 0), Command())
        self.assertEqual(c.reason, "invalid-clock")

    def test_nonfinite_clock_stops(self):
        for t in (math.nan, math.inf):
            c = Controller(); tick(c, t)
            self.assertEqual(c.reason, "invalid-clock")

    def test_invalid_configuration_rejected(self):
        for kwargs in ({'left_s': 0}, {'right_min_cm': 80}, {'rear_wall_cm': 2}, {'max_sensor_age_s': math.nan}):
            with self.assertRaises(ValueError): Config(**kwargs)

    def test_zone3_reverse_correction(self):
        p = Calibration().payloads(Command(0, -45))
        self.assertEqual(p['ZONE2'], bytes((1, 45)))
        self.assertEqual(p['ZONE3'], bytes((0, 45)))
        self.assertEqual(p['ZONE4'], bytes((1, 45)))

    def test_zone3_forward_correction(self):
        p = Calibration().payloads(Command(0, 50))
        self.assertEqual(p['ZONE2'], bytes((0, 50)))
        self.assertEqual(p['ZONE3'], bytes((1, 50)))

    def test_steering_polarity(self):
        self.assertEqual(Calibration().payloads(Command(-12, 0))['ZONE1'], bytes((0, 12)))
        self.assertEqual(Calibration().payloads(Command(12, 0))['ZONE1'], bytes((1, 12)))

    def test_uninverted_configuration(self):
        p = Calibration(False, False).payloads(Command(-12, -45))
        self.assertEqual(p['ZONE1'], bytes((1, 12)))
        self.assertEqual(p['ZONE2'], p['ZONE3'])

    def test_stop_payloads_have_zero_magnitude(self):
        self.assertTrue(all(v == bytes((0, 0)) for v in Calibration().payloads(Command()).values()))

    def test_payload_limits_rejected(self):
        for c in (Command(13, 0), Command(0, 256)):
            with self.assertRaises(ValueError): Calibration().payloads(c)


if __name__ == '__main__': unittest.main()
