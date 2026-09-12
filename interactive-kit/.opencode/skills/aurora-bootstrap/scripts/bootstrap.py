#!/usr/bin/env python3
"""Create a base Aurora project from a verified, pinned CMake template."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile


REPOSITORY = "https://hub.mos.ru/auroraos/demos/ApplicationTemplate.git"
BRANCH = "cmake-version"
COMMIT = "42c37ff2c8f8649a33b7f37fff72308521e2a3d1"
ORIGIN_FILE = ".aurora-template-origin.json"


def git(repository: Path, *arguments: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repository), *arguments],
        stderr=subprocess.PIPE,
        timeout=90,
    )


def is_verified(repository: Path) -> bool:
    try:
        resolved = git(repository, "rev-parse", f"{COMMIT}^{{commit}}").decode().strip()
        healthy = subprocess.run(
            ["git", "-C", str(repository), "fsck", "--full"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=90,
            check=False,
        ).returncode == 0
        return resolved == COMMIT and healthy
    except (OSError, subprocess.SubprocessError):
        return False


def acquire(cache_root: Path, offline: bool) -> tuple[Path, str]:
    cached_repository = cache_root / COMMIT
    if offline:
        if not is_verified(cached_repository):
            raise ValueError("offline mode requires a verified cache of the pinned commit")
        return cached_repository, "cache-offline"

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=cache_root, prefix="fetch-") as temporary:
            fetched = Path(temporary)
            git(fetched, "init", "--bare")
            git(fetched, "fetch", "--depth=1", REPOSITORY, BRANCH)
            branch_head = git(fetched, "rev-parse", "FETCH_HEAD").decode().strip()
            if branch_head != COMMIT:
                git(fetched, "fetch", "--depth=1", REPOSITORY, COMMIT)
            if not is_verified(fetched):
                raise ValueError("the upstream did not provide the pinned commit")

            if not cached_repository.exists():
                shutil.copytree(fetched, cached_repository)
            elif not is_verified(cached_repository):
                raise ValueError(
                    "the existing template cache failed verification; remove it explicitly"
                )
        return cached_repository, "remote"
    except (OSError, subprocess.SubprocessError) as error:
        if is_verified(cached_repository):
            return cached_repository, "cache-fallback"
        raise ValueError(
            "remote fetch failed and no verified cache is available"
        ) from error


def file_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def validate_inputs(arguments: argparse.Namespace) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+", arguments.app_id):
        raise ValueError(
            "application id must be lowercase reverse-DNS text, for example ru.example.demo"
        )
    shell_sensitive = "\n\r\x00%\\\"$`"
    for display_name in (arguments.display_name, arguments.display_name_ru):
        if not display_name.strip() or any(
            character in display_name for character in shell_sensitive
        ):
            raise ValueError(
                "display names must be non-empty single-line text without shell-sensitive characters"
            )


def extract_template(repository: Path, destination: Path) -> dict[str, str]:
    archive = git(repository, "archive", "--format=tar", COMMIT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as template_archive:
        members = template_archive.getmembers()
        unsafe = any(
            member.issym()
            or member.islnk()
            or member.name.startswith("/")
            or ".." in Path(member.name).parts
            for member in members
        )
        if unsafe:
            raise ValueError("the template archive contains an unsafe path or link")
        template_archive.extractall(destination, members=members, filter="data")
    return file_hashes(destination)


def replace_template_identity(
    stage: Path, app_id: str, display_name: str, display_name_ru: str
) -> None:
    short_name = app_id.rsplit(".", 1)[-1]
    namespace = app_id.rsplit(".", 1)[0]
    replacements = [
        ("ru.auroraos.ApplicationTemplate", app_id),
        ("Application Template", display_name),
        ("ApplicationTemplate", short_name),
        ("ru.auroraos", namespace),
    ]

    for path in sorted(stage.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass
            else:
                for old, new in replacements:
                    content = content.replace(old, new)
                path.write_text(content, encoding="utf-8")

        new_name = path.name
        for old, new in replacements:
            new_name = new_name.replace(old, new)
        if new_name != path.name:
            path.rename(path.with_name(new_name))

    cmake_path = stage / "CMakeLists.txt"
    cmake = cmake_path.read_text(encoding="utf-8")
    cmake = re.sub(
        r"^pkg_search_module\(AURORA auroraapp_i18n REQUIRED\)\n",
        "",
        cmake,
        flags=re.MULTILINE,
    )
    cmake_path.write_text(cmake, encoding="utf-8")

    spec_path = stage / "rpm" / f"{app_id}.spec"
    spec = spec_path.read_text(encoding="utf-8")
    spec = re.sub(
        r"^Summary:.*$",
        lambda _: f"Summary:    {display_name}",
        spec,
        flags=re.MULTILINE,
    )
    build_marker = "BuildRequires:  pkgconfig(Qt5Quick)\n"
    if build_marker not in spec:
        raise ValueError("the pinned template has an unexpected RPM BuildRequires section")
    spec = spec.replace(
        build_marker,
        build_marker + "BuildRequires:  cmake\nBuildRequires:  ninja\n",
        1,
    )
    spec_path.write_text(spec, encoding="utf-8")

    desktop_path = stage / f"{app_id}.desktop"
    desktop = desktop_path.read_text(encoding="utf-8")
    desktop = re.sub(
        r"^Name=.*$", lambda _: f"Name={display_name}", desktop, flags=re.MULTILINE
    )
    desktop = re.sub(
        r"^Name\[ru\]=.*$",
        lambda _: f"Name[ru]={display_name_ru}",
        desktop,
        flags=re.MULTILINE,
    )
    desktop = re.sub(r"^Permissions=.*$", "Permissions=", desktop, flags=re.MULTILINE)
    desktop_path.write_text(desktop, encoding="utf-8")


def extend_gitignore(stage: Path) -> None:
    gitignore_path = stage / ".gitignore"
    original = gitignore_path.read_text(encoding="utf-8").rstrip()
    additions = """

