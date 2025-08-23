"""
Formatting utilities for displaying memos in the terminal.

This module provides the MemoFormatter class, which is responsible for
formatting memos for display in the terminal using the Rich library.
It offers different formatting options:

- Panel format: Displays a memo in a bordered panel with icons
- Table format: Displays a memo as a table grid inside a panel

The formatter handles the visual presentation of memos, including styling,
layout, and the use of icons to represent different memo attributes.
This separation of formatting logic from the CLI commands helps maintain
a clean separation of concerns in the application.

testing
"""
import json
from pathlib import Path
from typing import Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from commit_memory import models
from commit_memory.security import decrypt


class MemoFormatter:
    def __init__(self, console: Console):
        self.console = console

    def _shared_meta(self, memo: models.Memo) -> Tuple[str, Optional[Path], str]:
        shared = memo.shared
        safe_title: str = "shared memo"
        safe_path_str: str = ""
        if shared is not None:
            if shared.title is not None and shared.title != "":
                safe_title = shared.title
            safe_path_str = shared.path or ""
        safe_path_obj = Path(safe_path_str) if safe_path_str else None
        return safe_title, safe_path_obj, safe_path_str

    def format_memo_panel(
        self, memo: models.Memo, title: str, border_style: str = "green"
    ) -> None:
        # Shared? try to decrypt; otherwise fall back to private rendering.
        if getattr(memo, "visibility", "private") == "shared":
            safe_title, p, path_str = self._shared_meta(memo)

            if not p or not p.exists():
                self.console.print(
                    Panel(
                        f"📦 Encrypted memo file not present: {path_str}\n"
                        f"Pull repo files/notes, "
                        f"or ask the author to share the bundle.",
                        title="📦 shared (missing file)",
                        border_style=border_style,
                        box=box.ROUNDED,
                    )
                )
                return

            try:
                obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                body = obj.get("body") or memo.memo
                author = obj.get("author") or memo.author
                created = obj.get("created") or (
                    memo.created.strftime("%Y-%m-%d %H:%M:%S")
                    if getattr(memo, "created", None)
                    else ""
                )
                mtitle = obj.get("title") or safe_title

                self.console.print(
                    Panel(
                        f"[cyan]🧠[/] {body}\n"
                        f"[bold]👤[/] {author}\n"
                        f"[bold]🕒[/] {created}\n"
                        f"[bold]🔓[/] shared",
                        title=f"🔓 [shared] {mtitle}  •  {title}",
                        border_style=border_style,
                        box=box.ROUNDED,
                    )
                )
                return
            except Exception:
                self.console.print(
                    Panel(
                        "You are not a recipient for this memo"
                        " or your private key is not available.\n"
                        "Ask the author to include your public "
                        "key in --to, or set AGE_KEY_FILE.",
                        title=f"🔒 [shared] {safe_title}  •  {title}",
                        border_style=border_style,
                        box=box.ROUNDED,
                    )
                )
                return

        self.console.print(
            Panel(
                f"[cyan]🧠[/] {memo.memo}\n"
                f"[bold]👤[/] {memo.author}\n"
                f"[bold]🕒[/] {memo.created:%Y-%m-%d %H:%M:%S}\n"
                f"[bold]🔒[/] {memo.visibility}",
                title=title,
                border_style=border_style,
                box=box.ROUNDED,
            )
        )

    def format_memo_table(self, memo: models.Memo, include_file: bool = False) -> Panel:
        """Format a memo as a table grid inside a panel"""
        tbl = Table.grid(expand=False)
        tbl.add_column(justify="right", style="bold bright_black")
        tbl.add_column()

        if include_file:
            tbl.add_row("📄 File-", f"{memo.file}:{memo.line}")
        tbl.add_row("🧠 Memo-", memo.memo)
        tbl.add_row("👤 Author-", memo.author)
        tbl.add_row("🕒 Created-", memo.created.strftime("%Y-%m-%d %H:%M:%S"))
        tbl.add_row("🔒 Visibility-", memo.visibility)

        return Panel(
            tbl, box=box.ROUNDED, border_style="green" if not include_file else "yellow"
        )

    def format_shared_panel(self, title, body, author, created, border_style="green"):
        self.console.print(
            Panel(
                f"[cyan]🧠[/] {body}\n[bold]👤[/] "
                f"{author}\n[bold]🕒[/] {created}\n[bold]🔓[/] shared",
                title=title,
                border_style=border_style,
                box=box.ROUNDED,
            )
        )

    def format_locked_shared_panel(self, title, hint, border_style="green", path=""):
        extra = f"\n[path] {path}" if path else ""
        self.console.print(
            Panel(hint + extra, title=title, border_style=border_style, box=box.ROUNDED)
        )
