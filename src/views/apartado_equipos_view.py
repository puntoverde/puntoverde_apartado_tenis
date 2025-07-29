from datetime import date, datetime, timedelta
import flet as ft
from flet_route import Params,Basket
from apartados_dao import ApartadoDao
import moment
from views.login_view import LoginView # Here NextView is imported from views/next_view.py
import views.equipos_view # Here NextView is imported from views/next_view.py
import threading

def ApartadoEquiposDetalleView(page:ft.Page,fv,id,id_espacio):
    print("inicia vista apartados")

    def fnAddEquipo(equipo_):
        fv.view_go('login',history_debug=True,duration=400, mode="right")
        fv.append("login",LoginView(page=page,fv=fv,equipo_=equipo_,id_espacio=id_espacio))
    
    def fnNavigateEquipo():
        fv.view_go('equipos',history_debug=True,duration=400, mode="left")
        fv.append("equipos",views.equipos_view.EquipoView(page=page,fv=fv,id=id_espacio))
        
        # basket.equipo=equipo_
        # page.go("/login")

    # id_espacio_deportivo=basket.id_espacio_deportivo

    # equipo_apartados=ApartadoDao.get_equipo_apartado(params.id_equipo)

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


    content_=ft.Container(
        expand=True,
        width=page.window.width,
        bgcolor=ft.Colors.GREY_200,
        border_radius=30,
        padding=20,
        content=ft.Text("")
    )


    def curtina(): 
        equipo_apartados=ApartadoDao.get_equipo_apartado(id)

        espacio_deportivos_map=map(lambda i:
                                   ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(content=ft.Row([
                                
            ft.Image(src=i["ruta_app"],width=100,),
            ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                     controls=[
                ft.Text(f"{i['nombre']}",size=30),
                ft.Text(i["duracion_prestamo"]),
                ft.Container(border_radius=10, padding=ft.padding.only(top=2,bottom=2,left=5,right=5),bgcolor=ft.Colors.AMBER_100,content=ft.Row([ft.Text(i["fecha_inicio"]),ft.Text(" a "),ft.Text(i["fecha_fin"])],alignment=ft.MainAxisAlignment.CENTER))           
            ])
        ]),padding=5)),equipo_apartados)

    
        page.bgcolor=ft.Colors.WHITE
        page.padding=20
        images = ft.Row(
            wrap=True,
            scroll=ft.ScrollMode.AUTO,
           alignment=ft.alignment.center,
           controls=espacio_deportivos_map
        )

        # esta libre tengo que llamara a el equipo
        if(len(equipo_apartados)==0):

            equipo_find=ApartadoDao.get_equipo_by_id(id)

            nombre=equipo_find["nombre"]
            tiempo_=equipo_find["duracion_prestamo"]
            fecha_inicio=datetime.now()+timedelta(minutes=5)
            fecha_fin=datetime.now()+timedelta(minutes=tiempo_)+timedelta(minutes=5)


            equipo_find["fecha_registro"]= datetime.now()
            equipo_find["fecha_inicio"]= fecha_inicio    
            equipo_find["fecha_fin"]= fecha_fin

            card_equipo=ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _:fnAddEquipo(equipo_find),content=ft.Row([
            ft.Image(src=equipo_find["ruta_app"],width=100,),
            ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                     controls=[
                ft.Text(nombre,size=30),
                ft.Text(tiempo_),
                ft.Container(border_radius=10, padding=ft.padding.only(top=2,bottom=2,left=5,right=5),bgcolor=ft.Colors.BLUE_100,content=ft.Row([ft.Text(fecha_inicio.strftime("%H:%M")),ft.Text(" a "),ft.Text(fecha_fin.strftime("%H:%M"))],alignment=ft.MainAxisAlignment.CENTER))
            ])
            ]),padding=5))

            images.controls.append(card_equipo)

        elif(len(equipo_apartados)==1):
            print("fecha del ultimo apartado")
            nombre=equipo_apartados[0]["nombre"]
            tiempo_=equipo_apartados[0]["duracion_prestamo"]
            fecha_inicio=datetime.strptime(f"{date.today()} {equipo_apartados[0]['fecha_fin']}", "%Y-%m-%d %H:%M:%S")+timedelta(minutes=5)
            fecha_fin=datetime.strptime(f"{date.today()} {equipo_apartados[0]['fecha_fin']}", "%Y-%m-%d %H:%M:%S")+timedelta(minutes=tiempo_)+timedelta(minutes=5)

            equipo_find=equipo_apartados[0]
            equipo_find["fecha_registro"]= datetime.now
            equipo_find["fecha_inicio"]= fecha_inicio 	    
            equipo_find["fecha_fin"]= fecha_fin

            card_equipo=ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _:fnAddEquipo(equipo_find),content=ft.Row([
            ft.Image(src=equipo_find["ruta_app"],width=100,),
            ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                     controls=[
                ft.Text(nombre,size=30),
                ft.Text(f"duracion prestamo {tiempo_}"),
                ft.Container(border_radius=10, padding=ft.padding.only(top=2,bottom=2,left=5,right=5),bgcolor=ft.Colors.BLUE_100,content=ft.Row([ft.Text(fecha_inicio.strftime("%H:%M")),ft.Text(" a "),ft.Text(fecha_fin.strftime("%H:%M"))],alignment=ft.MainAxisAlignment.CENTER))

            ])
            ]),padding=5))

            images.controls.append(card_equipo)
    
        elif(len(equipo_apartados)==2):
            print("fecha del ultimo apartado")
            nombre=equipo_apartados[1]["nombre"]
            tiempo_=equipo_apartados[1]["duracion_prestamo"]
            fecha_inicio=datetime.strptime(f"{date.today()} {equipo_apartados[1]['fecha_fin']}", "%Y-%m-%d %H:%M:%S")+timedelta(minutes=5)
            fecha_fin=datetime.strptime(f"{date.today()} {equipo_apartados[1]['fecha_fin']}", "%Y-%m-%d %H:%M:%S")+timedelta(minutes=tiempo_)+timedelta(minutes=5)

            equipo_find=equipo_apartados[1]
            equipo_find["fecha_registro"]= datetime.now
            equipo_find["fecha_inicio"]= fecha_inicio 	    
            equipo_find["fecha_fin"]= fecha_fin

            card_equipo=ft.Card(width=400,height=150,color=ft.Colors.WHITE,content=ft.Container(on_click=lambda _:fnAddEquipo(equipo_find),content=ft.Row([
            ft.Image(src=equipo_find["ruta_app"],width=100,),
            ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, 
                     controls=[
                ft.Text(nombre,size=30),
                ft.Text(f"duracion prestamo {tiempo_}"),
                ft.Container(border_radius=10, padding=ft.padding.only(top=2,bottom=2,left=5,right=5),bgcolor=ft.Colors.BLUE_100,content=ft.Row([ft.Text(fecha_inicio.strftime("%H:%M")),ft.Text(" a "),ft.Text(fecha_fin.strftime("%H:%M"))],alignment=ft.MainAxisAlignment.CENTER))

            ])
            ]),padding=5))

            images.controls.append(card_equipo)

        content_.content=images
        content_.update()
        print("cierra dialog........")
        page.close(dlg_modal)

    threading.Thread(target=curtina).start()

    # content_=ft.Container(
    #     expand=True,
    #     width=page.window.width,
    #     bgcolor=ft.Colors.GREY_200,
    #     border_radius=30,
    #     padding=20,
    #     content=images
    # )

    appbar_ = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK,icon_color="white",
                    icon_size=20,
                    # tooltip="Regresar",on_click=lambda _: page.go("/equipos/%s" %1)),
                    tooltip="Regresar",on_click=lambda _: fnNavigateEquipo()),
                    # tooltip="Regresar",on_click=lambda _: page.go("/equipos/%s" %id_espacio_deportivo)),
        leading_width=50,
        title=ft.Text("Apartado de equipos",style=ft.TextStyle(color=ft.Colors.WHITE)),
        center_title=False,
        bgcolor="#113448",
        actions=[],
    )


    def fnEventoWindows(e):
        content_.width=page.window.width
        page.update()

    page.window.on_event=fnEventoWindows

    # return ft.View(
    #     "/equipos/:id_equipo/apartado",
    #     controls=[appbar_,content_]
    # )
    # content_.update()
    # return ft.Column(controls=[ft.ElevatedButton(content=ft.Text("regresar"),on_click=lambda _: fv.go_back()),content_]) 
    return [appbar_,content_]