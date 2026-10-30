"""Auditable run evidence for reviewed controllers, not a general agent engine."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .mlr3_workflow import output_path
from .tool_execution_paths import ToolExecutionError, checked_path
from .tool_registry import repository_path


def utc_offset(value: str) -> timezone:
    if not isinstance(value, str) or not re.fullmatch(r"[+-](?:0[0-9]|1[0-4]):[0-5][0-9]", value):
        raise ToolExecutionError("invalid_workflow_utc_offset")
    hours, minutes = int(value[1:3]), int(value[4:6])
    if hours == 14 and minutes:
        raise ToolExecutionError("invalid_workflow_utc_offset")
    return timezone((1 if value[0] == "+" else -1) * timedelta(hours=hours, minutes=minutes))


def timestamp(zone: timezone) -> str:
    return datetime.now(zone).isoformat(timespec="microseconds")


def sha256(path: Path) -> str:
    return hashlib.sha256(checked_path(str(path)).read_bytes()).hexdigest()


def write_new(path: Path, value: dict | str) -> None:
    checked_path(str(path))
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False) + "\n")


class WorkflowEvents:
    """Timestamp actual controller boundaries; never accept arbitrary log text.

    Preflight events are buffered in memory and persisted if execution reserves a
    fresh output. No historical thoughts, nested tool calls or raw IO are invented.
    """
    ACTIONS = {"task_contract", "preflight", "generation_material", "compute", "verify", "delivery"}
    KINDS = {"decision", "action_started", "observation", "stopped"}
    STATUSES = {"planned", "running", "dry_run", "blocked", "succeeded", "failed", "passed", "prepared"}

    def __init__(self, zone: timezone):
        self.zone, self.items, self.output = zone, [], None

    def emit(self, kind: str, action: str, status: str, *, count: int | None = None) -> None:
        if kind not in self.KINDS or action not in self.ACTIONS or status not in self.STATUSES:
            raise ValueError("invalid_workflow_event")
        if count is not None and (type(count) is not int or not 0 <= count <= 1000000):
            raise ValueError("invalid_workflow_event_count")
        value = {"sequence": len(self.items) + 1, "occurred_at": timestamp(self.zone),
                 "record_type": "observed_controller_event", "kind": kind, "action": action, "status": status}
        if action in {"preflight", "compute"}:
            value["tool_id"] = "ml_regression_workflow"
        if count is not None:
            value["count"] = count
        self.items.append(value)
        if self.output is not None:
            with output_path(self.output, "events.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(value, separators=(",", ":")) + "\n")

    def attach(self, output: Path) -> None:
        if self.output is not None:
            raise ValueError("event_sink_already_attached")
        self.output = output
        write_new(output_path(output, "events.jsonl"), "".join(json.dumps(x, separators=(",", ":")) + "\n" for x in self.items))


def dependency_evidence(repo: Path, names: list[str]) -> tuple[dict, str]:
    """Retain a Git base and text changes for selected public dependencies only.

    New/untracked dependencies are represented as additions. The patch recovers
    LF-normalized UTF-8 text; both byte and normalized hashes are explicit. It is
    evidence for manual reconstruction, never automatically applied or executed.
    """
    def git(*args):
        try:
            return subprocess.run(["git", "--no-pager", *args], cwd=repo, capture_output=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError("dependency_evidence_unavailable") from None
    head = git("rev-parse", "--verify", "HEAD")
    commit = head.stdout.decode("ascii", errors="ignore").strip() if head.returncode == 0 else None
    if commit is not None and not re.fullmatch(r"[a-f0-9]{40,64}", commit):
        raise ValueError("dependency_evidence_unavailable")
    hashes, normalized, changed, patches = {}, {}, [], []
    for name in sorted(set(names)):
        # These source roots are public code/contracts; never select assets or configuration roots.
        if not name.startswith(("runtime/", "skills/model/shared/machine_learning_model/", "catalog/", "workflows/ml_regression/workflow.yaml")):
            raise ValueError("invalid_dependency_reference")
        path = repository_path(repo, name)
        for parent in (path, *path.parents):
            if parent == repo or not parent.is_relative_to(repo):
                break
            if (parent / ".git").exists():
                raise ValueError("nested_git_in_dependency_source")
        raw = path.read_bytes()
        if len(raw) > 1024 * 1024:
            raise ValueError("dependency_source_too_large")
        current = raw.decode("utf-8").replace("\r\n", "\n")
        hashes[name] = hashlib.sha256(raw).hexdigest()
        normalized[name] = hashlib.sha256(current.encode("utf-8")).hexdigest()
        base = git("show", commit + ":" + name) if commit else None
        exists = base is not None and base.returncode == 0
        previous = base.stdout.decode("utf-8").replace("\r\n", "\n") if exists else ""
        if not exists or previous != current:
            changed.append(name)
            patches.append("diff --git a/" + name + " b/" + name + "\n")
            if not exists:
                patches.append("new file mode 100644\n")
            for line in difflib.unified_diff(previous.splitlines(keepends=True), current.splitlines(keepends=True),
                    fromfile="a/" + name if exists else "/dev/null", tofile="b/" + name):
                patches.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
    return {"git_base": commit, "source_sha256": hashes, "source_sha256_lf_utf8": normalized,
            "changed_from_base": changed, "reconstruction": "git_base_plus_reviewed_lf_utf8_patch",
            "automatic_patch_application": False}, "".join(patches)


def check_replay_dependencies(repo: Path, declaration: Path, expected_names: list[str]) -> None:
    declaration = checked_path(str(declaration))
    if declaration.stat().st_size > 1024 * 1024:
        raise ValueError("invalid_dependency_declaration")
    evidence = json.loads(declaration.read_text(encoding="utf-8"))
    hashes = evidence.get("source_sha256") if isinstance(evidence, dict) else None
    # Check all keys before opening any referenced file; reject private/path injection.
    if not isinstance(hashes, dict) or set(hashes) != set(expected_names):
        raise ValueError("invalid_dependency_declaration")
    if any(not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value) for value in hashes.values()):
        raise ValueError("invalid_dependency_declaration")
    if any(sha256(repository_path(repo, name)) != value for name, value in hashes.items()):
        raise ValueError("frozen_workflow_dependency_changed")


def generation_material(output: Path, repo: Path, materials: dict[str, Path], dependencies: list[str],
                        task_name: str, generated_at: str) -> dict:
    bundle = output_path(output, "gen_script")
    bundle.mkdir(exist_ok=False)
    hashes = {}
    for name, source in materials.items():
        if name not in {"run.py", "task.json", "prompt.md", "prompt_ZH.md", "request.md", "request_ZH.md"}:
            raise ValueError("invalid_generation_material")
        raw = checked_path(str(source)).read_bytes()
        if len(raw) > 1024 * 1024:
            raise ValueError("generation_material_too_large")
        destination = output_path(bundle, name)
        with destination.open("xb") as stream:
            stream.write(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    evidence, patch = dependency_evidence(repo, dependencies)
    write_new(bundle / "dependencies.json", evidence)
    write_new(bundle / "dependencies.patch", patch)
    metadata = {"schema_version": 1, "task_name": task_name, "recorded_at": generated_at,
        "record_type": "declared_design_basis_before_computation", "execution_mode": "replay_reviewed_agent_authored_example",
        "llm_generation_in_this_run": False, "generation_model": None, "generation_settings": None,
        "historical_generation_trace": "not_captured", "materials_sha256": hashes,
        "decision_basis": ["fixed_synthetic_request", "schema_validated_task", "reviewed_skill_contract"],
        "trace_coverage": "controller_boundaries_and_verification_not_full_agent_or_R_trace"}
    write_new(bundle / "generation.json", metadata)
    write_new(bundle / "generation.md", "# Generation basis\n\n**English** | [中文](generation_ZH.md)\n\n"
        "Record type: declared design basis, recorded before computation. This run replays an agent-authored, reviewed program; it does not issue a new LLM generation call. Historical generation messages and model/settings were not captured.\n\n"
        "The request defines independent synthetic rows, target/features and released splits. The task fixes the seed, candidate budget and explanations. Training fits candidates, validation selects, and the final test evaluates frozen choices. A training-mean baseline, prediction reload and independent metrics check the computation. These are explicit design summaries, not hidden reasoning or a reconstructed historical transcript.\n\n"
        "Read request.md, task.json and prompt.md for exact requirements. run.py is the executed orchestration source. dependencies.json identifies reused public code; dependencies.patch preserves its differences from the Git base, including untracked additions, as LF-normalized text. No data, credentials or full repository tree is copied. Reconstruction is reviewed manually, not applied automatically.\n")
    write_new(bundle / "generation_ZH.md", "# 生成依据\n\n[English](generation.md) | **中文**\n\n"
        "记录类型：计算前保存的显式设计依据。本次重放代理编写并经审查的程序，不发起新的大模型代码生成调用。未捕获历史生成会话及其模型、生成设置。\n\n"
        "具体请求定义独立合成样本、目标/特征和发布划分；任务配置固定种子、候选预算与解释范围。训练集拟合候选、验证集选型，最终测试评估冻结选择；通过训练均值基线、模型重载和独立指标检查计算。这些内容是可核对的设计摘要，不是隐藏推理，也不是补写的历史逐步对话。\n\n"
        "具体要求见 request_ZH.md、task.json 和 prompt_ZH.md；run.py 是执行的编排代码。dependencies.json 标识复用的公共代码，dependencies.patch 以统一换行文本保留相对 Git 基准的改动及未跟踪新增文件。不复制数据、凭据或完整源码树；重建需人工审查，不自动应用补丁。\n")
    return {"materials_sha256": hashes, "dependencies": evidence}


def retrospective(output: Path, status: str, stage: str, zone: timezone, verification: dict | None) -> None:
    if status not in {"succeeded", "failed", "blocked"} or stage not in WorkflowEvents.ACTIONS:
        raise ValueError("invalid_retrospective_state")
    written = timestamp(zone)
    score = verification.get("independent_metrics", {}).get("test", {}) if verification else {}
    numeric = json.dumps(score, sort_keys=True, allow_nan=False)
    write_new(output_path(output, "retrospective.md"), "# Run retrospective\n\n**English** | [中文](retrospective_ZH.md)\n\n"
        f"Record type: retrospective summary. Written at: {written}. Computation/check status: {status}. Last stage: {stage}.\n\n"
        "This summary was written after the observed operations. events.jsonl contains timestamped controller events, with preflight buffered until a fresh run directory was reserved. It is not a full host-agent or internal R transcript. gen_script/generation.md records explicit design basis separately.\n\n"
        f"Independently checked test metrics: `{numeric}`. See verification.json when present, artifacts.json for scientific outputs and the separate runner receipt for process state. The authoritative overall delivery state is workflow.json; computation success alone does not confirm delivery integrity.\n\n"
        "Only a fixed synthetic input was used. Scientific approval and real-data generalization were not evaluated. Preserve any partial outputs; investigate failed checks and use a fresh batch after review. No final-test-driven retuning or automatic data promotion is authorized.\n")
    write_new(output_path(output, "retrospective_ZH.md"), "# 运行后回顾\n\n[English](retrospective.md) | **中文**\n\n"
        f"记录类型：回顾性摘要。撰写时间：{written}。计算/核验状态：{status}。最后阶段：{stage}。\n\n"
        "本摘要在实际操作后整理。events.jsonl 保存带时间的控制器事件；预检事件在内存中记录，取得全新运行目录后写入。该文件不是完整宿主代理会话或 R 内部执行轨迹。gen_script/generation_ZH.md 单独说明显式设计依据。\n\n"
        f"独立核对的测试指标：`{numeric}`。如已生成，可查看 verification.json、科学产物索引 artifacts.json 及独立执行器回执。最终交付状态以 workflow.json 为准；计算成功不等于交付完整性已确认。\n\n"
        "仅使用固定合成输入，未评估真实数据泛化或批准科学结论。保留部分产物，失败后先核查并使用新批次；不根据最终测试结果继续调参，不自动入库。\n")


def seal_run(output: Path, terminal: dict) -> None:
    """Seal intended terminal bytes, then publish terminal status exclusively."""
    terminal_bytes = (json.dumps(terminal, indent=2, allow_nan=False) + "\n").encode("utf-8")
    inventory = {}
    pending = [output]
    while pending:
        folder = pending.pop()
        for item in folder.iterdir():
            relative = item.relative_to(output).as_posix()
            safe = output_path(output, relative)  # Reject links/nested Git before descent or reads.
            if safe.is_dir():
                pending.append(safe)
            elif safe.is_file():
                if relative in {"delivery-sha256.json", "workflow.json"}:
                    raise ValueError("delivery_already_exists")
                inventory[relative] = sha256(safe)
    inventory["workflow.json"] = hashlib.sha256(terminal_bytes).hexdigest()
    write_new(output_path(output, "delivery-sha256.json"), {"file_sha256": inventory})
    with output_path(output, "workflow.json").open("xb") as stream:
        stream.write(terminal_bytes)
