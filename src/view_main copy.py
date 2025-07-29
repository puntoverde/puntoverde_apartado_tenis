import subprocess
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['WDM_LOG_LEVEL'] = '0'

import sys
import flet as ft
from flet_route import Routing,path
from views.espacios_deportivos_view import EspacioDeportivoView # Here IndexView is imported from views/index_view.py
from views.equipos_view import EquipoView # Here NextView is imported from views/next_view.py
from views.apartado_equipos_view import ApartadoEquiposDetalleView # Here NextView is imported from views/next_view.py
from views.login_view import LoginView # Here NextView is imported from views/next_view.py

def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

async def main(page: ft.Page):

    p = subprocess.Popen("./src/plugin_impresora/ESC_POS_3.5.1_W64.exe")
    # p = subprocess.Popen(resourse_path("plugin_impresora/ESC_POS_3.5.1_W64.exe"))

    page.title = "Apartado Canchas Tenis"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width=1300
    page.window.height=950  

    app_routes = [
        path(url="/",clear=True,view=EspacioDeportivoView), 
        path(url="/equipos/:id_espacio_deportivo", clear=True, view=EquipoView),
        path(url="/equipos/:id_equipo/apartado", clear=True, view=ApartadoEquiposDetalleView),
        path(url="/login", clear=True, view=LoginView),
    ]

    Routing(
        page=page, # Here you have to pass the page. Which will be found as a parameter in all your views
        app_routes=app_routes, # Here a list has to be passed in which we have defined app routing like app_routes
        not_found_view=EspacioDeportivoView
    )
    
    page.go(page.route)
   

ft.app(target=main,view=ft.AppView.FLET_APP_HIDDEN)