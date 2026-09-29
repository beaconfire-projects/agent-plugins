#!/usr/bin/env python3
"""Archive authorized Google Docs question images without changing source order.

JSON stdin: {document, metadata: {file_id}, source_before: {modifiedTime},
             source_after: {modifiedTime}}. --output-dir is a durable run directory.
Returns JSON with manifest/Markdown paths, counts, and review/refresh status.
No Google credentials are handled here. The caller obtains the document via Drive.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid


MAX_IMAGE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 20
SECTIONS = {"question list": "Question List", "code question list": "Code Question List"}
NON_QUESTION_HEADINGS = {"notes", "summary", "feedback", "interviewer feedback",
                         "candidate details", "candidate information", "interview details",
                         "job description", "answer list"}
MONOSPACE_FONTS = {"courier", "courier new", "consolas", "menlo", "monaco",
                   "source code pro", "roboto mono", "monospace"}


class ArchiveError(ValueError):
    """An input validation error, expressed as a non-sensitive code."""


class ImageDownloadError(Exception):
    def __init__(self, code, needs_refresh=False):
        self.code = code
        self.needs_refresh = needs_refresh
        super().__init__(code)


def _image_kind(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", "jpg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif", "gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp", "webp"
    raise ImageDownloadError("invalid_image")


def _validate_image_uri(uri):
    try:
        parsed = urllib.parse.urlsplit(uri)
        host = parsed.hostname or ""
        valid = (parsed.scheme == "https" and
                 (host == "googleusercontent.com" or host.endswith(".googleusercontent.com")) and
                 parsed.username is None and parsed.password is None and
                 parsed.port in (None, 443))
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise ImageDownloadError("unapproved_image_host")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download_image(uri):
    """Read one authorized, short-lived Google image URI; never persist the URI."""
    opener = urllib.request.build_opener(_NoRedirect())
    for attempt in range(4):
        _validate_image_uri(uri)
        request = urllib.request.Request(uri, headers={"Accept": "image/*"})
        try:
            with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
                mime = response.headers.get_content_type().lower()
                if mime not in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
                    raise ImageDownloadError("invalid_content_type")
                data = response.read(MAX_IMAGE_BYTES + 1)
                if len(data) > MAX_IMAGE_BYTES:
                    raise ImageDownloadError("image_too_large")
                detected, _ = _image_kind(data)
                if detected != mime:
                    raise ImageDownloadError("image_type_mismatch")
                return data, detected
        except urllib.error.HTTPError as error:
            try:
                if error.code in (301, 302, 303, 307, 308):
                    location = error.headers.get("Location")
                    if not location or attempt == 3:
                        raise ImageDownloadError("redirect_failed") from None
                    uri = urllib.parse.urljoin(uri, location)
                    continue
                raise ImageDownloadError(
                    f"http_{error.code}", needs_refresh=error.code in (401, 403, 404)
                ) from None
            finally:
                error.close()
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ImageDownloadError("network_error") from None
    raise ImageDownloadError("redirect_failed")


def _escape(value):
    """Source text is literal: it cannot inject links, images, or HTML."""
    value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"([\\`*_{}\[\]()#+.!|~-])", r"\\\1", value)


def _plain(paragraph):
    return "".join(e.get("textRun", {}).get("content", "")
                   for e in paragraph.get("elements", []))


def _section(text):
    key = re.sub(r"[_\s]+", " ", text.strip().rstrip(":：")).casefold()
    return SECTIONS.get(key)


def _heading_level(paragraph):
    style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
    match = re.fullmatch(r"HEADING_(\d)", style)
    return int(match.group(1)) if match else None


def _tabs(document):
    def visit(tabs):
        for i, tab in enumerate(tabs):
            props = tab.get("tabProperties", tab)
            content = tab.get("documentTab", tab)
            yield {"id": props.get("tabId", f"tab-{i}"),
                   "title": props.get("title", ""),
                   "body": content.get("body") or {},
                   "inline": content.get("inlineObjects") or document.get("inlineObjects") or {},
                   "positioned": content.get("positionedObjects") or document.get("positionedObjects") or {},
                   "lists": content.get("lists") or document.get("lists") or {}}
            yield from visit(tab.get("childTabs") or [])
    if document.get("tabs"):
        yield from visit(document["tabs"])
    else:
        yield {"id": "body", "title": "", "body": document.get("body") or {},
               "inline": document.get("inlineObjects") or {},
               "positioned": document.get("positionedObjects") or {},
               "lists": document.get("lists") or {}}


def _paragraphs(content):
    for element in content:
        if "paragraph" in element:
            yield element["paragraph"]
        for row in element.get("table", {}).get("tableRows", []):
            for cell in row.get("tableCells", []):
                yield from _paragraphs(cell.get("content", []))


def _image_uri(objects, object_id, positioned=False):
    obj = objects.get(object_id) or {}
    properties = "positionedObjectProperties" if positioned else "inlineObjectProperties"
    return obj.get(properties, {}).get("embeddedObject", {}).get("imageProperties", {}).get("contentUri")


def _list_marker(bullet, lists, counters):
    """Return a source-defined marker, or None when the connector omitted it."""
    list_id = bullet.get("listId")
    depth = bullet.get("nestingLevel", 0)
    levels = lists.get(list_id, {}).get("listProperties", {}).get("nestingLevels", [])
    if not isinstance(depth, int) or depth < 0 or depth >= len(levels):
        return None
    definition = levels[depth]
    current = counters.setdefault(list_id, {})
    current[depth] = current.get(depth, definition.get("startNumber", 1) - 1) + 1
    for deeper in list(current):
        if deeper > depth:
            del current[deeper]
    if definition.get("glyphSymbol"):
        return definition["glyphSymbol"]
    if definition.get("glyphType") != "DECIMAL":
        return None
    glyph_format = definition.get("glyphFormat", f"%{depth}.")
    referenced = [int(index) for index in re.findall(r"%(\d+)", glyph_format)]
    if any(index not in current or index >= len(levels) or
           levels[index].get("glyphType") != "DECIMAL" for index in referenced):
        return None
    return re.sub(r"%(\d+)", lambda match: str(current[int(match.group(1))]), glyph_format)


def _content_blocks(document):
    blocks, warnings = [], []
    tabs = list(_tabs(document))
    for tab in tabs:
        recognized = any(_section(_plain(p)) for p in _paragraphs(tab["body"].get("content", [])))
        if not recognized:
            warnings.append("section_boundaries_need_review")
        state = {"active": not recognized, "level": None, "section": None}
        tab_blocks = []
        list_counters = {}

        def position(path, element):
            result = {"tab_id": tab["id"], "path": path}
            for key in ("startIndex", "endIndex"):
                if key in element:
                    result[key] = element[key]
            return result

        def add(kind, pos, **fields):
            tab_blocks.append({"type": kind, "position": pos,
                               "section": state["section"], **fields})

        def add_image(object_id, pos, positioned=False):
            uri = _image_uri(tab["positioned"] if positioned else tab["inline"],
                             object_id, positioned)
            add("image", pos, object_id=object_id,
                placement="paragraph_anchor" if positioned else "inline", _uri=uri)

        def walk(content, path):
            for i, element in enumerate(content):
                here = path + [i]
                pos = position(here, element)
                if "paragraph" in element:
                    paragraph = element["paragraph"]
                    plain = _plain(paragraph)
                    heading = _section(plain)
                    level = _heading_level(paragraph)
                    bullet = paragraph.get("bullet")
                    marker = _list_marker(bullet, tab["lists"], list_counters) if bullet else None
                    if heading:
                        state.update(active=True, level=level, section=heading)
                        add("section", pos, text=heading)
                    elif recognized and level and state["active"]:
                        if plain.strip().rstrip(":：").casefold() in NON_QUESTION_HEADINGS:
                            state["active"] = False
                        elif not bullet and not re.match(r"\s*(?:Q(?:uestion)?\s*)?\d+[.):：]", plain, re.I):
                            if state["level"] is None or level <= state["level"]:
                                warnings.append("section_boundaries_need_review")
                    if not state["active"]:
                        continue
                    if bullet and marker is None:
                        warnings.append("list_glyph_needs_review")
                    fields = {"bullet": {"list_id": bullet.get("listId"),
                                         "nesting_level": bullet.get("nestingLevel", 0),
                                         "marker": marker}} if bullet else {}
                    add("paragraph_start", pos, **fields)
                    for j, run in enumerate(paragraph.get("elements", [])):
                        run_pos = position(here + ["paragraph", "elements", j], run)
                        if "textRun" in run:
                            text_run = run["textRun"]
                            font = text_run.get("textStyle", {}).get("weightedFontFamily", {}).get("fontFamily", "")
                            add("text", run_pos, text=text_run.get("content", ""),
                                monospace=font.casefold() in MONOSPACE_FONTS)
                        elif "inlineObjectElement" in run:
                            add_image(run["inlineObjectElement"].get("inlineObjectId", ""), run_pos)
                        elif "richLink" in run:
                            props = run["richLink"].get("richLinkProperties", {})
                            add("text", run_pos, text=props.get("title", "[linked resource]"))
                        elif "person" in run:
                            props = run["person"].get("personProperties", {})
                            add("text", run_pos, text=props.get("name", "[person]"))
                        else:
                            warnings.append("unsupported_paragraph_element")
                            add("notice", run_pos, text="Unsupported source element; check original document.")
                    add("paragraph_end", pos)
                    for j, object_id in enumerate(paragraph.get("positionedObjectIds") or []):
                        add_image(object_id, position(here + ["positionedObjectIds", j], element), True)
                elif "table" in element:
                    for row_index, row in enumerate(element["table"].get("tableRows", [])):
                        for col_index, cell in enumerate(row.get("tableCells", [])):
                            begin = len(tab_blocks)
                            walk(cell.get("content", []), here + ["table", row_index, col_index])
                            if len(tab_blocks) > begin:
                                tab_blocks.insert(begin, {"type": "table_cell", "position": pos,
                                    "row": row_index + 1, "column": col_index + 1})
        walk(tab["body"].get("content", []), ["body", "content"])
        if tab_blocks:
            blocks.append({"type": "tab", "tab_id": tab["id"], "text": tab["title"]})
            blocks.extend(tab_blocks)
    if not any(b["type"] in ("text", "image") for b in blocks):
        warnings.append("empty_document_needs_review")
    return blocks, sorted(set(warnings))


def _render_text(text, section, monospace):
    body = text.rstrip("\n")
    is_code = monospace or (section == "Code Question List" and (
        bool(re.search(r"(?:^|\n)(?: {2,}|\t)\S", body)) or
        bool(re.match(r"\s*(?:if|for|while|class|public|private|def|function)\b.*[{:;]", body))))
    if is_code:
        longest = max((len(run) for run in re.findall(r"`+", body)), default=0)
        fence = "`" * max(3, longest + 1)
        return f"\n\n{fence}\n{body}\n{fence}\n\n"
    # A single trailing newline terminates the source paragraph; internal breaks
    # must remain visible instead of being collapsed by Markdown rendering.
    return _escape(text).replace("\n", "  \n")


def _render(blocks, title, source_url, warnings):
    parts = [f"# {_escape(title)}\n\n[Original document]({source_url})\n\n"]
    if "section_boundaries_need_review" in warnings:
        parts.append("> Section boundaries need review; source body is retained in order.\n\n")
    if "list_glyph_needs_review" in warnings:
        parts.append("> Some original list markers are unavailable; • preserves their positions without inventing numbers.\n\n")
    if "empty_document_needs_review" in warnings:
        parts.append("> No question content was found; check the original document.\n\n")
    text_buffer, text_section, monospace = [], None, False

    def flush_text():
        nonlocal text_buffer, monospace
        if text_buffer:
            parts.append(_render_text("".join(text_buffer), text_section, monospace))
            text_buffer, monospace = [], False

    for block in blocks:
        kind = block["type"]
        if kind == "text":
            text_buffer.append(block["text"])
            text_section = block.get("section")
            monospace |= block.get("monospace", False)
            continue
        flush_text()
        if kind == "tab" and block["text"]:
            parts.append(f"\n\n## {_escape(block['text'])}\n\n")
        elif kind == "table_cell":
            parts.append(f"\n\n**Table row {block['row']}, column {block['column']}**\n\n")
        elif kind == "paragraph_start" and block.get("bullet"):
            bullet = block["bullet"]
            parts.append("  " * min(bullet["nesting_level"], 8) + _escape(bullet["marker"] or "•") + " ")
        elif kind == "paragraph_end":
            parts.append("\n\n")
        elif kind == "notice":
            parts.append(f"\n\n[{_escape(block['text'])}]\n\n")
        elif kind == "image":
            if block["status"] == "saved":
                path = block["path"].replace("%", "%25").replace(" ", "%20").replace("(", "%28").replace(")", "%29")
                parts.append(f"\n\n![Original image {block['occurrence']}](<{path}>)\n\n")
            else:
                parts.append(f"\n\n[Image unavailable: {block['error']}; see original document.]\n\n")
    flush_text()
    return "".join(parts).rstrip() + "\n"


def _write_private(path, data):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as output:
        output.write(data)


def archive_document(payload, output_dir, fetch_image=download_image):
    document = payload.get("document") or {}
    document = document.get("structuredContent", document)
    if not isinstance(document, dict):
        raise ArchiveError("invalid_document")
    file_id = (payload.get("metadata") or {}).get("file_id")
    if not isinstance(file_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", file_id):
        raise ArchiveError("invalid_file_id")
    if document.get("documentId") != file_id:
        raise ArchiveError("document_id_mismatch")
    before = (payload.get("source_before") or {}).get("modifiedTime")
    after = (payload.get("source_after") or {}).get("modifiedTime")
    if not isinstance(before, str) or not before or not isinstance(after, str) or not after:
        raise ArchiveError("source_version_missing")
    if before != after:
        raise ArchiveError("source_changed")
    blocks, warnings = _content_blocks(document)
    suffix = re.sub(r"[^A-Za-z0-9_-]", "-", before)[:50]
    archive = Path(output_dir).expanduser().resolve() / f"{file_id}-{suffix}-{uuid.uuid4().hex[:8]}"
    archive.mkdir(mode=0o700, parents=True, exist_ok=False)
    images_dir = archive / "images"
    images_dir.mkdir(mode=0o700)
    images, cache, needs_refresh = [], {}, False
    for block in blocks:
        if block["type"] != "image":
            continue
        uri = block.pop("_uri")
        block["occurrence"] = len(images) + 1
        try:
            if not uri:
                raise ImageDownloadError("missing_image_reference")
            # A URI cache avoids re-fetching repeated objects; all occurrences remain.
            if uri not in cache:
                try:
                    _validate_image_uri(uri)
                    data, mime = fetch_image(uri)
                    if not isinstance(data, bytes) or len(data) > MAX_IMAGE_BYTES:
                        raise ImageDownloadError("image_too_large" if isinstance(data, bytes) else "invalid_image")
                    detected, extension = _image_kind(data)
                    if mime != detected:
                        raise ImageDownloadError("image_type_mismatch")
                    digest = hashlib.sha256(data).hexdigest()
                    image_path = images_dir / f"{digest}.{extension}"
                    if not image_path.exists():
                        _write_private(image_path, data)
                    cache[uri] = {"status": "saved", "path": str(image_path),
                                  "sha256": digest, "mime_type": detected, "bytes": len(data)}
                except ImageDownloadError as error:
                    code = error.code if re.fullmatch(r"[a-z0-9_]+", str(error.code)) else "download_failed"
                    cache[uri] = {"status": "failed", "error": code,
                                  "needs_refresh": bool(error.needs_refresh)}
                except Exception:
                    cache[uri] = {"status": "failed", "error": "download_failed", "needs_refresh": False}
            block.update(cache[uri])
        except ImageDownloadError as error:
            block.update(status="failed", error=error.code, needs_refresh=error.needs_refresh)
        needs_refresh |= block.get("needs_refresh", False)
        images.append({key: value for key, value in block.items() if key != "type"})
    failed = sum(image["status"] != "saved" for image in images)
    needs_review = bool(warnings)
    status = "partial" if failed else "needs_review" if needs_review else "complete"
    source_url = f"https://docs.google.com/document/d/{file_id}/edit"
    manifest = {"schema_version": 1, "file_id": file_id, "source_modified_time": before,
                "source_url": source_url, "status": status, "needs_review": needs_review,
                "needs_refresh": needs_refresh, "warnings": warnings,
                "image_count": len(images), "displayable_image_count": len(images) - failed,
                "blocks": blocks, "images": images}
    manifest_path = archive / "manifest.json"
    markdown_path = archive / "questions.md"
    _write_private(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    _write_private(markdown_path, _render(blocks, document.get("title", file_id), source_url, warnings).encode("utf-8"))
    return {"manifest_path": str(manifest_path), "markdown_path": str(markdown_path),
            "status": status, "needs_review": needs_review, "needs_refresh": needs_refresh,
            "image_count": len(images), "displayable_image_count": len(images) - failed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        result = archive_document(payload, args.output_dir)
    except ArchiveError as error:
        print(json.dumps({"error": str(error)}))
        return 2
    except Exception:
        print(json.dumps({"error": "archive_failed"}))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
