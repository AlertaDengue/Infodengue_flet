import re
import time
from datetime import date
from typing import List

import flet as ft
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from flet.matplotlib_chart import MatplotlibChart
from flet.plotly_chart import PlotlyChart
from mosqlient import get_infodengue

from geodata.features import InfodengueMaps, STATES


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
        page.city_search.controls = [ft.ListTile(title=m, on_click=select_city(page, m), data=m) for m in matches]
        city_code = page.infodengue_maps.cities[matches[0]]
        page.city_search.value = city_name
        page.selected_city = city_name
        page.update()


def select_city(page, e):
    page.selected_city = e
    page.go('/')


def view_loading(page: ft.Page):
    return ft.View(
        route="/loading",
        controls=[
            page.appbar,
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Carregando dados..."),
                        ft.ProgressBar(value=None, visible=True, width=300, height=20)
                    ]
                ),
                expand=True
            ),
            page.navigation_bar
        ]
    )


def view_main(page: ft.Page):
    state_progress = ft.ProgressBar(value=None, visible=False, height=5)
    city_progress = ft.ProgressBar(value=None, visible=False, height=5)

    return ft.View(
        route='/',
        controls=[
            page.appbar,
            ft.Container(
                border=ft.border.all(1, "blue"),
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Sua Cidade", size=30, weight=ft.FontWeight.BOLD),
                        city_progress,
                        get_case_plot(page, city_progress)
                    ]),
                expand=True
            ),
            ft.Container(
                border=ft.border.all(1, "blue"),
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Seu Estado", size=30, weight=ft.FontWeight.BOLD),
                        state_progress,
                        get_state_case_map(page, state_progress)

                    ]),
                expand=True
            ),
            page.navigation_bar
            # Add more controls specific to "Infodengue"
        ],
        scroll=ft.ScrollMode.AUTO
    )


def view_settings(page: ft.Page):
    return ft.View(
        route='/settings',
        controls=[
            page.appbar,
            ft.Text("Configurações", size=30),
            page.navigation_bar
            # Add more controls specific to "Sua cidade"
        ],
        scroll=ft.ScrollMode.AUTO
    )


def get_state_case_map(page, progress):
    # Check if data is cached
    if page.selected_state not in page.state_data_cache:
        progress.visible = True
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
              legend_kwds={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.05), 'ncol': 2},
              )
    ax.set_axis_off()
    fig.tight_layout()
    map_view = MatplotlibChart(fig, expand=True, transparent=True, isolated=True)
    progress.visible = False
    return map_view


def get_city_data(page):
    """
    Get the data for the selected city and selected disease
    """
    casos = get_infodengue(
        start_date='2022-12-30',
        end_date=date.today().isoformat(),
        disease=page.selected_disease.lower(),
        uf=page.selected_state,
        geocode=page.infodengue_maps.cities[page.selected_city],
    )
    return casos


def get_case_plot(page, progress):
    """
    Get the plot of cases for the selected city and selected disease
    """
    progress.visible = True
    casos = get_city_data(page)
    fig = px.line(casos.reset_index(), x='data_iniSE', y='casos_est',
                  title=f"Casos de {page.selected_disease} em {page.selected_city}")
    progress.visible = False
    return PlotlyChart(fig, expand=True, isolated=True)


def get_state_data(page):
    # Initialize Infodengue and get Brasil map
    casos = get_infodengue(
        start_date='2022-12-30',
        end_date=date.today().isoformat(),
        disease=page.selected_disease.lower(),
        uf=page.selected_state,
    )
    casos = casos.groupby(['municipio_geocodigo', 'municipio_nome']).sum()
    map_geojson = page.infodengue_maps.get_feature(f"{page.selected_state}_distritos_CD2022")
    page.city_names = page.infodengue_maps.get_city_names()
    gdf = gpd.GeoDataFrame.from_features(map_geojson)
    gdf['CD_MUN'] = gdf['CD_MUN'].astype(int)
    mapa = pd.merge(gdf, casos.reset_index(), left_on='CD_MUN', right_on='municipio_geocodigo', how='left')
    return mapa


