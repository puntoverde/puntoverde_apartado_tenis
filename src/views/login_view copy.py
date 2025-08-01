#nativos
from datetime import datetime, timedelta

import base64
import io
from io import BytesIO
import threading
import time
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['WDM_LOG_LEVEL'] = '0'
import sys

import moment



#librerias
import flet as ft #marco de material
from flet_route import Params,Basket
import cv2 #acceso a acamara
from PIL import Image as ImagePil #visualizar fotos
import numpy as np # es de mnumero
from playsound3 import playsound #el sonido en la aplicacion
from deepface import DeepFace #reconocimiento facial
from cvzone.FaceMeshModule import FaceMeshDetector#wrap de mediapipe
from apartados_dao import ApartadoDao #"gestion de bd 
import pydash #es como el lodash de javascript 
import requests

#busca el path en un build
def resourse_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

import jpype
import jpype.imports

# jpype.startJVM(classpath = ["C:\\java_huella\\dist\\prueba_puente_python.jar"])
jpype.startJVM(classpath = ["./src/jar_huella/prueba_puente_python.jar"])
# jpype.startJVM(classpath = [resourse_path("huella_/prueba_puente_python.jar")])
import java
import javax
from javax.swing import *
from java.awt import *
from java.io import *
from prueba_puente_python import DigitalPersona

# variable de guarda el estado de la camara
# cap=None
cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
# cap=cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
# para iniciar el video, en un while indica que tiene que estar ciclando los fotogramas
init_video=False
#id de socio
id_socio=0
# variable que gurada el rostro desde bd
rostro_socio=None
# inicia en 15 para que no duere mucho no es 0 porque es mod 0 ejemplo mod de 0 % 30 =0 esto tomaria la imagen enseguida
counter=15
# indica que se esta realizando la validacion por parde de deepface es para el tiempo que tarde y no volver a ejecutar otra vez
is_valid_face=False
# se basa es media pipe y es para tomar la distancia y saber que es un rostro humano
detector_cvzone=FaceMeshDetector(maxFaces=1)

# espara irmarcondo los paso en los que se encuentra al meomento de buscar 0=nada 1=ya esta laccion 2=esta clasificacion 3=posicion 4=buscar
step=0
# indica cuando es true que se buscara el socio es para que no se use step ara todo
flag_buscar=False

num_intentos_facial=0




#carga el play sound para dar gracias.
def gracias():
        playsound("./src/assets/sound/thank-you-168416.mp3",block=False)        
        # playsound(resourse_path("assets/sound/thank-you-168416.mp3"),block=False)

#es improvisado realizo una verificacion con los dos modelos que se utilizan para que antes que todo se descarguen los modelos
def init_model():
    print("incia carga de los modelos")

    # imagen1=cv2.imread(resourse_path("assets/images/img1.jpg"))
    imagen1=cv2.imread("./src/assets/images/img1.jpg")
    # imagen2=cv2.imread(resourse_path("assets/images/img2.jpg"))
    imagen2=cv2.imread("./src/assets/images/img2.jpg")
    init_model=DeepFace.verify(img1_path=imagen1,img2_path=imagen2,model_name="VGG-Face",detector_backend="mediapipe",threshold=.55)
    print(init_model["distance"])
    print(init_model["verified"])
    init_model2=DeepFace.verify(img1_path=imagen1,img2_path=imagen2,model_name="Facenet512",detector_backend="mediapipe",threshold=.33)
    print(init_model2["distance"])
    print(init_model2["verified"])

    print("fin carga modelos")

#realizo verificaciones de inicio para que cargue de forma forzosa los modelos y se pone fuera de LoginView para que solo se ejecuten uan vez
threading.Thread(target=init_model).start()


