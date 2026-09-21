from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:8000"


def test_create_task_from_web():

    # Configuration de Chromium
    options = webdriver.ChromeOptions()
    options.binary_location = "/snap/bin/chromium"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")

    # Démarrer le navigateur
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Ouvrir l'interface Web
        driver.get(BASE_URL)

        # 2. Remplir le titre
        title_input = driver.find_element(By.ID, "title")
        title_input.send_keys("Selenium Task")

        # 3. Remplir la description
        description_input = driver.find_element(By.ID, "description")
        description_input.send_keys(
            "Created automatically by Selenium"
        )

        # 4. Cliquer sur le bouton Créer
        create_button = driver.find_element(
            By.CSS_SELECTOR,
            "button[type='submit']"
        )

        create_button.click()

        # 5. Attendre que la tâche apparaisse
        result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "task-result")
            )
        )

        # 6. Vérifier le résultat
        assert "Selenium Task" in result.text
        assert "Created automatically by Selenium" in result.text

    finally:
        # Toujours fermer Chromium
        driver.quit()
