"""
Docstring and signature helpers shared by all metrics.

Every metric is called through :class:`hydrometrics.core.base.MetricFunction`, which accepts
the same keyword arguments (``axis``, ``nan_policy``, ``sample_weight``, ``weight``,
``reduction``, ``align``) whatever the metric. :func:`unified_docstring` writes these
parameters and the exceptions they can raise into the docstring of the metric once, so the
individual docstrings only describe what is specific to the metric.
"""

from __future__ import annotations

import inspect
import re

_TITLES = {
    "Parameters", "Returns", "Yields", "Raises", "Warns", "See Also", "Notes",
    "References", "Examples", "Other Parameters",
}
_COMMON = {"axis", "nan_policy", "sample_weight", "weight", "reduction", "align"}


def _split(lines: list[str]) -> tuple[list[str], list[list]]:
    """Split a cleaned docstring into the head and ``[title, body_lines]`` sections."""
    head: list[str] = []
    sections: list[list] = []
    current = None
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and lines[i].strip() in _TITLES and re.fullmatch(r"-{3,}", lines[i + 1].strip()):
            current = [lines[i].strip(), []]
            sections.append(current)
            i += 2
            continue
        (current[1] if current else head).append(lines[i])
        i += 1
    return head, sections


def _entries(body: list[str]) -> list[list]:
    """Parse a Parameters or Raises body into ``[header, description_lines]`` entries."""
    entries: list[list] = []
    for line in body:
        if line and not line[0].isspace():
            entries.append([line, []])
        elif entries:
            entries[-1][1].append(line)
    for entry in entries:
        while entry[1] and not entry[1][-1].strip():
            entry[1].pop()
    return entries


def _name(header: str) -> str:
    return header.split(":")[0].strip()


def _standard_parameters(supports_weight: bool, supports_axis: bool) -> list[list]:
    axis = (
        ["axis : int, optional",
         ["    Axis along which to compute; ``None`` pools all values. For xarray inputs use ``dim``",
          "    (a dimension name) or ``axis``."]]
        if supports_axis else
        ["axis : None",
         ["    Not supported by this metric: any other value raises ``NotImplementedError``."]]
    )
    weight = (
        ["sample_weight : array-like, optional",
         ["    Weights of the observations, same shape as ``obs``, non-negative. NaN makes the pair",
          "    invalid. ``weight`` is accepted as an alias; passing both raises ``TypeError``."]]
        if supports_weight else
        ["sample_weight : None",
         ["    Not supported by this metric: a weight (or its alias ``weight``) raises",
          "    ``NotImplementedError``."]]
    )
    return [
        axis,
        ["nan_policy : {\"propagate\", \"omit\", \"raise\"}, default=\"omit\"",
         ["    Missing values (NaN) in ``obs``, ``sim`` or the weight. ``\"omit\"`` drops the affected",
          "    pairs, also along an axis; ``\"propagate\"`` returns NaN for the result, or for each",
          "    slice along ``axis``, that contains a NaN; ``\"raise\"`` raises ``ValueError``."]],
        weight,
        ["reduction : {\"mean\", \"sum\", \"none\"}, optional",
         ["    How an output with ``ndim > 0`` is reduced. By default an ``axis`` returns the array",
          "    over the remaining dimensions (``\"none\"``) and no ``axis`` returns the ``\"mean\"``."]],
        ["align : {\"strict\", \"inner\"}, default=\"strict\"",
         ["    Labelled inputs. ``\"strict\"`` raises ``ValueError`` if the indexes of two pandas objects (or the",
          "    coordinates of two xarray objects) differ; ``\"inner\"`` cuts them to the common labels, in the",
          "    order of ``obs``, before the NaN policy is applied. Inputs without labels are matched by",
          "    position; ``\"inner\"`` raises ``ValueError`` for them."]],
    ]


_STANDARD_RAISES = {
    "ValueError": [
        "    If the shapes of ``obs`` and ``sim`` are incompatible, a weight is negative or has the",
        "    wrong shape, ``nan_policy``, ``reduction`` or ``align`` is unknown, NaN is present with",
        "    ``nan_policy=\"raise\"``, or the labels of the inputs are not aligned (``align``).",
    ],
    "TypeError": ["    If ``sample_weight`` and ``weight`` are both given."],
    "NotImplementedError": [
        "    If a weight or an ``axis`` is given to a metric that does not support it.",
    ],
}


def unified_docstring(doc: str | None, *, supports_weight: bool = True, supports_axis: bool = True) -> str:
    """Return ``doc`` with the common parameters and the ``Raises`` section written out."""
    if not doc:
        return ""
    head, sections = _split(inspect.cleandoc(doc).splitlines())
    standard = _standard_parameters(supports_weight, supports_axis)

    for section in sections:
        title, body = section
        if title == "Parameters":
            kept = [e for e in _entries(body) if _name(e[0]) not in _COMMON]
            kept += standard
            section[1] = [line for header, desc in kept for line in [header, *desc]]
        elif title == "Raises":
            existing = {_name(e[0]): e[1] for e in _entries(body)}
            merged = []
            for exc, text in _STANDARD_RAISES.items():
                extra = [ln for ln in existing.pop(exc, [])]
                merged += [exc, *text, *extra]
            for exc, text in existing.items():
                merged += [exc, *text]
            section[1] = merged

    if not any(title == "Raises" for title, _ in sections):
        raises = [line for exc, text in _STANDARD_RAISES.items() for line in [exc, *text]]
        titles = [t for t, _ in sections]
        after = (titles.index("Returns") + 1) if "Returns" in titles else next(
            (i for i, t in enumerate(titles) if t in ("Notes", "References", "Examples")), len(titles))
        sections.insert(after, ["Raises", raises])

    out = list(head)
    while out and not out[-1].strip():
        out.pop()
    for title, body in sections:
        while body and not body[-1].strip():
            body = body[:-1]
        out += ["", title, "-" * len(title), *body]
    return "\n".join(out) + "\n"


def public_signature(func) -> inspect.Signature:
    """Signature of the public call of a metric: ``(obs, sim, *, <metric parameters>, <common>)``."""
    parameter = inspect.Parameter
    own = [
        p.replace(kind=parameter.KEYWORD_ONLY)
        for name, p in inspect.signature(func).parameters.items()
        if name not in {"obs", "sim"} | _COMMON
    ]
    common = [
        parameter("axis", parameter.KEYWORD_ONLY, default=None, annotation="int | None"),
        parameter("nan_policy", parameter.KEYWORD_ONLY, default="omit", annotation="NanPolicyType"),
        parameter("sample_weight", parameter.KEYWORD_ONLY, default=None, annotation="Any | None"),
        parameter("weight", parameter.KEYWORD_ONLY, default=None, annotation="Any | None"),
        parameter("reduction", parameter.KEYWORD_ONLY, default=None, annotation="ReductionType | None"),
        parameter("align", parameter.KEYWORD_ONLY, default="strict", annotation="AlignType"),
    ]
    return inspect.Signature(
        [
            parameter("obs", parameter.POSITIONAL_OR_KEYWORD, annotation="Any"),
            parameter("sim", parameter.POSITIONAL_OR_KEYWORD, annotation="Any"),
            *own,
            *common,
        ],
        return_annotation="MetricResult",
    )
