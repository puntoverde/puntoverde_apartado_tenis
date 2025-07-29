import subprocess
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['WDM_LOG_LEVEL'] = '0'

import sys
import flet as ft
import FleetingViews as fleetingviews
from views.espacios_deportivos_view import EspacioDeportivoView # Here IndexView is imported from views/index_view.py
# from views.equipos_view import EquipoView # Here NextView is imported from views/next_view.py
# from views.apartado_equipos_view import ApartadoEquiposDetalleView # Here NextView is imported from views/next_view.py
# from views.login_view import LoginView # Here NextView is imported from views/next_view.py

def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

async def main(page: ft.Page):

    # p = subprocess.Popen("./src/plugin_impresora/ESC_POS_3.5.1_W64.exe")
    p = subprocess.Popen(resourse_path("plugin_impresora/ESC_POS_3.5.1_W64.exe"))

    page.title = "Apartado Canchas Tenis"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width=1300
    page.window.height=950  

    view_definitions = {
    "espacio_deportivo": {
        "bgcolor": ft.Colors.BLUE_GREY,
        "vertical_alignment": ft.MainAxisAlignment.CENTER,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "on_dismount":lambda ctx:fv.update_view("espacio_deportivo", {"controls":[]})
    },
    "equipos": {
        # "bgcolor": ft.Colors.AMBER_900,
        "bgcolor": "#113448",
        "vertical_alignment": ft.MainAxisAlignment.CENTER,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "on_dismount":lambda ctx:fv.update_view("equipos", {"controls":[]})
    },
    "apartado": {
        # "bgcolor": ft.Colors.CYAN,
        "bgcolor": "#14bf98",
        "vertical_alignment": ft.MainAxisAlignment.CENTER,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "on_dismount":lambda ctx:fv.update_view("apartado", {"controls":[]})
    },

    "login": {
        # "bgcolor": ft.Colors.GREEN_100,
        "bgcolor": ft.Colors.WHITE,
        "vertical_alignment": ft.MainAxisAlignment.CENTER,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "on_dismount":lambda ctx:fv.update_view("login", {"controls":[]})
    },
}
    

    fv = fleetingviews.create_views(view_definitions=view_definitions, page=page)

    fv.append("espacio_deportivo",EspacioDeportivoView(page=page,fv=fv))

    # fv.view_go("home")
   

ft.app(target=main)