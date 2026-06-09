import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

# using the configuration from config.py, this function sends an email with the given HTML content as the body of the email
def enviar_correo_oferta(html_cuerpo):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
        print("Error de configuración: Faltan credenciales en el archivo .env")
        return False
        
    # building the email message with the specified sender, receiver, subject, and HTML body    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "¡Descuento Confirmado en PlayStation Plus!"
    
    # adapting the HTML body to include the offer details and a call to action for the user to check their PlayStation account
    msg.attach(MIMEText(html_cuerpo, 'html'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Correo de notificación enviado con éxito.")
        return True
    except Exception as e:
        print(f"Error crítico al enviar el correo por SMTP: {e}")
        return False