"""Official SDK tests, including a real local stdio subprocess and synthetic execution."""

import asyncio
import json
import os
from pathlib import Path
import sys
import threading
import time

import pytest

pytest.importorskip("mcp", reason="Install the mcp optional extra for protocol checks")
from mcp import Client
from mcp.client.stdio import StdioServerParameters

from runtime.mcp_server import create_server
from runtime.services.mcp_gateway import MCPGateway, MCPPolicy
from runtime.services.tool_process import child_environment, execute
from runtime.services.tool_execution_paths import ExecutionPaths


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def local_roots(tmp_path, monkeypatch):
    roots = {}
    for name, child in (("AIRMOSAIC_ASSETS_DIR", "workspace"),
                        ("AIRMOSAIC_CONFIG_DIR", "config"), ("AIRMOSAIC_AUTH_DIR", "auth")):
        path = tmp_path / child
        path.mkdir()
        monkeypatch.setenv(name, str(path))
        roots[name] = path
    monkeypatch.delenv("GCAM_RELEASE_DIR", raising=False)
    return roots


def test_official_client_metadata_and_public_resources(local_roots):
    async def check():
        async with Client(create_server(), read_timeout_seconds=10) as client:
            tools = await client.list_tools()
            gateway = MCPGateway()
            assert {t.name for t in tools.tools} == set(gateway.entries)
            resources = await client.list_resources()
            assert {r.uri for r in resources.resources} == {r["uri"] for r in gateway.resources()}
            result = await client.call_tool("airmosaic_list_datasets")
            assert not result.is_error and len(result.structured_content["result"]) == 9
            result = await client.call_tool("synthetic-private-marker", {})
            assert result.is_error and result.structured_content == {"error": "tool_not_exposed"}
            result = await client.call_tool("worldpop_download", {"parameters": {"project": "wpgp"}, "allow_network": True, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
            assert result.is_error and "synthetic-private-marker" not in result.model_dump_json()
            resource = await client.read_resource("airmosaic://catalog/skills")
            skills = json.loads(resource.contents[0].text)
            assert {s["name"] for s in skills} == {s["name"] for s in gateway.skills}
            resource = await client.read_resource("airmosaic://catalog/capabilities")
            capabilities = json.loads(resource.contents[0].text)
            assert capabilities["validation_scope"] == "metadata_consistency_only"
            assert capabilities["scientific_acceptance"] == "not_assessed"
            assert {s["name"] for s in capabilities["skills"]} == {s["name"] for s in skills}
            methods = await client.read_resource("airmosaic://catalog/methods")
            methods = json.loads(methods.contents[0].text)
            assert methods == capabilities["methods"]
            method_doc = await client.read_resource(methods[0]["resources"]["en"])
            assert "#" in method_doc.contents[0].text
            resource = await client.read_resource(skills[0]["resources"]["en"])
            assert "#" in resource.contents[0].text
        assert not list(local_roots["AIRMOSAIC_ASSETS_DIR"].iterdir())
    asyncio.run(check())


def test_official_stdio_subprocess_from_external_directory(tmp_path, local_roots):
    env = {k: os.environ[k] for k in ("SystemRoot", "WINDIR", "PATH") if k in os.environ}
    env.update({k: str(v) for k, v in local_roots.items()})
    async def check():
        params = StdioServerParameters(command=sys.executable,
            args=["-I", "-B", "-X", "utf8", "-m", "runtime.mcp_server"],
            cwd=tmp_path, env=env)
        async with Client(params, read_timeout_seconds=15) as client:
            tools = await client.list_tools()
            assert {t.name for t in tools.tools} == set(MCPGateway().entries)
            result = await client.call_tool("airmosaic_list_tools", {"category": "model"})
            assert not result.is_error and result.structured_content["result"]
            result = await client.call_tool("worldpop_download", {"parameters": {"project": "wpgp"}, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
            assert not result.is_error and result.structured_content["mode"] == "preview"
            assert "network_permission_required" in result.structured_content["result"]["blockers"]
    asyncio.run(check())


def test_authorized_mcp_executes_existing_aggregation_on_synthetic_rows(local_roots):
    pd = pytest.importorskip("pandas")
    source = local_roots["AIRMOSAIC_ASSETS_DIR"] / "data" / "rows.csv"
    source.parent.mkdir()
    pd.DataFrame([
        {"scenario": "synthetic", "source": "marketplace", "sector": "cement", "year": 2020,
         "region": region, "price": price, "quantity": quantity}
        for region, price, quantity in [("AH", 10, 2), ("BJ", 20, 1), ("China", 900, 100)]
    ]).to_csv(source, index=False)
    gateway = MCPGateway(policy=MCPPolicy(execution_tools=frozenset({"gcam_aggregate_provinces"})))
    async def check():
        async with Client(create_server(gateway)) as client:
            result = await client.call_tool("gcam_aggregate_provinces", {
                "parameters": {"input_csv": str(source)}, "dry_run": False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
            assert not result.is_error
            receipt = result.structured_content["result"]
            assert receipt["status"] == "succeeded" and receipt["scientific_validation"] == "not_run"
            assert str(source) not in result.model_dump_json()
            output = local_roots["AIRMOSAIC_ASSETS_DIR"] / "results" / "example_project" / receipt["run_id"] / "01_socioeconomic_natural_change" / "gcam_aggregate_provinces"
            row = pd.read_csv(output / "province_aggregate.csv").iloc[0]
            assert row["weighted_price"] == pytest.approx(40 / 3)
            assert row["quantity_sum"] == 3
    asyncio.run(check())


def test_protocol_cancellation_signals_worker(local_roots, monkeypatch):
    gateway = MCPGateway(policy=MCPPolicy(execution_tools=frozenset({"airmosaic_draft_causal_plan"})))
    started, cancelled = threading.Event(), threading.Event()
    def run(*args, cancel_event, **kwargs):
        started.set()
        if cancel_event.wait(5):
            cancelled.set()
        return {"status": "failed", "reason": "cancelled"}
    monkeypatch.setattr(gateway.runner, "run", run)
    async def check():
        async with Client(create_server(gateway)) as client:
            task = asyncio.create_task(client.call_tool("airmosaic_draft_causal_plan", {
                "parameters": {"question": "synthetic", "treatment": "x", "outcome": "y"}, "dry_run": False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}))
            assert await asyncio.to_thread(started.wait, 3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert await asyncio.to_thread(cancelled.wait, 5)
    asyncio.run(check())


def test_runner_cancellation_terminates_owned_process(local_roots):
    paths = ExecutionPaths(ROOT, "c" * 32, "airmosaic_list_datasets", project_id="example_project", stage="01_socioeconomic_natural_change")
    paths.create()
    event = threading.Event()
    timer = threading.Timer(0.2, event.set)
    timer.start()
    try:
        result = execute([sys.executable, "-I", "-c", "import time;time.sleep(30)"], paths.temp,
                         child_environment(paths, None), 30, capture=False, cancel_event=event)
    finally:
        timer.cancel()
    assert result[1] == "cancelled" and result[2] is True


def test_pre_cancelled_process_is_never_started(local_roots, monkeypatch):
    import subprocess
    event = threading.Event()
    event.set()
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: pytest.fail("cancelled process spawned"))
    assert execute([], Path.cwd(), {}, 30, False, cancel_event=event) == (None, "cancelled", True, b"")


def test_malformed_wire_requests_do_not_echo_values(tmp_path):
    async def check():
        env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "PATH") if key in os.environ}
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "-B", "-X", "utf8", "-m", "runtime.mcp_server",
            cwd=tmp_path, env=env, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        responses = []
        async def request(message):
            process.stdin.write((json.dumps(message)+'\n').encode())
            await process.stdin.drain()
            if 'id' in message:
                line = await asyncio.wait_for(process.stdout.readline(), 10)
                assert line
                responses.append(line)
                return json.loads(line)
        try:
            response = await request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "synthetic-test", "version": "1"}}})
            assert 'result' in response
            await request({"jsonrpc": "2.0", "method": "notifications/initialized"})
            for index, params in enumerate([
                {"name": "synthetic-private-marker", "arguments": {}},
                {"name": "airmosaic_list_tools", "arguments": {"category": "synthetic-private-marker"}},
                {"name": "airmosaic_list_tools", "arguments": ["synthetic-private-marker"]},
            ], 2):
                response = await request({"jsonrpc": "2.0", "id": index, "method": "tools/call", "params": params})
                assert 'error' in response or response['result']['isError']
            response = await request({"jsonrpc": "2.0", "id": 5, "method": "resources/read",
                                      "params": {"uri": "file:///synthetic-private-marker"}})
            assert 'error' in response
            response = await request({"jsonrpc": "2.0", "id": 6,
                                      "method": "synthetic-private-marker", "params": {}})
            assert response['error']['code'] == -32601
            assert response['error'].get('data') is None
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), 10)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
        stderr = await process.stderr.read()
        assert b'synthetic-private-marker' not in b''.join(responses) + stderr
    asyncio.run(check())


