import flet as ft


async def main(page: ft.Page):
    page.title = "Infodengue"
    def switch_view(index):
        if index == 0:
            page.views.clear()
            page.views.append(view_sua_cidade())
        elif index == 1:
            page.views.clear()
            page.views.append(view_brasil())
        elif index == 2:
            page.views.clear()
            page.views.append(view_forecasts())
        page.update()

    def view_sua_cidade():
        return ft.View(
            controls=[
                ft.Text("Sua cidade", size=30),
                # Add more controls specific to "Sua cidade"
            ]
        )

    def view_brasil():
        return ft.View(
            controls=[
                ft.Text("Brasil", size=30),
                # Add more controls specific to "Brasil"
            ]
        )

    def view_forecasts():
        return ft.View(
            controls=[
                ft.Text("Forecasts", size=30),
                # Add more controls specific to "Forecasts"
            ]
        )

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME, label="Sua cidade"),
            ft.NavigationDestination(icon=ft.icons.PUBLIC, label="Brasil"),
            ft.NavigationDestination(icon=ft.icons.WB_SUNNY, label="Forecasts"),
        ],
        on_change=lambda e: switch_view(e.control.selected_index)
    )
    switch_view(0)  # Initialize with the first view
    page.update()

app = ft.app(
    target=main,
    export_asgi_app=True,
    assets_dir="assets",
    # upload_dir="data"
)


def run():
    ft.app(
        target=main,
        assets_dir="assets",
        upload_dir="data"
    )


if __name__ == "__main__":
    pass
    run()
