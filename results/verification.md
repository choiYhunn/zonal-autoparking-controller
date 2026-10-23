# Verification record

The public reconstruction passed **26 unittest test methods** on Python 3.13 in the local Windows environment. The suite covers the sequence and time boundaries; detection hold/reset and inclusive range; strict rear threshold; zero, missing, nonfinite, stale, future and out-of-range inputs; no echo and timeout priority; terminal behavior; clock rejection; configuration checks; steering polarity; and Zone 3 encoding in forward, reverse and stop.

```sh
python -m unittest discover -s tests -v
python -m src.demo
```

The committed [demo output](model-demo.txt) is generated from synthetic samples and can be reproduced with the second command. It is not a vehicle log or a simulation of vehicle kinematics. GitHub Actions runs the same suite on Python 3.10 and 3.13; consult the workflow runs for their actual status.

Historical recovery: completed `parking.py` and versions 2–8 passed syntax compilation after replay. Historical skeleton remains incomplete; it was not edited or executed. Syntax checking establishes no motor behavior.

No new hardware test was performed. No parking success rate, pose accuracy, end-to-end latency, packet-loss rate, or functional-safety claim is made.
