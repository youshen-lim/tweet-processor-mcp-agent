"""
Sync the public-release copy (publish/) from the root repository.

Exports the files tracked at root HEAD into publish/, removes files that
are tracked in publish/ but no longer exist at root HEAD, and commits the
result in the publish repository. Secrets, state, and logs can never leak:
the export contains only root-tracked files, and the root .gitignore keeps
those out of tracking.

Curation: paths listed in EXCLUDES (internal work reports under
docs/archive/) are never exported to the public copy.

Usage:
    python scripts/sync_publish.py                 # sync and commit
    python scripts/sync_publish.py --dry-run       # show what would change
    python scripts/sync_publish.py --no-commit     # sync, leave changes staged
    python scripts/sync_publish.py --push          # sync, commit, and push
    python scripts/sync_publish.py -m "message"    # custom commit message
"""

import argparse
import io
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "publish"

# Path prefixes tracked at root that must NOT be exported to the public copy.
EXCLUDES = (
    "docs/archive/",
)


def git(args, cwd, capture=True):
    """Run a git command and return stdout (text). Raises on failure."""
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=capture,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}:\n{stderr}")
    return (result.stdout or "").strip()


def excluded(path):
    return any(path.startswith(prefix) for prefix in EXCLUDES)


def tracked_files(repo):
    return {f for f in git(["ls-files"], repo).splitlines() if f}


def main():
    parser = argparse.ArgumentParser(description="Sync publish/ from root HEAD")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without touching publish/")
    parser.add_argument("--no-commit", action="store_true",
                        help="sync and stage, but do not commit")
    parser.add_argument("--push", action="store_true",
                        help="push the publish repository after committing")
    parser.add_argument("-m", "--message", default=None,
                        help="commit message (default references root HEAD)")
    args = parser.parse_args()

    if not (PUBLISH / ".git").exists():
        sys.exit(f"ERROR: {PUBLISH} is not a git repository")

    # The export reads root HEAD, so uncommitted root changes are not synced.
    if git(["status", "--porcelain"], ROOT):
        print("WARNING: root working tree has uncommitted changes;")
        print("         only committed (HEAD) content is synced.")

    if git(["status", "--porcelain"], PUBLISH):
        sys.exit("ERROR: publish/ has uncommitted changes; commit or discard "
                 "them first so the sync cannot clobber local work.")

    root_head = git(["rev-parse", "--short", "HEAD"], ROOT)
    root_files = {f for f in tracked_files(ROOT) if not excluded(f)}
    stale = sorted(tracked_files(PUBLISH) - root_files)

    if args.dry_run:
        # Compare root HEAD blob hashes against the current publish files.
        changed = []
        for path in sorted(root_files):
            target = PUBLISH / path
            if not target.exists():
                changed.append(f"  add:    {path}")
                continue
            root_hash = git(["rev-parse", f"HEAD:{path}"], ROOT)
            pub_hash = git(["hash-object", "--", str(target)], PUBLISH)
            if root_hash != pub_hash:
                changed.append(f"  update: {path}")
        for path in stale:
            changed.append(f"  delete: {path}")
        if changed:
            print(f"Dry run: {len(changed)} change(s) against root {root_head}:")
            print("\n".join(changed))
        else:
            print(f"Dry run: publish/ is already in sync with root {root_head}")
        return

    # Export root HEAD into publish/, skipping excluded paths.
    archive = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=str(ROOT), capture_output=True,
    )
    if archive.returncode != 0:
        sys.exit(f"ERROR: git archive failed: {archive.stderr.decode(errors='replace')}")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        members = [m for m in tar.getmembers() if not excluded(m.name)]
        tar.extractall(path=str(PUBLISH), members=members, filter="data")

    for path in stale:
        git(["rm", "-q", "--", path], PUBLISH)

    git(["add", "-A"], PUBLISH)
    if not git(["status", "--porcelain"], PUBLISH):
        print(f"publish/ is already in sync with root {root_head}; nothing to commit.")
        return

    print(git(["diff", "--cached", "--stat"], PUBLISH))

    if args.no_commit:
        print("Changes staged in publish/ (per --no-commit, not committed).")
        return

    message = args.message or f"Sync with production workspace (root {root_head})"
    git(["commit", "-q", "-m", message], PUBLISH)
    print(f"Committed in publish/: {git(['log', '--oneline', '-1'], PUBLISH)}")

    if args.push:
        git(["push", "origin", "HEAD"], PUBLISH, capture=False)
        print("Pushed publish/ to origin.")


if __name__ == "__main__":
    main()
