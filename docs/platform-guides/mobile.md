# Mobile Platform Guide

## Overview

NetworkZero Monitor supports both Android and iOS platforms with optimized mobile implementations.

## Android

### Requirements

- Android 8.0 (API level 26) or higher
- Android Studio 4.0 or higher
- Android SDK

### Building

```bash
# Using Android Studio
# Open the project
# Build -> Build Bundle(s) / APK(s)

# Using Gradle
./gradlew assembleRelease
```

### Installation

Install via APK or through app store distribution (to be implemented).

### Permissions

The app requires the following permissions:
- Network access
- Background execution (for continuous monitoring)

### Features

- Battery-optimized monitoring
- Mobile-friendly UI
- Background monitoring support
- Network statistics

## iOS

### Requirements

- iOS 13.0 or higher
- Xcode 12.0 or higher
- Apple Developer account (for distribution)

### Building

```bash
# Using Xcode
# Open NetworkzeroMonitor.xcodeproj
# Product -> Build
```

### Installation

Install via TestFlight or App Store distribution (to be implemented).

### Permissions

The app requires:
- Network extensions capability
- Background modes

### Features

- iOS-native UI
- Integration with iOS networking
- Privacy-focused implementation
- Optimized power consumption

## Common Mobile Features

- Real-time network monitoring
- Historical data tracking
- Alert notifications
- Simplified interface for mobile use
- Offline data storage

## Troubleshooting

### Android

**VPN Required**: Network monitoring on Android may require VPN permissions.

**Battery Optimization**: Disable battery optimization for continuous monitoring.

### iOS

**Network Extensions**: Ensure Network Extensions capability is enabled.

**Background Refresh**: Enable background app refresh for continuous monitoring.

## Platform Differences

| Feature | Android | iOS |
|---------|---------|-----|
| Packet Capture | VPN API | Network Extensions |
| Background Monitoring | Foreground Service | Background Modes |
| UI Framework | Android SDK | UIKit/SwiftUI |
