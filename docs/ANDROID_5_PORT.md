# MetroList Android 5.0 / Xperia M4 Aqua E2303 — experiment, not a release

Target: **Android 5.0 / API 21**, **arm64-v8a** (E2303). The supplied MetroList snapshot
normally targets API 24 and uses recent AndroidX and Media3 dependencies.

## What this starter patch does

- Adds the **opt-in** Gradle property `android5Experiment=true` to keep `androidApp`,
  `shared` and the `opusDecoder` JNI minimum APIs in sync at 21.
- **Preserves upstream's API 24 default** when this property is absent.
- Adds a separate, manually-triggered GitHub Actions probe. It attempts a debug APK
  and saves a full Gradle log even if compilation fails.
- Includes a static dependency preflight report.

It does **not** fix the incompatible libraries or deliver a working Android 5 APK.
An APK from a successful initial build would still need real-device tests.

## Run without Android Studio (from your GitHub fork)

1. Put these changed files in your fork (or apply the included Git patch in Codespaces).
2. Open **Actions → Android 5 compatibility experiment → Run workflow**.
3. Open the workflow run's **Artifacts** and download `metro-android5-diagnostics`.
4. Start with `android5-summary.md`, which lists failed tasks, SDK conflicts
   and the most relevant Gradle excerpt. Use `android5-build.log` for full details.
   If an APK eventually builds, it appears as
   `metro-android5-debug-UNVERIFIED`; do not assume it works on Android 5.

The default **Build Android** workflow remains unchanged.

## Compatibility work still required

- Media3 1.12.x: modern Media3 raised its Android minimum to API 23; replace or
  port the playback layer to an API-21-capable library, then retest playback.
- Navigation 3 1.3.x: Navigation 3 targets API 23+. Rework navigation for API 21.
- Current Compose artifacts: AndroidX moved major Compose pieces from API 21 to
  API 23. Find compatible older versions, with coordinated source changes.
- Review **every** remaining AndroidX, Room 3, native/JNI, networking and
  security component for API-level compatibility and runtime behavior.
- Inspect newer Android API calls and provide guarded alternatives. Preserve
  search, playback, background playback and network error handling first.
- Check the merged manifest and test real playback and media controls on E2303.

References:
- https://developer.android.com/jetpack/androidx/releases/media3
- https://developer.android.com/guide/navigation/navigation-3/migration-guide
- https://developer.android.com/jetpack/androidx/versions

## Keep your phone and accounts safe

- This is an **app build** experiment. No bootloader unlocking or root is needed.
- Use only the debug APK from your own trusted fork; don't sideload arbitrary patched builds.
- Android 5.0 has unpatched OS security vulnerabilities; avoid sensitive logins.
- If the app is already installed under the same package ID but another signature,
  do not uninstall until you have backed up its local data (Android may wipe that data).

## Iterating

Run the workflow and fix the *first actual error* rather than overriding minimum
SDK checks or silently ignoring manifest-merge failures. Many changes are expected;
this is a multi-stage port, not a one-line backport.

## Current source snapshot (November 2026)

This checkout **already contains** the Android 5 experiment, the Android SDK
setup action v4, and the following dependency experiments:

- `androidx.browser:browser` 1.9.0 (previously 1.10.0).
- Koin 4.1.1 (previously 4.3.0-Beta1).

These versions were lowered for compatibility investigations; they do **not**
prove a successful compile or playback. Upstream defaults are still affected by
these two version-catalog changes, so test normal builds too.

### Scope of remaining port work

The repository still uses Media3 1.12.0-beta01, Navigation 3 1.3.0-alpha04,
Compose 1.13.0-rc01 and Room 3.0.3. Several contemporary AndroidX components
require API 23+. Legacy versions are **not** necessarily drop-in replacements,
because app code may use their newer APIs. Media3 Inspector, for example, did
not exist in older API-21-era Media3 versions.

Prefer investigating an older architectural baseline / smaller independent
legacy client if the dependency graph remains incompatible. Do **not** present
a successful `assembleDebug` as proof of Android 5 runtime compatibility.

Official AndroidX references:
- https://developer.android.com/jetpack/androidx/releases/media3
- https://developer.android.com/jetpack/androidx/releases/navigation3
- https://developer.android.com/jetpack/androidx/versions
