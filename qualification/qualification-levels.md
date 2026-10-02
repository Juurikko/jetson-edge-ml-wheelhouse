# Qualification levels

The project uses explicit evidence levels rather than a generic “works” label.

| Level | Name | Meaning |
|---|---|---|
| Q0 | SOURCE_LOCKED | Exact source revision and relevant patches are frozen. |
| Q1 | BUILD_STATIC_CPU | Build/package/static/native-object checks pass without claiming GPU execution. |
| Q2 | DEVICE_GPU | The exact artifact executes the intended physical GPU operation on the target device. |
| Q3 | STACK_HIL | Multiple components execute together on the physical target, with hardware-in-the-loop evidence where applicable. |
| Q4 | MODEL_APPLICATION | The real model/application path executes correctly on frozen application data. |
| Q5 | PERFORMANCE | Controlled performance/energy measurements exist for the qualified application path. |
| Q6 | OFFLINE_CONTAINER | Reproducible offline/containerized deployment is qualified. |

A higher level does not imply every possible operation in the package has been tested. Each artifact report states the exact scope and limitations.

Cross-device raw-output parity is **deployment fidelity**, not semantic accuracy. Semantic accuracy must be measured separately against suitable reference labels.
