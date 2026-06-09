import asyncio
from playwright.async_api import async_playwright
from src.config import PS_PLUS_URL

# obtain the prices of the PS Plus plans by scraping the official PlayStation website using Playwright
async def obtener_precios_psplus():
    resultados = {}
    
    # init Playwright and launch a headless browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # set a user agent to mimic a real browser and avoid potential blocks
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        print("Conectando a la plataforma de PlayStation...")
        await page.goto(PS_PLUS_URL, wait_until="domcontentloaded")
        
        print("Esperando a que carguen los elementos de la tienda...")
        await page.wait_for_selector("#essential", timeout=15000)
        
        # plans to scrape the prices from, we will look for these selectors in the page
        planes = ["#essential", "#extra", "#deluxe"]
        
        for plan in planes:
            nombre_plan = plan.replace('#', '').upper()
            resultados[nombre_plan] = {
                "ofertas": [],
                "legal": ""
            }
            
            tab_locator = page.locator(f"div{plan}")
            if await tab_locator.count() > 0:
                
                # click the tab to load the content of the plan, this is necessary because the page uses dynamic loading and we need to trigger it to get the correct data
                await tab_locator.evaluate("el => el.click()")
                
                # wait a bit for the content to load after clicking the tab, this is crucial to ensure we get the correct data
                await page.wait_for_timeout(1500)
                
                contenedor_plan = page.locator(f"div{plan} + main")
                
                # extract the offers for the current plan, i´ll look for up to 3 offers (monthly, quarterly, yearly)
                for i in range(3):
                    locator_titulo = contenedor_plan.locator(f'[data-qa="mfe-tier-selector#standalonePrice#offer{i}#title"]')
                    locator_precio = contenedor_plan.locator(f'div[data-qa="mfe-tier-selector#standalonePrice#offer{i}"]')
                    locator_desc = contenedor_plan.locator(f'[data-qa="mfe-tier-selector#standalonePrice#offer{i}#description"]')
                    
                    if await locator_titulo.count() > 0:
                        titulo = await locator_titulo.inner_text()
                        precio_raw = await locator_precio.inner_text()
                        
                        descripcion = ""
                        if await locator_desc.count() > 0:
                            descripcion = await locator_desc.inner_text()
                        
                        lineas_precio = [line.strip() for line in precio_raw.split('\n') if line.strip()]
                        
                        resultados[nombre_plan]["ofertas"].append({
                            "periodo": titulo,
                            "detalles_precio": lineas_precio,
                            "descripcion": descripcion
                        })
                        
                # extract the legal text if it exists
                locator_legal = contenedor_plan.locator('[data-qa="mfe-tier-selector#standalonePrice#footer#legalText"]')
                if await locator_legal.count() > 0:
                    resultados[nombre_plan]["legal"] = await locator_legal.inner_text()
            else:
                print(f"No se pudo encontrar la pestaña del plan: {nombre_plan}")
        await browser.close()
    return resultados