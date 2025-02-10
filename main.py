import flet as ft
import pandas as pd
from mosqlient import get_infodengue
import datetime
from geodata.wfs import InfodengueMaps
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
from flet.plotly_chart import PlotlyChart
from flet.matplotlib_chart import  MatplotlibChart


def view_sua_cidade(page: ft.Page):
    return ft.View(
        appbar=page.appbar,
        controls=[
            ft.Text("Sua cidade", size=30),
            page.navigation_bar
            # Add more controls specific to "Sua cidade"
        ],
        scroll=ft.ScrollMode.AUTO
    )


def view_state(page: ft.Page):
    # Initialize Infodengue and get Brasil map
    casos = get_infodengue(
        start_date='2022-12-30',
        end_date='2023-01-30',
        disease='dengue',
        uf=page.selected_state
    )
    casos = casos.groupby(['municipio_geocodigo','municipio_nome']).sum()
    map_geojson = page.infodengue_maps.get_feature(f"{page.selected_state}_distritos_CD2022")
    gdf = gpd.GeoDataFrame.from_features(map_geojson)
    gdf['CD_MUN'] = gdf['CD_MUN'].astype(int)
    mapa = pd.merge(gdf, casos.reset_index(), left_on='CD_MUN', right_on='municipio_geocodigo', how='left')
    fig, ax = plt.subplots()
    mapa.plot(ax=ax,column='casos', scheme='natural_breaks',legend=True, legend_kwds={'bbox_to_anchor': (1.31, 1)})
    ax.set_axis_off()
    # fig = px.choropleth(mapa, geojson=mapa.geometry, color='casos', locations=mapa.index, hover_name='municipio_nome')
    # fig.update_geos(fitbounds="locations", visible=False)
    # Create WebView to display the map
    map_view = MatplotlibChart(fig, expand=True)

    return ft.View(
        appbar=page.appbar,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("Mapa do Estado", size=30, weight=ft.FontWeight.BOLD),
                    map_view,
                ]),
                expand=True
            ),
            page.navigation_bar
        ],
    )


def view_forecasts(page: ft.Page):
    return ft.View(
        appbar=page.appbar,
        controls=[
            ft.Text("Forecasts", size=30),
            page.navigation_bar
            # Add more controls specific to "Forecasts"
        ],
        scroll=ft.ScrollMode.AUTO
    )

def start_map_server(page: ft.Page):
    # Initialize Infodengue and get Brasil map
    page.infodengue_maps = InfodengueMaps()



async def main(page: ft.Page):
    page.title = "Infodengue"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    
    # Create state dropdown
    state_dropdown = ft.Dropdown(
        width=100,
        options=[
            ft.dropdown.Option("RJ"),
            ft.dropdown.Option("SP"),
            ft.dropdown.Option("MG"),
            ft.dropdown.Option("ES"),
        ],
        value="RJ",
        on_change=lambda e: change_state(e.data),
    )
    
    def change_state(new_state):
        page.selected_state = new_state
        if len(page.views) > 0 and isinstance(page.views[-1], ft.View):
            switch_view(1)  # Refresh state view
    
    # Create the app bar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CORONAVIRUS_OUTLINED),
        leading_width=40,
        title=ft.Text("InfoDengue"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_GREY,
        actions=[
            state_dropdown,
            ft.IconButton(ft.Icons.SETTINGS),
            ft.IconButton(ft.Icons.HELP_OUTLINE),
        ],
    )
    
    # Initialize selected state
    page.selected_state = "RJ"
    start_map_server(page)
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
                view_state(page)
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
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="Seu Estado"),
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
