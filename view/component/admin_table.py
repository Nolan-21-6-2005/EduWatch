import json
from pathlib import Path
import streamlit.components.v1 as components


_COMPONENT_DIR = Path(__file__).resolve().parent
_JS = (_COMPONENT_DIR / "admin_table.js").read_text(encoding="utf-8")


MEDCARE_TABLE_CSS = r'''
* { box-sizing: border-box; }
html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: #18212f;
}
body { overflow-x: hidden; }

.eduwatch-table {
    width: 100%;
    background: #fff;
    border: 1px solid #e4e9ee;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 6px 22px rgba(24, 33, 47, .055);
}

.toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 2px 2px 12px;
    flex-wrap: wrap;
}
.toolbar-left, .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.search, .control {
    height: 40px;
    border: 1px solid #e2e8ee;
    outline: none;
    font: inherit;
    font-size: 13px;
    color: #465261;
    background: #f7f9fb;
}
.search {
    min-width: 270px;
    border-radius: 21px;
    padding: 0 15px;
}
.search::placeholder { color: #9aa4af; }
.search:focus {
    border-color: #a8d9ba;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(45, 187, 109, .08);
}
.control {
    border-radius: 10px;
    padding: 0 13px;
    cursor: pointer;
    background: #fff;
    font-weight: 600;
}
.control:hover { background: #f7f9fb; }
.primary {
    height: 40px;
    border: 1px solid #2dbb6d;
    border-radius: 10px;
    background: #2dbb6d;
    color: #fff;
    padding: 0 14px;
    font-weight: 650;
    cursor: pointer;
}
.primary:hover { background: #229a59; }

.table-wrap {
    overflow: auto;
    border: 1px solid #e7ecf1;
    border-radius: 13px;
    background: #fff;
}
table {
    width: 100%;
    min-width: 790px;
    border-collapse: separate;
    border-spacing: 0;
}
thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f7f9fb;
    color: #778391;
    font-size: 11px;
    font-weight: 750;
    text-align: left;
    padding: 13px 12px;
    border-bottom: 1px solid #e3e8ed;
    white-space: nowrap;
}
thead th[data-sort] { cursor: pointer; }
thead th[data-sort]:hover { color: #2dbb6d; }
tbody td {
    padding: 12px;
    background: #fff;
    border-bottom: 1px solid #edf0f3;
    font-size: 13px;
    color: #566273;
    vertical-align: middle;
}
tbody tr:hover td { background: #fbfcfd; }
tbody tr:last-child td { border-bottom: none; }
tbody td:first-child { color: #8994a1; font-weight: 600; }

.person {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 190px;
}
.avatar {
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    border-radius: 50%;
    object-fit: cover;
    background: #eef3f0;
    border: 1px solid #e3e9e5;
}
.person strong, td strong { color: #26303d; font-weight: 650; }
.muted {
    display: block;
    color: #97a1ad;
    font-size: 11px;
    font-weight: 400;
    margin-top: 2px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}
.badge::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}
.badge.active { color: #26945a; background: #eaf8ef; }
.badge.inactive { color: #8b96a2; background: #f1f4f6; }
.badge.admin { color: #3478f6; background: #edf4ff; }
.badge.teacher { color: #7c4edb; background: #f5f1ff; }
.badge.guard { color: #c98218; background: #fff5e6; }

.actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 5px;
}
.icon-btn {
    width: 32px;
    height: 32px;
    border: 1px solid #e5eaf0;
    border-radius: 50%;
    background: #fff;
    color: #687584;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: .15s ease;
}
.icon-btn:hover { background: #f5f8fa; color: #26303d; }
.icon-btn.danger:hover { background: #fff2f3; color: #d33f4c; border-color: #f0c9cd; }

.select {
    min-width: 105px;
    border: 1px solid #e4e9ee;
    border-radius: 18px;
    padding: 7px 10px;
    background: #fff;
    color: #566273;
    font: inherit;
    font-size: 12px;
    outline: none;
}
.select:focus { border-color: #a8d9ba; }

.notice {
    display: none;
    padding: 9px 12px;
    margin: 0 0 10px;
    border-radius: 9px;
    background: #edf9f1;
    color: #166534;
    font-size: 12px;
}
.empty { padding: 42px; text-align: center; color: #97a1ad; }

.footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 12px;
    padding: 0 3px 2px;
    color: #98a2ad;
    font-size: 11px;
}
.pagination { display: flex; align-items: center; gap: 5px; }
.page-btn {
    width: 30px;
    height: 30px;
    border: 1px solid #e5eaf0;
    border-radius: 50%;
    background: #fff;
    color: #7a8694;
    cursor: pointer;
}
.page-btn:hover { background: #f5f8fa; }
.page-btn.active { background: #3478f6; color: #fff; border-color: #3478f6; }

.modal-backdrop {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 50;
    background: rgba(24, 33, 47, .30);
    backdrop-filter: blur(3px);
}
.modal-backdrop.show { display: flex; }
.modal {
    width: min(420px, calc(100% - 30px));
    padding: 20px;
    background: #fff;
    border: 1px solid #e4e9ee;
    border-radius: 15px;
    box-shadow: 0 20px 60px rgba(24, 33, 47, .18);
}
.modal h3 { margin: 0 0 7px; color: #18212f; font-size: 18px; }
.modal p { margin: 0 0 15px; color: #7b8794; font-size: 13px; line-height: 1.55; }
.modal input {
    width: 100%;
    height: 42px;
    border: 1px solid #e0e6ec;
    border-radius: 10px;
    padding: 0 12px;
    outline: none;
}
.modal input:focus { border-color: #a8d9ba; box-shadow: 0 0 0 3px rgba(45,187,109,.08); }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }

@media(max-width: 900px) {
    .search { min-width: 220px; }
    .eduwatch-table { padding: 9px; }
}
'''


def _component_html(
    table_type: str,
    data: list[dict],
    *,
    api_base: str = "http://127.0.0.1:8000",
) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    js = _JS.replace("__TABLE_TYPE__", table_type).replace("__API_BASE__", api_base.rstrip("/"))
    return f"""
        <!doctype html>
        <html lang="vi">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0">
        <style>{MEDCARE_TABLE_CSS}</style>
        </head>
        <body>
        <div class="eduwatch-table" id="app"></div>
        <div class="modal-backdrop" id="modal">
          <div class="modal">
            <h3 id="modal-title">Xác nhận</h3>
            <p id="modal-text"></p>
            <input id="modal-input" type="password" placeholder="Mật khẩu mới" style="display:none">
            <div class="modal-actions">
              <button class="control" id="modal-cancel">Hủy</button>
              <button class="primary" id="modal-ok">Xác nhận</button>
            </div>
          </div>
        </div>
        <script>
        window.__EDUWATCH_DATA__ = {payload};
        </script>
        <script>{js}</script>
        </body>
        </html>
        """


def render_admin_table(
    table_type: str,
    data: list[dict],
    *,
    api_base: str = "http://127.0.0.1:8000",
    height: int = 720,
):
    components.html(
        _component_html(table_type, data, api_base=api_base),
        height=height,
        scrolling=False,
    )
