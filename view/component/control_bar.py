"""Camera actions embedded in the camera iframe."""


def render_camera_control_bar(role: int) -> str:
    """Only supervision gets the snapshot control; AI is a Streamlit control."""
    if role != 1:
        return ""

    icon_camera = (
        '<svg viewBox="0 0 24 24" width="22" height="22" '
        'fill="currentColor" aria-hidden="true">'
        '<path d="M9 3 7.2 5H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3.2L15 3H9zm3 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/>'
        '</svg>'
    )
    return f'''<div class="camera-control-bar">
      <div class="control-actions">
        <button class="control-btn snapshot-btn" onclick="takeSnapshot()" type="button">
          {icon_camera}<span>Chụp ảnh</span>
        </button>
      </div>
    </div>'''
