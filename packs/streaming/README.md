# Pack: streaming

Opt in by adding `"streaming"` to `project.json → active_packs`. For OTT / video-player / streaming apps
(often layered with the `mobile` pack). Adds playback, DRM, ads, and QoE specifics to the gates.

## What this pack adds
- Playback QoE (start time, rebuffer ratio, bitrate) becomes tracked KPIs.
- DRM + ad-insertion + analytics-beacon verification becomes part of the testing gate.
- Network-resilience paths become part of the testing gate.

## Setup checklist
- [ ] Player matrix decided (AVPlayer / ExoPlayer / Akta-Lura / web) and logged.
- [ ] DRM/FairPlay/Widevine license acquisition + expiry/renewal tested.
- [ ] Adaptive bitrate switching verified across network conditions.
- [ ] Multi-audio + subtitle/caption rendering verified.
- [ ] Ad insertion (SSAI/CSAI) tested; OMSDK viewability + tracking beacons fire.
- [ ] Analytics (Conviva/Segment) wired; QoE events validated.
- [ ] Live: edge behavior, latency target, recovery from drop, DVR window.
- [ ] Cast handoff (Chromecast/AirPlay) tested.

## KPIs to add
- Video start time, video start failures, rebuffer ratio, average bitrate, exit-before-video-start, ad fill/error rate, concurrent viewers.

## Recommended skills
`engineering:testing-strategy`, `engineering:incident-response`, `operations:runbook`, `engineering:architecture`.
