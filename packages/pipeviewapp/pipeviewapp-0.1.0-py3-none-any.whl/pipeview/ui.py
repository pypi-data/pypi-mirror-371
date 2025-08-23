# src/pipeview/ui.py
import sys
import os
import json
import csv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Static
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.binding import Binding

CACHE_FILE_PATH = os.path.join(os.path.expanduser("~"), ".pipeview_cache")

def parse_from_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f: raw_data = f.read()
    lines = raw_data.strip().splitlines()
    if not lines: return [], [], "empty"
    try:
        parsed = json.loads(raw_data);
        if isinstance(parsed, list): return parsed, list(parsed[0].keys()), "json"
    except (Exception): pass
    try:
        ld_data = [json.loads(line) for line in lines]
        if ld_data: return ld_data, sorted(list(set(k for i in ld_data for k in i.keys()))), "ldjson"
    except (Exception): pass
    try:
        reader = csv.DictReader(lines); csv_data = list(reader)
        if csv_data: return csv_data, list(reader.fieldnames), "csv"
    except (Exception): pass
    return [{"line": ln} for ln in lines], ["line"], "text"

class DetailScreen(ModalScreen):
    CSS = "#detail-view { align: center middle; width: 80%; height: 80%; background: $surface; border: thick $primary; padding: 1 2;}"
    def __init__(self, data: dict): super().__init__(); self.data = data
    def compose(self) -> ComposeResult:
        yield Vertical(Static(json.dumps(self.data, indent=2)), Static("\n[yellow]Press Esc to close"), id="detail-view")
    def on_key(self, event) -> None:
        if event.key == "escape": self.app.pop_screen()

class PipeViewApp(App):
    BINDINGS = [Binding("q,ctrl+c", "quit", "Quit", priority=True), Binding("f", "focus_filter", "Filter")]
    def __init__(self, data, headers, fmt): super().__init__(); self.master, self.headers, self.fmt = data, headers, fmt
    def compose(self) -> ComposeResult:
        yield Header(f"PipeView - {self.fmt.upper()}"); yield Input(placeholder="Filter..."); yield DataTable(cursor_type="row"); yield Footer()
    def on_mount(self) -> None:
        tbl = self.query_one(DataTable); tbl.add_columns(*self.headers); self.update_table(self.master); self.query_one(Input).focus()
    def update_table(self, data: list):
        tbl = self.query_one(DataTable); tbl.clear()
        for row in data: tbl.add_row(*[str(row.get(h, '')) for h in self.headers])
    def on_input_changed(self, msg: Input.Changed):
        q = msg.value.lower()
        if not q: self.update_table(self.master)
        else: self.update_table([r for r in self.master if any(q in str(v).lower() for v in r.values())])
    def on_data_table_row_selected(self, e):
        q = self.query_one(Input).value.lower()
        data = self.master if not q else [r for r in self.master if any(q in str(v).lower() for v in r.values())]
        if e.cursor_row < len(data): self.push_screen(DetailScreen(data[e.cursor_row]))
    def action_focus_filter(self): self.query_one(Input).focus()

def main():
    if not os.path.exists(CACHE_FILE_PATH):
        print(f"Error: Cache file not found.", file=sys.stderr)
        print("Run 'some-command | pipeview-cache' first to capture data.", file=sys.stderr)
        sys.exit(1)
    data, headers, fmt = parse_from_file(CACHE_FILE_PATH)
    if data:
        app = PipeViewApp(data, headers, fmt)
        app.run()
    else:
        print("Cache file is empty or could not be parsed.")

if __name__ == "__main__":
    main()