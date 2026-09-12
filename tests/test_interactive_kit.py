"""Structural and deterministic checks for the copyable interactive kit."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "interactive-kit"
BOOTSTRAP_PATH = KIT / ".opencode/skills/aurora-bootstrap/scripts/bootstrap.py"

module_spec = importlib.util.spec_from_file_location("interactive_bootstrap", BOOTSTRAP_PATH)
bootstrap = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(bootstrap)


class InteractiveKitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="interactive-kit-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def make_template(self) -> Path:
        stage = self.root / "stage"
        (stage / "rpm").mkdir(parents=True)
        (stage / "src").mkdir()
        (stage / "CMakeLists.txt").write_text(
            "pkg_search_module(AURORA auroraapp_i18n REQUIRED)\n"
            "find_package(Qt5 COMPONENTS Core Qml Gui Quick LinguistTools REQUIRED)\n"
            "target_link_libraries(ApplicationTemplate Qt5::Quick)\n",
            encoding="utf-8",
        )
        (stage / "rpm/ru.auroraos.ApplicationTemplate.spec").write_text(
            "Summary:    Application Template\n"
            "BuildRequires:  pkgconfig(Qt5Quick)\n",
            encoding="utf-8",
        )
        (stage / "ru.auroraos.ApplicationTemplate.desktop").write_text(
            "Name=Application Template\n"
            "Name[ru]=Шаблон приложения\n"
            "Permissions=Internet\n",
            encoding="utf-8",
        )
        (stage / "src/main.cpp").write_text(
            'QStringLiteral("ru.auroraos"); // ApplicationTemplate\n',
            encoding="utf-8",
        )
        (stage / ".gitignore").write_text("*.rpm\n", encoding="utf-8")
        return stage

    def test_repository_contains_no_legacy_pipeline(self):
        legacy_paths = (
            ".opencode",
            "docs",
            "experiments",
            "openspec",
            "reports",
            "tools",
            "aurora.local.example.json",
            "opencode.json",
            "versions.json",
        )
        for relative_path in legacy_paths:
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_distribution_has_only_declared_roles_skills_and_command(self):
        agents = {path.stem for path in (KIT / ".opencode/agents").glob("*.md")}
        skills = {path.parent.name for path in (KIT / ".opencode/skills").glob("*/SKILL.md")}
        commands = {path.stem for path in (KIT / ".opencode/commands").glob("*.md")}
        self.assertEqual(
            agents,
            {
                "orchestrator",
                "architect",
                "integration-researcher",
                "aurora-researcher",
                "ui-researcher",
                "implementer",
                "reviewer",
            },
        )
        self.assertEqual(
            skills,
            {
                "aurora-bootstrap",
                "aurora-contract",
                "aurora-build-feedback",
                "aurora-review",
                "aurora-device-observation",
            },
        )
        self.assertEqual(commands, {"aurora-init"})

        config = json.loads((KIT / "opencode.json").read_text(encoding="utf-8"))
        serialized = json.dumps(config).lower()
        self.assertEqual(config["default_agent"], "orchestrator")
        self.assertNotIn("permission", config)
        self.assertNotIn("claude_in_mobile", serialized)
        self.assertNotIn("aurora-harness", serialized)

        local_config = json.loads(
            (KIT / "aurora.local.json").read_text(encoding="utf-8")
        )
        self.assertEqual(local_config["sdk"], "~/AuroraOS/bin/sfdk")
        self.assertEqual(local_config["audb"], "audb")
        self.assertEqual(
            local_config["device"], "Aurora OS Emulator 5.2.1.200"
        )
        self.assertIsNone(local_config["signing_key"])
        self.assertIsNone(local_config["signing_cert"])

        required_local_permissions = {
            '"*": ask',
            "external_directory: ask",
            "doom_loop: ask",
            "read:",
            '"*.env": ask',
            "list: allow",
            "glob: allow",
            "grep: allow",
            "lsp: allow",
            '"duckduckgo_*": allow',
            '"aurora_*": allow',
            "todowrite:",
            "task:",
            "edit:",
            "bash:",
            "question:",
            "skill:",
            '"ls *": allow',
            '"find * -delete*": ask',
            '"python3 --version*": allow',
        }
        for agent_path in (KIT / ".opencode/agents").glob("*.md"):
            frontmatter = agent_path.read_text(encoding="utf-8").split("---", 2)[1]
            for permission in required_local_permissions:
                self.assertIn(permission, frontmatter, f"{agent_path.name}: {permission}")

    def test_base_adaptation_adds_no_network_capability(self):
        stage = self.make_template()
        bootstrap.replace_template_identity(
            stage, "ru.example.demo", "Demo", "Демо"
        )
        bootstrap.extend_gitignore(stage)

        cmake = (stage / "CMakeLists.txt").read_text(encoding="utf-8")
        spec = (stage / "rpm/ru.example.demo.spec").read_text(encoding="utf-8")
        desktop = (stage / "ru.example.demo.desktop").read_text(encoding="utf-8")
        self.assertNotIn("auroraapp_i18n", cmake)
        self.assertNotIn("Qt5::Network", cmake)
        self.assertNotIn("Qt5Network", spec)
        self.assertIn("BuildRequires:  cmake", spec)
        self.assertIn("BuildRequires:  ninja", spec)
        self.assertIn("Permissions=\n", desktop)
        self.assertIn("Name=Demo", desktop)
        self.assertIn("Name[ru]=Демо", desktop)
        self.assertIn("aurora.local.json", (stage / ".gitignore").read_text())

    def test_decision_pipeline_preserves_evidence_and_probe_status(self):
        agents = KIT / ".opencode/agents"
        integration = (agents / "integration-researcher.md").read_text(encoding="utf-8")
        platform = (agents / "aurora-researcher.md").read_text(encoding="utf-8")
        architect = (agents / "architect.md").read_text(encoding="utf-8")
        orchestrator = (agents / "orchestrator.md").read_text(encoding="utf-8")
        reviewer = (agents / "reviewer.md").read_text(encoding="utf-8")
        contract = (KIT / ".opencode/skills/aurora-contract/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("security contract for external protocols", integration)
        self.assertIn("exact composition", integration)
        self.assertIn("proves only the behavior that it actually implements", platform)
        self.assertIn("evidence-composition gate", architect)
        self.assertIn("never label a probe-dependent option as recommended", architect)
        self.assertIn("run a decision gate", orchestrator)
        self.assertIn("reject source laundering", orchestrator)
        self.assertIn("pre-contract decision review", reviewer)
        self.assertIn("never changes a `probe` into a verified fact", contract)

    def test_one_hour_pipeline_prioritizes_primary_outcome_and_critical_tests(self):
        agents = KIT / ".opencode/agents"
        orchestrator = (agents / "orchestrator.md").read_text(encoding="utf-8")
        architect = (agents / "architect.md").read_text(encoding="utf-8")
        implementer = (agents / "implementer.md").read_text(encoding="utf-8")
        reviewer = (agents / "reviewer.md").read_text(encoding="utf-8")
        build = (KIT / ".opencode/skills/aurora-build-feedback/SKILL.md").read_text(
            encoding="utf-8"
        )
        device = (KIT / ".opencode/skills/aurora-device-observation/SKILL.md").read_text(
            encoding="utf-8"
        )
        review_skill = (KIT / ".opencode/skills/aurora-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        contract = (KIT / ".opencode/skills/aurora-contract/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("bootstrap before research", orchestrator)
        self.assertIn("primary observable demo outcome", orchestrator)
        self.assertIn("at most eight atomic facts, 500 words and 4,500 characters", orchestrator)
        self.assertIn("separate model", orchestrator)
        self.assertIn("device names/indices", orchestrator)
        self.assertIn("do not suggest values derived from a third-party service", orchestrator)
        self.assertIn("configuration and technical layers are prerequisites, not batches", architect)
        self.assertIn("retry of the exact failed operation", implementer)
        self.assertIn("behavior-to-evidence matrix", reviewer)
        self.assertIn("late completion", reviewer)
        self.assertIn("behavior-to-evidence matrix", contract)
        self.assertIn("Do not assume `sfdk engine status` exists", build)
        self.assertIn("`apptool`", build)
        self.assertIn("Aurora external signature", build)
        self.assertIn("`rpmsign-external verify`", build)
        self.assertIn("may report payload digests as `BAD`", build)
        self.assertIn("never mutate persistent `sfdk config`", build)
        self.assertIn("helper scripts as executable code", reviewer)
        self.assertIn("separate model/mirror", reviewer)
        self.assertIn("device names containing spaces", reviewer)
        self.assertIn("unintended mixed-language active", review_skill)
        self.assertIn("source `.ts` check does not prove the packaged `.qm`", review_skill)
        self.assertIn("glob/search command that honors", review_skill)
        self.assertIn("round-trip with `lconvert`", build)
        self.assertIn("no-echo", build)
        self.assertIn("stdin-only target transport", review_skill)
        self.assertIn("aurora-device-observation", orchestrator)
        self.assertIn(
            'edit:\n    "*": deny\n    "docs/**": allow',
            orchestrator,
        )
        self.assertIn("delegate even a narrow repair", orchestrator)
        self.assertIn("ApplicationAlreadyLaunching", device)
        self.assertIn("may not mark a manual", device)
        self.assertIn("exact resolved emulator", device)
        self.assertIn("invoke `audb` from `PATH`", device)
        self.assertIn("audb screenshot --output /tmp/<name>.png", device)
        self.assertIn('"command -v audb": allow', orchestrator)
        self.assertIn('"audb screenshot --output /tmp/*": allow', orchestrator)
        self.assertIn('"audb tap *": allow', orchestrator)
        self.assertNotIn('"audb install": allow', orchestrator)

    def test_portable_kit_contains_no_experiment_product(self):
        forbidden = ("yandex", "яндекс", "yadisk", "cloudfiles", "ru.tomsk")
        for path in KIT.rglob("*"):
            if not path.is_file() or "node_modules" in path.parts:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
            for marker in forbidden:
                self.assertNotIn(marker, content, f"{marker!r} leaked into {path}")

    def test_publish_overwrites_template_files_and_preserves_other_files(self):
        stage = self.make_template()
        (stage / "README.md").write_text("template readme", encoding="utf-8")
        destination = self.root / "destination"
        destination.mkdir()
        (destination / "rpm").mkdir()
        (destination / "rpm/keep.txt").write_text("unchanged", encoding="utf-8")
        (destination / "README.md").write_text("kit readme", encoding="utf-8")
        (destination / ".opencode").mkdir()
        (destination / ".opencode/config.json").write_text("{}", encoding="utf-8")

        published = bootstrap.publish_template(stage, destination)

        self.assertEqual((destination / "README.md").read_text(), "template readme")
        self.assertEqual(
            (destination / "rpm/keep.txt").read_text(encoding="utf-8"),
            "unchanged",
        )
        self.assertEqual(
            (destination / ".opencode/config.json").read_text(encoding="utf-8"),
            "{}",
        )
        self.assertIn("README.md", published["overwritten_paths"])
        self.assertIn("CMakeLists.txt", published["created_paths"])

    def test_publish_rolls_back_overwritten_and_created_files(self):
        stage = self.make_template()
        destination = self.root / "destination"
        destination.mkdir()
        (destination / "CMakeLists.txt").write_text("original", encoding="utf-8")
        original_copy = bootstrap.shutil.copy2

        def fail_on_spec(source, target, *args, **kwargs):
            if Path(source).parent.name == "rpm" and Path(source).suffix == ".spec":
                raise OSError("injected copy failure")
            return original_copy(source, target, *args, **kwargs)

        with mock.patch.object(bootstrap.shutil, "copy2", side_effect=fail_on_spec):
            with self.assertRaisesRegex(OSError, "injected copy failure"):
                bootstrap.publish_template(stage, destination)

        self.assertEqual((destination / "CMakeLists.txt").read_text(), "original")
        self.assertFalse((destination / "src/main.cpp").exists())
        self.assertFalse((destination / "ru.auroraos.ApplicationTemplate.desktop").exists())

    def test_publish_rejects_symbolic_link_target_before_writes(self):
        stage = self.make_template()
        destination = self.root / "destination"
        destination.mkdir()
        outside = self.root / "outside"
        outside.write_text("outside", encoding="utf-8")
        (destination / "CMakeLists.txt").symlink_to(outside)

        with self.assertRaisesRegex(ValueError, "symbolic link"):
            bootstrap.publish_template(stage, destination)

        self.assertEqual(outside.read_text(encoding="utf-8"), "outside")
        self.assertEqual(
            sorted(path.name for path in destination.iterdir()),
            ["CMakeLists.txt"],
        )

    def test_git_repository_is_created_once(self):
        destination = self.root / "project"
        destination.mkdir()

        created = bootstrap.ensure_git_repository(destination)
        existing = bootstrap.ensure_git_repository(destination)

        self.assertEqual(created, {"state": "created", "root": str(destination)})
        self.assertEqual(existing, {"state": "existing", "root": str(destination)})
        self.assertTrue((destination / ".git").is_dir())
        branch = bootstrap.git(destination, "symbolic-ref", "--short", "HEAD")
        self.assertEqual(branch.decode().strip(), "main")

    def test_git_repository_in_parent_is_reused(self):
        parent = self.root / "parent"
        parent.mkdir()
        bootstrap.ensure_git_repository(parent)
        destination = parent / "application"
        destination.mkdir()

        result = bootstrap.ensure_git_repository(destination)

        self.assertEqual(result, {"state": "existing", "root": str(parent)})
        self.assertFalse((destination / ".git").exists())

    def test_command_interpolation_characters_are_rejected(self):
        arguments = type(
            "Arguments",
            (),
            {
                "app_id": "ru.example.demo",
                "display_name": "$(touch unexpected)",
                "display_name_ru": "Демо",
            },
        )()
        with self.assertRaisesRegex(ValueError, "shell-sensitive"):
            bootstrap.validate_inputs(arguments)

    def test_pin_is_the_official_cmake_branch(self):
        self.assertEqual(
            bootstrap.REPOSITORY,
            "https://hub.mos.ru/auroraos/demos/ApplicationTemplate.git",
        )
        self.assertEqual(bootstrap.BRANCH, "cmake-version")
        self.assertEqual(
            bootstrap.COMMIT, "42c37ff2c8f8649a33b7f37fff72308521e2a3d1"
        )


if __name__ == "__main__":
    unittest.main()
