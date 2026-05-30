# Pack: mobile

Opt in by adding `"mobile"` to `project.json → active_packs`. For iOS / tvOS / Android (and React Native).
Layers mobile specifics onto the core testing, security, and deployment gates.

## What this pack adds
- Store-compliance and signing become part of the deployment gate.
- Device/OS matrix testing becomes part of the testing gate.
- App size, cold-start, and crash-free rate become tracked KPIs.

## Architecture defaults
- iOS/tvOS: Swift + SwiftUI (UIKit where needed); tvOS focus engine considered up front.
- Android: Kotlin (+ Compose); min/target SDK decided and logged.
- CI/CD: GitHub Actions + Fastlane + Match for signing; tag-based release workflow.

## Setup checklist
- [ ] Min + target OS decided and logged (decision).
- [ ] Signing automated (Fastlane + Match / Play signing); no secrets in repo or binary.
- [ ] Crash + performance monitoring wired (crash-free rate as a KPI).
- [ ] Analytics SDK integrated (Segment/Amplitude) and events verified on device.
- [ ] Device matrix defined (min OS, latest OS, representative classes; tvOS remote nav).
- [ ] Accessibility (Dynamic Type / VoiceOver / TalkBack) checked.
- [ ] Store metadata, screenshots, privacy nutrition labels prepared.
- [ ] Staged rollout configured.

## KPIs to add
- Crash-free sessions %, cold-start time, app size, store rating, D1/D7 retention.

## Recommended skills
`engineering:testing-strategy`, `engineering:code-review`, `engineering:architecture`, `operations:compliance-tracking`.