def LoginView(page:ft.Page,params:Params,basket:Basket):

    print("inicia vista login")

    # es una lista donde se guardaran temporalmente los socios
    lista_socios_validados=[]
    
    id_equipo=basket.equipo["cve_equipo"]
    nombre_equipo_=basket.equipo["nombre"]
    descripcion_equipo_=basket.equipo["descripcion"]
    tiempo_equipo_=basket.equipo["duracion_prestamo"]
    fecha_inicio_equipo_=basket.equipo["fecha_inicio"]
    fecha_fin_equipo_=basket.equipo["fecha_fin"]
    min_socios_equipo_=basket.equipo["min_socios"]
    nombre_text=""

    #propiedades de la ventana
    page.title = "Apartado Equipo Polideportivo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER  

    #bottonsheet componente 
    bs = ft.Ref[ft.BottomSheet]()

    #controles que acceden a cierto campo
    check_dobles=ft.Checkbox(label="Dobles",width=180,shape=ft.RoundedRectangleBorder(radius=2),visible=False)
    if(min_socios_equipo_>1):
        check_dobles.visible=True

    #inicia la camara 
    def init_camara():
        # global cap,init_video
        global init_video
        #se usa cv2.CAP_DSHOW por que la camara logitech lo necesitaba
        # cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        #se pone en fullHD---- esta linea se encuentra al inicio de este archivo porq se cambio a que la camara siempre este encendida
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        init_video=True
        #while para estar leyendo los fotogramas
        while init_video:
            fn_init_video()


    #proceso de pintar y mostrar la imagen con los cambios de distancia y ovalo etc
    def fn_init_video():       
        ret,frame=cap.read()#lee el fotograma 
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)#pone el fotograma a bgr para que se vea correctamente 
        frame=cv2.flip(frame,1)# se pone como espejo
        frame=frame[0:640,460:820]#recorta solo esl centro de la camara y que se vea como celular
        #ejemplo la camara toma 1280 x 720 y pasaremos un recorte de 640 x 360 -- 1280/2=640 ese es el centro y queremos 360 de ancho esto lo dividimos en 2 = 180
        #del punto central es 640-180=460 y 640+180=820 entonces el punto x es 460 a 820 y el punto y es 0 lo mas alto y llegar a 640 

        mask=np.zeros((640, 360),dtype=np.uint8) #se crea un aimagen en negro de la misma dimesion punto en y - x=640 360
        mask=cv2.ellipse(mask,(180,320),(150,200) ,0,0,360,(255),-1)#se crea un ellipse en la imagen de negro llamada mascara 
        mask2=cv2.bitwise_not(mask)##con bitwise solo se muestra el interior  del ovalo

        image_mask_ovalo=cv2.bitwise_and(frame,frame,mask=mask)  

        # fondo=cv2.imread(resourse_path("assets/images/wp.jpeg"))
        fondo=cv2.imread("./src/assets/images/wp.jpeg")
        fondo=fondo[0:640,460:820]
        # imagen que muestra fuera del ovalo y lo convina con fondo para que se vea como opacidad
        image_mask_ovalo_inverso=cv2.addWeighted(frame,0.9,fondo,0.1,0)        
        image_mask_ovalo_inverso=cv2.bitwise_and(image_mask_ovalo_inverso,image_mask_ovalo_inverso,mask=mask2)
        image_final_ovalo=cv2.add(image_mask_ovalo, image_mask_ovalo_inverso)
        
        #1 es que tiene foto y entra a validar
        visualizar(image_final_ovalo,frame)

    def visualizar(imagen_,image_origin):
        global counter,is_valid_face
        # busca un rostro con cvzone(mediapipe)
        _,faces_cv_zone=detector_cvzone.findFaceMesh(imagen_,draw=False)
        if faces_cv_zone:
            # el primer rostro encontrado
            face_=faces_cv_zone[0]
            # ojo izq
            pointLeft=face_[145]
            # ojo der
            pointRigth=face_[374]
            #punto de la nariz
            pointNose=face_[4] 
            # proceso para calcular la distanca y guardar en variale d
            w,_=detector_cvzone.findDistance(pointLeft,pointRigth)
            W=6.3
            f=840
            d=(W*f)/w
            cv2.circle(imagen_,pointNose,5,(250, 193, 19),cv2.FILLED)#dibuja circulo en la nariz
            #estas dos llineas dibujan la cruz en medio de la imagen como guia
            cv2.line(imagen_,(180,320),(180,380),(250, 193, 19),2)
            cv2.line(imagen_,(150,350),(210,350),(250, 193, 19),2)

            # valida la distancia entre un rango de 40 a 70 cm de distancia y que la nariz este en el punto central mayor a 150 y menor a 210 en x y mayor a 320 y menor a 380b en y
            if(d>35 and d<70 and pointNose[0]>150 and pointNose[0]<210 and pointNose[1]>320 and pointNose[1]<380):
                #se pinta un rectangulo en la orilla de color amarilllo para indicar que se esta leyendo el rostro
                imagen_=cv2.rectangle(imagen_,(0,0),(360,640),(250, 193, 19),30)
                #inicia con la captura cada 30 segundos y siepre no este ya en proceso una verificacion
                if counter % 30 == 0  and is_valid_face==False:
                    # ejecuta el hilo para verificar pasandole la imagen original
                    threading.Thread(target=match,kwargs={'frame':image_origin}).start()                    
                counter=counter+1
        #proceso para convertir la imagen a base64 y mostrarla 
        im =ImagePil.fromarray(imagen_)
        buffered = BytesIO()
        im.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        imagen_video.src_base64=img_str
        imagen_video.update() 
                

    def setTextInput(e):
        if(step==0):
            txt_accion.value="%s%s"%(txt_accion.value,e)
            txt_accion.update()        
        elif(step==2):
            txt_posicion.value="%s%s"%(txt_posicion.value,e)
            txt_posicion.update()
    def setTextInputClasificacion(e):
        if(step==1):
            txt_clasificacion.value=e
            txt_clasificacion.update()    

    def clear():
        global init_video,id_socio,is_valid_face,counter,step
        init_video=False#cancela con esto el while que muestra los fotogramas
        id_socio=0#se regresa el id de socio a 0
        is_valid_face=False#indica que no se esta en proceso de verificacion
        counter=20# se reinicia el contador a el origen 
        # se verifica que la camara no este encendida 
        # if cap is not None and cap.isOpened():
        #     cap.release()


        txt_accion.value=None
        txt_accion.border_color=ft.Colors.AMBER
        

        txt_clasificacion.value=None
        txt_clasificacion.border_color=None

        txt_posicion.value=None
        txt_posicion.border_color=None

        txt_nombre.value=""

        txt_accion.focus()
        step=0
        
        time.sleep(1)
        imagen_video.src_base64=None
        imagen_video.src=None
        imagen_video.src="images/capture_rostro.png"
        page.update()

    def init_facial():  
        global id_socio,rostro_socio        
        if(bs.current is not None):
            page.close(bs.current)
        image=ApartadoDao.get_foto(id_socio)
        if(image[0] is not None):
            print("if convierte rostro y abre camara ")
            image_ = ImagePil.open(io.BytesIO(image[0])).convert("RGB")
            rostro_socio = np.array(image_)
            init_camara()                
        else:             
            page.open(ft.SnackBar(ft.Text("Usuario no tiene aún foto registrada.",style=ft.TextStyle(size=50,color="#000000")),bgcolor="#F48430",width=350,duration=4000))                
            

    def init_fingerprint():
        global id_socio
        if(bs.current is not None):
            page.close(bs.current) 

        def createAndShowGUI():  

            num_intentos_=0

            def VerificacionHuella(e):
                
                nonlocal num_intentos_

                maximo_socios=min_socios_equipo_
                tiempo_apartado=tiempo_equipo_
                if(min_socios_equipo_>1 and check_dobles.value==True):
                    maximo_socios=maximo_socios*2
                    tiempo_apartado=tiempo_apartado+30
                       
                try:
                    if(e=="VerificandoStart"):
                        img = ImageIcon("./src/assets/images/fingerprint/finger_scan.png").getImage()
                        # img = ImageIcon(resourse_path("assets/images/fingerprint/finger_scan.png")).getImage() 
                        newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                        lblHuella.setIcon(ImageIcon(newimg))
                    elif(e=="VerificandoEnd"):
                        img = ImageIcon("./src/assets/images/fingerprint/finger.png").getImage()
                        # img = ImageIcon(resourse_path("assets/images/fingerprint/finger.png")).getImage()
                        newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                        lblHuella.setIcon(ImageIcon(newimg))
                    elif(e=="Verificar"):
                        verificado=digitalPersona.verificarHuella(huella_[0])                      
                        num_intentos_=num_intentos_+1                                
                        lblIntentos.setText(f"intento {num_intentos_} de 3")        
                        if(verificado):
                            
                            digitalPersona.stop()

                            img = ImageIcon("./src/assets/images/fingerprint/finger_check.png").getImage()
                            # img = ImageIcon(resourse_path("assets/images/fingerprint/finger_check.png")).getImage()
                            newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                            lblHuella.setIcon(ImageIcon(newimg))

                            # inicio del codigo para registro de prestamo...
                            if(maximo_socios>1):
                                lista_socios_validados.append(id_socio)
                                print(lista_socios_validados)
                                index=0
                                for i in lista_socios_validados:
                                    print(i)
                                    botton=group_account.controls[index]
                                    index+=1
                                    print(botton)
                                    botton.icon_color="green300"
                                    botton.update()                                
                                page.open(ft.SnackBar(ft.Text("Usuario Agregado",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor=ft.Colors.BLUE,width=350,duration=4000))                                             
                                
                    

                            # si solo es por socios se realiza el registro
                            if(maximo_socios==1):
                                print("registra un solo apartado")                 
                                ApartadoDao.registrar_apartado(id_socio,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)                                
                                audio=threading.Thread(target=gracias)
                                audio.start()
                                time.sleep(3)
                                print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                                clear()
                                page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))                              
                                page.go("/")

                            elif(maximo_socios==len(lista_socios_validados)):
                                print("Registra el apatrado ucuando se cumplan los minimo de socios")
                                print("registra un solo apartado")   
                                print(lista_socios_validados)             
                                print(id_equipo) 
                                print(tiempo_apartado) 
                                ApartadoDao.registrar_apartado_dos(lista_socios_validados,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)                                
                                audio=threading.Thread(target=gracias)
                                audio.start()
                                time.sleep(3)                                 
                                print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                                clear()                                
                                page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))                              
                                page.go("/")
                            else:
                                print("entra porq aun no se cumplen el total de socios...")
                                clear()

                            frame.dispose()
                        
                            
                        elif(num_intentos_==3):
                            digitalPersona.stop()
                            print("cierra por el numero de intentos y no registra nadaaa")
                            clear()
                            num_intentos_=0
                            frame.dispose()
                            page.open(ft.SnackBar(ft.Text("Tres intentos de validación fallidos",style=ft.TextStyle(size=60,color="#000000")),bgcolor="#FFB300",width=350,duration=3000))
                            
                        else:
                            img = ImageIcon("./src/assets/images/fingerprint/finger_error.png").getImage()
                            # img = ImageIcon(resourse_path("assets/images/fingerprint/finger_error.png")).getImage()
                            newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                            lblHuella.setIcon(ImageIcon(newimg))
                except java.lang.Exception as ex:
                    print("xxx")   
                    frame.dispose()   


            huella_=ApartadoDao.get_huella(id_socio)
            digitalPersona=DigitalPersona(VerificacionHuella)
            # al iniciar lo primero que tenemos que hacer es cerrar en caso de que se quedara abierto los listener del lector
            digitalPersona.stop()

            #funciones
            frame = JFrame("Varificacion")
            frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
            frame.setAlwaysOnTop(True)
            frame.setFocusableWindowState(True)

            img = ImageIcon("./src/assets/images/fingerprint/finger_scan.png").getImage()
            # img = ImageIcon(resourse_path("assets/images/fingerprint/finger_scan.png")).getImage()
            newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)

            frame.setLayout(None)
            lblHuella= JLabel()
            lblHuella.setBounds(10,20,230,310)
            lblHuella.setIcon(ImageIcon(newimg))
            frame.getContentPane().add(lblHuella)

            @jpype.JImplements(java.awt.event.ActionListener)
            class ActionPer:
                @jpype.JOverride
                def actionPerformed(self,evt):
                    try:                
                        digitalPersona.start()
                        digitalPersona.Iniciar()
                        boton1.setText("Iniciado")
                        boton1.setBackground(Color.GREEN)
                    except java.lang.Exception as ex:
                        print(ex)

            boton1= JButton("Iniciar")
            boton1.setBounds(20,350,100,30)
            frame.getContentPane().add(boton1)
            boton1.addActionListener(ActionPer())

            lblIntentos=JLabel("intento 0 de 3")
            lblIntentos.setBounds(130,350,100,30)
            frame.getContentPane().add(lblIntentos)

            frame.setBounds(10,10,266,450)
            frame.setResizable(False)
            frame.setVisible(True)
    

        # Start an event loop thread to handling gui events
        @jpype.JImplements(java.lang.Runnable)
        class Launch:
            @jpype.JOverride
            def run(self):
                createAndShowGUI()
        javax.swing.SwingUtilities.invokeLater(Launch())
        

    def enter_btn(_):
        global step,flag_buscar     
        if(step==0 and len(txt_accion.value)>0):
            txt_accion.border_color=None
            txt_accion.update()

            if(int(txt_accion.value)<=150):
                txt_clasificacion.border_color=ft.Colors.AMBER
                txt_clasificacion.update()
                txt_clasificacion.focus()
                step=1
            else:
                txt_posicion.border_color=ft.Colors.AMBER
                txt_posicion.update()
                txt_posicion.focus()
                step=2
            print("enter")
        elif(step==1 and len(txt_clasificacion.value)>0):
            txt_clasificacion.border_color=None
            txt_clasificacion.update()

            txt_posicion.border_color=ft.Colors.AMBER
            txt_posicion.update()
            txt_posicion.focus()
            step=2
            print("enter")
        elif(step==2 and len(txt_posicion.value)>0):
            txt_posicion.border_color=None
            txt_posicion.update()

            txt_accion.border_color=ft.Colors.AMBER
            txt_accion.update()
            txt_accion.focus()
            step=0
            flag_buscar=True
            buscar(0)
            print("enter")
        
    def buscar(_):
        global id_socio,rostro_socio,init_video
        nonlocal nombre_text
        # nonlocal lista_socios_validados
        print("entra a buscar")

        if(flag_buscar==False):
            page.open(ft.SnackBar(ft.Text("Debe estar completa el numero de accion y posicion",style=ft.TextStyle(size=50,color="#000000")),bgcolor="#FFB300",width=350,duration=4000))              
            return      

        clasificacion_=0
        if(txt_clasificacion.value=='A'): clasificacion_=1
        elif(txt_clasificacion.value=='B'): clasificacion_=2
        elif(txt_clasificacion.value=='C'): clasificacion_=3

        data=ApartadoDao.get_socio(txt_accion.value,clasificacion_,txt_posicion.value)
        print(data)
        if data is not None:
            id_socio=data["cve_socio"]

            exist_tem=pydash.some(lista_socios_validados,lambda i: i == id_socio)
            

            valid_apartado=ApartadoDao.validad_apartado(id_socio)      
            terminal_permiso=ApartadoDao.get_socio_terminal(id_socio)           
            if(valid_apartado is not None and terminal_permiso==0):
                page.open(ft.SnackBar(ft.Text("Este usuario ya cuenta con un apartado",style=ft.TextStyle(size=50,color="#000000")),bgcolor="#F50057",width=350,duration=4000))
                return 
            
            if(exist_tem and terminal_permiso==0):
                page.open(ft.SnackBar(ft.Text("Este usuario ya esta en grupo para apartado",style=ft.TextStyle(size=50,color="#000000")),bgcolor="#FFB300",width=350,duration=4000))                
                return

            txt_nombre.value="%s %s %s" %(data["apellido_paterno"],data["apellido_materno"],data["nombre"])
            nombre_text=f"{data['apellido_paterno']} {data['apellido_materno']} {data['nombre']}"
            print(nombre_text)
            txt_nombre.update()

            if(data["is_huella"]==0 and data["is_foto"]==0):
                page.open(ft.SnackBar(ft.Text("Este usuario no cuenta con foto o huella registrada",style=ft.TextStyle(size=50,color="#000000")),bgcolor="#F50057",width=350,duration=4000))
            elif(data["is_huella"]==1 and data["is_foto"]==0):
                init_fingerprint()
            elif(data["is_huella"]==0 and data["is_foto"]==1):
                init_facial()
            else:            
                #bottonsheet componente 
                ft.BottomSheet(
                    ref=bs,
                    on_dismiss=lambda _:print("se cerro"),
                    dismissible=False,
                    content=ft.Container(
                        width=1300,
                        height=430,
                        padding=50,
                        content=ft.Column(
                            tight=True,
                            controls=[
                                ft.Row(controls=[                                    
                                    ft.Button(content=ft.Image(src="images/facial-recognition_6877256.png",width=260),style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),on_click=lambda _:init_facial()),                                    
                                    ft.Button(content=ft.Image(src="images/fingerprint-scan.png",width=260),style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),on_click=lambda _:init_fingerprint()),
                                ]),
                                ft.Row(controls=[
                                    ft.Text("1",size=40,width=260,text_align=ft.TextAlign.CENTER),
                                    ft.Text("2",size=40,width=260,text_align=ft.TextAlign.CENTER),
                                ]),
                                ft.Text("Elige como autenticarte! 1- rostro 2- huella",size=20),
                                ]
                                ),),)

                page.open(bs.current)

            
        else:
            page.open(ft.SnackBar(ft.Text("No existe usuario",style=ft.TextStyle(size=60,color="#000000")),bgcolor="#F50057",width=350,duration=4000))            

    def print_ticket_apartado(espacio,equipo,usuario,inicio,fin):
        print(inicio)
        now_=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        inicio_=inicio.strftime("%H:%M:%S")
        fin_=fin.strftime("%H:%M:%S")
        payload = {
            "serial": "",
            "nombreImpresora": "EPSON TM-T20ll",
            "operaciones": [
                            {"nombre": "EscribirTexto",
                            "argumentos": [
                            "CLUB PUNTO VERDE DE LEON S.A. de C.V.\n"+
                            f"{espacio} - {equipo} \n"+
                              "Apartada por:\n"+
                            f"{usuario}\n"+
                              "Fecha de Aparatado:\n"+
                            f"{now_}\n"+
                              "Hora Inicio:\n"+
                            f"{inicio_}\n"+
                              "Hora Fin:\n"+
                            f"{fin_}\n"
                            ]},
                            {
                            "nombre": "Corte",
                            "argumentos": [1]
                            }
                            ]
                    }
        data_response=requests.post("http://localhost:8000/imprimir",json=payload)
        print(data_response)   



    def match(frame):
        global init_video,is_valid_face,num_intentos_facial
        # nombre_text

                   

        # indeica que emepieza la validacion 
        is_valid_face=True
        image_scan_face.src="images/face-scan_info_32.png"
        image_scan_face.update()

        is_success, im_buf_arr = cv2.imencode(".jpg", cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY))
        byte_im = im_buf_arr.tobytes()

        print("inicia verificacion")
        print(counter)

        maximo_socios=min_socios_equipo_
        tiempo_apartado=tiempo_equipo_
        if(min_socios_equipo_>1 and check_dobles.value==True):
            maximo_socios=maximo_socios*2
            tiempo_apartado=tiempo_apartado+30



        # DeepFace.build_model("VGG-Face")
        DeepFace.build_model('VGG-Face')
        data=DeepFace.verify(img1_path=frame,img2_path=rostro_socio,model_name="VGG-Face",detector_backend="mediapipe",threshold=.50)
        print("VGG-Face: ")
        print(data["distance"])
        if data is not None and data["verified"]: 


            if(maximo_socios>1):
                lista_socios_validados.append(id_socio)
                print(lista_socios_validados)
                index=0
                for i in lista_socios_validados:
                    print(i)
                    botton=group_account.controls[index]
                    index+=1
                    print(botton)
                    botton.icon_color="green300"
                    botton.update()
                page.open(ft.SnackBar(ft.Text(f"Usuario Agregado",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor=ft.Colors.BLUE_ACCENT_200,width=350,duration=4000)) 
                    

            # si solo es por socios se realiza el registro
            if(maximo_socios==1):
                print("registra un solo apartado")                 
                ApartadoDao.registrar_apartado(id_socio,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)              
                audio=threading.Thread(target=gracias)
                audio.start()
                time.sleep(3)
                print(nombre_text)
                print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                clear()                
                page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))                
                page.go("/")
            elif(maximo_socios==len(lista_socios_validados)):
                print("Registra el apatrado ucuando se cumplan los minimo de socios")
                print("registra un solo apartado")   
                print(lista_socios_validados)             
                print(id_equipo) 
                print(tiempo_apartado) 
                ApartadoDao.registrar_apartado_dos(lista_socios_validados,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)               
                audio=threading.Thread(target=gracias)
                audio.start()
                time.sleep(3)
                print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                clear()
                page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))
                page.go("/")
            else:
                print("entra porq aun no se cumplen el total de socios...")
                clear()

        else: 
            data2=DeepFace.verify(img1_path=frame,img2_path=rostro_socio,model_name="Facenet512",detector_backend="mediapipe",threshold=.33)
            print("Facenet512: ")
            print(data2["distance"])
            if data2 is not None and data2["verified"]:
                

                if(maximo_socios>1):
                    lista_socios_validados.append(id_socio)
                    print(lista_socios_validados)
                    index=0
                    for i in lista_socios_validados:
                        print(i)
                        botton=group_account.controls[index]
                        index+=1
                        print(botton)
                        botton.icon_color="green300"
                        botton.update()
                    page.open(ft.SnackBar(ft.Text(f"Usuario Agregado",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor=ft.Colors.BLUE,width=350,duration=4000)) 
                    

                # si solo es por socios se realiza el registro
                if(maximo_socios==1):
                    print("registra un solo apartado")                 
                    ApartadoDao.registrar_apartado(id_socio,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)                  
                    audio=threading.Thread(target=gracias)
                    audio.start()
                    time.sleep(3)
                    print(nombre_text)
                    print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                    clear()
                    page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))                
                    page.go("/")
                elif(maximo_socios==len(lista_socios_validados)):
                    print("Registra el apatrado ucuando se cumplan los minimo de socios")
                    print("registra un solo apartado")   
                    print(lista_socios_validados)             
                    print(id_equipo) 
                    print(tiempo_apartado) 
                    ApartadoDao.registrar_apartado_dos(lista_socios_validados,id_equipo,tiempo_apartado,fecha_inicio_equipo_,fecha_fin_equipo_)                    
                    audio=threading.Thread(target=gracias)
                    audio.start()
                    time.sleep(3)
                    print_ticket_apartado(descripcion_equipo_,nombre_equipo_,nombre_text,fecha_inicio_equipo_,fecha_fin_equipo_)
                    clear()
                    page.open(ft.SnackBar(ft.Text("Registro apartado con exito",style=ft.TextStyle(size=60,color="#ffffff")),bgcolor="#00695C",width=350,duration=4000))                
                    page.go("/")
                else:
                    print("entra porq aun no se cumplen el total de socios...")
                    clear()

        print("finaliza verificacion")

        num_intentos_facial=num_intentos_facial+1
        text_intentos.value=f"intento {num_intentos_facial} de 3"
        text_intentos.update()
        # page.update()

        is_valid_face=False
        image_scan_face.src="images/face-scan_32.png"
        image_scan_face.update()

        #si ya es el intento tres ya termina 
        if(num_intentos_facial==3):
            num_intentos_facial=0
            clear()
            text_intentos.value=f"intento 0 de 3"
            text_intentos.update()
            page.open(ft.SnackBar(ft.Text("Tres intentos de validación fallidos",style=ft.TextStyle(size=60,color="#000000")),bgcolor="#FFB300",width=350,duration=3000))
            # init_video=False#cancela con esto el while que muestra los fotogramas
            # id_socio=0#se regresa el id de socio a 0
            # is_valid_face=False#indica que no se esta en proceso de verificacion
            # return  

 

    imagen_video=ft.Image(src="images/capture_rostro.png",width=360,height=640,border_radius=10)

    text_intentos= ft.Text(f"intento 0 de 3")
    image_scan_face=ft.Image(src="images/face-scan_32.png",width=32,height=32,border_radius=10)
    
    txt_accion=ft.TextField(border_color=ft.Colors.AMBER,hint_text="Numero Accion",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),autofocus=True,read_only=True)
    txt_clasificacion=ft.TextField(hint_text="Clasificacion",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),read_only=True)
    txt_posicion=ft.TextField(hint_text="Posicion",hint_style=ft.TextStyle(size=20),text_align="center",text_size=50,max_length=4,content_padding=ft.Padding(top=2,bottom=2,right=0,left=0),read_only=True)
    
    txt_nombre=ft.Text("nombre del usuario.",theme_style=ft.TextThemeStyle.TITLE_MEDIUM)
    btn_buscar=ft.ElevatedButton(content=ft.Icon(name=ft.Icons.CHECK,size=40,color=ft.Colors.WHITE),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.Colors.TEAL_ACCENT,color=ft.Colors.WHITE,width=90,height=90,on_click=enter_btn)
    
    text_fecha_fin=ft.Text(moment.date(fecha_fin_equipo_).format("hh:mm"),size=30)
    
    

    group_account=ft.Row([],alignment=ft.MainAxisAlignment.CENTER)

    if(min_socios_equipo_>1):
        # for i in lista_socios_validados:
        for i in range(min_socios_equipo_):
            group_account.controls.append(ft.IconButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_color="grey300",
                    icon_size=40,
                    tooltip=f"Pause record-{i}",
                ),)

    def fn_checkbox_changed(e):
        nonlocal fecha_fin_equipo_
        
        if(e.data=="true"):
            print("agrega array")
            # for i in lista_socios_validados:
            for i in range(min_socios_equipo_):
                group_account.controls.append(ft.IconButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        icon_color="grey300",
                        icon_size=40,
                        tooltip=f"Pause record-{i}",))
            fecha_fin_equipo_=(fecha_fin_equipo_+timedelta(minutes=30))
            text_fecha_fin.value=moment.date(fecha_fin_equipo_).format("hh:mm")
        else:
            print("elimina Array")
            for i in range(min_socios_equipo_):
                group_account.controls.pop()
            fecha_fin_equipo_=(fecha_fin_equipo_-timedelta(minutes=30))
            text_fecha_fin.value=moment.date(fecha_fin_equipo_).format("hh:mm")
        page.update()
        

    check_dobles.on_change=fn_checkbox_changed

    def on_keyboard(e: ft.KeyboardEvent):
        global step,flag_buscar
        print(e)
        print(bs.current)
        if((e.key =="Numpad 1" or e.key=="1") and bs.current is not None and bs.current.open):            
            init_facial()            
        elif((e.key =="Numpad 2" or e.key=="2") and bs.current is not None and bs.current.open):        
            init_fingerprint()
        elif(e.key =="Numpad 1" or e.key=="1"):
            print("text 1")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,1)
                txt_accion.update()
            elif(step==1):
                txt_clasificacion.value="A"
                txt_clasificacion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,1)
                txt_posicion.update()
        elif(e.key =="Numpad 2" or e.key=="2"):
            print("text 2")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,2)
                txt_accion.update()
            elif(step==1):
                txt_clasificacion.value="B"
                txt_clasificacion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,2)
                txt_posicion.update()
        elif(e.key =="Numpad 3" or e.key=="3"):
            print("text 3")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,3)
                txt_accion.update()
            elif(step==1):
                txt_clasificacion.value="C"
                txt_clasificacion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,3)
                txt_posicion.update()
        elif(e.key =="Numpad 4" or e.key=="4"):
            print("text 4")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,4)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,4)
                txt_posicion.update()
        elif(e.key =="Numpad 5" or e.key=="5"):
            print("text 5")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,5)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,5)
                txt_posicion.update()
        elif(e.key =="Numpad 6" or e.key=="6"):
            print("text 6")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,6)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,6)
                txt_posicion.update()
        elif(e.key =="Numpad 7" or e.key=="7"):
            print("text 7")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,7)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,7)
                txt_posicion.update()
        elif(e.key =="Numpad 8" or e.key=="8"):
            print("text 8")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,8)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,8)
                txt_posicion.update()
        elif(e.key =="Numpad 9" or e.key=="9"):
            print("text 9")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,9)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,9)
                txt_posicion.update()
        elif(e.key =="Numpad 0" or e.key=="0"):
            print("text 0")
            if(step==0):
                txt_accion.value="%s%s"%(txt_accion.value,0)
                txt_accion.update()
            elif(step==2):
                txt_posicion.value="%s%s"%(txt_posicion.value,0)
                txt_posicion.update()
        elif(e.key =="Enter"):

            if(step==0 and len(txt_accion.value)>0):
                txt_accion.border_color=None
                txt_accion.update()

                if(int(txt_accion.value)<=150):
                    txt_clasificacion.border_color=ft.Colors.AMBER
                    txt_clasificacion.update()
                    txt_clasificacion.focus()
                    step=1
                else:
                    txt_posicion.border_color=ft.Colors.AMBER
                    txt_posicion.update()
                    txt_posicion.focus()
                    step=2
                print("enter")
            elif(step==1 and len(txt_clasificacion.value)>0):
                txt_clasificacion.border_color=None
                txt_clasificacion.update()

                txt_posicion.border_color=ft.Colors.AMBER
                txt_posicion.update()
                txt_posicion.focus()
                step=2
                print("enter")
            elif(step==2 and len(txt_posicion.value)>0):
                txt_posicion.border_color=None
                txt_posicion.update()

                txt_accion.border_color=ft.Colors.AMBER
                txt_accion.update()
                txt_accion.focus()
                step=0
                flag_buscar=True
                buscar(0)
                print("enter")
            # else:
                
        elif(e.key=="Numpad Multiply"):
            clear()    

    page.on_keyboard_event=on_keyboard

    
    
    content_=ft.Row([ft.Container(content=ft.Card(content=ft.Column([
        check_dobles,       
        ft.Text(basket.equipo["descripcion"],size=40),
        ft.Image(src=basket.equipo["ruta_app"],width=330,fit=ft.ImageFit.COVER),        
        ft.Row([
        ft.Text(moment.date(fecha_inicio_equipo_).format("hh:mm"),size=30),
        ft.Text("a",size=20),
        text_fecha_fin,
        ],alignment=ft.MainAxisAlignment.CENTER),
        group_account
    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),color=ft.Colors.GREY_200),width=450,height=550),
    ft.Column(controls=[ 
               
        ft.Row([
            ft.Container(width=220,content=txt_accion),
            ft.Container(width=220,content=txt_clasificacion),
            ft.Container(width=220,content=txt_posicion),
        ],alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
                ft.Card(content=
                        ft.Container(content=
                    ft.Column(
                        [
                        ft.Card(content=ft.Container(content=imagen_video),color=ft.Colors.BLUE_GREY),
                        ft.Row([
                        text_intentos,
                        image_scan_face,
                        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN,width=360),
                        
                        
                        ]
                ),padding=5)),
            ft.Column([
                # mytime,
                ft.Container(width=300,height=60,bgcolor=ft.Colors.BLUE_GREY_100,content=txt_nombre,alignment=ft.alignment.center,border_radius=10,padding=5),
             
            ft.Row(
            controls=[
                ft.ElevatedButton(text="A",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=35)),bgcolor=ft.Colors.BLUE_100,color=ft.Colors.WHITE,on_click=lambda _:setTextInputClasificacion("A")),
                ft.ElevatedButton(text="B",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=35)),bgcolor=ft.Colors.BLUE_100,color=ft.Colors.WHITE,on_click=lambda _:setTextInputClasificacion("B")),
                ft.ElevatedButton(text="C",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=35)),bgcolor=ft.Colors.BLUE_100,color=ft.Colors.WHITE,on_click=lambda _:setTextInputClasificacion("C")),
            ]
        ),
            ft.Row(
            controls=[
                ft.ElevatedButton(text="7",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(7)),
                ft.ElevatedButton(text="8",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(8)),
                ft.ElevatedButton(text="9",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(9)),
            ]
        ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(text="4",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(4)),
                    ft.ElevatedButton(text="5",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(5)),
                    ft.ElevatedButton(text="6",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(6)),
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(text="1",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(1)),
                    ft.ElevatedButton(text="2",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(2)),
                    ft.ElevatedButton(text="3",style=ft.ButtonStyle(shape=ft.CircleBorder(),padding=35,text_style=ft.TextStyle(size=40)),on_click=lambda _:setTextInput(3)),                    
                ]
            ),
            ft.Row(
                 controls=[
                    ft.ElevatedButton(text="0",style=ft.ButtonStyle(shape=ft.CircleBorder(),text_style=ft.TextStyle(size=40)),width=90,height=90,on_click=lambda _:setTextInput(0)),
                    ft.ElevatedButton(content=ft.Icon(name=ft.Icons.CLEAR,size=40,color=ft.Colors.WHITE),style=ft.ButtonStyle(shape=ft.CircleBorder()),bgcolor=ft.Colors.RED_ACCENT,color=ft.Colors.WHITE,width=90,height=90,on_click=lambda _:threading.Thread(target=clear).start()),
                    btn_buscar,
                ]
            )
            ])
            # )
            
            ],alignment=ft.MainAxisAlignment.CENTER),
        
        ])
        ],vertical_alignment=ft.CrossAxisAlignment.CENTER,alignment=ft.MainAxisAlignment.CENTER)

    appbar_ = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK,icon_color="white",
                    icon_size=20,
                    tooltip="Regresar",on_click=lambda _:  page.go("/equipos/%s/apartado" %id_equipo)),
        leading_width=50,
        title=ft.Text("Validacion de Apartado"),
        center_title=False,
        bgcolor=ft.Colors.GREEN,
        actions=[],
    )

    

    return ft.View("/login",
        controls=[appbar_,ft.Container(content=ft.Text("informacion de el apartado"),bgcolor=ft.Colors.AMBER),content_]
    )