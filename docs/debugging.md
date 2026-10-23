# Field debugging and revisions

센서 수신, FSM 판단, 명령 송신과 실제 바퀴 동작을 나눠 확인했습니다. 아래의 '수정'은 당시 코드 변경이 확인된다는 뜻이며, 각 변경의 실물 성공 여부는 별도로 표시합니다.

| Observation | Diagnosis / response | Evidence boundary |
|---|---|---|
| `PARKING DONE` printed but vehicle did not work | User then reported ECU firmware had not been uploaded; investigate setup separately from FSM | Print and user report survive. A local send result `True` only means the socket send did not raise |
| Rear default 0 could satisfy `<=15` | v3 added explicit nonpositive-data exclusion and sensor-age diagnostics | Code defect and edit recovered; the early log does not itself record a rear reading of 0 |
| Initial skeleton lacked the CENTER_STEER next-state assignment | Completed code assigned REVERSE_TO_WALL | Skeleton and generated code recoverable; no claim that this alone caused all vehicle failures |
| Vehicle kept going straight / did not enter slot | v3 logged state, four sensor distances, age and detection timers; v4 changed alignment maneuver | v3 trace enters REVERSE_TO_WALL and times out; v4 trace stays in PASS_EDGE until timeout |
| Rear values reached 16–18 cm, still not DONE in v3 | Old arrival threshold was <=15 cm; v4 introduced 20 cm tuning | Values are log samples, not a measured final parking error |
| PASS_EDGE waited for clearance that never persisted | User specified a five-step maneuver; v5 removed edge-wait states and used timed movement after detection | User specification and code rewrite recovered |
| Physical left/right appeared reversed | v6 changed LEFT_STEER from -12 to +12 and RIGHT_STEER from +12 to -12 | User observation and sign edits; no calibrated steering-angle trace |
| Two wheels turned in opposite directions under reverse | v7 introduced per-zone inversion with all flags initially false | Configuration mechanism recovered |
| Zone 2 reversed, Zone 3 slowly moved forward under v6 | Compare Zone 2 and 3 firmware; v8 set Zone 3 inversion true | Same direction/pin logic supports a polarity/wiring hypothesis; exact physical wiring and post-fix run remain unknown |

The firmware comparison shows different zone numbers/CAN IDs and diagnostic strings but the same drive-direction branch. That narrows the investigation; it does not independently prove which motor leads were swapped. The historical assistant's stronger wiring claim is treated as a hypothesis here.

## What the new tests establish

The regression suite checks the specified five-step order and timing boundaries, continuous detection, strict rear threshold, rejection of 0/missing/stale data, 4000 no-echo behavior, timeout priority, terminal stopping and per-zone direction bytes. It also tests both inverted and uninverted calibration. These are deterministic host checks of newly written code.

## Next physical checks

Before a new parking trial: lift the drive wheels and test each zone's positive/negative/zero command; measure steering center and both signs; verify sensor freshness and no-echo behavior; disconnect the command link and establish the actual ECU stop behavior. Then record a full parking run with firmware/program hashes, video, sensor logs and an independent final-pose measurement. These checks have not been performed in this recovery.
