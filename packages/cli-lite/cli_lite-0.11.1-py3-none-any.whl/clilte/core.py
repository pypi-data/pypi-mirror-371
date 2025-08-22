from __future__ import annotations

import functools
import importlib
import inspect
import re
import sys
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import InitVar, dataclass, field
from importlib_metadata import entry_points
from pathlib import Path
from typing import Callable, TypeVar, Union, Optional, Any

from arclet.alconna import (
    Alconna,
    Args,
    Arparma,
    CommandMeta,
    Option,
    command_manager,
    namespace,
)
from arclet.alconna.base import Help, Shortcut, Completion
from arclet.alconna.exceptions import SpecialOptionTriggered
from typing_extensions import TypeAlias

from .formatter import RichConsoleFormatter, ShellTextFormatter

cli_instance: ContextVar[CommandLine] = ContextVar("litecli")

pattern = re.compile(r"(?P<module>[\w.]+)\s*" r"(:\s*(?P<attr>[\w.]+))?\s*$")


Callback: TypeAlias = Union[str, None, Callable[[Optional["Next"]], Optional[str]]]
Next: TypeAlias = Callable[[Optional[Callback]], Optional[str]]
Middleware: TypeAlias = Callable[[Arparma, Next], Optional[str]]
Queue: TypeAlias = list[Callable[[Optional[Next]], Optional[str]]]


def compose(callback: Callback, next_: Optional[Next]):
    if callable(callback):
        return callback(next_)
    return callback


def handle_argv():
    path = Path(sys.argv[0])
    head = path.stem
    if head == "__main__":
        head = path.parent.stem
    return head


@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str = field(default="Unknown")
    tags: list[str] = field(default_factory=list)
    author: list[str] = field(default_factory=list)
    priority: int = field(default=16)


class BasePlugin(metaclass=ABCMeta):
    def __init__(self):
        self.metadata: PluginMetadata = self.meta()
        command = self.init()
        if isinstance(command, Alconna):
            self.name: str = command.name
            self.command: Alconna = command
            if (
                not self.command.meta.description
                or self.command.meta.description == "Unknown"
            ):
                self.command.meta.description = self.metadata.description or self.metadata.name or "Unknown"
            if (
                not self.command.help_text
                or self.command.help_text == "Unknown"
            ):
                self.command.help_text = self.command.meta.description

            command_manager.delete(self.command)
            ns = cli_instance.get()._command.namespace_config
            self.command.namespace = ns.name
            self.command.path = f"{ns.name}::{self.command.name}"
            self.command.prefixes = []
            self.command.options = [opt for opt in self.command.options if not isinstance(opt, (Help, Shortcut, Completion))]

            self.command.meta.fuzzy_match = ns.fuzzy_match or self.command.meta.fuzzy_match
            self.command.meta.raise_exception = ns.raise_exception or self.command.meta.raise_exception
            self.command._hash = self.command._calc_hash()
            command_manager.register(self.command)
        else:
            self.name: str = command[0].name
            self.option: Option = command[0]
            self.show_in_subcommand: bool = command[1]

    @property
    def local(self):
        """以插件所在的模块名作为子命令的名称"""
        module = self.__module__.split(".")[-1]
        if module == "__main__":
            return handle_argv()
        return module

    @abstractmethod
    def init(self) -> Alconna | tuple[Option, bool]:
        """
        插件创建方法, 该方法只会调用一次

        若返回 Alconna, 则表示创建一个新的子命令, 该子命令的名称为插件的名称

        若返回 tuple[Option, bool], 则表示该插件向全局命令行添加一个选项, 其中 bool 值表示是否在子命令中显示该选项
        """

    @abstractmethod
    def meta(self) -> PluginMetadata:
        """
        提供描述信息的方法
        """

    @abstractmethod
    def dispatch(self, result: Arparma, next_: Next) -> str | None:
        """
        插件的处理方法, 该方法会在命令行解析完成后调用

        Args:
            result (Arparma): 解析结果
            next_ (Next): 下一个插件的回调函数
        Returns:
            str | None: 返回值为 str 时将打印该字符串
        """


_storage: dict[str, list[type[BasePlugin]]] = {}
TPlugin = TypeVar("TPlugin", bound=BasePlugin)


def register(target: str):
    def wrapper(cls: type[BasePlugin]):
        _storage.setdefault(target, []).append(cls)
        return cls

    return wrapper