async def start_map_server(page: ft.Page):
    """
    Start the Infodengue map server client class and get the Brasil map
    """

    page.infodengue_maps.get_state_geojson(page.selected_state)
    page.city_names = page.infodengue_maps.get_city_names()
    page.city_search.options = [ft.dropdown.Option(city) for city in page.city_names]
    page.city_search.value = page.city_names[0]
    page.is_loading = False
    page.go("/")


async def main(page: ft.Page):
    page.title = "Infodengue"
    page.adaptive = True
    page.infodengue_maps = InfodengueMaps()
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    page.city_names = []
    # page.pr = ft.ProgressBar(value=None, visible=True, height=5)  # Initialize progress bar
    # page.add(page.pr)
    # page.update()

    # Initialize selected state
    page.selected_state = "RJ"
    page.selected_city = "Rio de Janeiro"
    page.selected_disease = "Dengue"
    page.state_data_cache = {}
    page.is_loading = True

    async def change_state(e):
        new_state = e.data.split(" - ")[0]
        if new_state != page.selected_state:
            state_geojson = page.infodengue_maps.get_state_geojson(new_state)
            page.selected_state = new_state
            page.city_names = page.infodengue_maps.get_city_names()
            page.selected_city = page.city_names[0]
            fill_city_search(page)
            # if len(page.views) > 0 and isinstance(page.views[-1], ft.View):
            page.go('/')  # Refresh main view

    # Create state dropdown
    state_dropdown = ft.Dropdown(
        width=200,
        menu_height=200,
        dense=True,
        options=[ft.dropdown.Option(f"{state} - {name}") for state, name in STATES.items()],
        value="RJ - Rio de Janeiro",
        on_change=change_state,
    )

    def fill_city_search(page):
        page.city_search.options = [ft.dropdown.Option(city) for city in page.city_names]
        page.city_search.value = page.city_names[0]
        page.city_search.enable_filter = True
        page.update()

    # Initialize city search bar
    page.city_search = ft.Dropdown(
        width=200,
        dense=True,
        options=[],
        enable_filter=False,
        on_change=lambda e: select_city(page, e.data),
    )

    def change_disease(disease):
        if disease != page.selected_disease:
            page.selected_disease = disease
            if len(page.views) > 0 and isinstance(page.views[-1], ft.View):
                page.go('/')  # Refresh main view

    def create_appbar():
        disease_dropdown = ft.Dropdown(
            width=200,
            dense=True,
            options=[ft.dropdown.Option(disease) for disease in ["Dengue", "Zika", "Chikungunya"]],
            value="Dengue",
            on_change=lambda e: change_disease(e.data),
        )
        # Create the app bar

        appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.CORONAVIRUS_OUTLINED),
            leading_width=40,
            title=ft.Text("InfoDengue"),
            center_title=False,
            bgcolor=ft.Colors.BLUE_GREY,
            actions=[
                state_dropdown,
                page.city_search,
                disease_dropdown,
                ft.IconButton(ft.Icons.SETTINGS),
                ft.IconButton(ft.Icons.HELP_OUTLINE),
            ],
            )
        return appbar


    page.appbar = create_appbar()
    page.update()

    def switch_view(route):
        print(route, page.selected_state, page.selected_city)
        page.views.clear()
        page.views.append(
            view_main(page)
        )
        if route == '/' and page.is_loading:
                page.go('/loading')

        elif route == '/settings':  # Settings
            page.views.append(
                view_settings(page)
            )
        elif route == '/loading':
            page.views.append(
                view_loading(page)
            )


        page.update()


    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Infodengue Report"),
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="Configurações"),
        ],
        on_change=lambda e: switch_view('/' if e.control.selected_index==0 else '/settings')
    )

    page.run_task(start_map_server, page)


    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


    # switch_view(0)
    page.on_route_change = switch_view
    page.on_view_pop = view_pop
    page.route = '/'
    page.go(page.route)  # Initialize with the first view


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
