import flet as ft
from flet_route import Params,Basket
from apartados_dao import ApartadoDao
from views.equipos_view import EquipoView # Here NextView is imported from views/next_view.py

def EspacioDeportivoView(page:ft.Page,fv):

    print("inicio vista espacios deportivos")

    def navigateEquipos(e):
        fv.view_go('equipos',history_debug=True,duration=400, mode="right")
        fv.set_working("equipos")
        fv.wadd(EquipoView(page=page,fv=fv,id=e))

 
    espacio_deportivos=ApartadoDao.get_espacio_deportivo()
    # espacio_deportivos_map=map(lambda i:ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _: page.go("/equipos/%s" %i["cve_espacio_deportivo"]),content=ft.Row([
    # espacio_deportivos_map=map(lambda i:ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _:fv.view_go('settings'),content=ft.Row([
    espacio_deportivos_map=map(lambda i:ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _:navigateEquipos(i["cve_espacio_deportivo"]),content=ft.Row([
        ft.Image(src=i["ruta_app"],width=100,),
        ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                 controls=[
            ft.Text(i["nombre"],size=30),            
            ft.Divider(),
            ft.Text(i["ubicacion"]),
        ])
    ]),padding=5),elevation=3),espacio_deportivos)

    page.bgcolor=ft.Colors.WHITE
    page.padding=20
    images = ft.Row(
        wrap=True,
        scroll=ft.ScrollMode.AUTO,
       alignment=ft.alignment.center,
       controls=espacio_deportivos_map
    )

    content_=ft.Container(
        expand=True,
        width=page.window.width,
        bgcolor=ft.Colors.GREY_300,
        border_radius=30,
        padding=20,
        content=images
    )
    
    def fnEventoWindows(e):
        content_.width=page.window.width
        page.update()

    page.window.on_event=fnEventoWindows

    return content_