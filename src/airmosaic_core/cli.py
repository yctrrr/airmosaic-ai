from __future__ import annotations

import argparse
import json
from pathlib import Path

from .services.causal_design import CausalDesignService
from .services.data_access import DataAccessService
from .services.data_catalog import DataCatalogService
from .services.tool_registry import CATEGORIES, STATUSES, ToolRegistryError, ToolRegistryService, format_tool_table
from .services.tool_runner import ToolRunnerService
from .services.tool_execution_paths import ToolExecutionError, parse_parameters


class _PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's normal errors echo rejected values, including private paths.
        self.exit(2, json.dumps({"error": "invalid_cli_arguments", "message": "Use --help for accepted arguments."}) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _PrivateArgumentParser(prog="airmosaic")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_datasets = subparsers.add_parser("list-datasets")
    list_datasets.add_argument("--layer")
    list_datasets.add_argument("--skill")
    list_datasets.add_argument("--domain")

    describe = subparsers.add_parser("describe-dataset")
    describe.add_argument("dataset_id")

    search = subparsers.add_parser("search-datasets")
    search.add_argument("query")

    availability = subparsers.add_parser("check-availability")
    availability.add_argument("dataset_id")
    availability.add_argument("--pattern", default="*")

    causal = subparsers.add_parser("draft-causal-plan")
    causal.add_argument("--question", required=True)
    causal.add_argument("--treatment", required=True)
    causal.add_argument("--outcome", required=True)
    causal.add_argument("--unit", default="county-year")

    tools = subparsers.add_parser("list-tools", help="List registered tools and read-only prerequisite checks")
    tools.add_argument("--category", choices=list(CATEGORIES))
    tools.add_argument("--skill")
    tools.add_argument("--status", choices=STATUSES)
    tools.add_argument("--query", help="Match all whitespace-separated terms in tool metadata")
    tools.add_argument("--format", choices=("table", "json"), default="table")
    detail = subparsers.add_parser("describe-tool", help="Show tool metadata and actual entrypoint")
    detail.add_argument("tool_id")
    detail.add_argument("--format", choices=("table", "json"), default="json")
    check = subparsers.add_parser("check-tool", help="Check prerequisites without running or logging in")
    check.add_argument("tool_id")
    run = subparsers.add_parser("run-tool", help="Run a reviewed CLI/Python adapter with task boundaries")
    run.add_argument("tool_id")
    sources = run.add_mutually_exclusive_group()
    sources.add_argument("--params", help="Non-secret JSON object; prefer --params-file for private task text")
    sources.add_argument("--params-file", help="Explicit non-secret JSON under config, data or public examples")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--allow-network", action="store_true")
    run.add_argument("--confirm-browser-session", action="store_true")
    run.add_argument("--timeout", type=int, default=300)
    run.add_argument("--run-id", help="Optional fresh 32-character lowercase hex ID")
    return parser


def main() -> None:
    parser = build_parser()

    args = parser.parse_args()
    if args.command == "run-tool":
        try:
            payload = ToolRunnerService().run(
                args.tool_id, parse_parameters(args.params) if args.params is not None else None,
                params_file=args.params_file, dry_run=args.dry_run, allow_network=args.allow_network,
                confirm_browser_session=args.confirm_browser_session, timeout=args.timeout, run_id=args.run_id,
            )
        except (ToolExecutionError, ToolRegistryError) as error:
            parser.exit(2, json.dumps({"error": "tool_execution_error", "reason": str(error)}) + "\n")
        except (OSError, ValueError, RuntimeError):
            parser.exit(2, json.dumps({"error": "tool_execution_error", "reason": "preflight_failed"}) + "\n")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload["status"] in {"blocked", "failed"}:
            parser.exit(3)
        return
    if args.command in {"list-tools", "describe-tool", "check-tool"}:
        try:
            registry = ToolRegistryService()
            if args.command == "list-tools":
                payload = registry.list_tools(args.category, args.skill, args.status, args.query)
            elif args.command == "describe-tool":
                payload = registry.describe_tool(args.tool_id)
            else:
                payload = registry.check_tool(args.tool_id)
        except ToolRegistryError as error:
            # Do not render parser/YAML exceptions, source text or local paths.
            parser.exit(2, json.dumps({"error": "tool_registry_error", "message": str(error)}) + "\n")
        if getattr(args, "format", "json") == "table":
            print(format_tool_table(payload if isinstance(payload, list) else [payload]))
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    catalog = DataCatalogService()

    if args.command == "list-datasets":
        payload = [
            {
                "dataset_id": item.dataset_id,
                "name": item.name,
                "domain": item.domain,
                "layer": item.layer,
                "skill_id": item.skill_id,
                "skill_path": item.skill_path,
                "access_mode": item.access_mode,
                "description": item.description,
            }
            for item in catalog.list_datasets(
                layer=args.layer,
                skill=args.skill,
                domain=args.domain,
            )
        ]
    elif args.command == "describe-dataset":
        payload = catalog.describe_dataset(args.dataset_id)
    elif args.command == "search-datasets":
        payload = [
            {
                "dataset_id": item.dataset_id,
                "name": item.name,
                "domain": item.domain,
                "layer": item.layer,
                "skill_id": item.skill_id,
            }
            for item in catalog.search_datasets(args.query)
        ]
    elif args.command == "check-availability":
        access = DataAccessService(catalog=catalog)
        result = access.check_local_availability(args.dataset_id, args.pattern)
        payload = {
            "dataset_id": result.dataset_id,
            "cache_root": str(result.cache_root),
            "existing_files": [str(Path(path)) for path in result.existing_files],
            "missing_hint": result.missing_hint,
        }
    elif args.command == "draft-causal-plan":
        payload = CausalDesignService().draft_plan(
            question=args.question,
            treatment=args.treatment,
            outcome=args.outcome,
            unit=args.unit,
        ).to_dict()
    else:
        raise ValueError(f"Unhandled command: {args.command}")

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
