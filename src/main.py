import asyncio
import re
from src.scraper import obtener_precios_psplus
from src.notifier import enviar_correo_oferta
from src.config import PS_PLUS_URL

async def main():
    print("=== INICIANDO RASTREADOR AVANZADO DE PS PLUS ===")
    
    try:
        datos_planes = await obtener_precios_psplus()
    except Exception as e:
        print(f"Error durante la ejecución del scraping: {e}")
        return

    hubo_oferta = False
    
    # initialize the HTML string that will contain the offer cards to be included in the email body
    html_tarjetas = ""

    for plan, info in datos_planes.items():
        ofertas = info["ofertas"]
        print(f"\nAnalizando categoría: {plan}")
        
        for oferta in ofertas:
            periodo = oferta["periodo"]
            detalles = oferta["detalles_precio"]
            descripcion = oferta.get("descripcion", "")
            
            # searching for keywords in the description to extract the offer expiration date, if available. If not found, a default message is set indicating that the offer deadline is not specified on the page.
            fecha_finalizacion = "Plazo de oferta no especificado en la página."
            if descripcion:
                # separating the description into sentences and looking for keywords that indicate the offer expiration date, such as "finaliza", "hasta", "termina" or "antes del". If any of these keywords are found in a sentence, that sentence is extracted as the offer expiration information.
                for oracion in descripcion.split("."):
                    if any(palabra in oracion.lower() for palabra in ["finaliza", "hasta", "termina", "antes del"]):
                        fecha_finalizacion = oracion.strip()
                        break

            texto_completo = " ".join(detalles)
            valores_precio = re.findall(r"US\$\s*([\d.]+)", texto_completo)
            
            es_oferta = len(valores_precio) >= 2 or any("%" in d or "ahorra" in d.lower() for d in detalles)
            
            if es_oferta and len(valores_precio) >= 2:
                hubo_oferta = True
                precio_original = float(valores_precio[0])
                precio_oferta = float(valores_precio[-1])
                
                porcentaje_desc = round(((precio_original - precio_oferta) / precio_original) * 100)
                
                print(f"  ¡OFERTA DETECTADA! {periodo} | Antes: US${precio_original} -> Ahora: US${precio_oferta} (-{porcentaje_desc}%)")
                
                html_tarjetas += f"""
                <div style="background-color: #ffffff; border-left: 5px solid #0072ce; padding: 20px; margin-bottom: 25px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <span style="background-color: #df1616; color: #ffffff; font-size: 11px; font-weight: bold; padding: 4px 8px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 10px;">¡Descuento Activo!</span>
                    <h2 style="margin: 0 0 5px 0; color: #003087; font-size: 20px; font-family: sans-serif;">PlayStation Plus {plan}</h2>
                    <p style="margin: 0 0 15px 0; font-size: 15px; color: #555555; font-weight: bold;">Suscripción: {periodo}</p>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 4px 0; font-size: 14px; color: #777777;">Precio Estándar:</td>
                            <td style="padding: 4px 0; font-size: 14px; color: #777777; text-decoration: line-through; text-align: right;">US$ {precio_original:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; font-size: 16px; color: #333333; font-weight: bold;">Precio Rebajado:</td>
                            <td style="padding: 4px 0; font-size: 18px; color: #00875a; font-weight: bold; text-align: right;">US$ {precio_oferta:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; font-size: 14px; color: #df1616; font-weight: bold;">Ahorro Directo:</td>
                            <td style="padding: 4px 0; font-size: 15px; color: #df1616; font-weight: bold; text-align: right;">¡Ahórrate un {porcentaje_desc}%!</td>
                        </tr>
                    </table>
                    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eeeeee; font-size: 12px; color: #666666; font-style: italic;">
                        <strong>Vigencia:</strong> {fecha_finalizacion}
                    </div>
                </div>
                """
            else:
                precio_regular = valores_precio[0] if valores_precio else "No disponible"
                print(f"  {periodo}: US${precio_regular} (Precio Estándar)")

    if hubo_oferta:
        # building the complete HTML email body by embedding the generated offer cards and including a call to action button that directs the user to the PlayStation Store to check the offers in their account. Finally, the email is sent using the enviar_correo_oferta function from notifier.py, passing the complete HTML as an argument.
        html_completo = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #f4f4f9;">
                <div style="background-color: #003087; padding: 25px; text-align: center; border-radius: 6px 6px 0 0;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 0.5px;">Alerta de Ofertas PS Plus</h1>
                </div>
                <div style="padding: 20px 0;">
                    <p style="color: #333333; font-size: 16px; margin-bottom: 20px;">Se han verificado los precios actuales en la tienda y se detectaron promociones:</p>
                    
                    {html_tarjetas}
                    
                    <div style="text-align: center; margin-top: 25px;">
                        <a href="{PS_PLUS_URL}" style="background-color: #003087; color: #ffffff; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.15);">Ir a la PlayStation Store</a>
                    </div>
                </div>
                <div style="text-align: center; padding: 20px; font-size: 11px; color: #999999; border-top: 1px solid #dddddd; margin-top: 20px;">
                    Aviso automático enviado desde Python Tracker.
                </div>
            </div>
        </body>
        </html>
        """
        enviar_correo_oferta(html_completo)
    else:
        print("\nTodos los precios corresponden al estándar comercial. No se enviará ningún correo.")

if __name__ == "__main__":
    asyncio.run(main())