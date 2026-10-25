import flet as ft


def create_layout(
    sidebar,
    resize_handle,
    page_content,
    player_bar,
    lyrics_panel,
):
    main_row = ft.Row(
        controls=[
            sidebar,
            resize_handle,
            page_content,
            lyrics_panel,
        ],
        expand=True,
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Column(
        controls=[
            main_row,
            player_bar,
        ],
        expand=True,
        spacing=10,
    )
