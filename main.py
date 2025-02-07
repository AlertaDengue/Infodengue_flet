import flet as ft

def view_sua_cidade(page: ft.Page):
    return ft.View(
        controls=[
            ft.Text("Sua cidade", size=30),
            page.navigation_bar
            # Add more controls specific to "Sua cidade"
        ],
        scroll=ft.ScrollMode.AUTO
    )

def view_brasil(page: ft.Page):
    return ft.View(
        controls=[
            ft.Text("Brasil", size=30),
            page.navigation_bar
            # Add more controls specific to "Brasil"
        ],
        scroll=ft.ScrollMode.AUTO
    )

def view_forecasts(page: ft.Page):
    return ft.View(
        controls=[
            ft.Text("Forecasts", size=30),
            page.navigation_bar
            # Add more controls specific to "Forecasts"
        ],
        scroll=ft.ScrollMode.AUTO
    )

async def main(page: ft.Page):
    page.title = "Infodengue"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.YELLOW,
    )
    page.update()

    def switch_view(index):
        if index == 0:
            page.views.clear()
            page.views.append(
            view_sua_cidade(page)
            )
        elif index == 1:
            page.views.clear()
            page.views.append(
            view_brasil(page)
            )

        elif index == 2:
            page.views.clear()
            page.views.append(
            view_forecasts(page)
            )
        page.update()


    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Sua cidade"),
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="Brasil"),
            ft.NavigationBarDestination(icon=ft.Icons.WB_SUNNY, label="Forecasts"),
        ],
        on_change=lambda e: switch_view(e.control.selected_index)
    )
    switch_view(0)  # Initialize with the first view
    page.update()
#
# app = ft.app(
#     target=main,
#     export_asgi_app=True,
#     assets_dir="assets"
# )


def run():
    ft.app(
        target=main,
        assets_dir="assets",
    )


if __name__ == "__main__":
    run()