@dataclass(repr=True)
class CommandLine:
    title: str
    version: str
    _name: InitVar[str | None] = field(default=None)
    load_preset: bool = field(default=True)
    rich: bool = field(default=False)
    fuzzy_match: InitVar[bool] = field(default=False)
    plugins: dict[type[BasePlugin], BasePlugin] = field(default_factory=dict, init=False)
    _command: Alconna = field(init=False)
    callback: Callable[[Arparma], None] = field(
        default_factory=lambda: (lambda x: None), init=False
    )
    formatter_type: type[ShellTextFormatter | RichConsoleFormatter] = field(init=False)

    def __post_init__(self, _name: str | None, fuzzy_match: bool):
        self.formatter_type = RichConsoleFormatter if self.rich else ShellTextFormatter
        if _name is None:
            self._command = Alconna(
                formatter_type=self.formatter_type ,
                meta=CommandMeta(fuzzy_match=fuzzy_match, description=self.title),
            )
        else:
            self._command = Alconna(
                _name,
                formatter_type=self.formatter_type ,
                meta=CommandMeta(fuzzy_match=fuzzy_match, description=self.title),
            )
        self.formatter_type.global_options.append(self._command.options[0])  # type: ignore
        self.formatter_type.main_name = self._command.header_display
        with namespace(self.name) as np:
            np.headers = []
            np.separators = (" ",)
            np.fuzzy_match = fuzzy_match
            np.formatter_type = self.formatter_type

    @property
    def name(self):
        return self._command.command

    @classmethod
    def current(cls):
        return cli_instance.get()

    @contextmanager
    def using(self):
        token = cli_instance.set(self)
        yield
        cli_instance.reset(token)

    def arguments(self, args: Args):
        command_manager.delete(self._command)
        self._command.args.__merge__(args)
        command_manager.register(self._command)

    def set_callback(self, callback: Callable[[Arparma], None]):
        self.callback = callback

    def add(self, *command: type[TPlugin]):
        for cls in command:
            if cls in self.plugins:
                continue
            self.plugins[cls] = cls  # type: ignore

    def load_all(self):
        with self.using():
            plgs: list[BasePlugin] = [cls() for cls in self.plugins]
            for plg in plgs:
                self.plugins[plg.__class__] = plg
                if hasattr(plg, "command") and isinstance(plg.command, Alconna):
                    self._command.add(plg.command)
                elif hasattr(plg, "option") and isinstance(plg.option, Option):
                    with command_manager.update(self._command):
                        self._command.options.insert(0, plg.option)
                    if getattr(plg, "show_in_subcommand", False):
                        self.formatter_type.global_options.insert(0, plg.option)

    def preset(self):
        for cls in _storage.get(self._command.command, []) + _storage.get("*", []):
            self.add(cls)

    def load_register(self, target: str):
        if target in (self._command.command, "*"):
            return
        for cls in _storage.get(target, []):
            self.add(cls)

    def load_entry(self):
        for entry in entry_points().select(group=f"litecli.{self.name}.plugins"):
            self.add(entry.load())

    def load_plugin(self, name: str | Path):
        if isinstance(name, Path):
            module = importlib.import_module(".".join(name.parts[:-1] + (name.stem,)))
            for _, plug in inspect.getmembers(
                module, lambda x: isinstance(x, type) and issubclass(x, BasePlugin)
            ):
                if plug is BasePlugin:
                    continue
                self.add(plug)  # type: ignore
            return
        match = pattern.match(name)
        if not match:
            raise ModuleNotFoundError(name)
        module = importlib.import_module(match.group("module"))
        if not match.group("attr"):
            for _, plug in inspect.getmembers(
                module, lambda x: isinstance(x, type) and issubclass(x, BasePlugin)
            ):
                if plug is BasePlugin:
                    continue
                self.add(plug)  # type: ignore
            return
        attrs = filter(None, (match.group("attr") or "").split("."))
        plug = functools.reduce(getattr, attrs, module)
        if not issubclass(plug, BasePlugin):  # type: ignore
            raise TypeError(f"target {plug} is not a plugin")
        self.add(plug)

    def load_plugins(self, dirname: str | Path):
        dir_path = Path(dirname)
        if not dir_path.exists():
            raise FileNotFoundError(f"directory {dirname} not exists")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"target {dirname} is not a directory")
        for path in dir_path.iterdir():
            if path.name.startswith("_"):
                continue
            if path.suffix == ".py":
                self.load_plugin(path)
            elif path.is_dir():
                self.load_plugins(path)

    def get_plugin(self, plg: type[TPlugin]) -> TPlugin | None:
        return next(
            (x for x in self.plugins.values() if isinstance(x, plg)),
            None,
        )

    def query(self, *tag: str):
        yield from filter(
            lambda x: set(x.metadata.tags).issuperset(tag), self.plugins.values()
        )

    @property
    def help(self):
        return self._command.get_help()

    def _handle_dispatch(self, res: Arparma):
        queue: Queue = [
            functools.partial(plg.dispatch, res)  # type: ignore
            for plg in sorted(self.plugins.values(), key=lambda x: x.metadata.priority)
        ]
        index = 0

        def _next(callback: Optional[Callback] = None) -> Optional[str]:
            nonlocal index
            try:
                if callback is not None:
                    queue.append(lambda next_: compose(callback, next_))
                index += 1
                if index > len(queue):
                    return None
                return queue[index - 1](_next)
            except Exception as e:
                print(repr(e))

        return _next()

    def main(self, *args: str):
        if self.load_preset:
            self.preset()
        self.load_entry()
        self.load_all()
        if args:
            res = self._command.parse(list(args))  # type: ignore
        else:
            head = handle_argv()
            argv = [(f"\"{arg}\"" if any(arg.count(sep) for sep in self._command.separators) else arg) for arg in sys.argv[1:]]
            if head != self._command.command:
                res = self._command.parse(argv)  # type: ignore
            else:
                res = self._command.parse([head, *argv])  # type: ignore
        if not res.matched:
            if isinstance(res.error_info, SpecialOptionTriggered):
                return
            return print(res.error_info)
        if res.non_component and not res.all_matched_args:
            return print(self.help)
        with self.using():
            if ans := self._handle_dispatch(res):
                print(ans)
            else:
                self.callback(res)


__all__ = ["PluginMetadata", "BasePlugin", "CommandLine", "register"]
