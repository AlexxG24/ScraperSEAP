import random
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# URL SEAP pentru licitatii publice - sortat dupa data publicarii (descrescator)
SEAP_URL = "https://www.e-licitatie.ro/pub/notices/contract-notices/list/0/0"

def random_delay(min_seconds=1, max_seconds=3):
    """Delay aleatoriu pentru comportament uman"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_like_scroll(driver):
    """Scroll aleatoriu pentru comportament uman"""
    for _ in range(random.randint(2, 4)):
        scroll_amount = random.randint(100, 400)
        driver.execute_script(f'window.scrollBy(0, {scroll_amount})')
        time.sleep(random.uniform(0.5, 1.5))

def get_daily_auctions():
    """Extrage licitatiile publicate azi"""
    
    # Configurare Chrome cu optiuni anti-detectie
    options = Options()
    options.add_argument('--lang=ro-RO')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
    
    # Lanseaza browser cu webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Ascunde webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        '''
    })
    
    try:
        print(f"[{datetime.now()}] Accesez SEAP...")
        random_delay(1, 2)
        
        # Navigheaza la pagina
        driver.get(SEAP_URL)
        
        # Simuleaza comportament uman
        random_delay(3, 5)
        human_like_scroll(driver)
        
        # Asteapta sa se incarce lista
        print(f"[{datetime.now()}] Astept incarcarea listei...")
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.u-items-list__content')))
        
        # Data de azi
        today = datetime.now().strftime('%d.%m.%Y')
        today_file = datetime.now().strftime('%Y-%m-%d')
        
        random_delay(2, 3)
        
        # === APLICARE FILTRE ===
        print(f"[{datetime.now()}] Aplic filtrele...")
        
        try:
            # Scroll sus pentru a vedea filtrele
            driver.execute_script("window.scrollTo(0, 0);")
            random_delay(1, 2)
            
            # 1. STARE CURENTA PROCEDURA: "In desfasurare"
            print(f"  [1] Setez Stare curenta procedura = In desfasurare...")
            try:
                stare_input = driver.execute_script("""
                    var labels = document.querySelectorAll('label');
                    for (var i = 0; i < labels.length; i++) {
                        if (labels[i].innerText.toLowerCase().includes('stare curenta')) {
                            var parent = labels[i].closest('.col-md-3');
                            if (parent) {
                                return parent.querySelector('input.k-input[role="combobox"]');
                            }
                        }
                    }
                    return null;
                """)
                if stare_input:
                    stare_input.click()
                    random_delay(0.5, 1)
                    stare_input.clear()
                    stare_input.send_keys("In desfasurare")
                    random_delay(1, 1.5)
                    stare_input.send_keys(Keys.ARROW_DOWN)
                    stare_input.send_keys(Keys.ENTER)
                    print(f"      [OK] Stare selectata")
                    random_delay(0.5, 1)
            except Exception as e:
                print(f"      [WARN] Eroare stare: {e}")
            
            # 2. DOMENIU DE ACTIVITATE: "Constructii"
            print(f"  [2] Setez Domeniu de activitate = Constructii...")
            try:
                domeniu_input = driver.execute_script("""
                    var labels = document.querySelectorAll('label');
                    for (var i = 0; i < labels.length; i++) {
                        if (labels[i].innerText.toLowerCase().includes('domeniu')) {
                            var parent = labels[i].closest('.col-md-3');
                            if (parent) {
                                return parent.querySelector('input.k-input[role="combobox"]');
                            }
                        }
                    }
                    return null;
                """)
                if domeniu_input:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", domeniu_input)
                    random_delay(0.5, 1)
                    domeniu_input.click()
                    random_delay(0.5, 1)
                    domeniu_input.clear()
                    for char in "Constructii":
                        domeniu_input.send_keys(char)
                        time.sleep(0.05)
                    random_delay(1.5, 2)
                    domeniu_input.send_keys(Keys.ARROW_DOWN)
                    random_delay(0.3, 0.5)
                    domeniu_input.send_keys(Keys.ENTER)
                    print(f"      [OK] Domeniu selectat")
                    random_delay(0.5, 1)
            except Exception as e:
                print(f"      [WARN] Eroare domeniu: {e}")
            
            # 3. DATA PUBLICARE: de la data de azi (setez direct via Kendo API)
            print(f"  [3] Setez Data publicare = azi ({today})...")
            try:
                # Folosesc Kendo API pentru a seta data direct
                result = driver.execute_script(f"""
                    var labels = document.querySelectorAll('label');
                    for (var i = 0; i < labels.length; i++) {{
                        if (labels[i].innerText.toLowerCase().includes('data publicare')) {{
                            var parent = labels[i].closest('.col-md-3');
                            if (parent) {{
                                var input = parent.querySelector('input[data-role="datepicker"]');
                                if (input) {{
                                    var widget = $(input).data('kendoDatePicker');
                                    if (widget) {{
                                        widget.value(new Date());
                                        widget.trigger('change');
                                        return 'kendo';
                                    }}
                                }}
                                // Fallback: seteaza direct in input
                                var inputField = parent.querySelector('input.k-input');
                                if (inputField) {{
                                    inputField.value = '{today}';
                                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    inputField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    return 'input';
                                }}
                            }}
                        }}
                    }}
                    return null;
                """)
                if result:
                    print(f"      [OK] Data publicare setata via {result}")
                else:
                    print(f"      [WARN] Nu am gasit datepicker pentru Data publicare")
                random_delay(1, 1.5)
            except Exception as e:
                print(f"      [WARN] Eroare data publicare: {e}")
            
            # 4. DATA LIMITA DEPUNERE: de la data de azi
            print(f"  [4] Setez Data limita depunere >= azi ({today})...")
            try:
                data_depunere_input = driver.execute_script("""
                    var labels = document.querySelectorAll('label, span');
                    for (var i = 0; i < labels.length; i++) {
                        if (labels[i].innerText.toLowerCase().includes('data limita depunere')) {
                            var parent = labels[i].closest('.col-md-3');
                            if (parent) {
                                var inputs = parent.querySelectorAll('input.k-input');
                                return inputs[0]; // primul input = "De la data"
                            }
                        }
                    }
                    return null;
                """)
                if data_depunere_input:
                    data_depunere_input.click()
                    random_delay(0.5, 1)
                    data_depunere_input.clear()
                    data_depunere_input.send_keys(today)
                    random_delay(0.5, 1)
                    data_depunere_input.send_keys(Keys.ENTER)
                    print(f"      [OK] Data limita depunere setata")
                    random_delay(0.5, 1)
            except Exception as e:
                print(f"      [WARN] Eroare data depunere: {e}")
            
            random_delay(1, 2)
            
            # 5. APASA BUTONUL FILTREAZA
            print(f"  [5] Apas butonul FILTREAZA...")
            filtreaza_btn = driver.find_element(By.ID, 'THE-SEARCH-BUTTON')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filtreaza_btn)
            random_delay(0.5, 1)
            driver.execute_script("arguments[0].click();", filtreaza_btn)
            print(f"      [OK] Buton FILTREAZA apasat")
            
            # Asteapta sa se reincarce lista cu rezultatele filtrate
            random_delay(4, 6)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.u-items-list__content')))
            print(f"  [OK] Lista reincarcata cu rezultate filtrate")
                
        except Exception as e:
            print(f"  [WARN] Eroare la aplicare filtre: {e}")
            driver.save_screenshot('filter_error.png')
        
        # Scroll in jos pentru a vedea paginarea
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay(2, 3)
        
        # Salveaza screenshot pentru debugging
        driver.save_screenshot('seap_page.png')
        print(f"  [DEBUG] Screenshot salvat: seap_page.png")
        
        # Extrage numarul total de licitatii din paginare
        # Format: "rezultate pe pagina dintr-un total de: X"
        total_licitatii = 0
        import re
        import json
        
        try:
            # Cauta in zona de paginare
            paginare_elem = driver.find_element(By.CSS_SELECTOR, '#container-sizing .u-items-list__content')
            paginare_text = driver.find_element(By.TAG_NAME, 'body').text
            
            # Extrage numarul din "dintr-un total de: X"
            match = re.search(r'dintr-un\s+total\s+de[:\s]+(\d[\d\.,]*)', paginare_text.lower())
            if match:
                num_str = match.group(1).replace('.', '').replace(',', '')
                total_licitatii = int(num_str)
                print(f"  [INFO] Total licitatii filtrate: {total_licitatii}")
            else:
                # Fallback: cauta pattern alternativ
                match = re.search(r'total\s+de[:\s]+(\d[\d\.,]*)', paginare_text.lower())
                if match:
                    num_str = match.group(1).replace('.', '').replace(',', '')
                    total_licitatii = int(num_str)
        except Exception as e:
            print(f"  [DEBUG] Eroare la extragere total: {e}")
        
        # Totalul filtrat ESTE numarul de licitatii care ne intereseaza
        licitatii_azi = total_licitatii
        
        print(f"  [INFO] Licitatii vizibile pe pagina: {licitatii_azi}")
        
        print(f"\n{'='*50}")
        print(f"REZULTATE SEAP - {today}")
        print(f"{'='*50}")
        print(f"  🔥 LICITATII AZI: {licitatii_azi}")
        print(f"  Total in sistem: {total_licitatii}")
        print(f"{'='*50}")
        
        # Salveaza in fisier JSON pentru PWA
        result = {
            "date": today,
            "todayCount": licitatii_azi,
            "totalInSystem": total_licitatii,
            "lastUpdate": datetime.now().isoformat()
        }
        
        with open('seap_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] Date salvate in: seap_data.json")
        
        # Salveaza si in log
        log_file = f'seap_log_{today_file}.txt'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} | Azi: {licitatii_azi} | Total: {total_licitatii}\n")
        
        return licitatii_azi
        
    except Exception as e:
        print(f"[EROARE] {e}")
        # Screenshot pentru debugging
        driver.save_screenshot('error_screenshot.png')
        print("Screenshot salvat: error_screenshot.png")
        return 0
        
    finally:
        random_delay(1, 2)
        driver.quit()

def main():
    print("="*50)
    print("SEAP Scraper - Licitatii Zilnice")
    print("="*50)
    
    count = get_daily_auctions()
    
    print(f"\n[{datetime.now()}] Script finalizat. Licitatii gasite: {count}")

if __name__ == "__main__":
    main()
