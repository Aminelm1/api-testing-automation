from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://api:8000"
SELENIUM_URL = "http://127.0.0.1:4444/wd/hub"


def test_create_task_from_web():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=options
    )

    try:
        # Ouvrir l'interface Web
        driver.get(BASE_URL)

        # Remplir le formulaire
        driver.find_element(By.ID, "title").send_keys(
            "Selenium Task"
        )

        driver.find_element(By.ID, "description").send_keys(
            "Created automatically by Selenium"
        )

        # Créer la tâche
        driver.find_element(
            By.CSS_SELECTOR,
            "button[type='submit']"
        ).click()

        # Attendre l'affichage du résultat
        result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "task-result")
            )
        )

        # Vérifications
        assert "Selenium Task" in result.text
        assert "Created automatically by Selenium" in result.text

    finally:
        driver.quit()
