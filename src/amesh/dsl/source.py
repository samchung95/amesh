from __future__ import annotations

import copy
import json
from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from dataclasses import dataclass
from io import StringIO
from typing import Any, Literal, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import MarkedYAMLError, StreamMark
from ruamel.yaml.nodes import MappingNode, Node, SequenceNode

from .models import SourcePosition, SourceRange

PathPart = str | int
SourcePath = tuple[PathPart, ...]


class FlowDocumentError(ValueError):
    """Raised when a source document cannot be decoded into an editable mapping."""


class FlowSourceSyntaxError(FlowDocumentError):
    def __init__(self, message: str, source_range: SourceRange) -> None:
        super().__init__(message)
        self.source_range = source_range


@dataclass(frozen=True)
class SourceMap:
    ranges: Mapping[SourcePath, SourceRange]

    def range_for(self, path: Sequence[PathPart]) -> SourceRange | None:
        candidate = tuple(path)
        while True:
            source_range = self.ranges.get(candidate)
            if source_range is not None:
                return source_range
            if not candidate:
                return None
            candidate = candidate[:-1]


@dataclass
class EditableFlowDocument:
    _data: CommentedMap
    source_format: Literal["yaml", "json"]

    @property
    def data(self) -> dict[str, Any]:
        return cast(dict[str, Any], _to_plain(self._data))

    def set_value(self, path: Sequence[PathPart], value: Any) -> None:
        if not path:
            raise FlowDocumentError("an edit path must identify a field")
        container: Any = self._data
        for part in path[:-1]:
            if isinstance(part, str) and isinstance(container, MutableMapping):
                if part not in container:
                    raise FlowDocumentError(f"edit path does not exist: {format_path(path)}")
                container = container[part]
            elif isinstance(part, int) and isinstance(container, MutableSequence):
                try:
                    container = container[part]
                except IndexError as exc:
                    raise FlowDocumentError(
                        f"edit path does not exist: {format_path(path)}"
                    ) from exc
            else:
                raise FlowDocumentError(f"edit path does not exist: {format_path(path)}")

        final = path[-1]
        if isinstance(final, str) and isinstance(container, MutableMapping):
            container[final] = value
            return
        if isinstance(final, int) and isinstance(container, MutableSequence):
            try:
                container[final] = value
            except IndexError as exc:
                raise FlowDocumentError(f"edit path does not exist: {format_path(path)}") from exc
            return
        raise FlowDocumentError(f"edit path does not exist: {format_path(path)}")

    def render(self) -> str:
        if self.source_format == "json":
            return json.dumps(self.data, indent=2, ensure_ascii=False) + "\n"
        stream = StringIO()
        _round_trip_yaml().dump(self._data, stream)
        return stream.getvalue()


@dataclass(frozen=True)
class ParsedFlowSource:
    data: dict[str, Any]
    source_map: SourceMap | None


def parse_editable_flow_document(source: str | bytes) -> EditableFlowDocument:
    text = _decode(source)
    try:
        loaded = _round_trip_yaml().load(text)
    except MarkedYAMLError as exc:
        raise FlowSourceSyntaxError(str(exc), range_from_mark(_error_mark(exc))) from exc
    if not isinstance(loaded, CommentedMap):
        raise FlowDocumentError("flow document must decode to an object")
    source_format: Literal["yaml", "json"] = "json" if text.lstrip().startswith("{") else "yaml"
    return EditableFlowDocument(loaded, source_format)


def parse_flow_source(
    source: str | bytes | dict[str, Any],
    *,
    include_source_map: bool = True,
) -> ParsedFlowSource:
    if isinstance(source, dict):
        return ParsedFlowSource(copy.deepcopy(source), None)
    text = _decode(source)
    editable = parse_editable_flow_document(text)
    return ParsedFlowSource(
        editable.data,
        parse_flow_source_map(text) if include_source_map else None,
    )


def parse_flow_source_map(source: str | bytes) -> SourceMap:
    """Build source ranges for an already-parsed textual flow document."""
    text = _decode(source)
    try:
        node = _base_yaml().compose(text)
    except MarkedYAMLError as exc:
        raise FlowSourceSyntaxError(str(exc), range_from_mark(_error_mark(exc))) from exc
    return SourceMap(_node_ranges(node))


def format_path(path: Sequence[PathPart]) -> str:
    if not path:
        return "$"
    return ".".join(str(part) for part in path)


def range_from_mark(mark: StreamMark) -> SourceRange:
    start = SourcePosition(line=mark.line + 1, column=mark.column + 1, offset=mark.index)
    end = SourcePosition(line=mark.line + 1, column=mark.column + 2, offset=mark.index + 1)
    return SourceRange(start=start, end=end)


def _decode(source: str | bytes) -> str:
    if isinstance(source, str):
        return source
    try:
        return source.decode("utf-8")
    except UnicodeDecodeError as exc:
        mark = SourceRange(
            start=SourcePosition(line=1, column=1, offset=exc.start),
            end=SourcePosition(line=1, column=2, offset=exc.end),
        )
        raise FlowSourceSyntaxError("flow document must be UTF-8", mark) from exc


def _round_trip_yaml() -> YAML:
    parser = YAML(typ="rt", pure=True)
    parser.allow_duplicate_keys = False
    parser.preserve_quotes = True
    parser.indent(mapping=2, sequence=4, offset=2)
    return parser


def _base_yaml() -> YAML:
    parser = YAML(typ="base", pure=True)
    parser.allow_duplicate_keys = False
    return parser


def _error_mark(error: MarkedYAMLError) -> StreamMark:
    mark = error.problem_mark or error.context_mark
    if mark is None:
        return StreamMark("<flow>", 0, 0, 0)
    return cast(StreamMark, mark)


def _node_ranges(node: Node | None) -> dict[SourcePath, SourceRange]:
    ranges: dict[SourcePath, SourceRange] = {}
    if node is not None:
        _collect_node_ranges(node, (), ranges)
    return ranges


def _collect_node_ranges(
    node: Node,
    path: SourcePath,
    ranges: dict[SourcePath, SourceRange],
) -> None:
    ranges[path] = SourceRange(
        start=SourcePosition(
            line=node.start_mark.line + 1,
            column=node.start_mark.column + 1,
            offset=node.start_mark.index,
        ),
        end=SourcePosition(
            line=node.end_mark.line + 1,
            column=node.end_mark.column + 1,
            offset=node.end_mark.index,
        ),
    )
    if isinstance(node, MappingNode):
        for key_node, value_node in node.value:
            key = str(key_node.value)
            child_path = (*path, key)
            _collect_node_ranges(value_node, child_path, ranges)
    elif isinstance(node, SequenceNode):
        for index, value_node in enumerate(node.value):
            _collect_node_ranges(value_node, (*path, index), ranges)


def _to_plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_to_plain(item) for item in value]
    return value
