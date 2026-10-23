# Provenance and contribution

## Recovery

The July 8, 2026 private session contains the uploaded incomplete `parking.py`, generated file bodies, successful replacement operations, copy operations and user-pasted HPC logs. All five archived chunks (p001–p005) were checked against the full conversation. Recovery replayed file creation, copies and replacements in memory; historical shell commands were not executed. Failed tool operations were skipped and every applied replacement required exactly one match. Recovered complete scripts pass syntax compilation only; that is not a new hardware run.

A preserved local `parking.py` was found in the Windows user-home directory, outside the workshop folder. It contains the skeleton with the first next-state blank filled, while other blanks remain. Compared with the session's uploaded skeleton, the only textual change is that first assignment and its comment. Its raw SHA-256 is `115ec5c07d75a2dea3100c5685dc0a8d16fcea53e728f85275f709a0fb2a6b51`.

No standalone preserved `parking_2.py`–`parking_8.py` was found in the searched local corpus. Their historical content was reconstructed from session operations and must not be called recovered original files. The early completed `parking.py` and `parking_2.py` bodies are identical after UTF-8/LF serialization.

| Version | Recoverable change | Evidence / status |
|---|---|---|
| parking.py, local | Incomplete provided skeleton; first transition filled | Preserved local file, not a final controller |
| parking.py, completed | Blanks and missing transition completed | Historical generated body; replayed copy |
| parking_2.py | Completed baseline, old <=15 cm rear rule | Generated body; subsequent terminal output, version inferred from adjacent upload request |
| parking_3.py | Sensor/state/age/decision logs and rear nonpositive guard | Replayed edits; attached terminal run reaches wall approach then timeout |
| parking_4.py | Central tuning, left-forward alignment, rear threshold 20 | Replayed edits; named HPC run remains in PASS_EDGE then timeout |
| parking_5.py | User's five-step timed FSM, right range 10..70 cm, rear timeout 10 s | Replayed edits; no complete run log |
| parking_6.py | Steering-sign inversion | Replayed edits; user reports vehicle wheel behavior under v6 |
| parking_7.py | Per-zone inversion mechanism, flags initially false | Replayed edits; no complete run log |
| parking_8.py | Enable Zone 3 drive inversion | Replayed edit and historical syntax-check output; post-fix vehicle result unknown |

[Recovery hashes](../results/recovery-hashes.csv) describe replay serialization, not original HPC byte hashes. Local private recovery metadata records exact source locations and operation chronology. Raw source, complete logs and private conversation text are not published.

## Why the earlier review missed the application

The previous portfolio review compared the workshop-distributed ZIP with `experiment5` and `project/` trees. That comparison was useful for the ZCU/ECU baseline, but excluded the HPC application downloaded into the Windows home directory. It also did not inspect the July 8 conversation's generated files, edits and run attachments. The SCP prompt records the user-home working directory and `.` as download destination, which explains the surviving file's location. The evidence gap in that narrower comparison did not establish absence of HPC design or field debugging.

## Responsibility

| Area | Attribution |
|---|---|
| ZCU/ECU code, bridge protocol and original HPC skeleton | Workshop-provided baseline; not claimed as my original work |
| Maneuver requirements | I specified detection, phase order, timing, steering and rear threshold after observing the vehicle |
| Python coding | AI-assisted generation and edits under my integration and test direction |
| Hardware integration | I deployed/executed the HPC application and reported sensor/actuator behavior; logs support execution and sensor reception |
| Debugging | I identified inadequate maneuvering, reversed steering and asymmetric wheel behavior, and requested comparison and correction |
| Outcome | Sensor reception and earlier FSM execution/timeout observed; final autonomous parking success unknown |
| This public code | Newly authored portable reconstruction with explicit added guards and host tests; no workshop source copied into `src/` |

The new code replaces threaded global state, sockets and wall-clock polling with immutable inputs and a deterministic controller. Its MIT license applies to new code/documents only. No license is asserted over the workshop skeleton, historical scripts, course figures or private archive. No company artifacts, device MAC addresses, private addresses, credentials or student identifiers are included.
