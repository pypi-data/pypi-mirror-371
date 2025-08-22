import json
from unittest import mock

import pytest

from sphinx_bioschemas import BioschemasDirective


# Minimal docutils state mock
class DummyReporter:
    def error(self, message, line=None):
        return f"ERROR: {message}"


class DummyStateMachine:
    reporter = DummyReporter()


class DummyState:
    document = None


def make_directive(content=None, arguments=None, options=None):
    directive = BioschemasDirective(
        name="bioschemas",
        arguments=arguments or [],
        options=options or {},
        content=content or [],
        lineno=1,
        content_offset=0,
        block_text="",
        state=DummyState(),
        state_machine=DummyStateMachine(),
    )
    return directive


def test_embedded_yaml_content():
    yaml_content = [
        '"@context": https://schema.org/',
        '"@type": LearningResource',
        "name: Example",
    ]
    directive = make_directive(content=yaml_content, options={"format": "yaml"})
    result = directive.run()
    assert len(result) == 1
    html = result[0].astext()
    assert '<script type="application/ld+json">' in html
    data = json.loads(html.split(">", 1)[1].rsplit("<", 1)[0])
    assert data["@type"] == "LearningResource"
    assert data["name"] == "Example"


def test_embedded_json_content():
    json_content = [
        "{",
        '  "@context": "https://schema.org/",',
        '  "@type": "LearningResource",',
        '  "name": "Example"',
        "}",
    ]
    directive = make_directive(content=json_content, options={"format": "json"})
    result = directive.run()
    assert len(result) == 1
    html = result[0].astext()
    data = json.loads(html.split(">", 1)[1].rsplit("<", 1)[0])
    assert data["@type"] == "LearningResource"
    assert data["name"] == "Example"


def test_yaml_file(monkeypatch):
    file_content = (
        '"@context": https://schema.org/\n"@type": LearningResource\nname: Example\n'
    )
    with (
        mock.patch("os.path.isfile", return_value=True),
        mock.patch("builtins.open", mock.mock_open(read_data=file_content)),
    ):
        directive = make_directive(arguments=["bioschemas.yaml"])
        result = directive.run()
        assert len(result) == 1
        html = result[0].astext()
        data = json.loads(html.split(">", 1)[1].rsplit("<", 1)[0])
        assert data["@type"] == "LearningResource"
        assert data["name"] == "Example"


def test_missing_file():
    with mock.patch("os.path.isfile", return_value=False):
        directive = make_directive(arguments=["missing.yaml"])
        result = directive.run()
        assert "Bioschemas file not found" in result[0]


def test_unsupported_format():
    directive = make_directive(content=["foo: bar"], options={"format": "xml"})
    result = directive.run()
    assert "Unsupported format" in result[0]


def test_no_content_or_file():
    directive = make_directive()
    result = directive.run()
    assert "No schema content or file path provided" in result[0]
