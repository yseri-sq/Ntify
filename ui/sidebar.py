import flet as ft


def create_sidebar(width=220, compact=False, on_navigate=None):
    items = [
        ("Home", ft.Icons.HOME),
        ("Search", ft.Icons.SEARCH),
        ("Like", ft.Icons.FAVORITE),
        ("Podcasts", ft.Icons.PODCASTS),
    ]

    menu_rows = []

    for title, icon_name in items:
        icon = ft.Icon(icon_name, size=28, color="#FFFFFF")

        if compact:
            item = ft.Container(
                content=icon,
                tooltip=title,
                alignment=ft.Alignment.CENTER,
                width=48,
                height=44,
                border_radius=8,
                ink=True,
                on_click=lambda e, name=title: (
                    on_navigate(name) if on_navigate else None
                ),
            )
        else:
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        icon,
                        ft.Text(title, size=15, color="#FFFFFF"),
                    ],
                    spacing=12,
                ),
                padding=10,
                border_radius=8,
                ink=True,
                on_click=lambda e, name=title: (
                    on_navigate(name) if on_navigate else None
                ),
            )

        menu_rows.append(item)

    return ft.Container(
        content=ft.Column(controls=menu_rows, spacing=8),
        width=width,
        border_radius=12,
        bgcolor="#181818",
        padding=8 if compact else 16,
        alignment=ft.Alignment.TOP_LEFT,
        animate=200,
    )
