#!/usr/bin/env python3
"""Summarize the FIRST actionable Android 5 build blocker from a Gradle log.

This script is diagnostic only. It neither modifies APKs nor suppresses Android
manifest checks. The workflow writes the result into its artifact and job summary.
"""
from pathlib import Path
import re
import sys

LOG = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('android5-build.log')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('android5-summary.md')

lines = LOG.read_text(encoding='utf-8', errors='replace').splitlines() if LOG.exists() else []

MANIFEST_RE = re.compile(
    r'uses-sdk:minSdkVersion\s+(\d+)\s+cannot be smaller than version\s+(\d+)'
    r'\s+declared in library\s+\[([^\]]+)\]', re.IGNORECASE
)
SENTINELS = (
    'BUILD FAILED', 'FAILURE: Build failed', 'Execution failed for task',
    'Could not resolve', 'Could not find', 'Manifest merger failed',
    'Unresolved reference', 'No matching variant',
    'Android resource linking failed', 'incompatible version of Kotlin',
)

def code(s: str) -> str:
    return s.replace('`', "'").replace('\r', '')

out = [
    '# MetroList Android 5 / API 21 build diagnostic',
    '',
    '**Target:** Sony Xperia M4 Aqua E2303 (Android 5.0, API 21).',
    '**Caution:** This does not certify any build or APK as Android 5 compatible.',
    '',
]

if not lines:
    out += [
        'No `android5-build.log` was created. Failure likely happened before Gradle.',
        'Inspect the failed GitHub Actions **setup** or **checkout** step.',
    ]
else:
    matches = []
    for index, line in enumerate(lines):
        m = MANIFEST_RE.search(line)
        if m:
            record = (m.group(1), m.group(2), m.group(3))
            if record not in matches:
                matches.append(record)
    if matches:
        out += [
            '## Android minimum-SDK conflicts',
            '',
            '| App API | Library minimum | Incompatible library |',
            '|---|---|---|',
        ]
        for app, libmin, lib in matches:
            out.append(f'| {app} | {libmin} | `{code(lib)}` |')
        out += [
            '',
            'A manifest failure is a real compatibility warning. **Do not** use',
            '`tools:overrideLibrary` or edit an AAR manifest to hide it.',
            'Identify an API-21-capable library **and** check source-API compatibility.',
        ]
    else:
        out += [
            'No minimum-SDK conflict was detected in the log. This does **not**',
            'mean the app is compatible; the build might have failed earlier or later.',
        ]

    failed_tasks = []
    for line in lines:
        match = re.search(r'^> Task (:[\w:.-]+) FAILED\s*$', line.strip())
        if match and match.group(1) not in failed_tasks:
            failed_tasks.append(match.group(1))
    if failed_tasks:
        out += ['', '## Failed Gradle task(s)', '']
        for task in failed_tasks[:15]:
            out.append(f'- `{code(task)}`')

    # Extract a short actionable excerpt around the *first* root error,
    # prefer Gradle's "What went wrong" summary over the final stack trace.
    what = next((i for i, line in enumerate(lines) if line.strip() == '* What went wrong:'), None)
    if what is not None:
        excerpt = lines[what:what + 38]
        for limit, line in enumerate(excerpt):
            if line.strip().startswith('* Try:') or line.strip().startswith('* Exception is:'):
                excerpt = excerpt[:limit]
                break
    else:
        first = next((i for i, line in enumerate(lines) if any(s.lower() in line.lower() for s in SENTINELS)), None)
        excerpt = lines[max(0, first - 2):first + 18] if first is not None else lines[-20:]

    if excerpt:
        out += ['', '## Relevant error excerpt', '', '```text']
        out += [line[:500].replace('```', "~~~") for line in excerpt]
        out.append('```')

    if any('BUILD SUCCESSFUL' in line for line in lines) and not any('BUILD FAILED' in line for line in lines):
        out += ['', '**Gradle reports success.** Test the generated APK on real API 21',
                'hardware before claiming support: install, launch, search, playback,',
                'background audio and error handling.']

out += ['', 'Full details: `android5-build.log` and `android5-preflight.txt` in the artifact.']
result = '\n'.join(out) + '\n'
OUT.write_text(result, encoding='utf-8')
print(result)
