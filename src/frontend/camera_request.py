import requests
import streamlit as st
from helper.script_loader import load_file

css_code = load_file("view/style/style.css")
toggle_camera = load_file("src/frontend/toggle_camera.js")

ai_icon = '<span class="material-symbols-rounded">psychology</span>'

def connect_camera():
    """Hiển thị 4 camera và thanh điều khiển ngay bên dưới camera grid.

    HTML/CSS/JavaScript của camera chạy trong st.iframe().
    Toggle Detector cũng nằm trong iframe để có giao diện pill giống mockup.
    """
    live_src = "http://localhost:8000/video"
    img_src = "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=900"

    html = f"""
    <!doctype html>
    <html lang="vi">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" rel="stylesheet">
        <style>
            {css_code}

            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow-x: hidden;
            }}

            .camera-shell {{
                width: 100%;
                padding: 0;
            }}

            .camera-grid {{
                height: 570px;
            }}

            /* Thanh control nằm ngay dưới grid, không còn khoảng trống lớn. */
            .camera-control-bar {{
                margin-top: 12px;
                min-height: 78px;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 14px;
                background: #ffffff;
                border: 1px solid #e4e9ee;
                border-radius: 20px;
                box-shadow: 0 6px 22px rgba(24, 33, 47, 0.055);
            }}

            .control-actions {{
                display: flex;
                align-items: center;
                gap: 10px;
                flex: 0 0 auto;
            }}

            .control-btn {{
                height: 46px;
                padding: 0 22px;
                border: 0;
                border-radius: 999px;
                font-family: inherit;
                font-size: 13px;
                font-weight: 700;
                cursor: pointer;
                transition: transform .15s ease, background .15s ease;
            }}

            .control-btn:active {{
                transform: scale(.98);
            }}

            .snapshot-btn {{
                background: #e9edef;
                color: #202832;
            }}

            .snapshot-btn:hover {{
                background: #dfe4e7;
            }}

            .record-btn {{
                background: #fff1f2;
                color: #d84c58;
            }}

            .record-btn.active {{
                background: #ffe2e5;
                color: #c93645;
            }}

            .control-divider {{
                width: 1px;
                height: 40px;
                background: #e2e7eb;
                margin: 0 4px;
            }}

            .detector-control {{
                margin-left: auto;
                display: flex;
                align-items: center;
                gap: 14px;
                min-width: 235px;
                justify-content: flex-end;
            }}

            .detector-copy {{
                text-align: right;
                line-height: 1.1;
            }}

            .detector-label {{
                color: #2dbb6d;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: .12em;
                text-transform: uppercase;
            }}

            .detector-state {{
                margin-top: 4px;
                color: #29323d;
                font-size: 12px;
                font-weight: 500;
            }}

            /* Toggle pill giống mockup: xanh khi bật, xám khi tắt. */
            .detector-switch {{
                position: relative;
                width: 62px;
                height: 34px;
                flex: 0 0 62px;
                border: 0;
                border-radius: 999px;
                padding: 0;
                background: #cfd6db;
                cursor: pointer;
                transition: background .2s ease;
                box-shadow: inset 0 0 0 1px rgba(0,0,0,.04);
            }}

            .detector-switch.on {{
                background: #2dbb6d;
            }}

            .detector-knob {{
                position: absolute;
                top: 4px;
                left: 4px;
                width: 26px;
                height: 26px;
                border-radius: 50%;
                background: #ffffff;
                box-shadow: 0 2px 7px rgba(24,33,47,.18);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #2dbb6d;
                font-size: 12px;
                transition: left .2s ease, color .2s ease;
            }}

            .detector-switch.on .detector-knob {{
                left: 32px;
            }}

            .detector-switch.off .detector-knob {{
                color: #87929b;
            }}

            .record-dot {{
                display: inline-block;
                width: 8px;
                height: 8px;
                margin-right: 6px;
                border-radius: 50%;
                background: currentColor;
                vertical-align: 1px;
            }}

            @media (max-width: 900px) {{
                .camera-grid {{ height: 500px; }}
                .camera-control-bar {{ flex-wrap: wrap; }}
                .detector-control {{ margin-left: 0; width: 100%; justify-content: flex-start; }}
                .detector-copy {{ text-align: left; }}
            }}
        </style>
    </head>
    <body>
        <div class="camera-shell">
            <div id="grid" class="camera-grid">
                <div class="camera-box">
                    <span class="camera-label">Camera Chính (Live)</span>
                    <div class="camera-toolbar">
                        <button class="camera-btn" onclick="toggleCamera(this)">⛶</button>
                    </div>
                    <img src="{live_src}" onclick="selectCamera(this.closest('.camera-box'))" alt="Camera chính">
                </div>

                <div class="camera-box">
                    <span class="camera-label">Camera Phụ 1</span>
                    <div class="camera-toolbar">
                        <button class="camera-btn" onclick="toggleCamera(this)">⛶</button>
                    </div>
                    <img src="{img_src}" onclick="selectCamera(this.closest('.camera-box'))" alt="Camera phụ 1">
                </div>

                <div class="camera-box">
                    <span class="camera-label">Camera Phụ 2</span>
                    <div class="camera-toolbar">
                        <button class="camera-btn" onclick="toggleCamera(this)">⛶</button>
                    </div>
                    <img src="{img_src}" onclick="selectCamera(this.closest('.camera-box'))" alt="Camera phụ 2">
                </div>

                <div class="camera-box">
                    <span class="camera-label">Camera Phụ 3</span>
                    <div class="camera-toolbar">
                        <button class="camera-btn" onclick="toggleCamera(this)">⛶</button>
                    </div>
                    <img src="{img_src}" onclick="selectCamera(this.closest('.camera-box'))" alt="Camera phụ 3">
                </div>
            </div>

            <div class="camera-control-bar">
                <div class="control-actions">
                    <button class="control-btn snapshot-btn" onclick="takeSnapshot()">▣&nbsp; Chụp ảnh</button>
                    <button id="recordButton" class="control-btn record-btn" onclick="toggleRecording()">
                        <span class="record-dot"></span> Ghi hình
                    </button>
                </div>

                <div class="control-divider"></div>

                <div class="detector-control">
                    <div class="detector-copy">
                        <div class="detector-label">TRÍ TUỆ NHÂN TẠO</div>
                        <div id="detectorState" class="detector-state">Đang hoạt động</div>
                    </div>

                    <button id="detectorSwitch" class="detector-switch on" onclick="toggleDetector()" aria-label="Bật tắt detector">
                        <span class="detector-knob"><span class="material-symbols-rounded">psychology</span></span>
                    </button>
                </div>
            </div>
        </div>

        <script>
            {toggle_camera}

            let recording = false;
            let detectorActive = true;

            async function post(url) {{
                try {{
                    const response = await fetch(url, {{ method: "POST" }});
                    if (!response.ok) throw new Error("Request failed");
                    return true;
                }} catch (error) {{
                    console.error(error);
                    return false;
                }}
            }}

            async function toggleRecording() {{
                const button = document.getElementById("recordButton");
                const next = !recording;
                const ok = await post(next ? "http://localhost:8000/start" : "http://localhost:8000/stop");
                if (!ok) return;

                recording = next;
                button.classList.toggle("active", recording);
                button.innerHTML = recording
                    ? '<span class="record-dot"></span> Dừng ghi'
                    : '<span class="record-dot"></span> Ghi hình';
            }}

            async function toggleDetector() {{
                const next = !detectorActive;
                const ok = await post(next ? "http://localhost:8000/model/start" : "http://localhost:8000/model/stop");
                if (!ok) return;

                detectorActive = next;
                const button = document.getElementById("detectorSwitch");
                const state = document.getElementById("detectorState");

                button.classList.toggle("on", detectorActive);
                button.classList.toggle("off", !detectorActive);
                button.querySelector(".detector-knob").innerHTML = detectorActive ? '{ai_icon}' : '{ai_icon}';
                state.textContent = detectorActive ? "Đang hoạt động" : "Đã tắt";
            }}

            function takeSnapshot() {{
                const camera = document.querySelector(".camera-box.selected img") || document.querySelector(".camera-box img");
                if (!camera) return;

                const canvas = document.createElement("canvas");
                canvas.width = camera.naturalWidth || camera.clientWidth;
                canvas.height = camera.naturalHeight || camera.clientHeight;
                const ctx = canvas.getContext("2d");

                try {{
                    ctx.drawImage(camera, 0, 0, canvas.width, canvas.height);
                    const link = document.createElement("a");
                    link.download = "eduwatch-snapshot.jpg";
                    link.href = canvas.toDataURL("image/jpeg", .92);
                    link.click();
                }} catch (error) {{
                    alert("Không thể chụp ảnh từ camera này.");
                }}
            }}
        </script>
    </body>
    </html>
    """

    st.iframe(html, height=690)


def start_camera():
    """Giữ lại API cũ để các page khác có thể dùng nếu cần."""
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False

    st.session_state.camera_running = not st.session_state.camera_running

    if st.session_state.camera_running:
        requests.post("http://localhost:8000/start")
    else:
        requests.post("http://localhost:8000/stop")


def activate_camera(model_active):
    """Giữ lại API cũ cho code cũ; detector hiện dùng toggle trong iframe."""
    st.session_state.last_model_state = model_active

    if model_active:
        requests.post("http://localhost:8000/model/start")
    else:
        requests.post("http://localhost:8000/model/stop")
