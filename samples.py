import os
import asyncio
import sys
import inspect

from IPython.display import display, Markdown, Javascript
import nest_asyncio
nest_asyncio.apply()


class SamplePipelines:
    EXAMPLES_DIR = r"Pipeline\examples"
    EXAMPLE_COLLECTION = {
         'basic': '01_basic_pipeline.py',
         'vars': '02_publishing_variables.py',
         'custom_objs': '03_object_registry.py',
         'api_call': '04_api_interaction.py',
         'queues': '05_queue_interaction.py',
         'dependency': '06_conditional_execution.py',
         'on_error': '07_on_error_handling.py',
         'before_after': '08_before_after_hooks.py',
         'step_timeout': '09_step_timeout.py',
         'global_timeout': '10_global_timeout_and_policy.py',
         'parallel': '11_parallel_execution.py',
         'mixed_async_sync': '12_mixed_async_sync.py',
         'save_and_load': '13_save_and_load.py',
         'yaml_pipeline': '14_yaml_pipeline.yaml',
         'json_pipeline': '15_json_pipeline.json',
         'decorators': '16_decorators_usage.py',
         'templates': '17_template_executor.py',
         'eventing': '18_staged_event_trigger.py',
         'trigger_chaining': '19_trigger_chaining.py',
         'visualize': '20_visualizer_demo.py',
         'fanout_replay': '21_event_fanout_replay.py',
    }

    def __init__(self, example: str):
        self.use(example)

    def _resolve_file_path(self) -> str:
        fname = self.EXAMPLE_COLLECTION.get(self.name)
        if not fname:
            raise ValueError(f"Example '{self.name}' not found in EXAMPLE_COLLECTION.")
        fpath = os.path.join(self.EXAMPLES_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Example file not found at {fpath}")
        return fpath

    def use(self, example: str):
        """Switch to a different example dynamically."""
        self.name = example
        self.file_path = self._resolve_file_path()
        self.code_type = os.path.splitext(self.file_path)[1]
        self._last_snippet = None
        return self

    @classmethod
    def list(cls):
        print("Available examples:")
        for key, fname in cls.EXAMPLE_COLLECTION.items():
            print(f"- {key}: {fname}")

    def show(self, as_text=False, snippet=False):
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        if snippet:
            lines = self._extract_snippet(lines)

        content = "".join(lines).strip()
        self._last_snippet = content
        block_type = "python" if self.code_type == ".py" else "yaml"
        markdown_block = f"```{block_type}\n{content}\n```"

        if as_text or "ipykernel" not in sys.modules:
            print(markdown_block)
        else:
            display(Markdown(markdown_block))
            display(Javascript(f"""
                navigator.clipboard.writeText({repr(content)});
                console.log("Code copied to clipboard!");
            """))

        return self

    def snippet(self, as_text=False, return_text=True):
        """Show and/or return only the steps section of the example."""
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        lines = self._extract_snippet(lines)
        content = "".join(lines).strip()
        self._last_snippet = content

        if not return_text:
            self.show(as_text=as_text, snippet=True)
            return self

        return content

    def _extract_snippet(self, lines):
        if self.code_type == ".py":
            in_steps, bracket_balance = False, 0
            snippet_lines = []
            for line in lines:
                if not in_steps and line.strip().startswith("steps"):
                    in_steps = True
                if in_steps:
                    snippet_lines.append(line)
                    bracket_balance += line.count("[") - line.count("]")
                    if bracket_balance == 0 and "]" in line:
                        break
            return snippet_lines
        elif self.code_type in [".yaml", ".yml", ".json"]:
            in_steps = False
            indent_level = None
            snippet_lines = []
            for line in lines:
                if not in_steps and line.strip().startswith("steps:"):
                    in_steps = True
                    indent_level = len(line) - len(line.lstrip())
                    snippet_lines.append(line)
                    continue
                if in_steps:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > indent_level or not line.strip():
                        snippet_lines.append(line)
                    else:
                        break
            return snippet_lines
        else:
            raise ValueError("Unsupported file type for snippet().")

    def copy(self):
        if not self._last_snippet:
            raise RuntimeError("Nothing to copy. Call show() or snippet() first.")
        if "ipykernel" in sys.modules:
            display(Javascript(f"""
                navigator.clipboard.writeText({repr(self._last_snippet)});
                console.log("Copied to clipboard!");
            """))
        else:
            print("[WARNING] Clipboard copy only supported in Jupyter.")

    def execute(self):
        async def _run():
            if self.code_type == ".py":
                sandbox_globals = {"__name__": "__main__"}
                sandbox_locals = {}
                with open(self.file_path, "r") as f:
                    code = f.read()
                exec(code, sandbox_globals, sandbox_locals)
            else:
                from my_pipeline.executor import PipelineExecutor
                executor = PipelineExecutor(name=self.name, steps=self.file_path)
                await executor.execute()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(_run())
        else:
            return asyncio.create_task(_run())
