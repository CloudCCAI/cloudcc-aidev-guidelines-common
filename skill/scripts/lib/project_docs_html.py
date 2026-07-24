from __future__ import annotations

import hashlib
import html
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from .state_io import SimpleYamlError, clean_value, split_front_matter


DOCUMENT_ROOTS = (Path("docs/design"), Path("docs/specs"))
SOURCE_DIGEST_META = "cc-aidev-source-sha256"
GENERATOR_VERSION_META = "cc-aidev-generator-version"
GENERATOR_VERSION = "4"
_DIGEST_RE = re.compile(
    rf'<meta\s+name="{SOURCE_DIGEST_META}"\s+content="([0-9a-f]{{64}})"\s*/?>',
    re.IGNORECASE,
)
_GENERATOR_VERSION_RE = re.compile(
    rf'<meta\s+name="{GENERATOR_VERSION_META}"\s+content="([^"]+)"\s*/?>',
    re.IGNORECASE,
)
_FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([A-Za-z0-9_+.-]*)\s*$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_UNORDERED_RE = re.compile(r"^\s*[-+*]\s+(.+)$")
_ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_TABLE_DIVIDER_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


@dataclass(frozen=True)
class PairStatus:
    source: Path
    output: Path
    digest: str
    current: bool
    reason: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def source_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def companion_path(source: Path) -> Path:
    return source.with_suffix(".html")


def project_root_for_document(source: Path) -> Path | None:
    resolved = source.resolve()
    for parent in resolved.parents:
        if parent.name not in {"design", "specs"}:
            continue
        if parent.parent.name == "docs":
            return parent.parent.parent
    return None


def is_project_document(source: Path, project_root: Path) -> bool:
    try:
        relative = source.resolve().relative_to(project_root.resolve())
    except ValueError:
        return False
    if source.suffix.lower() != ".md":
        return False
    return any(relative.is_relative_to(root) for root in DOCUMENT_ROOTS)


def discover_documents(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    documents: list[Path] = []
    for relative_root in DOCUMENT_ROOTS:
        directory = root / relative_root
        if directory.is_dir():
            documents.extend(path for path in directory.rglob("*.md") if path.is_file())
    return sorted(set(documents), key=lambda path: path.relative_to(root).as_posix())


def inspect_pair(source: Path) -> PairStatus:
    output = companion_path(source)
    digest = source_digest(source)
    if not output.is_file():
        return PairStatus(source, output, digest, False, "missing")
    prefix = output.read_text(encoding="utf-8", errors="replace")[:8192]
    match = _DIGEST_RE.search(prefix)
    if not match:
        return PairStatus(source, output, digest, False, "missing source digest")
    if match.group(1).lower() != digest:
        return PairStatus(source, output, digest, False, "source digest mismatch")
    generator_match = _GENERATOR_VERSION_RE.search(prefix)
    if not generator_match or generator_match.group(1) != GENERATOR_VERSION:
        return PairStatus(source, output, digest, False, "generator version mismatch")
    return PairStatus(source, output, digest, True, "current")


def validate_project_documents(project_root: Path) -> list[str]:
    root = project_root.resolve()
    errors: list[str] = []
    for source in discover_documents(root):
        status = inspect_pair(source)
        if status.current:
            continue
        relative_source = source.relative_to(root).as_posix()
        relative_output = status.output.relative_to(root).as_posix()
        errors.append(
            f"{relative_source}: paired human-readable HTML `{relative_output}` is {status.reason}; "
            "run `python3 <skill>/scripts/generate-project-docs-html.py "
            f"{relative_source} --write`"
        )
    return errors


def _safe_url(raw_url: str) -> str:
    cleaned = raw_url.strip()
    parsed = urlsplit(cleaned)
    if parsed.scheme.lower() not in {"", "http", "https", "mailto"}:
        return "#"
    return html.escape(cleaned, quote=True)


def _inline_markdown(text: str) -> str:
    tokens: dict[str, str] = {}

    def protect(fragment: str) -> str:
        key = f"\x00TOKEN{len(tokens)}\x00"
        tokens[key] = fragment
        return key

    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"`([^`\n]+)`",
        lambda match: protect(f"<code>{match.group(1)}</code>"),
        escaped,
    )
    escaped = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;.*?&quot;)?\)",
        lambda match: protect(
            f'<img src="{_safe_url(html.unescape(match.group(2)))}" '
            f'alt="{html.escape(html.unescape(match.group(1)), quote=True)}" loading="lazy">'
        ),
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;.*?&quot;)?\)",
        lambda match: protect(
            f'<a href="{_safe_url(html.unescape(match.group(2)))}">'
            f"{html.escape(html.unescape(match.group(1)))}</a>"
        ),
        escaped,
    )
    escaped = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)
    for key, fragment in tokens.items():
        escaped = escaped.replace(key, fragment)
    return escaped


