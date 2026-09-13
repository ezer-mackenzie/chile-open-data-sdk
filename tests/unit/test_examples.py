"""Keep the runnable quick start aligned with its documented behavior."""

import runpy
from pathlib import Path

import httpx

from chile_open_data import ChileOpenDataClient


def test_quickstart(monkeypatch, capsys):
    def handler(request):
        assert request.url.path == "/api/3/action/package_search"
        return httpx.Response(
            200, json={"success": True, "result": {"results": [{"title": "Transport"}]}}
        )

    def make_client():
        return ChileOpenDataClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr("chile_open_data.ChileOpenDataClient", make_client)
    runpy.run_path(
        str(Path(__file__).parents[2] / "examples" / "quickstart.py"), run_name="__main__"
    )
    assert capsys.readouterr().out == "Transport\n"
