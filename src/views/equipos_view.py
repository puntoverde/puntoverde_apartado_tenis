import asyncio
import flet as ft
from flet_route import Params,Basket
from apartados_dao import ApartadoDao
import moment
import threading
from views.apartado_equipos_view import ApartadoEquiposDetalleView # Here NextView is imported from views/next_view.py
import views.espacios_deportivos_view

def EquipoView(page:ft.Page,fv,id):
    print("inicia Vista Equipos")

    # basket.id_espacio_deportivo=params.id_espacio_deportivo

    def navigateApartados(e):
        print("click datos... %s" %e)
        
        fv.view_go('apartado',history_debug=True,duration=400, mode="right")
        fv.append("apartado",ApartadoEquiposDetalleView(page=page,fv=fv,id=e,id_espacio=id))

    def navigateEspacio():
        
        fv.view_go('espacio_deportivo',history_debug=True,duration=400, mode="left")
        fv.append("espacio_deportivo",views.espacios_deportivos_view.EspacioDeportivoView(page=page,fv=fv))

    dlg_modal = ft.AlertDialog(
        modal=True,
        # title=ft.Text("Cargando..."),
        content= ft.Column(controls=[
ft.Container(content=ft.ProgressRing(stroke_width=10,color=ft.Colors.WHITE),width=250,height=250),
ft.Text("Espere ...",style=ft.TextStyle(size=35,color=ft.Colors.WHITE))
        ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER) ,
        elevation=0,
        bgcolor=ft.Colors.TRANSPARENT
        )

    page.open(dlg_modal)

    # equipos_=ApartadoDao.get_equipos_by_espacio_deportivo(params.id_espacio_deportivo)

    content_=ft.Container(
        expand=True,
        width=page.window.width,
        bgcolor=ft.Colors.GREY_200,
        border_radius=30,
        padding=20,
        # content=images
        content=ft.Text("")
    )
   
    def curtina(): 
        # equipos_=ApartadoDao.get_equipos_by_espacio_deportivo(params.id_espacio_deportivo)
        equipos_=ApartadoDao.get_equipos_by_espacio_deportivo(id)

        equipos_map=map(lambda i:
                            #    ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _: page.go("/equipos/%s/apartado" %i["cve_equipo"]),content=ft.Row([
                               ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _: navigateApartados(i["cve_equipo"]),content=ft.Row([
        ft.Image(src=i["ruta_app"],width=100,),
        ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                 controls=[
            ft.Text(i["nombre"],size=30),
            ft.Text(f"{i['duracion_prestamo']} minutos",style=ft.TextStyle(size=16)),
            ft.Container(border_radius=10,padding=ft.padding.only(top=2,bottom=2,left=5,right=5),bgcolor=ft.Colors.GREEN_200 if i["disponible"] is None else ft.Colors.AMBER_200,content= ft.Text("Disponible ahora",style=ft.TextStyle(size=18,weight=ft.FontWeight.W_400)) if i["disponible"] is None else ft.Text(f"Disponible hasta { moment.date(i["disponible"]).add(minute=5).format('hh:mm') }",style=ft.TextStyle(size=18,weight=ft.FontWeight.W_400)) ),
        ])
        ]),padding=5)),equipos_)

        page.bgcolor=ft.Colors.WHITE
        page.padding=20
        images = ft.Row(
        wrap=True,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.alignment.center,
        controls=equipos_map
        )

        content_.content=images
        content_.update()
        print("cierra dialog........")
        page.close(dlg_modal)

    threading.Thread(target=curtina).start()
    
    appbar_ = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK,icon_color="white",
                    icon_size=20,
                    # tooltip="Regresar",on_click=lambda _: page.go("/")),
                    tooltip="Regresar",on_click=lambda _: navigateEspacio()),
        leading_width=50,
        title=ft.Text("Apartado de equipos",style=ft.TextStyle(color=ft.Colors.WHITE)),
        center_title=False,
        bgcolor="#14bf98",        
    )

    def fnEventoWindows(e):
        content_.width=page.window.width
        page.update()

    page.window.on_event=fnEventoWindows


    # return ft.View(
    #     "/equipos/:id_espacio_deportivo",     
    #     controls=[appbar_,content_]
    # )

    return [appbar_,content_]