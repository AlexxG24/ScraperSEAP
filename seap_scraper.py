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

def get_daily_auctions(target_date=None):
    """Extrage licitatiile publicate la o anumita data (default: azi)"""
    
    # Configurare Chrome cu optiuni anti-detectie
    options = Options()
    
    # Detecteaza daca ruleaza in CI (GitHub Actions)
    import os
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
    
    options.add_argument('--lang=ro-RO')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
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
        
        # Data tinta (default: azi)
        if target_date:
            # Parseaza data furnizata (format: DD.MM.YYYY sau YYYY-MM-DD)
            try:
                if '-' in target_date:
                    date_obj = datetime.strptime(target_date, '%Y-%m-%d')
                else:
                    date_obj = datetime.strptime(target_date, '%d.%m.%Y')
                today = date_obj.strftime('%d.%m.%Y')
                today_file = date_obj.strftime('%Y-%m-%d')
                print(f"[INFO] Colectez date pentru: {today}")
            except ValueError:
                print(f"[EROARE] Format data invalid: {target_date}. Folosesc data de azi.")
                today = datetime.now().strftime('%d.%m.%Y')
                today_file = datetime.now().strftime('%Y-%m-%d')
        else:
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
            paginare_text = driver.find_element(By.TAG_NAME, 'body').text
            
            # Debug: salveaza textul paginii
            with open('page_text.txt', 'w', encoding='utf-8') as f:
                f.write(paginare_text)
            print(f"  [DEBUG] Text pagina salvat in page_text.txt")
            
            # Extrage numarul din "dintr-un total de: X"
            match = re.search(r'dintr-un\s+total\s+de[:\s]+(\d[\d\.,]*)', paginare_text.lower())
            if match:
                num_str = match.group(1).replace('.', '').replace(',', '')
                total_licitatii = int(num_str)
                print(f"  [INFO] Total licitatii filtrate: {total_licitatii}")
            else:
                # Fallback 1: numara codurile SCN cu data de azi
                today_pattern = today.replace('.', r'\.')
                scn_matches = re.findall(rf'SCN\d+\s*\n\s*{today_pattern}', paginare_text)
                if scn_matches:
                    total_licitatii = len(scn_matches)
                    print(f"  [INFO] Numar licitatii gasite cu SCN + data azi: {total_licitatii}")
                else:
                    # Fallback 2: numara aparitiile datei de azi in format HH:MM
                    date_time_matches = re.findall(rf'{today_pattern}\s+\d{{2}}:\d{{2}}', paginare_text)
                    if date_time_matches:
                        total_licitatii = len(date_time_matches)
                        print(f"  [INFO] Numar licitatii gasite cu data+ora: {total_licitatii}")
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
        
        # Salveaza in fisier JSON pentru PWA (cu istoric zilnic)
        # Citeste istoricul existent (local, apoi fallback la Gist)
        history = []
        total_all_time = 0
        
        # Incearca fisierul local
        try:
            with open('seap_data.json', 'r', encoding='utf-8') as f:
                existing = json.load(f)
                history = existing.get('history', [])
                total_all_time = existing.get('totalAllTime', 0)
        except:
            pass
        
        # Daca istoricul local e gol sau prea mic, incearca Gist-ul
        if len(history) < 2:
            try:
                import urllib.request
                gist_url = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json'
                req = urllib.request.Request(f'{gist_url}?t={int(time.time())}')
                with urllib.request.urlopen(req, timeout=10) as resp:
                    gist_data = json.loads(resp.read().decode('utf-8'))
                    gist_history = gist_data.get('history', [])
                    if len(gist_history) > len(history):
                        history = gist_history
                        total_all_time = gist_data.get('totalAllTime', 0)
                        print(f"  [INFO] Istoric recuperat din Gist ({len(history)} zile)")
            except Exception as e:
                print(f"  [WARN] Nu am putut citi Gist-ul: {e}")
        
        # Verifica daca ziua curenta exista deja in istoric
        today_entry = next((h for h in history if h['date'] == today), None)
        if today_entry:
            # Actualizeaza intrarea existenta
            today_entry['count'] = licitatii_azi
        else:
            # Adauga ziua noua
            history.append({"date": today, "count": licitatii_azi})
        
        # Sorteaza istoricul dupa data (cronologic)
        history.sort(key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'))
        
        # Pastreaza doar ultimele 30 zile
        history = history[-30:]
        
        # Recalculeaza totalAllTime ca suma tuturor count-urilor din istoric
        total_all_time = sum(h['count'] for h in history)
        
        result = {
            "history": history,
            "totalAllTime": total_all_time,
            "lastUpdate": datetime.now().isoformat()
        }
        
        with open('seap_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] Date salvate in: seap_data.json (Total all-time: {total_all_time})")
        
        # Update GitHub Gist pentru PWA live (folosind gh api - nu se blocheaza)
        import subprocess
        try:
            with open('seap_data.json', 'r', encoding='utf-8') as f:
                content = f.read()
            proc = subprocess.run(
                ['gh', 'api', '--method', 'PATCH', '/gists/916c4f36e09196cd4e83e8e3bafe947a',
                 '-f', f'files[seap_data.json][content]={content}'],
                capture_output=True, text=True, timeout=30
            )
            if proc.returncode == 0:
                print(f"[INFO] Gist actualizat - PWA va afisa datele noi!")
            else:
                print(f"[WARN] Gist update failed: {proc.stderr}")
        except subprocess.TimeoutExpired:
            print(f"[WARN] Gist update timeout")
        except Exception as gist_err:
            print(f"[WARN] Nu am putut actualiza Gist: {gist_err}")
        
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

def get_missing_days():
    """Detecteaza zilele lucratoare lipsa din istoric"""
    import json
    
    # Citeste istoricul existent
    history = []
    try:
        with open('seap_data.json', 'r', encoding='utf-8') as f:
            existing = json.load(f)
            history = existing.get('history', [])
    except:
        pass
    
    # Fallback la Gist
    if len(history) < 2:
        try:
            import urllib.request
            gist_url = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json'
            req = urllib.request.Request(f'{gist_url}?t={int(time.time())}')
            with urllib.request.urlopen(req, timeout=10) as resp:
                gist_data = json.loads(resp.read().decode('utf-8'))
                history = gist_data.get('history', [])
        except:
            pass
    
    if not history:
        print("[WARN] Nu exista istoric. Nimic de recuperat.")
        return []
    
    # Gaseste prima si ultima data din istoric
    dates_in_history = set()
    for h in history:
        try:
            dates_in_history.add(datetime.strptime(h['date'], '%d.%m.%Y').date())
        except:
            pass
    
    if not dates_in_history:
        return []
    
    start_date = min(dates_in_history)
    end_date = datetime.now().date()
    
    # Gaseste zilele lucratoare lipsa
    missing = []
    current = start_date
    while current <= end_date:
        # 0=luni ... 4=vineri (zile lucratoare)
        if current.weekday() < 5 and current not in dates_in_history:
            missing.append(current.strftime('%d.%m.%Y'))
        current += timedelta(days=1)
    
    return missing

def main():
    import sys
    
    print("="*50)
    print("SEAP Scraper - Licitatii Zilnice")
    print("="*50)
    
    # Mod recuperare: --recover
    if len(sys.argv) > 1 and sys.argv[1] == '--recover':
        missing = get_missing_days()
        if not missing:
            print("[INFO] Nu sunt zile lipsa!")
            return
        
        print(f"[INFO] Zile lucratoare lipsa: {len(missing)}")
        for d in missing:
            print(f"  - {d}")
        
        for i, date in enumerate(missing):
            print(f"\n{'='*50}")
            print(f"[{i+1}/{len(missing)}] Recuperez {date}...")
            print(f"{'='*50}")
            count = get_daily_auctions(date)
            print(f"[OK] {date}: {count} licitatii")
            # Pauza intre rulari pentru a nu supraincarca SEAP
            if i < len(missing) - 1:
                wait_time = random.randint(10, 20)
                print(f"[INFO] Astept {wait_time}s inainte de urmatoarea zi...")
                time.sleep(wait_time)
        
        print(f"\n[INFO] Recuperare completa! {len(missing)} zile procesate.")
        return
    
    # Verifica daca s-a furnizat o data specifica
    target_date = None
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        print(f"[INFO] Data tinta specificata: {target_date}")
    
    count = get_daily_auctions(target_date)
    
    print(f"\n[{datetime.now()}] Script finalizat. Licitatii gasite: {count}")

if __name__ == "__main__":
    main()
