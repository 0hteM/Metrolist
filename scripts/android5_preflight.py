#!/usr/bin/env python3
"""Static advisory only: no dependency resolution, compilation, or APK verification."""
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TARGET = 21
MODULES = [
    "androidApp/build.gradle.kts",
    "shared/build.gradle.kts",
    "opusDecoder/build.gradle.kts",
]

print("MetroList Android 5.0 compatibility preflight (static analysis only)")
print(f"Requested minimum Android API: {TARGET} (Android 5.0)")
for module in MODULES:
    content = (ROOT / module).read_text(encoding="utf-8")
    if 'providers.gradleProperty("android5Experiment")' not in content:
        raise SystemExit(f"MISSING EXPERIMENT SWITCH: {module}")
    print(f"[configured] {module}: API 21 with -Pandroid5Experiment=true; API 24 otherwise")

versions = tomllib.loads((ROOT / "gradle/libs.versions.toml").read_text(encoding="utf-8"))["versions"]
print("\nPinned dependencies that require investigation/replacement:")
for name, label in [
    ("media3", "Modern Media3: upstream raised minSdk to 23"),
    ("nav3Core", "Navigation 3: guidance requires minSdk 23"),
    ("compose", "Recent Compose AndroidX: default minSdk 23"),
    ("room", "Room 3: compatibility not yet audited"),
    ("activity", "AndroidX Activity: compatibility not yet audited"),
    ("work", "AndroidX WorkManager: compatibility not yet audited"),
]:
    print(f"[review] {name} {versions.get(name, 'unknown')}: {label}")
print("\nWARNING: Passing minSdk=21 to Gradle does not mean this APK can build or run.")
print("Never suppress manifest minSdk errors using tools:overrideLibrary without replacing incompatible APIs.")
