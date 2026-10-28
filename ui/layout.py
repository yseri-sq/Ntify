import flet as ft


def create_layout(
    sidebar,
    resize_handle,
    page_content,
    player_bar,
    lyrics_panel,
    title_bar,
):
    content_area = ft.Container(
        content=page_content,
        expand=1,
        padding=0,
    )

    lyrics_panel.expand = None

    main_row = ft.Row(
        controls=[
            sidebar,
            resize_handle,
            content_area,
            lyrics_panel,
        ],
        expand=True,
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Column(
        controls=[
            title_bar,
            main_row,
            player_bar,
        ],
        expand=True,
        spacing=8,
    )
