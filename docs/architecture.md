# HPC–ZCU–ECU architecture

HPC에서 주차 순서와 센서 판단을 맡고 ZCU가 Ethernet과 CAN을 연결하며 ECU가 센서·구동기를 다루는 구조입니다. 아래 인터페이스는 보존된 워크숍 소스와 당시 HPC 코드·실행 기록을 대조했습니다. 통신 기반과 ECU 펌웨어는 제공 코드입니다.

| Layer | Responsibility | Ownership / evidence |
|---|---|---|
| HPC | Receive zone sensor data, decide parking state, issue steering/drive commands | My sequence and integration, AI-assisted Python; historical source recovered by replay |
| ZCU ×4 | Raspberry Pi, Python/SocketCAN, raw Ethernet bridge on `eth0` | Workshop baseline, source inspected; not redistributed |
| ECU ×4 | Arduino, FreeRTOS, MCP2515 CAN interface, ultrasonic sensing and actuator output | Workshop baseline; Zone 2/3 drive behavior compared during debugging |
| PC model | Deterministic ticks and sensor snapshots, logical commands and payload encoding | New independent Python implementation; no transport |

Sensor path: ultrasonic → ECU sensor CAN frame → ZCU raw-Ethernet forwarding → HPC sensor store → FSM. Command path: FSM → per-zone command encoding → raw Ethernet → ZCU CAN forwarding → ECU motor pins. A successful HPC socket send does not acknowledge ECU reception or wheel movement.

## Interfaces inspected

| Zone | Physical role | Command | Sensor | Heartbeat | Additional |
|---|---|---:|---:|---:|---|
| 1 | Front / steering | `0x11` | `0x13` | `0x14` | Steering feedback `0x12` |
| 2 | Right / drive | `0x21` | `0x23` | `0x24` | |
| 3 | Left / drive | `0x31` | `0x33` | `0x34` | |
| 4 | Rear / drive | `0x41` | `0x43` | `0x44` | |

CAN bitrate: 500 kbit/s, Classical CAN with up to eight payload bytes. This workshop is not evidence of a CAN-FD implementation. Ethernet uses EtherType `0x88B5`, magic `ZCAN`, version 1 and `!4sBBBBHB8s`: magic, version, message type, source zone, destination zone, CAN identifier, DLC, eight data bytes. These are inspected protocol fields, not a standardized automotive Ethernet stack or TSN implementation.

The baseline ZCU runs keepalive, filtered CAN-to-HPC and HPC-to-CAN threads. The baseline ECU source contains sensor/heartbeat tasks and CAN mutex access. Source task periods describe intended configuration, not measured real-time behavior.

## Public model boundary

`Controller.tick()` consumes caller-supplied monotonic time and two `Sample` values. It returns a logical `Command`; `Calibration.payloads()` converts sign and magnitude for four zones. There is no raw socket, CAN driver, scheduling thread or board package. The demo supplies invented sensor values for a reproducible host example.

The historical v8 correction requests left with +12 and right with -12, and reverses the speed sign for Zone 3. The new model expresses logical left as -12 and applies steering inversion in the adapter. This keeps vehicle intent separate from wiring convention. The ±12 values are command units used as degrees in the workshop code; achieved wheel angle was not independently measured.

Hardware identification: the historical terminal prompt names a D3-G TOPST system. No BSP, driver development or independent board-image verification is claimed. No current connection to that workshop HPC was available for this recovery.
