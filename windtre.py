from playwright.sync_api import sync_playwright
import os
from datetime import datetime

URL = "https://areaclienti.windtre.it/login"
USER = "utente"
PWD = "password"
NUM_TEL = "0550000000"

# Recupera l'ultima fattura per il numero specificato
with sync_playwright() as p:
    browser = None
    curdir = os.path.dirname(os.path.abspath(__file__))

    try:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # Pagina di login
        page.goto(URL, wait_until='networkidle')

        # Inserimento user e password
        page.click("div.welcome-back >> button.btn-desktop")
        page.fill("#username", USER)
        page.fill("#password", PWD)

        with page.expect_navigation(wait_until='networkidle'):
            page.click("span >> text=ACCEDI")

        # Imposta il numero per il quale si vuole l'ultima fattura,
        # (se il selettore esiste, nel caso si abbia più di un numero)
        try:
            cambia = page.wait_for_selector("span >> text='Cambia linea'", timeout=5000)
        except Exception:
            pass
        else:
            cambia.click()
            sim = page.query_selector(f"div.sim-item__col  >> text={NUM_TEL}")
            sim.click()
            page.click("span >> text=CONTINUA")

        with page.expect_navigation(wait_until='networkidle'):
            page.click("span >> text='VISUALIZZA FATTURE'")

        # Scarica nella directory corrente il file pdf della fattura più recente.
        with page.expect_download() as download_info:
            page.click("#invoice_table >> td >> img[alt=PDF]")
        download = download_info.value
        download.save_as(f"{curdir}/fattura_windtre.pdf")
    except Exception as e:
        now = datetime.now()
        print(f"\n{now:%Y-%m-%d %H:%M}: {e}")
    finally:
        if browser is not None:
            browser.close()
