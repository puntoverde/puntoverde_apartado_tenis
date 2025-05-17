import jpype
import jpype.imports

# jpype.startJVM()
jpype.startJVM(classpath = ["C:\\java_huella\\dist\\prueba_puente_python.jar"])
import java
import javax
from javax.swing import *
from java.awt import *
from java.io import *
from apartados_dao import ApartadoDao #"gestion de bd 
from prueba_puente_python import DigitalPersona

from asyncio import Future


num_intentos=0

def fnDigitalPersona_():

    

    def createAndShowGUI():  

        def VerificacionHuella(e):
        
            global num_intentos
            try:
                if(e=="VerificandoStart"):
                    img = ImageIcon("./src/assets/images/fingerprint/finger_scan.png").getImage()
                    newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                    lblHuella.setIcon(ImageIcon(newimg))
                elif(e=="VerificandoEnd"):
                    img = ImageIcon("./src/assets/images/fingerprint/finger.png").getImage()
                    newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                    lblHuella.setIcon(ImageIcon(newimg))
                elif(e=="Verificar"):
                    verificado=digitalPersona.verificarHuella(huella_[0])
                    print(verificado)
                    num_intentos=num_intentos+1
                    lblIntentos.setText(f"intento {num_intentos} de 3")        
                    if(verificado):
                        print("listo verificoy cierra y registra apartado")
                        img = ImageIcon("./src/assets/images/fingerprint/finger_check.png").getImage()
                        newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                        lblHuella.setIcon(ImageIcon(newimg))
                        return True
                    elif(num_intentos==3):
                        print("cierra por el numero de intentos y no registra nadaaa")
                        return False
                    else:
                        img = ImageIcon("./src/assets/images/fingerprint/finger_error.png").getImage()
                        newimg = img.getScaledInstance(230, 310,  java.awt.Image.SCALE_SMOOTH)
                        lblHuella.setIcon(ImageIcon(newimg))
            except java.lang.Exception as ex:
                print("xxx")      


        huella_=ApartadoDao.get_huella(11499) 
        digitalPersona=DigitalPersona(VerificacionHuella)

        #funciones

        frame = JFrame("Varificacion")
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)

        img = ImageIcon("./src/assets/images/fingerprint/finger_scan.png").getImage()
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
                    print("error de ")
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