def _synthetic_process_gateway(tmp_path):
    """A catalog-bound fixture starts a parent and descendant, without network."""
    import shutil
    import yaml
    from runtime.services.tool_registry import ToolRegistryService
    repo = tmp_path / 'synthetic-repository'
    for directory in ['catalog/tools', 'catalog/schemas', 'methods']:
        (repo / directory).mkdir(parents=True)
    (repo / 'methods/index.yaml').write_text('schema_version: 2\nmethods: []\n', encoding='utf-8')
    (repo / 'catalog/skills.yaml').write_text(
        'schema_version: 1\npurpose: Synthetic process fixture\nskills: []\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'catalog/schemas/tool.schema.json', repo / 'catalog/schemas/tool.schema.json')
    manifest = yaml.safe_load((ROOT / 'catalog/tools/worldpop_download.yaml').read_text(encoding='utf-8'))
    manifest['requirements']['python_packages'] = []
    guide = repo / manifest['documentation']
    guide.parent.mkdir(parents=True)
    guide.write_text('Synthetic fixture', encoding='utf-8')
    source = repo / manifest['entrypoint']['path']
    source.parent.mkdir(parents=True)
    source.write_text('''import argparse, json, os, subprocess, sys, time
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--project')
p.add_argument('--root')
a = p.parse_args()
root = Path(a.root)
child_code = "from pathlib import Path; import sys,time; p=Path(sys.argv[1])" + chr(10) + "while True:" + chr(10) + " p.write_text(str(time.time_ns()))" + chr(10) + " time.sleep(0.02)"
child = subprocess.Popen([sys.executable, '-I', '-c', child_code, str(root/'heartbeat')])
(root/'process.json').write_text(json.dumps({'parent': os.getpid(), 'child': child.pid}))
while True:
 time.sleep(0.1)
''', encoding='utf-8')
    (repo / 'catalog/tools/worldpop_download.yaml').write_text(yaml.safe_dump(manifest), encoding='utf-8')
    tool = frozenset({'worldpop_download'})
    return MCPGateway(ToolRegistryService(repo), MCPPolicy(tool, tool))


@pytest.mark.parametrize('finish', ['cancel', 'disconnect'])
def test_mcp_cancellation_finalizes_real_runner_and_descendant(tmp_path, local_roots, finish):
    gateway = _synthetic_process_gateway(tmp_path)
    workspace = local_roots['AIRMOSAIC_ASSETS_DIR']
    async def check():
        task = None
        handles = []
        try:
            async with Client(create_server(gateway), read_timeout_seconds=15) as client:
                task = asyncio.create_task(client.call_tool('worldpop_download', {
                    'parameters': {'project': 'synthetic'}, 'dry_run': False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"}))
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline:
                    if task.done():
                        pytest.fail(f'Synthetic fixture returned before cancellation: {task.result().structured_content}')
                    probes = list((workspace / 'results/example_project').glob('*/01_socioeconomic_natural_change/worldpop_download/process.json'))
                    if probes and (probes[0].parent / 'heartbeat').exists():
                        break
                    await asyncio.sleep(0.02)
                else:
                    pytest.fail('Synthetic process fixture did not start')
                identities = json.loads(probes[0].read_text())
                if os.name == 'nt':
                    import ctypes
                    from ctypes import wintypes
                    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
                    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
                    kernel.OpenProcess.restype = wintypes.HANDLE
                    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
                    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
                    handles = [kernel.OpenProcess(0x100000, False, identities[key]) for key in ('parent', 'child')]
                    assert all(handles)
                if finish == 'cancel':
                    task.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await task
            # Exiting the client without cancelling its call exercises disconnect.
            if task is not None:
                await asyncio.gather(task, return_exceptions=True)
            records = list((workspace / 'results/example_project').glob('*/records/worldpop_download/record.json'))
            assert len(records) == 1
            receipt = json.loads(records[0].read_text(encoding='utf-8'))
            assert receipt['status'] == 'failed' and receipt['reason'] == 'cancelled'
            assert receipt['process_tree_cleanup_confirmed'] is True and 'finished_at' in receipt
            assert str(workspace) not in json.dumps(receipt)
            if handles:
                assert all(kernel.WaitForSingleObject(handle, 1000) == 0 for handle in handles)
            else:
                heartbeat = probes[0].parent / 'heartbeat'
                previous = heartbeat.read_text()
                await asyncio.sleep(0.15)
                assert heartbeat.read_text() == previous
        finally:
            if task is not None and not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
            for handle in handles:
                kernel.CloseHandle(handle)
    asyncio.run(check())


def test_queued_call_waits_for_cancelled_worker_cleanup(local_roots, monkeypatch):
    gateway = MCPGateway(policy=MCPPolicy(execution_tools=frozenset({'airmosaic_draft_causal_plan'})))
    started, cancellation_seen, release_cleanup, second_started = [threading.Event() for _ in range(4)]
    def run(name, parameters, *, cancel_event, **options):
        if parameters['question'] == 'first':
            started.set()
            assert cancel_event.wait(5)
            cancellation_seen.set()
            assert release_cleanup.wait(5)
            return {'status': 'failed', 'reason': 'cancelled'}
        second_started.set()
        return {'status': 'succeeded'}
    monkeypatch.setattr(gateway.runner, 'run', run)
    async def check():
        async with Client(create_server(gateway), read_timeout_seconds=15) as client:
            def request(question):
                return client.call_tool('airmosaic_draft_causal_plan', {
                    'parameters': {'question': question, 'treatment': 'x', 'outcome': 'y'}, 'dry_run': False, "project_id": "example_project", "stage": "01_socioeconomic_natural_change"})
            first = asyncio.create_task(request('first'))
            assert await asyncio.to_thread(started.wait, 3)
            second = asyncio.create_task(request('second'))
            try:
                first.cancel()
                assert await asyncio.to_thread(cancellation_seen.wait, 3)
                await asyncio.sleep(0.05)
                assert not second_started.is_set()
            finally:
                release_cleanup.set()
            await asyncio.gather(first, return_exceptions=True)
            result = await second
            assert not result.is_error and second_started.is_set()
    asyncio.run(check())
