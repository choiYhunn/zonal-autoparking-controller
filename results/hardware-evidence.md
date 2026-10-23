# Historical hardware evidence

2026-07-08 실물 결과와 현재 PC 모델 결과를 구분합니다. 아래는 당시 사용자 제공 실행 기록의 짧은 발췌입니다. 장비 MAC·주소·접속 정보는 제외했고, 상태·센서 수치와 실패 결과를 유지했습니다. 원본 로그와 대화 전체는 비공개로 보존합니다.

## Earlier diagnostic run, parking_3 lineage

```text
[STATE] --> SCAN_RIGHT | ZONE1=4000cm ZONE2=171cm ZONE3=4000cm ZONE4=4000cm
[STATE] --> PASS_EDGE | ZONE1=56cm ZONE2=51cm ZONE3=38cm ZONE4=71cm
[STATE] --> EMPTY_FOUND_STOP | ZONE1=261cm ZONE2=62cm ZONE3=104cm ZONE4=65cm
[STATE] --> ALIGN_FORWARD | ZONE1=319cm ZONE2=65cm ZONE3=43cm ZONE4=42cm
[STATE] --> STEER_RIGHT | ZONE1=312cm ZONE2=69cm ZONE3=42cm ZONE4=63cm
[STATE] --> REVERSE_RIGHT | ZONE1=237cm ZONE2=70cm ZONE3=35cm ZONE4=53cm
[STATE] --> CENTER_STEER | ZONE1=331cm ZONE2=55cm ZONE3=94cm ZONE4=105cm
[STATE] --> REVERSE_TO_WALL | ZONE1=252cm ZONE2=55cm ZONE3=48cm ZONE4=115cm
[HB] state=REVERSE_TO_WALL elapsed=7.9s cmd=(0, -45) | ZONE4=16cm
[RX] sensor ZONE4 can_id=0x43 dist=18cm
[PARKING] STOPPED: rear wall not detected
```

The original lines contain additional labels and sensor ages; those fields were removed for readability. This is a shortened extract, not a full raw trace. It supports four-zone sensor reception, state progression and timeout. It does not establish completed parking. The then-active threshold was <=15 cm. Logged sample ages are not measured Ethernet or CAN latency.

## Named parking_4 run

```text
[STATE] --> SCAN_RIGHT | ZONE2=184cm ZONE4=0cm[NO-DATA]
[STATE] --> PASS_EDGE | ZONE2=35cm ZONE4=60cm
[HB] state=PASS_EDGE elapsed=6.0s cmd=(0, 55) | ZONE2=59cm ZONE4=75cm
[PARKING] STOPPED: occupied slot edge not found
```

The edge-wait condition prevented later maneuver states in this run. The user then explicitly supplied the five-step sequence implemented in v5.

## Result boundaries

| Claim | What survives |
|---|---|
| HPC process ran | Terminal output, sensor updates and state logs |
| Four zones supplied sensor data | All four zone readings in the diagnostic trace |
| Vehicle behavior observed | User reports about motion, wrong steering and Zone 3 forward motion under reverse |
| Final v8 correction implemented | Replayable Zone 3 inversion edit and syntax check |
| Correction fixed the wheel / final parking succeeded | No post-v8 hardware run, video or final-pose measurement found |
| Emergency stop physically worked / network watchdog | Stop command print exists; physical stop and final ECU link-loss handling not established |
| New public FSM tests | Host-only; [verification record](verification.md) |

An early run printed `PARKING DONE`, but the user reported that the vehicle was not working and later noted missing firmware upload. The early controller also permitted a zero rear default to satisfy its arrival predicate. This output is therefore excluded from successful-parking claims.
