import flet as ft


def create_title_bar(page: ft.Page):
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True

    def minimize(e):
        page.window.minimized = True

    def maximize(e):
        page.window.maximized = not page.window.maximized

    async def close(e):
        await page.window.close()

    def window_button(icon, tooltip, on_click, hover_color="#282828"):
        return ft.IconButton(
            icon=icon,
            icon_size=16,
            icon_color="#B3B3B3",
            tooltip=tooltip,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
                overlay_color=hover_color,
            ),
        )

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.WindowDragArea(
                    content=ft.Container(
                        content=ft.Text(
                            "Ntify",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        padding=ft.Padding.only(left=16),
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    expand=True,
                ),
                window_button(
                    ft.Icons.MINIMIZE,
                    "Свернуть",
                    minimize,
                ),
                window_button(
                    ft.Icons.CROP_SQUARE,
                    "Развернуть",
                    maximize,
                ),
                window_button(
                    ft.Icons.CLOSE,
                    "Закрыть",
                    close,
                    hover_color="#E81123",
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=40,
        bgcolor="#121212",
        padding=ft.Padding.only(left=4, right=6),
    )
