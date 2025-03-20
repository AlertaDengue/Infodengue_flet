import flet as ft
import pandas as pd
from mosqlient import get_infodengue
from typing import List, Optional
import datetime
from geodata.features import InfodengueMaps, STATES
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
    loading_view = ft.Column(
        controls=[
            ft.ProgressRing(),
            ft.Text("Carregando dados do estado...", size=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    if page.is_loading:
        return ft.View(
            appbar=page.appbar,
            controls=[
                ft.Container(
                    content=loading_view,
                    alignment=ft.alignment.center,
                    expand=True
                ),
                page.navigation_bar
            ],
        )

    # Check if data is cached
    if page.selected_state not in page.state_data_cache:
        page.is_loading = True
        page.update()
        
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
        
        # Cache the processed data
        page.state_data_cache[page.selected_state] = mapa
        page.is_loading = False
    else:
        mapa = page.state_data_cache[page.selected_state]

    fig, ax = plt.subplots()
    mapa.plot(ax=ax,
              column='casos',
              scheme='natural_breaks',
              legend=True,
              )
    ax.set_axis_off()
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
    """
    Start the Infodengue map server client class and get the Brasil map
    """
    page.infodengue_maps = InfodengueMaps()



async def main(page: ft.Page):
    page.title = "Infodengue"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    
    # Initialize cache and loading state
    page.state_data_cache = {}
    page.is_loading = False
    
    # Create state dropdown
    state_dropdown = ft.Dropdown(
        width=200,
        options=[ft.dropdown.Option(f"{state} - {name}") for state, name in STATES.items()],
        value="RJ - Rio de Janeiro",
        on_change=lambda e: change_state(e.data),
    )
    
    def change_state(new_state):
        if new_state != page.selected_state:
            page.selected_state = new_state
            city_search.load_cities_data(new_state)
            if len(page.views) > 0 and isinstance(page.views[-1], ft.View):
                switch_view(1)  # Refresh state view
    
    # Create city search autocomplete


    # Initialize city search
    city_search = CitySearch(page)

    await create_appbar(city_search, page, state_dropdown)

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


async def create_appbar(city_search, page, state_dropdown):
    # Create the app bar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CORONAVIRUS_OUTLINED),
        leading_width=40,
        title=ft.Text("InfoDengue"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_GREY,
        actions=[
            city_search,
            state_dropdown,
            ft.IconButton(ft.Icons.SETTINGS),
            ft.IconButton(ft.Icons.HELP_OUTLINE),
        ],
    )


class CitySearch(ft.TextField):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.search_field = ft.TextField(
            label="Buscar cidade...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.update_suggestions,
            width=300
        )
        self.suggestions = ft.ListView(
            spacing=10,
            padding=20,
            width=300,
            height=200,
            visible=False
        )
        self.cities_data = pd.DataFrame()

    def load_cities_data(self, state: str):
        """Load cities data for the selected state"""
        if state not in self.page.state_data_cache:
            return
        self.cities_data = self.page.state_data_cache[state][
            ['municipio_nome', 'municipio_geocodigo']].drop_duplicates()

    async def update_suggestions(self, e):
        query = self.search_field.value.lower()
        if len(query) > 2:
            matches = self.cities_data[
                self.cities_data['municipio_nome'].str.lower().str.contains(query)
            ].head(10)

            self.suggestions.controls = [
                ft.ListTile(
                    title=ft.Text(row['municipio_nome']),
                    on_click=lambda e, code=row['municipio_geocodigo']: self.select_city(e, code),
                )
                for _, row in matches.iterrows()
            ]
            self.suggestions.visible = True
        else:
            self.suggestions.visible = False
        await self.update_async()

    async def select_city(self, e, geocode: int):
        self.search_field.value = ""
        self.suggestions.visible = False
        await self.update_async()
        # TODO: Handle city selection
        print(f"Selected city geocode: {geocode}")

    def build(self):
        return ft.Column(
            [
                self.search_field,
                self.suggestions
            ]
        )

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