# Local OpenCode and Aurora SDK state
aurora.local.json
.aurora/
.agent-logs/
.opencode/node_modules/
__pycache__/
*.pyc
build/
"""
    gitignore_path.write_text(original + additions, encoding="utf-8")


def publish_template(stage: Path, destination: Path) -> dict[str, list[str]]:
    destination.mkdir(parents=True, exist_ok=True)
    stage_directories = sorted(
        (path for path in stage.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
    )
    stage_files = sorted(path for path in stage.rglob("*") if path.is_file())

    for source in [*stage_directories, *stage_files]:
        relative = source.relative_to(stage)
        target = destination / relative
        if target.is_symlink():
            raise ValueError(f"template target must not be a symbolic link: {target}")
        if source.is_dir() and target.exists() and not target.is_dir():
            raise ValueError(f"template directory conflicts with a file: {target}")
        if source.is_file() and target.exists() and not target.is_file():
            raise ValueError(f"template file conflicts with a directory: {target}")

    created_directories: list[Path] = []
    created_files: list[Path] = []
    overwritten: list[str] = []
    with tempfile.TemporaryDirectory(prefix="aurora-bootstrap-backup-") as temporary:
        backup_root = Path(temporary)
        backups: list[tuple[Path, Path]] = []
        try:
            for source in stage_directories:
                target = destination / source.relative_to(stage)
                if not target.exists():
                    target.mkdir()
                    created_directories.append(target)

            for source in stage_files:
                relative = source.relative_to(stage)
                target = destination / relative
                if target.exists():
                    backup = backup_root / relative
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, backup)
                    backups.append((backup, target))
                    overwritten.append(str(relative))
                else:
                    created_files.append(target)
                shutil.copy2(source, target)
        except Exception:
            for target in reversed(created_files):
                if target.exists() or target.is_symlink():
                    target.unlink()
            for backup, target in reversed(backups):
                shutil.copy2(backup, target)
            for target in reversed(created_directories):
                try:
                    target.rmdir()
                except OSError:
                    pass
            raise

    return {
        "top_level_paths": sorted(item.name for item in stage.iterdir()),
        "created_paths": sorted(
            str(path.relative_to(destination))
            for path in [*created_directories, *created_files]
        ),
        "overwritten_paths": sorted(overwritten),
    }


def ensure_git_repository(destination: Path) -> dict[str, str]:
    existing = subprocess.run(
        ["git", "-C", str(destination), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=30,
        check=False,
    )
    if existing.returncode == 0:
        return {"state": "existing", "root": existing.stdout.strip()}

    subprocess.run(
        ["git", "-C", str(destination), "init", "--initial-branch=main"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
        check=True,
    )
    return {"state": "created", "root": str(destination)}


def create(arguments: argparse.Namespace) -> None:
    validate_inputs(arguments)
    destination = Path(arguments.destination).absolute()
    if destination.is_symlink():
        raise ValueError("destination must not be a symbolic link")

    repository, retrieval = acquire(Path(arguments.cache).expanduser().absolute(), arguments.offline)
    with tempfile.TemporaryDirectory(prefix="aurora-bootstrap-") as temporary:
        stage = Path(temporary)
        upstream_hashes = extract_template(repository, stage)
        replace_template_identity(
            stage,
            arguments.app_id,
            arguments.display_name,
            arguments.display_name_ru,
        )
        extend_gitignore(stage)

        origin = {
            "schema_version": 1,
            "repository": REPOSITORY,
            "branch": BRANCH,
            "commit": COMMIT,
            "retrieval": retrieval,
            "application_id": arguments.app_id,
            "display_name": arguments.display_name,
            "display_name_ru": arguments.display_name_ru,
            "aurora_sdk_baseline": "5.2.1.200",
            "upstream_sha256": upstream_hashes,
            "generated_sha256": file_hashes(stage),
            "adaptations": [
                "renamed application identifiers and display names",
                "removed the unused auroraapp_i18n CMake lookup",
                "added cmake and ninja RPM build dependencies",
                "kept application-specific Qt modules and desktop permissions absent",
                "added local OpenCode and SDK paths to .gitignore",
            ],
        }
        (stage / ORIGIN_FILE).write_text(
            json.dumps(origin, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        published = publish_template(stage, destination)
        git_repository = ensure_git_repository(destination)

    print(
        json.dumps(
            {
                "created": str(destination),
                "branch": BRANCH,
                "commit": COMMIT,
                "retrieval": retrieval,
                "git_repository": git_repository,
                **published,
            },
            ensure_ascii=False,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--display-name-ru", required=True)
    parser.add_argument("--destination", default=".")
    parser.add_argument(
        "--cache",
        default=str(Path.home() / ".cache/aurora-opencode/templates"),
    )
    parser.add_argument("--offline", action="store_true")
    arguments = parser.parse_args()
    try:
        create(arguments)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
