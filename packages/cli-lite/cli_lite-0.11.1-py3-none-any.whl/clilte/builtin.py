from __future__ import annotations

import json
import os
from pprint import pformat
from pathlib import Path
from typing import Any
from arclet.alconna import Alconna, Arparma, CommandMeta, Option, Subcommand
from .core import register, BasePlugin, PluginMetadata, CommandLine


@register("*")
class Version(BasePlugin):
    def init(self):
        return Option("--version|-V", help_text="show the version and exit"), False

    def dispatch(self, result: Arparma, next_):
        if result.find("version"):
            return CommandLine.current().version
        return next_(None)

    def meta(self) -> PluginMetadata:
        return PluginMetadata(
            "version", "0.1.0", "version", ["version"], ["RF-Tar-Railt"], 0
        )


@register("builtin.cache")
class Cache(BasePlugin):
    path: Path
    data: dict[str, Any]

    def init(self) -> Alconna:
        self.path = Path(f'.{CommandLine.current().name}.json')
        self.data = {}
        if self.path.exists():
            with self.path.open('r+', encoding='UTF-8') as f_obj:
                self.data.update(json.load(f_obj))
        return Alconna(
            "cache",
            Subcommand("clear", help_text="清理缓存"),
            Subcommand("show", help_text="显示内容"),
            meta=CommandMeta("管理缓存")
        )

    def dispatch(self, result: Arparma, next_):
        if result.find("cache.show"):
            return f"""\
---------------------------------
in "{os.getcwd()}{os.sep}{self.path.name}":
{pformat(self.data)}
"""
        if result.find("cache.clear"):
            self.data.clear()
            if self.path.exists():
                self.path.unlink(True)
                return f"---------------------------------\nremoved {os.getcwd()}{os.sep}{self.path.name}."
            return "cache cleared"
        if result.find("cache"):
            return self.command.get_help()
        return next_(None)

    def meta(self) -> PluginMetadata:
        return PluginMetadata("cache", "0.1.0", "管理缓存", ["cache", "dev"], ["RF-Tar-Railt"])

    def save(self):
        with self.path.open('w+', encoding='UTF-8') as f_obj:
            json.dump(self.data, f_obj, ensure_ascii=False, indent=4)
