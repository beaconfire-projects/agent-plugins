import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.error
from email.message import Message
import io
import stat


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_interview_doc.py"
SPEC = importlib.util.spec_from_file_location("render_interview_doc", SCRIPT)
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)

PNG = b"\x89PNG\r\n\x1a\n" + b"test-image"
URI = "https://lh3.googleusercontent.com/private-image?secret=TOKEN"


def text(value):
    return {"textRun": {"content": value}}


def image(object_id="img1"):
    return {"inlineObjectElement": {"inlineObjectId": object_id}}


def paragraph(*elements, **extra):
    return {"paragraph": {"elements": list(elements), **extra}}


def objects(uri=URI):
    return {"img1": {"inlineObjectProperties": {"embeddedObject": {
        "imageProperties": {"contentUri": uri}}}}}


def payload(content=None, **document_fields):
    doc = {"documentId": "doc123", "body": {"content": content or []},
           "inlineObjects": objects()}
    doc.update(document_fields)
    return {"document": doc, "metadata": {"file_id": "doc123"},
            "source_before": {"modifiedTime": "2026-09-29T10:00:00Z"},
            "source_after": {"modifiedTime": "2026-09-29T10:00:00Z"}}


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def archive(self, data, fetch=None):
        result = renderer.archive_document(
            data, self.directory.name,
            fetch_image=fetch or (lambda uri: (PNG, "image/png")))
        manifest = json.loads(Path(result["manifest_path"]).read_text())
        markdown = Path(result["markdown_path"]).read_text()
        return result, manifest, markdown

    def test_q1_image_q2_and_metadata_exclusion(self):
        data = payload([
            paragraph(text("Candidate: Private Name\n")),
            paragraph(text("Question List:\n")),
            paragraph(text("1. Start coding?\n")),
            paragraph(image()),
            paragraph(text("2. Explain the sliding window.\n")),
            paragraph(text("Notes\n"), paragraphStyle={"namedStyleType": "HEADING_1"}),
            paragraph(text("Not question content\n")),
        ])
        result, manifest, md = self.archive(data)
        self.assertLess(md.index("1\\. Start"), md.index("!["))
        self.assertLess(md.index("!["), md.index("2\\. Explain"))
        self.assertNotIn("Private Name", md)
        self.assertNotIn("Not question content", md)
        self.assertEqual(manifest["status"], "complete")
        self.assertEqual(result["image_count"], 1)

    def test_mixed_runs_and_positioned_image_anchor(self):
        data = payload([
            paragraph(text("Question List")),
            paragraph(text("Before "), image(), text(" after\n"),
                      positionedObjectIds=["float1"]),
            paragraph(text("Next")),
        ], positionedObjects={"float1": {"positionedObjectProperties": {
            "embeddedObject": {"imageProperties": {"contentUri": URI}}}}})
        _, manifest, md = self.archive(data)
        self.assertLess(md.index("Before"), md.index("!["))
        self.assertLess(md.index("!["), md.index("after"))
        self.assertLess(md.index("after"), md.rindex("!["))
        self.assertLess(md.rindex("!["), md.index("Next"))
        self.assertEqual(len(manifest["images"]), 2)
        self.assertEqual(manifest["images"][1]["placement"], "paragraph_anchor")

    def test_both_sections_nested_tabs_and_table_image_only(self):
        table = {"table": {"tableRows": [{"tableCells": [
            {"content": [paragraph(image())]},
            {"content": [paragraph(text("right cell"))]},
        ]}]}}
        data = payload(tabs=[{
            "tabProperties": {"tabId": "tab1", "title": "First"},
            "documentTab": {"body": {"content": [
                paragraph(text("Question List")), paragraph(text("Question")),
                paragraph(text("Code Question List")), table,
            ]}, "inlineObjects": objects()},
            "childTabs": [{"tabProperties": {"tabId": "tab2", "title": "Second"},
                           "documentTab": {"body": {"content": [
                               paragraph(text("QUESTION LIST")), paragraph(image())]},
                               "inlineObjects": objects()}}],
        }])
        result, manifest, md = self.archive(data)
        self.assertIn("Code Question List", md)
        self.assertIn("Table row 1, column 1", md)
        self.assertIn("right cell", md)
        self.assertEqual(result["image_count"], 2)
        self.assertEqual({i["position"]["tab_id"] for i in manifest["images"]}, {"tab1", "tab2"})

    def test_flat_tabs_and_structured_content_wrapper(self):
        data = payload(tabs=[{"tabId": "flat", "title": "Flat tab",
                             "body": {"content": [paragraph(text("Question List")),
                                                  paragraph(image())]},
                             "inlineObjects": objects()}])
        data["document"] = {"structuredContent": data["document"]}
        result, _, _ = self.archive(data)
        self.assertEqual(result["image_count"], 1)

    def test_image_in_section_heading_preserves_run_order(self):
        result, _, md = self.archive(payload([
            paragraph(image(), text("Question List"), image()),
            paragraph(text("Next question")),
        ]))
        self.assertEqual(result["image_count"], 2)
        self.assertLess(md.index("!["), md.index("Question List"))
        self.assertLess(md.index("Question List"), md.rindex("!["))

    def test_tab_without_section_is_retained_and_flagged(self):
        data = payload(tabs=[
            {"tabId": "questions", "body": {"content": [
                paragraph(text("Question List")), paragraph(text("Question"))]}},
            {"tabId": "unlabeled", "body": {"content": [
                paragraph(text("Unlabeled content")), paragraph(image())]},
             "inlineObjects": objects()},
        ])
        result, manifest, md = self.archive(data)
        self.assertEqual(result["image_count"], 1)
        self.assertTrue(manifest["needs_review"])
        self.assertIn("Unlabeled content", md)

    def test_unstyled_section_does_not_swallow_numbered_heading(self):
        result, manifest, md = self.archive(payload([
            paragraph(text("Question List")),
            paragraph(text("1. Explain threads"), image(),
                      paragraphStyle={"namedStyleType": "HEADING_2"}),
        ]))
        self.assertEqual(result["image_count"], 1)
        self.assertIn("Explain threads", md)

    def test_decimal_source_list_start_and_symbol_preserved(self):
        data = payload([
            paragraph(text("Question List")),
            paragraph(text("First question"), bullet={"listId": "numbered"}),
            paragraph(image()),
            paragraph(text("Second question"), bullet={"listId": "numbered"}),
            paragraph(text("Symbol item"), bullet={"listId": "symbols"}),
        ], lists={
            "numbered": {"listProperties": {"nestingLevels": [
                {"glyphType": "DECIMAL", "glyphFormat": "%0.", "startNumber": 5}]}},
            "symbols": {"listProperties": {"nestingLevels": [{"glyphSymbol": "○"}]}},
        })
        _, manifest, md = self.archive(data)
        self.assertIn("5\\. First question", md)
        self.assertIn("6\\. Second question", md)
        self.assertIn("○ Symbol item", md)
        self.assertFalse(manifest["needs_review"])
        self.assertLess(md.index("5\\."), md.index("!["))
        self.assertLess(md.index("!["), md.index("6\\."))

    def test_unknown_list_format_review_without_invented_numbers(self):
        _, manifest, md = self.archive(payload([
            paragraph(text("Question List")),
            paragraph(text("Question"), bullet={"listId": "unknown"}),
        ]))
        self.assertTrue(manifest["needs_review"])
        self.assertIn("• Question", md)

    def test_code_whitespace_and_prose_linebreaks_preserved(self):
        code = "if (true) {\n    return 1;\n}\n"
        _, _, md = self.archive(payload([
            paragraph(text("Code Question List")),
            paragraph(text(code), image(), text("Explanation line 1\nExplanation line 2\n")),
        ]))
        self.assertIn("```\n" + code + "```", md)
        self.assertIn("Explanation line 1  \nExplanation line 2", md)
        self.assertLess(md.index(code), md.index("!["))
        self.assertLess(md.index("!["), md.index("Explanation line 1"))

    def test_monospace_runs_merge_and_fence_is_safe(self):
        run1 = text("print(```")
        run1["textRun"]["textStyle"] = {"weightedFontFamily": {"fontFamily": "Courier New"}}
        run2 = text(")\n")
        _, _, md = self.archive(payload([
            paragraph(text("Question List")), paragraph(run1, run2),
        ]))
        self.assertIn("````\nprint(```)\n````", md)

    def test_archive_permissions_private_and_empty_document_reviewed(self):
        result, manifest, _ = self.archive(payload())
        self.assertTrue(manifest["needs_review"])
        archive = Path(result["manifest_path"]).parent
        self.assertEqual(stat.S_IMODE(archive.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((archive / "images").stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(Path(result["manifest_path"]).stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(Path(result["markdown_path"]).stat().st_mode), 0o600)
        result, _, _ = self.archive(payload([paragraph(image())]))
        image_file = next(Path(result["manifest_path"]).parent.rglob("*.png"))
        self.assertEqual(stat.S_IMODE(image_file.stat().st_mode), 0o600)

    def test_occurrences_preserved_files_deduplicated_and_no_uri_saved(self):
        data = payload([paragraph(text("Question List")), paragraph(image(), image())])
        _, manifest, md = self.archive(data)
        self.assertEqual(len(manifest["images"]), 2)
        self.assertEqual(manifest["images"][0]["path"], manifest["images"][1]["path"])
        self.assertEqual(md.count("!["), 2)
        files = list(Path(self.directory.name).rglob("*.png"))
        self.assertEqual(len(files), 1)
        for path in Path(self.directory.name).rglob("*"):
            if path.suffix in (".json", ".md"):
                self.assertNotIn(URI, path.read_text())
                self.assertNotIn("TOKEN", path.read_text())
                self.assertNotIn("contentUri", path.read_text())

    def test_version_or_id_mismatch_rejected_before_writing(self):
        for field in ("version", "id", "missing_version"):
            with self.subTest(field=field):
                data = payload([paragraph(image())])
                if field == "version":
                    data["source_after"]["modifiedTime"] = "changed"
                elif field == "id":
                    data["metadata"]["file_id"] = "another_doc"
                else:
                    del data["source_before"]["modifiedTime"]
                with self.assertRaises(renderer.ArchiveError):
                    self.archive(data)
                self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_failed_images_visible_sanitized_and_refresh_signaled(self):
        def fail(uri):
            raise renderer.ImageDownloadError("http_403", needs_refresh=True)
        result, manifest, md = self.archive(payload([
            paragraph(text("Question List")), paragraph(image()),
        ]), fail)
        self.assertEqual(manifest["status"], "partial")
        self.assertTrue(result["needs_refresh"])
        self.assertIn("Image unavailable: http_403", md)
        self.assertNotIn("TOKEN", json.dumps(manifest) + md)

    def test_unexpected_fetch_error_cannot_leak_url(self):
        def fail(uri):
            raise RuntimeError(uri)
        _, manifest, md = self.archive(payload([paragraph(image())]), fail)
        self.assertNotIn("TOKEN", json.dumps(manifest) + md)
        self.assertIn("download_failed", md)

    def test_invalid_response_and_missing_object_not_silently_dropped(self):
        result, manifest, md = self.archive(payload([
            paragraph(text("Question List")), paragraph(image(), image("missing")),
        ]), lambda uri: (b"<html>not an image</html>", "image/png"))
        self.assertEqual(result["image_count"], 2)
        self.assertEqual(result["displayable_image_count"], 0)
        self.assertEqual(manifest["status"], "partial")
        self.assertIn("invalid_image", md)
        self.assertIn("missing_image_reference", md)

    def test_no_section_preserves_body_with_review_marker_and_safe_text(self):
        _, manifest, md = self.archive(payload([
            paragraph(text("![remote](https://evil.example/image.png)\n")),
            paragraph(image()),
        ]))
        self.assertTrue(manifest["needs_review"])
        self.assertEqual(manifest["status"], "needs_review")
        self.assertIn("Section boundaries need review", md)
        self.assertNotIn("![remote](https", md)
        self.assertEqual(md.count("!["), 1)

    def test_each_archive_is_immutable_snapshot(self):
        data = payload([paragraph(text("Question List")), paragraph(image())])
        first, _, _ = self.archive(data)
        original = Path(first["markdown_path"]).read_bytes()
        second, _, _ = self.archive(data)
        self.assertNotEqual(first["manifest_path"], second["manifest_path"])
        self.assertEqual(Path(first["markdown_path"]).read_bytes(), original)


class DownloadTests(unittest.TestCase):
    @staticmethod
    def response(data=PNG, mime="image/png"):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.headers.get_content_type.return_value = mime
        response.read.return_value = data
        return response

    def test_non_google_https_uri_rejected_without_network(self):
        for uri in ("http://lh3.googleusercontent.com/a", "https://evil.example/a",
                    "https://googleusercontent.com.evil.example/a",
                    "https://u:p@lh3.googleusercontent.com/a", "file:///etc/passwd"):
            with self.subTest(uri=uri), self.assertRaises(renderer.ImageDownloadError):
                renderer.download_image(uri)

    def test_response_size_mime_and_signature_checked(self):
        for data, mime, expected in (
                (b"<html>", "text/html", "invalid_content_type"),
                (b"<html>", "image/png", "invalid_image"),
                (PNG, "image/jpeg", "image_type_mismatch"),
                (PNG + b"x" * renderer.MAX_IMAGE_BYTES, "image/png", "image_too_large")):
            with self.subTest(expected=expected):
                opener = mock.Mock()
                opener.open.return_value = self.response(data, mime)
                with mock.patch.object(renderer.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaises(renderer.ImageDownloadError) as raised:
                        renderer.download_image(URI)
                    self.assertEqual(raised.exception.code, expected)

    def test_redirect_host_is_validated_before_follow(self):
        headers = Message()
        headers["Location"] = "https://evil.example/leak"
        opener = mock.Mock()
        opener.open.side_effect = urllib.error.HTTPError(URI, 302, "Found", headers, io.BytesIO())
        with mock.patch.object(renderer.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(renderer.ImageDownloadError) as raised:
                renderer.download_image(URI)
        self.assertEqual(raised.exception.code, "unapproved_image_host")
        self.assertEqual(opener.open.call_count, 1)

    def test_success_and_expired_authorized_uri(self):
        opener = mock.Mock()
        opener.open.return_value = self.response()
        with mock.patch.object(renderer.urllib.request, "build_opener", return_value=opener):
            self.assertEqual(renderer.download_image(URI), (PNG, "image/png"))
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 20)
        for status in (401, 403, 404):
            with self.subTest(status=status):
                opener.open.side_effect = urllib.error.HTTPError(URI, status, URI, Message(), io.BytesIO())
                with mock.patch.object(renderer.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaises(renderer.ImageDownloadError) as raised:
                        renderer.download_image(URI)
                self.assertEqual(str(raised.exception), f"http_{status}")
                self.assertTrue(raised.exception.needs_refresh)


if __name__ == "__main__":
    unittest.main()
