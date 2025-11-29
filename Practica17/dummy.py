import smtplib
from email import encoders
from email.message import EmailMessage
#Servidor SMTP de Hotmail: smtp-mail.outlook.com
#Servidor SMTP de Gmail: smtp.gmail.com
try:
    servidorSmtp=smtplib.SMTP('smtp.gmail.com',587)
    servidorSmtp.ehlo()
    servidorSmtp.starttls()
    servidorSmtp.login('ibero.contacto.computo@gmail.com','pass')
    mensaje=EmailMessage()
    mensaje['From']='ibero.contacto.computo@gmail.com'
    mensaje['To']='a2305103@correo.uia.mx'

    mensaje['Subject']='Mensaje de Prueba desde Python'
    texto='Este es el contenido del cuerpo del mensaje'
    mensaje.set_content(texto)
    servidorSmtp.sendmail('ibero.contacto.computo@gmail.com','a2305103@correo.uia.mx',mensaje.as_string())

    print('Mensaje enviado')
except:
    print('Error al enviar correo')
