import flet as ft


async def main(page: ft.Page):
    page.title = "Infodengue"
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME, label="Sua cidade"),
            ft.NavigationDestination(icon=ft.icons.PUBLIC, label="Brasil"),
            ft.NavigationDestination(icon=ft.icons.WB_SUNNY, label="Forecasts"),
        ]
    )
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
