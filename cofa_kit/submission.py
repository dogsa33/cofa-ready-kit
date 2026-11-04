"""Bounded, read-only workspace inventory, not a platform submission verdict."""
import heapq
import math
import os
from pathlib import Path, PureWindowsPath
import stat
import time

from .core import KitError


def _linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 1024)


def _required_file(root, value):
    if '\x00' in value:
        raise KitError('Required file paths must not contain a null character.')
    path = Path(value.replace('\\', '/'))
    windows = PureWindowsPath(value)
    if not value or path.is_absolute() or windows.drive or windows.root or '..' in path.parts or ':' in value or not path.parts:
        raise KitError('Required files must be workspace-relative paths without .. or a drive.')
    current = root
    result = {'path': path.as_posix()}
    try:
        for part in path.parts:
            current = current / part
            info = current.lstat()
            if _linked(info):
                return {**result, 'status': 'linked'}
        if not stat.S_ISREG(info.st_mode):
            return {**result, 'status': 'not_file'}
        return {**result, 'status': 'present' if info.st_size else 'empty', 'size_bytes': info.st_size}
    except (FileNotFoundError, NotADirectoryError):
        return {**result, 'status': 'missing'}
    except OSError:
        return {**result, 'status': 'unreadable'}


def submission_check(workspace, required=(), *, limit_bytes=10_000_000_000,
                     max_entries=100_000, max_seconds=10):
    """Count all regular-file paths including hidden files; never follow links.

    Sizes are metadata observed during traversal, not an atomic snapshot. Hard links
    are counted per path. The platform's packaging/exclusion rules are unknown.
    """
    if not isinstance(limit_bytes, int) or limit_bytes < 1:
        raise KitError('limit_bytes must be a positive integer.')
    if not isinstance(max_entries, int) or not 1 <= max_entries <= 1_000_000:
        raise KitError('max_entries must be between 1 and 1000000.')
    if not math.isfinite(max_seconds) or not 0 < max_seconds <= 60:
        raise KitError('max_seconds must be greater than 0 and at most 60.')
    root = Path(workspace).expanduser().absolute()
    info = root.lstat()
    if _linked(info) or not stat.S_ISDIR(info.st_mode):
        raise KitError('workspace must be a directory, not a link or reparse point.')
    if len(required) > 100:
        raise KitError('At most 100 required paths can be checked.')
    required_results = [_required_file(root, value) for value in required]
    started = time.monotonic()
    total = files = entries = directories = issue_count = 0
    issues, largest, stack = [], [], []

    def issue(path, reason):
        nonlocal issue_count
        issue_count += 1
        if len(issues) < 20:
            issues.append({'path': path, 'reason': reason})

    try:
        stack.append((root, os.scandir(root)))
        while stack:
            parent, iterator = stack[-1]
            if time.monotonic() - started >= max_seconds:
                issue('.', 'time_limit')
                break
            try:
                entry = next(iterator)
            except StopIteration:
                iterator.close()
                stack.pop()
                continue
            except OSError:
                issue(parent.relative_to(root).as_posix(), 'directory_unreadable')
                iterator.close()
                stack.pop()
                continue
            if entries >= max_entries:
                issue('.', 'entry_limit')
                break
            entries += 1
            relative = Path(entry.path).relative_to(root).as_posix()
            try:
                info = entry.stat(follow_symlinks=False)
                if _linked(info):
                    issue(relative, 'link_or_reparse_point_not_followed')
                elif stat.S_ISDIR(info.st_mode):
                    directories += 1
                    stack.append((Path(entry.path), os.scandir(entry.path)))
                elif stat.S_ISREG(info.st_mode):
                    files += 1
                    total += info.st_size
                    heapq.heappush(largest, (info.st_size, relative))
                    if len(largest) > 10:
                        heapq.heappop(largest)
                else:
                    issue(relative, 'special_file_not_counted')
            except OSError:
                issue(relative, 'unreadable_or_changed')
    except OSError:
        issue('.', 'directory_unreadable')
    finally:
        for _, iterator in stack:
            iterator.close()
    complete = issue_count == 0
    within_limit = False if total > limit_bytes else (True if complete else None)
    return {
        'ok': complete and within_limit is True and all(item['status'] == 'present' for item in required_results),
        'scope': 'Local on-disk inventory only; not platform packaging, editor save status, correctness, or submission completion.',
        'workspace': str(root), 'complete': complete,
        'file_count': files, 'directory_count': directories, 'entries_checked': entries,
        'total_bytes': total, 'limit_bytes': limit_bytes, 'within_limit': within_limit,
        'required_files': required_results,
        'largest_files': [{'path': path, 'size_bytes': size} for size, path in sorted(largest, reverse=True)],
        'issue_count': issue_count, 'issues': issues,
        'notes': [
            'Includes hidden files, .git, dependencies and the kit; no automatic exclusions or deletions.',
            '10 GB defaults to 10000000000 bytes as a conservative preparation threshold, not a platform unit specification.',
            'Sizes can change during or after this scan. Confirm saved files and final size in the exam screen.',
        ],
    }
