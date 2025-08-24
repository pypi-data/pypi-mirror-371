from __future__ import annotations

import os
from pathlib import Path

from agentsdk.tools.FileSystemTool import FileSystemTool
from agentsdk.tools.ShellTool import ShellTool


def test_filesystem_tool_read_write(tmp_path: Path) -> None:
    tool = FileSystemTool(root=tmp_path)
    res = tool.run(operation="write", path="a.txt", content="hello")
    assert res == "OK"
    text = tool.run(operation="read", path="a.txt")
    assert text == "hello"


def test_filesystem_tool_list(tmp_path: Path) -> None:
    tool = FileSystemTool(root=tmp_path)
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "a.txt").write_text("1", encoding="utf-8")
    out = tool.run(operation="list", path="x")
    assert "a.txt" in out


def test_shell_tool(tmp_path: Path) -> None:
    tool = ShellTool(root=tmp_path)
    out = tool.run(command="echo hi")
    assert "hi" in out


