import os
import shutil
import tempfile
from pathlib import Path

import pytest

from pokie.codegen.template import TemplateProcessor


class TestTemplateProcessor:
    def test_init_default(self):
        tp = TemplateProcessor()
        assert tp.template_paths == []

    def test_init_with_paths(self):
        tp = TemplateProcessor(template_paths=["/tmp/a", "/tmp/b"])
        assert tp.template_paths == ["/tmp/a", "/tmp/b"]

    def test_get_template_path_empty_list(self):
        tp = TemplateProcessor()
        result = tp.get_template_path("anything")
        assert result is None

    def test_get_template_path_not_found(self):
        tp = TemplateProcessor(template_paths=["/nonexistent/path"])
        result = tp.get_template_path("anything")
        assert result is None

    def test_get_template_path_found(self):
        tmpdir = tempfile.mkdtemp()
        try:
            subdir = os.path.join(tmpdir, "my_template")
            os.makedirs(subdir)
            tp = TemplateProcessor(template_paths=[tmpdir])
            result = tp.get_template_path("my_template")
            assert result is not None
            assert result.name == "my_template"
        finally:
            shutil.rmtree(tmpdir)

    def test_process_raises_for_nonexistent_source(self):
        tp = TemplateProcessor()
        with pytest.raises(ValueError, match="invalid source directory"):
            tp.process(Path("/nonexistent"), Path("/tmp/dest"), {})

    def test_process_raises_when_source_is_file(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            tp = TemplateProcessor()
            with pytest.raises(ValueError, match="is not a directory"):
                tp.process(Path(tmpfile.name), Path("/tmp/dest"), {})
        finally:
            os.unlink(tmpfile.name)

    def test_process_raises_when_dest_is_file(self):
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            tp = TemplateProcessor()
            with pytest.raises(ValueError, match="is not a directory"):
                tp.process(Path(tmpdir), Path(tmpfile.name), {})
        finally:
            shutil.rmtree(tmpdir)
            os.unlink(tmpfile.name)

    def test_read_tpl(self):
        tmpfile = tempfile.NamedTemporaryFile(mode="w", suffix=".tpl", delete=False)
        try:
            tmpfile.write("Hello {{name}}")
            tmpfile.close()
            tp = TemplateProcessor()
            content = tp.read_tpl(Path(tmpfile.name))
            assert content == "Hello {{name}}"
        finally:
            os.unlink(tmpfile.name)

    def test_process_creates_output(self):
        src_dir = tempfile.mkdtemp()
        dest_dir = tempfile.mkdtemp()
        try:
            # Create a template file
            tpl_file = os.path.join(src_dir, "output.txt.tpl")
            with open(tpl_file, "w") as f:
                f.write("Hello {{name}}!")

            tp = TemplateProcessor()
            tp.process(Path(src_dir), Path(dest_dir), {"{{name}}": "World"})

            output_file = os.path.join(dest_dir, "output.txt")
            assert os.path.exists(output_file)
            with open(output_file, "r") as f:
                assert f.read() == "Hello World!"
        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(dest_dir)