def _table_cells(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", stripped)]


def _starts_block(lines: list[str], index: int) -> bool:
    line = lines[index]
    if not line.strip():
        return True
    if _FENCE_RE.match(line) or _HEADING_RE.match(line):
        return True
    if _UNORDERED_RE.match(line) or _ORDERED_RE.match(line):
        return True
    if line.lstrip().startswith(">") or re.fullmatch(r"\s*(?:---+|\*\*\*+|___+)\s*", line):
        return True
    return index + 1 < len(lines) and "|" in line and bool(_TABLE_DIVIDER_RE.match(lines[index + 1]))


def render_markdown(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    lines = markdown.splitlines()
    output: list[str] = []
    headings: list[tuple[int, str, str]] = []
    heading_count = 0
    section_open = False
    index = 0

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            output.append("</div></details>")
            section_open = False

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        fence = _FENCE_RE.match(line)
        if fence:
            marker, language = fence.groups()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].lstrip().startswith(marker):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            language_class = re.sub(r"[^A-Za-z0-9_-]", "", language)
            class_attribute = f' class="language-{language_class}"' if language_class else ""
            output.append(
                f"<pre><code{class_attribute}>{html.escape(chr(10).join(code_lines))}</code></pre>"
            )
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            label = heading.group(2).strip()
            heading_count += 1
            anchor = f"section-{heading_count}"
            headings.append((level, label, anchor))
            rendered_label = _inline_markdown(label)
            if level == 2:
                close_section()
                output.append(
                    f'<details class="document-section" open id="{anchor}">'
                    f"<summary><h2>{rendered_label}</h2><span aria-hidden=\"true\">⌄</span></summary>"
                    '<div class="section-content">'
                )
                section_open = True
            else:
                output.append(f'<h{level} id="{anchor}">{rendered_label}</h{level}>')
            index += 1
            continue

        if re.fullmatch(r"\s*(?:---+|\*\*\*+|___+)\s*", line):
            output.append("<hr>")
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and _TABLE_DIVIDER_RE.match(lines[index + 1]):
            headers = _table_cells(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(_table_cells(lines[index]))
                index += 1
            output.append('<div class="table-wrap"><table><thead><tr>')
            output.extend(f"<th>{_inline_markdown(cell)}</th>" for cell in headers)
            output.append("</tr></thead><tbody>")
            for row in rows:
                output.append("<tr>")
                output.extend(f"<td>{_inline_markdown(cell)}</td>" for cell in row)
                output.append("</tr>")
            output.append("</tbody></table></div>")
            continue

        unordered = _UNORDERED_RE.match(line)
        ordered = _ORDERED_RE.match(line)
        if unordered or ordered:
            list_tag = "ul" if unordered else "ol"
            item_pattern = _UNORDERED_RE if unordered else _ORDERED_RE
            output.append(f"<{list_tag}>")
            while index < len(lines):
                item = item_pattern.match(lines[index])
                if not item:
                    break
                value = item.group(1)
                task = re.match(r"^\[([ xX])\]\s+(.+)$", value)
                if task:
                    checked = " checked" if task.group(1).lower() == "x" else ""
                    output.append(
                        '<li class="task-item">'
                        f'<input type="checkbox" disabled{checked}>'
                        f"<span>{_inline_markdown(task.group(2))}</span></li>"
                    )
                else:
                    output.append(f"<li>{_inline_markdown(value)}</li>")
                index += 1
            output.append(f"</{list_tag}>")
            continue

        if line.lstrip().startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].lstrip().startswith(">"):
                quote_lines.append(lines[index].lstrip()[1:].lstrip())
                index += 1
            output.append(f"<blockquote>{_inline_markdown(' '.join(quote_lines))}</blockquote>")
            continue

        paragraph: list[str] = []
        while index < len(lines) and not _starts_block(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        if not paragraph:
            paragraph.append(line.strip())
            index += 1
        output.append(f"<p>{_inline_markdown(' '.join(paragraph))}</p>")

    close_section()
    return "\n".join(output), headings


def _read_document(source: Path) -> tuple[dict[str, object], str]:
    text = source.read_text(encoding="utf-8")
    try:
        return split_front_matter(text)
    except SimpleYamlError:
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for index in range(1, len(lines)):
                if lines[index].strip() == "---":
                    body = "\n".join(lines[index + 1 :])
                    return {}, body
        return {}, text


def _document_title(source: Path, fields: dict[str, object], body: str) -> str:
    title = clean_value(fields.get("title"))
    if title:
        return title
    for line in body.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return re.sub(r"[`*_~]", "", match.group(1)).strip()
    return source.stem


def _without_leading_h1(body: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if not re.match(r"^#\s+.+$", line):
            return body
        del lines[index]
        while index < len(lines) and not lines[index].strip():
            del lines[index]
        rendered = "\n".join(lines)
        return rendered + ("\n" if body.endswith("\n") and rendered else "")
    return body


def _metadata_items(fields: dict[str, object]) -> list[tuple[str, str, str]]:
    labels = (
        ("feature_id", "功能", "id"),
        ("status", "状态", "status"),
        ("work_type", "类型", "type"),
        ("owner_slug", "负责人", "owner"),
        ("updated_at", "更新时间", "updated"),
        ("updated_by", "更新人", "author"),
    )
    items: list[tuple[str, str, str]] = []
    for key, label, css_name in labels:
        value = clean_value(fields.get(key))
        if value and value.lower() not in {"none", "n/a"}:
            items.append((label, value, css_name))
    return items


def render_document(
    source: Path,
    *,
    project_root: Path | None = None,
    generated_at: str | None = None,
) -> str:
    source = source.resolve()
    fields, body = _read_document(source)
    title = _document_title(source, fields, body)
    rendered_body, headings = render_markdown(_without_leading_h1(body))
    digest = source_digest(source)
    timestamp = generated_at or utc_now()
    root = project_root.resolve() if project_root else project_root_for_document(source)
    source_label = source.relative_to(root).as_posix() if root else source.name
    toc_items = [
        f'<li class="toc-level-{level}"><a href="#{anchor}">{_inline_markdown(label)}</a></li>'
        for level, label, anchor in headings
        if level >= 2
    ]
    metadata = _metadata_items(fields)
    metadata_html = "".join(
        f'<div class="meta-item meta-{css_name}"><span>{html.escape(label)}</span>'
        f"<strong>{html.escape(value)}</strong></div>"
        for label, value, css_name in metadata
    )
    toc_html = "\n".join(toc_items) if toc_items else '<li class="toc-empty">本文没有二级标题</li>'
    status = clean_value(fields.get("status", ""))
    status_class = re.sub(r"[^a-z0-9_-]", "-", status.lower())

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="{SOURCE_DIGEST_META}" content="{digest}">
  <meta name="{GENERATOR_VERSION_META}" content="{GENERATOR_VERSION}">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --paper: #ffffff;
      --ink: #17212b;
      --muted: #66727f;
      --line: #dfe5eb;
      --accent: #176b87;
      --accent-soft: #e8f3f6;
      --code: #f3f5f7;
      --shadow: 0 18px 50px rgba(21, 35, 48, .08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font: 16px/1.72 -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .page {{ display: grid; grid-template-columns: minmax(220px, 280px) minmax(0, 900px); gap: 28px;
      max-width: 1240px; margin: 0 auto; padding: 28px; align-items: start; }}
    .sidebar {{ position: sticky; top: 24px; max-height: calc(100vh - 48px); overflow: auto;
      background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 20px; }}
    .eyebrow {{ margin: 0 0 8px; color: var(--accent); font-size: 12px; font-weight: 750;
      letter-spacing: .08em; text-transform: uppercase; }}
    .source {{ margin: 0 0 18px; color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }}
    .toc-title {{ margin: 16px 0 8px; font-size: 13px; }}
    .toc {{ list-style: none; margin: 0; padding: 0; font-size: 14px; }}
    .toc li {{ margin: 3px 0; }}
    .toc a {{ display: block; padding: 5px 8px; border-radius: 7px; color: #33414d; text-decoration: none; }}
    .toc a:hover {{ background: var(--accent-soft); color: var(--accent); }}
    .toc-level-3 {{ padding-left: 12px; }}
    .toc-level-4, .toc-level-5, .toc-level-6 {{ padding-left: 24px; }}
    .toc-empty {{ color: var(--muted); padding: 5px 8px; }}
    main {{ min-width: 0; }}
    .hero, article {{ background: var(--paper); border: 1px solid var(--line); box-shadow: var(--shadow); }}
    .hero {{ border-radius: 20px; padding: clamp(24px, 5vw, 48px); margin-bottom: 20px; }}
    .hero h1 {{ margin: 0; font-size: clamp(28px, 4vw, 44px); line-height: 1.2; letter-spacing: -.025em; }}
    .notice {{ margin: 18px 0 0; padding: 12px 14px; border-left: 3px solid var(--accent);
      background: var(--accent-soft); color: #315461; font-size: 14px; }}
    .metadata {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 22px; }}
    .meta-item {{ padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; background: #fbfcfd; }}
    .meta-item span {{ display: block; color: var(--muted); font-size: 12px; }}
    .meta-item strong {{ display: block; margin-top: 2px; overflow-wrap: anywhere; }}
    .meta-status strong {{ color: var(--accent); }}
    .meta-updated strong {{ white-space: nowrap; font-size: 13px; }}
    article {{ border-radius: 20px; padding: clamp(22px, 5vw, 48px); }}
    article > h1:first-child {{ margin-top: 0; }}
    h1, h2, h3, h4 {{ line-height: 1.32; color: #13202a; }}
    h1 {{ font-size: 2rem; }} h2 {{ font-size: 1.45rem; }} h3 {{ margin-top: 1.7em; font-size: 1.16rem; }}
    p, ul, ol, blockquote, pre, .table-wrap {{ margin: 1em 0; }}
    li + li {{ margin-top: .35em; }}
    blockquote {{ margin-left: 0; padding: 10px 18px; border-left: 4px solid #9bbbc6;
      background: #f5f9fa; color: #42535d; }}
    code {{ padding: .15em .38em; border-radius: 5px; background: var(--code);
      font: .9em/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    pre {{ overflow: auto; padding: 18px; border-radius: 12px; background: #17212b; color: #e8edf1; }}
    pre code {{ padding: 0; background: transparent; color: inherit; }}
    img {{ display: block; max-width: 100%; height: auto; margin: 18px auto; border-radius: 10px; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #f5f8fa; }} tr:last-child td {{ border-bottom: 0; }}
    .task-item {{ list-style: none; margin-left: -22px; display: flex; gap: 8px; align-items: flex-start; }}
    .task-item input {{ margin-top: .42em; }}
    .document-section {{ margin: 20px 0; border: 1px solid var(--line); border-radius: 14px; overflow: clip; }}
    .document-section > summary {{ display: flex; align-items: center; justify-content: space-between;
      gap: 12px; padding: 15px 18px; cursor: pointer; background: #f8fafb; list-style: none; }}
    .document-section > summary::-webkit-details-marker {{ display: none; }}
    .document-section > summary h2 {{ margin: 0; font-size: 1.35rem; }}
    .document-section > summary span {{ color: var(--muted); transition: transform .18s ease; }}
    .document-section:not([open]) > summary span {{ transform: rotate(-90deg); }}
    .section-content {{ padding: 2px 18px 14px; }}
    .footer {{ color: var(--muted); text-align: center; font-size: 12px; padding: 18px; }}
    @media (max-width: 820px) {{
      .page {{ display: block; padding: 14px; }}
      .sidebar {{ position: static; max-height: none; margin-bottom: 14px; }}
      .hero, article {{ border-radius: 14px; box-shadow: none; }}
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ display: block; max-width: none; padding: 0; }}
      .sidebar {{ display: none; }}
      .hero, article {{ border: 0; box-shadow: none; padding: 0; }}
      .document-section {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body class="status-{html.escape(status_class, quote=True)}">
  <div class="page">
    <aside class="sidebar">
      <p class="eyebrow">Human-readable view</p>
      <p class="source">{html.escape(source_label)}</p>
      <strong class="toc-title">本文目录</strong>
      <ol class="toc">{toc_html}</ol>
    </aside>
    <main>
      <header class="hero">
        <p class="eyebrow">设计与规格文档</p>
        <h1>{html.escape(title)}</h1>
        <div class="metadata">{metadata_html}</div>
        <p class="notice">此 HTML 面向人类阅读，由 Markdown 自动生成；事实源仍是
          <code>{html.escape(source_label)}</code>。</p>
      </header>
      <article>{rendered_body}</article>
      <footer class="footer">生成时间：{html.escape(timestamp)} · 生成器版本：{GENERATOR_VERSION}</footer>
    </main>
  </div>
</body>
</html>
"""


def write_companion(
    source: Path,
    *,
    project_root: Path | None = None,
    generated_at: str | None = None,
) -> Path:
    source = source.resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise ValueError(f"expected an existing Markdown file: {source}")
    root = project_root.resolve() if project_root else project_root_for_document(source)
    if root is None or not is_project_document(source, root):
        raise ValueError(f"Markdown must be under docs/design or docs/specs: {source}")
    output = companion_path(source)
    if inspect_pair(source).current:
        return output
    rendered = render_document(source, project_root=root, generated_at=generated_at)
    output.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=str(output.parent),
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), 0o644)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def sync_project_documents(
    project_root: Path,
    *,
    generated_at: str | None = None,
) -> list[Path]:
    root = project_root.resolve()
    outputs: list[Path] = []
    for source in discover_documents(root):
        if inspect_pair(source).current:
            continue
        outputs.append(write_companion(source, project_root=root, generated_at=generated_at))
    return outputs
