"""A Sphinx extension for embedding Bioschemas markup in documentation."""

import datetime
import json
import logging
import os

import yaml
from docutils import nodes
from docutils.parsers import rst
from sphinx.application import Sphinx

logger = logging.getLogger("sphinx-bioschemas")
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

__version__ = "0.1.1"


def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return obj


class BioschemasDirective(rst.Directive):
    """Class of the Bioschemas."""

    has_content = False  # In the future we might allow to embed the content bit
    required_arguments = 0  # Make file path optional
    optional_arguments = 1  # File path is now optional
    has_content = True  # Allow embedded content

    option_spec = {
        "format": lambda arg: arg.lower(),  # e.g., "json" or "yaml"
    }

    def run(self) -> list[nodes.raw]:
        data = None
        # If content is provided, use it
        if self.content:
            fmt = self.options.get("format", "yaml")
            content_str = "\n".join(self.content)
            if fmt == "yaml":
                if yaml is None:
                    error = self.state_machine.reporter.error(
                        "pyyaml is required for YAML support.", line=self.lineno
                    )
                    return [error]
                data = yaml.safe_load(content_str)
                data = convert_dates(data)
            elif fmt == "json":
                data = json.loads(content_str)
            else:
                error = self.state_machine.reporter.error(
                    "Unsupported format. Use 'json' or 'yaml'.", line=self.lineno
                )
                return [error]
        elif self.arguments:
            file_path = self.arguments[0]
            if not os.path.isfile(file_path):
                error = self.state_machine.reporter.error(
                    f"Bioschemas file not found: {file_path}", line=self.lineno
                )
                return [error]
            _, ext = os.path.splitext(file_path)
            if ext.lower() in [".yaml", ".yml"]:
                if yaml is None:
                    error = self.state_machine.reporter.error(
                        "pyyaml is required for YAML support.", line=self.lineno
                    )
                    return [error]
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    data = convert_dates(data)
            elif ext.lower() in [".json", ".jsonld"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                error = self.state_machine.reporter.error(
                    "Unsupported file type. Use .json, .yaml, or .yml", line=self.lineno
                )
                return [error]
        else:
            error = self.state_machine.reporter.error(
                "No schema content or file path provided.", line=self.lineno
            )
            return [error]

        jsonld_str = json.dumps(data, indent=2)
        html = f'<script type="application/ld+json">\n{jsonld_str}\n</script>'
        return [nodes.raw("", html, format="html")]


def setup(app: Sphinx):
    """
    Setup function for the sphinx-bioschemas extension.
    """
    app.add_directive("bioschemas", BioschemasDirective)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
