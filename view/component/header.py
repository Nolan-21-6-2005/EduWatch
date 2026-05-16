from nicegui import ui


def show_header():
    with ui.row().classes(
        "w-full h-[76px] bg-white px-8 border-b border-gray-100 items-center justify-between"
    ):

        # ===== LEFT: SEARCH =====
        with ui.row().classes(
            "items-center bg-gray-100 rounded-2xl px-5 py-3 w-[420px] gap-3"
        ):
            ui.icon("search", size="20px").classes("text-gray-400")

            ui.input(
                placeholder="Tòa nhà, Phòng học..."
            ).props(
                "borderless dense"
            ).classes(
                "flex-1 text-sm bg-transparent"
            )

        # ===== CENTER: NAVIGATION =====
        with ui.row().classes(
            "gap-10 items-center"
        ):

            ui.label("Tổng quan").classes(
                """
                text-green-700 font-semibold text-base
                border-b-2 border-green-500 pb-2 cursor-pointer
                """
            )

            ui.label("Phân tích").classes(
                """
                text-gray-400 text-base
                hover:text-green-700 cursor-pointer
                transition
                """
            )

        # ===== RIGHT: ACTIONS =====
        with ui.row().classes(
            "gap-5 items-center"
        ):

            ui.button(
                icon="notifications"
            ).props("flat round").classes(
                "text-gray-500"
            )

            ui.button(
                icon="settings"
            ).props("flat round").classes(
                "text-gray-500"
            )
