# main.py
import subprocess
import os
import threading
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, Box
from prompt_toolkit.formatted_text import ANSI


def get_installed_formulae():
    result = subprocess.run(["brew", "leaves"], capture_output=True, text=True)
    return result.stdout.strip().split("\n")


def get_formula_info(formula):
    result = subprocess.run(
        ["brew", "info", "--json=v2", formula],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        import json
        info = json.loads(result.stdout)
        desc = info["formulae"][0].get("desc", "No description available")
        return desc
    return "Error fetching info."


class BrewCleaner:
    def __init__(self):
        self.formulae = get_installed_formulae()
        self.selected = set()
        self.cursor = 0
        self.info_text = ""
        self.info_loading = False
        self.loading_formula = None
        self.scroll_offset = 0

        # UI widgets
        self.list_window = Window(content=FormattedTextControl(self._get_formatted_list), always_hide_cursor=True)
        self.info_window = Window(content=FormattedTextControl(lambda: self.info_text), height=3)
        self.status_bar = Window(content=FormattedTextControl("Press ↑/↓ to navigate, Space to select, Enter to uninstall, c-c to exit"), height=1, style="reverse")

        # Key bindings
        kb = KeyBindings()

        @kb.add("up")
        def _(event):
            self.cursor = (self.cursor - 1) % len(self.formulae)
            self._update_info()

        @kb.add("down")
        def _(event):
            self.cursor = (self.cursor + 1) % len(self.formulae)
            self._update_info()

        @kb.add("space")
        def _(event):
            current = self.formulae[self.cursor]
            if current in self.selected:
                self.selected.remove(current)
            else:
                self.selected.add(current)

        @kb.add("enter")
        def _(event):
            if self.selected:
                event.app.exit(result=list(self.selected))
            else:
                event.app.exit(result=[])

        @kb.add("c-c")
        def _(event):
            event.app.exit(result=[])

        self.application = Application(
            layout=Layout(
                HSplit(
                    [
                        Frame(self.list_window, title="Installed Formulae"),
                        Frame(self.info_window, title="Info"),
                        self.status_bar,
                    ]
                )
            ),
            key_bindings=kb,
            full_screen=True,
        )
        self._update_info()

    def _update_info(self):
        current = self.formulae[self.cursor]
        self.loading_formula = current
        self.info_text = f"{current}: Loading..."
        self.info_loading = True

        def _fetch_info():
            desc = get_formula_info(current)
            if self.loading_formula == current:
                self.info_text = f"{current}: {desc}"
                self.info_loading = False
                self.application.invalidate()

        threading.Thread(target=_fetch_info).start()

    def _get_formatted_list(self):
        lines = []
        if self.list_window.render_info:
            height = self.list_window.render_info.window_height
            if self.cursor < self.scroll_offset:
                self.scroll_offset = self.cursor
            if self.cursor >= self.scroll_offset + height:
                self.scroll_offset = self.cursor - height + 1

            visible_formulae = self.formulae[self.scroll_offset:self.scroll_offset + height]
            for idx, f in enumerate(visible_formulae):
                actual_idx = self.scroll_offset + idx
                prefix = "[x]" if f in self.selected else "[ ]"
                cursor = "👉" if actual_idx == self.cursor else "  "
                lines.append(f"{cursor} {prefix} {f}")
        else: # Before first render
            for idx, f in enumerate(self.formulae):
                prefix = "[x]" if f in self.selected else "[ ]"
                cursor = "👉" if idx == self.cursor else "  "
                lines.append(f"{cursor} {prefix} {f}")

        return ANSI("\n".join(lines))

    def run(self):
        result = self.application.run()
        if result:
            print("Uninstalling:", ", ".join(result))
            subprocess.run(["brew", "uninstall", *result])
        else:
            print("No formulae selected.")


def main():
    if not os.isatty(0):
        print("This script requires an interactive terminal.")
    else:
        BrewCleaner().run()

if __name__ == "__main__":
    main()