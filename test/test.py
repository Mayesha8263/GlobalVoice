import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialise driver
def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    return driver

# Login user
def login(driver):
    try:
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nav-link') and contains(text(), 'Login')]")))
        login_button.click()

        login_username_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
        login_password_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "password")))
        login_username_input.send_keys("Mayesha Islam")
        login_password_input.send_keys("mayesha123")

        login_submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#LoginModal button[type='submit']")))
        login_submit_button.click()
    except Exception as e:
        print(f"An error occurred: {e}")

# Translate input text
def translate_text(driver, query, result, input_lang, output_lang):
    try: 
        driver.get("http://localhost:5173/translator/")
        login(driver)
        input_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "input_language")))
        input_language.click()
        input_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//select[@id='input_language']/option[@value='{input_lang}']")))
        input_language_option.click()

        input_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input")))
        input_text.send_keys(query)

        output_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "target_language")))
        output_language.click()
        output_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//select[@id='target_language']/option[@value='{output_lang}']")))
        output_language_option.click()

        translate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Translate')]")
        translate_button.click()

        translated_text = WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "translated-text")))

        time.sleep(20)

        assert translated_text.text == result, "Translated text not displayed"
        print("Translate function test passed.")
        return translated_text.text
    except Exception as e:
         print(f"An error occurred: {e}")

# Translate text then press speech icon
def text_to_speech(driver, query, result, input_lang, output_lang):
    translate_text(driver, query, result, input_lang, output_lang)
    translated_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "translated-text")))
    speak_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "speak-button")))
    speak_button.click()
    time.sleep(5)
    print("Text spoken successfully.")

# Translate text & detect language
def auto_detect_language(driver, query, detected):
    try: 
        driver.get("http://localhost:5173/translator/")
        login(driver)
        input_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input")))
        input_text.send_keys(query)

        output_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "target_language")))
        output_language.click()
        output_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='target_language']/option[@value='fra_Latn']")))
        output_language_option.click()

        translate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Translate')]")
        translate_button.click()

        translated_text = WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "translated-text")))

        input_language_dropdown = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input_language")))
        selected_option = input_language_dropdown.find_element(By.CSS_SELECTOR, "option:checked")

        time.sleep(10)

        assert selected_option.text == detected, "Detected input language is incorrect"
        print("Automatic language detection function test passed.")
    except Exception as e:
         print(f"An error occurred: {e}")

# Translate text then save phrase
def save_phrases(driver, query, result, input_lang, output_lang):
    try:
        driver.get("http://localhost:5173/translator/")
        translated_text = translate_text(driver, query, result, input_lang, output_lang)

        save_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "output-save-button")))
        save_button.click()

        time.sleep(5)

        phrasebook_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "My Phrasebook")))
        phrasebook_link.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "saved-outputs")))
        saved_outputs = driver.find_elements(By.CLASS_NAME, "saved-outputs")
        time.sleep(5)
        found = False
        for output in saved_outputs:
            if translated_text in output.text:
                found = True
                break
        
        if found:
            print("Saved phrase found and test passed.")
        else:
            print("Saved phrase not found, test failed.")

    except Exception as e:
         print(f"An error occurred: {e}")

# Remove saved phrase
def remove_phrase(driver, phrase_text):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        phrasebook_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "My Phrasebook")))
        phrasebook_link.click()
        saved_ouputs = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "saved-outputs")))

        time.sleep(5)
        
        output_items = saved_ouputs.find_elements(By.CLASS_NAME, "language-item")
        for output_item in output_items:
            if phrase_text in output_item.text:
                remove_button = output_item.find_element(By.CLASS_NAME, "remove-button")
                remove_button.click()
                print(f"Removed phrase: {phrase_text} and test passed.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")

# Add translation box
def add_translation_box():
    add_translation_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "add-button")))
    add_translation_button.click()

# Select target language from dropdown list
def select_language(index, language):
    language_dropdown_xpath = f"//select[@name='target_language_{index}']"
    language_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, language_dropdown_xpath)))
    driver.execute_script("arguments[0].scrollIntoView();", language_dropdown)
    time.sleep(1)
    language_dropdown.click()

    language_option_xpath = f"//select[@name='target_language_{index}']/option[@value='{language}']"
    language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, language_option_xpath)))
    language_option.click()

# Translate multiple translation boxes
def translate_boxes():
    translate_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "translate-button")))
    for button in translate_buttons:
        driver.execute_script("arguments[0].scrollIntoView();", button)
        time.sleep(1)
        button.click()

# Retrieve translations
def get_translated_texts():
    translated_text_elements = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//p[@class='translated-text']"))
    )
    translated_texts = [element.text for element in translated_text_elements]
    return translated_texts

