import flet as ft
from mosqlient import get_infodengue
import datetime
from geodata.wfs import InfodengueMaps
import geopandas as gpd
import plotly.express as px
from flet.plotly_chart import PlotlyChart


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
    info_dengue = InfodengueMaps()
    casos_por_estado = get_infodengue(
        start_date='2022-12-30',
        end_date='2023-01-30',
        disease='dengue',
        uf='RJ'
    )
    map_geojson = info_dengue.get_feature("RJ_distritos_2022")
    # gdf = gpd.GeoDataFrame.from_features(map_geojson)
    fig = px.choropleth(casos_por_estado, geojson=map_geojson, color='casos', locations='distrito')

    # Create WebView to display the map
    map_view = PlotlyChart(fig, height=500, width=500)

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
