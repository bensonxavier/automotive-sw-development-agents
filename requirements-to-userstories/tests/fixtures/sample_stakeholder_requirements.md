# Stakeholder Requirements

## Assumptions & Operating Design Domain (ODD)
- Vehicle: Passenger car, SAE Level 2 ADAS
- Speed range: 60–130 km/h
- Road type: Structured roads with visible lane markings

## SR-LKA-001: Lane Detection
**Category:** Functional
**Description:** The system shall detect the left and right lane boundary markings.
**Rationale:** Core perception capability.
**Source:** Systems Engineer

## SR-LKA-002: Driver Hands-Off Detection
**Category:** Safety
**Description:** The system shall detect hands-off-wheel condition within 15 seconds.
**Rationale:** Keeps the driver in the control loop.
**Source:** Safety Engineer
**ASIL:** C
**Safety Note:** The warning sequence is safety relevant.