# Translate all translation boxes
def run_language_comparison_test(driver, query, translations):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        input_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "input_language")))
        input_language.click()
        input_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='input_language']/option[@value='eng_Latn']")))
        input_language_option.click()

        input_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input")))
        input_text.send_keys(query)

        for i in range(2):
            add_translation_box()
        
        output_languages = ["fra_Latn", "arb_Arab", "ben_Beng"]
        for i, language in enumerate(output_languages):
            select_language(i, language)
        translate_boxes()
        time.sleep(20)
        
        translated_texts = get_translated_texts()
        time.sleep(20)

        for i, translation in enumerate(translated_texts):
            assert translation == translations[i], f"Translation incorrect for language {output_languages[i]}"

        print("Language comparison test passed.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Remove translation boxes
def remove_translation_box(driver, query):
    try:
        driver.get("http://localhost:5173/translator/")
        for i in range(2):
            add_translation_box()
        time.sleep(2)

        for i in range(2):
            remove_buttons = driver.find_elements(By.CLASS_NAME, "remove-button-translate")
            button = remove_buttons[i-1]
            driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)
            button.click()
            time.sleep(2)
        
        remaining_boxes = driver.find_elements(By.CLASS_NAME, "output-field-container")
        assert len(remaining_boxes) == 0, "Not all translation boxes are removed"

        print("Remove translation boxes test passed.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Update user profile
def update_profile(driver, new_username, new_email):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Profile")))
        profile_link.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-form")))

        username_input = driver.find_element(By.CSS_SELECTOR, ".profile-input[type='text']")
        username_input.clear()
        username_input.send_keys(new_username)

        email_input = driver.find_element(By.CSS_SELECTOR, ".profile-input[type='email']")
        email_input.clear()
        email_input.send_keys(new_email)

        update_button = driver.find_element(By.ID, "updateProfileBtn")
        update_button.click()

        print("Profile update test passed.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Add favourite languages in user profile
def add_fav_lang(driver, new_language):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Profile")))
        profile_link.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-form")))

        select_language = Select(driver.find_element(By.CSS_SELECTOR, "select[multiple]"))
        select_language.select_by_visible_text(new_language)

        update_button = driver.find_element(By.ID, "updateProfileBtn")
        update_button.click()

        time.sleep(1)

        print(f"Language '{new_language}' added to favorite languages successfully and test passed.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Remove a favourite language from user profile
def remove_language(driver, language):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        profile_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Profile")))
        profile_link.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-form")))

        time.sleep(1)

        fav_langs = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "favLangs")))
        language_items = fav_langs.find_elements(By.CLASS_NAME, "language-item")
        for language_item in language_items:
            if language in language_item.text:
                remove_button = language_item.find_element(By.CLASS_NAME, "remove-button")
                remove_button.click()

                update_button = driver.find_element(By.ID, "updateProfileBtn")
                update_button.click()

                print(f"Language '{language}' removed from favorite languages successfully and test passed.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")

# Add a favourite language, translate text, check if phrase has automatically saved
def auto_save_fav_lang_phrases(driver, query, new_language, new_language_code):
    try:
        driver.get("http://localhost:5173/translator/")
        login(driver)
        add_fav_lang(driver, new_language)

        translator = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Translator")))
        translator.click()

        input_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "input_language")))
        input_language.click()
        input_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='input_language']/option[@value='eng_Latn']")))
        input_language_option.click()

        input_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "input")))
        input_text.send_keys(query)

        output_language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "target_language")))
        output_language.click()
        output_language_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//select[@id='target_language']/option[@value='{new_language_code}']")))
        output_language_option.click()

        translate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Translate')]")
        translate_button.click()

        translated_text = WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "translated-text")))

        time.sleep(20)

        driver.get("http://localhost:5173/translator/")
        login(driver)

        phrasebook_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "My Phrasebook")))
        phrasebook_link.click()

        translator = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "saved-outputs")))
        saved_outputs = translator.find_elements(By.CLASS_NAME, "saved-outputs")
        time.sleep(10)
        found = False
        for output in saved_outputs:
            if translated_text.text in output.text:
                found = True
                break
        
        if found:
            print("Saved phrase found and test passed.")
        else:
            print("Saved phrase not found, test failed.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    driver = init_driver()
    # Testing simple sentences
    translate_text(driver, 'Hello World', 'Salut le monde', 'eng_Latn', 'fra_Latn')
    # Testing complex sentences
    translate_text(driver, 'In the labyrinthine corridors of bureaucratic red tape, navigating the intricacies of policy implementation becomes an arduous task for government officials striving to enact meaningful change.', "Dans les couloirs labyrinthiques de la bureaucratie, la navigation dans les subtilités de la mise en œuvre des politiques devient une tâche ardue pour les fonctionnaires qui s'efforcent de faire un changement significatif.", 'eng_Latn', 'fra_Latn')
    # Testing sentences with special characters
    translate_text(driver, 'مرحبا، كيف حالك', 'Hey, how are you?', 'arb_Arab','eng_Latn')
    text_to_speech(driver, 'Hello World', 'Salut le monde', 'eng_Latn', 'fra_Latn')
    auto_detect_language(driver, 'Hello how are you' , 'Detected - English')
    save_phrases(driver, 'Hello World', 'Salut le monde', 'eng_Latn', 'fra_Latn')
    remove_phrase(driver, 'Salut le monde' )
    run_language_comparison_test(driver, 'Hello World', ['Salut le monde', 'مرحباً يا عالم', 'হ্যালো ওয়ার্ল্ড'])
    remove_translation_box(driver, 'Hello World')
    update_profile(driver, 'Mayesha Islam', 'MayeshaIslam@email.com')
    add_fav_lang(driver, "Assamese")
    remove_language(driver, "Assamese")
    auto_save_fav_lang_phrases(driver, "Testing", "Spanish", "spa_Latn")
    time.sleep(8)
    driver.quit()