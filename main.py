from typing import List
import flet as ft
import pandas as pd
import re
from mosqlient import get_infodengue
from typing import List, Optional
import datetime
from geodata.features import InfodengueMaps, STATES
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
from flet.plotly_chart import PlotlyChart
from flet.matplotlib_chart import  MatplotlibChart


def find_substring_matches(query: str, strings: List[str], max_results: int = 10) -> List[str]:
    """Find strings that contain the query as a substring (case insensitive)"""
    if not query:
        return []

    # Create a regex pattern that matches the query anywhere in the string
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    # Find all matches and sort by position of match (earlier matches get higher priority)
    matches = sorted(
        (s for s in strings if pattern.search(s)),
        key=lambda s: pattern.search(s).start()
    )

    return matches[:max_results]

def find_city(page, city_name):
    matches = find_substring_matches(city_name, page.city_names)
    if matches:
        page.city_search.controls = [ft.ListTile(title=m, on_click=select_city(page,m), data=m) for m in matches]
        city_code = page.infodengue_maps.cities[matches[0]]
        page.city_search.value = city_name
        page.update()

def select_city(page, city_name):
    page.selected_city = city_name
    # page.city_search.close_view()
    page.update()
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
    # Check if data is cached
    if page.selected_state not in page.state_data_cache:

        mapa = get_state_data(page)

        # Cache the processed data
        page.state_data_cache[page.selected_state] = mapa

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


def get_state_data(page):
    # Initialize Infodengue and get Brasil map
    casos = get_infodengue(
        start_date='2022-12-30',
        end_date='2023-01-30',
        disease='dengue',
        uf=page.selected_state
    )
    casos = casos.groupby(['municipio_geocodigo', 'municipio_nome']).sum()
    map_geojson = page.infodengue_maps.get_feature(f"{page.selected_state}_distritos_CD2022")
    page.city_names = page.infodengue_maps.get_city_names()
    gdf = gpd.GeoDataFrame.from_features(map_geojson)
    gdf['CD_MUN'] = gdf['CD_MUN'].astype(int)
    mapa = pd.merge(gdf, casos.reset_index(), left_on='CD_MUN', right_on='municipio_geocodigo', how='left')
    return mapa


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
    page.infodengue_maps.get_state_geojson(page.selected_state)
    page.city_names = page.infodengue_maps.get_city_names()




async def main(page: ft.Page):
    page.title = "Infodengue"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    # page.pr = ft.ProgressRing(
    #     width=15,
    #     height=5,
    #     value=None,
    #
    #     color=ft.Colors.BLUE,
    # )
    # page.add(page.pr)
    page.update()

    # Initialize selected state
    page.selected_state = "RJ"
    page.state_data_cache = {}
    page.is_loading = True
    start_map_server(page)
    # page.pr.value=1.0
    page.update()
    
    # Create state dropdown
    state_dropdown = ft.Dropdown(
        width=200,
        options=[ft.dropdown.Option(f"{state} - {name}") for state, name in STATES.items()],
        value="RJ - Rio de Janeiro",
        on_change=lambda e: change_state(e.data),
    )
    
    def change_state(new_state):
        new_state = new_state.split(" - ")[0]
        if new_state != page.selected_state:
            state_geojson = page.infodengue_maps.get_state_geojson(new_state)
            page.selected_state = new_state
            page.city_names = page.infodengue_maps.get_city_names()
            if len(page.views) > 0 and isinstance(page.views[-1], ft.View):
                switch_view(1)  # Refresh state view
    

    def handle_tap(e):
        page.city_search.open_view()

    # Initialize city search bar
    page.city_search = ft.SearchBar(
        # label="Cidade",
        bar_hint_text="Digite o nome da cidade",
        # icon=ft.Icons.SEARCH,
        width=300,
        on_submit=lambda e: find_city(page, e.data),
        on_change=lambda e: find_city(page, e.data),
        on_tap = handle_tap,
        controls = [ft.ListTile(title=ft.Text(f"{city}"), on_click=lambda e: select_city(page, city) ) for city in page.city_names]
    )

    create_appbar(page, page.city_search, state_dropdown)



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
            ft.NavigationBarDestination(icon=ft.Icons.WB_SUNNY, label="Previsões"),
        ],
        on_change=lambda e: switch_view(e.control.selected_index)
    )
    switch_view(0)  # Initialize with the first view
    page.update()


def create_appbar(page, city_search, state_dropdown):
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
