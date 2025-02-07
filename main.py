import flet as ft
from geodata.wfs import Infodengue

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
    # Initialize Infodengue and get Brasil map
    info_dengue = Infodengue()
    brasil_map = info_dengue.get_feature("casos_dengue_brasil_mun")
    
    # Create WebView to display the map
    map_view = ft.WebView(
        url="http://info.dengue.mat.br/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=casos_dengue_brasil_mun&styles=&bbox=-73.9872354,-33.7683777,-34.7299934,5.24448639&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
        width=800,
        height=600,
    )

    return ft.View(
        controls=[
            ft.Text("Mapa do Brasil", size=30, weight=ft.FontWeight.BOLD),
            map_view,
            page.navigation_bar
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
