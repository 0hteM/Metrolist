#!/usr/bin/env python3
"""First-pass, API 21-oriented Room3 -> Room 2.7.2 source migration for MetroList.

Run from repository root on the android5-dependency-audit branch.
This is an experimental source migration, NOT a verified working APK.
Does not delete database files, alter schema versions, or run Gradle.
"""
from pathlib import Path
import sys
import subprocess

root = Path.cwd()
# Do not edit a default/main branch in a live repository.
if (root / '.git').exists():
    branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True,
                            text=True, check=True).stdout.strip()
    if not branch or branch in ('main', 'master'):
        sys.exit(f'Refusing to edit branch {branch!r}. Switch to a separate Android 5 test branch first.')
required = (
    root / 'gradle/libs.versions.toml',
    root / 'shared/src/commonMain/kotlin/com/metrolist/shared/db/MusicDatabase.kt',
    root / 'shared/src/commonMain/kotlin/com/metrolist/shared/db/DatabaseMigrations.kt',
    root / 'shared/src/commonMain/kotlin/com/metrolist/shared/db/DatabaseTransaction.kt',
)
missing = [str(p.relative_to(root)) for p in required if not p.is_file()]
if missing:
    sys.exit('Not in the MetroList source root; missing: ' + ', '.join(missing))

# Make no changes unless all prerequisite patterns match. This allows safe
# application to the newer android5-dependency-audit branch as well as ZIP.
original = {}
updates = {}

def stage(path: Path, new: str):
    old = path.read_text(encoding='utf-8')
    original[path] = old
    if new != old:
        updates[path] = new

def replace_once(text, old, new, source):
    count = text.count(old)
    if count != 1:
        raise ValueError(f'{source}: expected 1 instance of {old!r}, found {count}')
    return text.replace(old, new, 1)

try:
    catalog = required[0]
    old = catalog.read_text(encoding='utf-8')
    new = replace_once(old, 'room = "3.0.3"', 'room = "2.7.2"', catalog)
    new = replace_once(new, 'module = "androidx.room3:room3-runtime"', 'module = "androidx.room:room-runtime"', catalog)
    new = replace_once(new, 'module = "androidx.room3:room3-compiler"', 'module = "androidx.room:room-compiler"', catalog)
    stage(catalog, new)

    source_paths = list((root / 'shared/src').rglob('*.kt')) + list((root / 'androidApp/src').rglob('*.kt'))
    for path in source_paths:
        old = path.read_text(encoding='utf-8')
        if 'androidx.room3' not in old:
            continue
        new = old.replace('androidx.room3.', 'androidx.room.')
        # Room 3 renamed the older Room 2 converters.
        new = new.replace('ColumnTypeConverters', 'TypeConverters')
        new = new.replace('ColumnTypeConverter', 'TypeConverter')
        if path.name == 'DatabaseMigrations.kt':
            new = new.replace('override suspend fun migrate(connection: SQLiteConnection)',
                              'override fun migrate(connection: SQLiteConnection)')
        if path.name in ('LegacyUserLyricsRecovery.kt', 'LegacyPlaylistCoverRecovery.kt', 'MusicDatabase.desktop.kt'):
            new = new.replace('override suspend fun onOpen(connection: SQLiteConnection)',
                              'override fun onOpen(connection: SQLiteConnection)')
        stage(path, new)

    txn = required[3]
    old = txn.read_text(encoding='utf-8')
    assert 'import androidx.room3.withWriteTransaction' in old, 'Expected original Room3 transaction helper'
    new = old.replace('import androidx.room3.withWriteTransaction',
                      'import androidx.room.immediateTransaction\nimport androidx.room.useWriterConnection')
    new = replace_once(new,
        'suspend fun <R> MusicDatabase.withDatabaseTransaction(block: suspend () -> R): R = withWriteTransaction { block() }',
        'suspend fun <R> MusicDatabase.withDatabaseTransaction(block: suspend () -> R): R =\n    useWriterConnection { transactor ->\n        transactor.immediateTransaction { block() }\n    }', txn)
    stage(txn, new)

    # Sanity checks before any writing happens.
    assert len(updates) >= 60, f'Unexpectedly few files ({len(updates)})'
    assert 'room = "2.7.2"' in updates[catalog]
    assert 'androidx.room3:' not in updates[catalog]
    assert 'androidx.room3.' not in updates[txn]
    for path,new in updates.items():
        if path.suffix == '.kt' and 'androidx.room3.' in new:
            raise ValueError(f'Unconverted Room3 import in {path}')

except Exception as error:
    sys.exit(f'Migration preflight failed; NO files were modified: {error}')

for path, new in sorted(updates.items()):
    path.write_text(new, encoding='utf-8')

print(f'Prepared Room 2.7.2 API 21 migration across {len(updates)} files.')
print('Room 3 -> Room 2 packages and TypeConverters updated; migrations/callbacks/transaction adapted.')
print('Next: git diff --check; then commit on android5-dependency-audit and run Actions.')
print('This is an uncompiled first pass; review compiler output and test databases on disposable installs.')
