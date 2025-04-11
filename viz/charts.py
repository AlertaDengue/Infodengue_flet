import flet as ft
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from flet.matplotlib_chart import MatplotlibChart
from flet.plotly_chart import PlotlyChart
from mosqlient import get_infodengue
from datetime import date

def _create_container(page, text=""):
    """
    Create a container for state selection and map display.
    """
    cnt = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(f"{text}"),
            ]
        ),
        border=ft.border.all(1, "blue"),
        padding=20,
        border_radius=10,
        expand=True,
        tooltip="Click to load data",
    )
    return cnt

def prepare_state_container(page):
    def get_state_data():
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
        page.state_data_cache[page.selected_state] = mapa
        return mapa
    def get_state_case_map(e):
        """
        Get the state case map and display it in the container.
        :param e:
        :return:
        """
        print("loading")
        cnt.content.controls.append(pbar)
        page.update()
        # Check if data is cached
        if page.selected_state not in page.state_data_cache:
            mapa = get_state_data()
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
        cnt.content.controls.append(map_view)
        dbutton.disabled = True
        pbar.visible = False
        page.update()
    cnt = _create_container(page, f"{page.selected_state}-{page.selected_city}-{page.selected_disease}")
    pbar = ft.ProgressBar(value=None, visible=True, width=300, height=20)
    dbutton = ft.ElevatedButton(
        text="Baixar dados",
        on_click=get_state_case_map,
        icon=ft.icons.DOWNLOAD_FOR_OFFLINE,
        tooltip="Baixa e plota os dados",
    )
    cnt.content.controls.append(dbutton)
    return cnt

def prepare_city_container(page):
    def get_city_data():
        # Initialize Infodengue and get Brasil map
        casos = get_infodengue(
            start_date='2022-12-30',
            end_date=date.today().isoformat(),
            disease=page.selected_disease.lower(),
            uf=page.selected_state,
            geocode=page.infodengue_maps.cities[page.selected_city],
        )
        return casos

    def get_case_plot(e):
        """
        Get the plot of cases for the selected city and selected disease
        """
        cnt.content.controls.append(pbar)
        page.update()
        if page.selected_city not in page.city_data_cache:
            casos = get_city_data()
            page.city_data_cache[page.selected_city] = casos
        else:
            casos = page.city_data_cache[page.selected_city]

        fig = px.line(casos.reset_index(), x='data_iniSE', y='casos_est',
                      title=f"Casos de {page.selected_disease} em {page.selected_city}")
        case_plot = PlotlyChart(fig, expand=True, isolated=True)
        cnt.content.controls.append(case_plot)
        pbar.visible = False
        dbutton.disabled = True
        page.update()
    cnt = _create_container(page, f"{page.selected_city}-{page.selected_disease}")
    pbar = ft.ProgressBar(value=None, visible=True, width=300, height=10)
    dbutton = ft.ElevatedButton(
        text="Baixar dados",
        on_click=get_case_plot,
        icon=ft.icons.DOWNLOAD_FOR_OFFLINE,
        tooltip="Baixa e plota os dados",
    )
    cnt.content.controls.append(dbutton)

    return cnt