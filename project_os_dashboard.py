from __future__ import annotations

from pathlib import Path

from project_os.views import render_dashboard


ROOT = Path(__file__).resolve().parent


def main() -> None:
    render_dashboard(ROOT)


if __name__ == "__main__":
    main()
