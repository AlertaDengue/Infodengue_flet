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
from viz.charts import prepare_state_container, prepare_city_container


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


def view_main(page: ft.Page, statecnt, citycnt):
    return ft.View(
        route='/',
        controls=[
            page.appbar,
            citycnt,
            statecnt,
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
            # Add more controls specific to "Settings"
        ],
        scroll=ft.ScrollMode.AUTO
    )

async def start_map_server(page: ft.Page):
    """
    Start the Infodengue map server client class and get the Brasil map
    """

    page.infodengue_maps.get_state_geojson(page.selected_state)
    page.city_names = page.infodengue_maps.get_city_names()
    page.city_search.options = [ft.dropdown.Option(city) for city in page.city_names]
    page.city_search.value = page.city_names[0]
    page.is_loading = False
    page.pr.visible = False
    page.update()


async def main(page: ft.Page):
    page.title = "Infodengue"
    page.adaptive = True
    page.infodengue_maps = InfodengueMaps()
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    page.city_names = []
    page.pr = ft.ProgressBar(value=None, visible=True, height=5)  # Initialize progress bar
    page.add(page.pr)
    page.update()

    # Initialize selected state
    page.selected_state = "RJ"
    page.selected_city = "Rio de Janeiro"
    page.selected_disease = "Dengue"
    page.state_data_cache = {}
    page.city_data_cache = {}
    page.is_loading = True

    async def change_state(e):
        new_state = e.data.split(" - ")[0]
        if new_state != page.selected_state:
            page.pr.visible=True
            page.update()
            state_geojson = page.infodengue_maps.get_state_geojson(new_state)
            page.selected_state = new_state
            page.city_names = page.infodengue_maps.get_city_names()
            page.selected_city = page.city_names[0]
            fill_city_search(page)
            page.update()
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
                page.update()  # Refresh main view

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
                ft.IconButton(ft.Icons.DRAW, tooltip= "Refresh page", on_click=lambda _: page.update()),
                ft.IconButton(ft.Icons.HELP_OUTLINE),
            ],
            )
        return appbar


    page.appbar = create_appbar()
    page.update()

    def switch_view(route):
        # print(route, page.selected_state, page.selected_city)
        page.views.clear()
        page.update()
        page.views.append(
            ft.View(
                route='/',
                controls=[
                    page.appbar,
                    prepare_city_container(page),
                    prepare_state_container(page),
                    # page.navigation_bar
                    # Add more controls specific to "Infodengue"
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
        # if route == '/settings':  # Settings
        #     page.views.append(
        #         view_settings(page)
        #     )
        page.update()


    # page.navigation_bar = ft.NavigationBar(
    #     destinations=[
    #         ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Infodengue Report"),
    #         ft.NavigationBarDestination(icon=ft.Icons.PUBLIC, label="Configurações"),
    #     ],
    #     on_change=lambda e: switch_view('/' if e.control.selected_index==0 else '/settings')
    # )


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
