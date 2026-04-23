import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000")


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1440, 1200)

    yield driver
    driver.quit()


def wait_for_presence(browser, by, value, timeout=10):
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_for_visible(browser, by, value, timeout=10):
    return WebDriverWait(browser, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def wait_for_text(browser, by, value, expected_text, timeout=10):
    WebDriverWait(browser, timeout).until(
        lambda driver: expected_text in driver.find_element(by, value).text
    )


def open_app(browser):
    browser.get(BASE_URL)

    wait_for_visible(browser, By.ID, "task-form")
    wait_for_visible(browser, By.ID, "form-title")
    wait_for_visible(browser, By.ID, "feedback")
    wait_for_text(browser, By.ID, "feedback", "Tasks loaded successfully.")

    wait_for_presence(browser, By.ID, "pending-tasks")
    wait_for_presence(browser, By.ID, "in_progress-tasks")
    wait_for_presence(browser, By.ID, "done-tasks")


def create_task(browser, title, description, status):
    title_input = browser.find_element(By.ID, "title")
    description_input = browser.find_element(By.ID, "description")
    status_select = Select(browser.find_element(By.ID, "status"))
    submit_btn = browser.find_element(By.ID, "submit-btn")

    title_input.clear()
    title_input.send_keys(title)
    description_input.clear()
    description_input.send_keys(description)
    status_select.select_by_value(status)
    submit_btn.click()


def test_app_loads_successfully(browser):
    open_app(browser)

    assert "Task Management App" in browser.title
    assert browser.find_element(By.ID, "form-title").text == "Create Task"
    assert browser.find_element(By.ID, "api-base-url").text.startswith("http://")

    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "Tasks Board" in page_text
    assert "Pending" in page_text
    assert "In Progress" in page_text
    assert "Done" in page_text


def test_user_can_create_task_from_ui(browser):
    open_app(browser)

    create_task(
        browser,
        title="Acceptance Task",
        description="Created from Selenium",
        status="pending",
    )

    wait_for_text(browser, By.ID, "pending-tasks", "Acceptance Task")
    wait_for_text(browser, By.ID, "pending-tasks", "Created from Selenium")

    pending_column = browser.find_element(By.ID, "pending-tasks")
    assert "Acceptance Task" in pending_column.text
    assert "Created from Selenium" in pending_column.text


def test_user_can_create_task_in_done_column(browser):
    open_app(browser)

    create_task(
        browser,
        title="Done Task",
        description="Should appear in done",
        status="done",
    )

    wait_for_text(browser, By.ID, "done-tasks", "Done Task")
    wait_for_text(browser, By.ID, "done-tasks", "Should appear in done")

    done_column = browser.find_element(By.ID, "done-tasks")
    assert "Done Task" in done_column.text
    assert "Should appear in done" in done_column.text


def test_user_can_edit_task_from_ui(browser):
    open_app(browser)

    create_task(
        browser,
        title="Original Title",
        description="Original description",
        status="pending",
    )

    wait_for_text(browser, By.ID, "pending-tasks", "Original Title")

    task_cards = browser.find_elements(By.CSS_SELECTOR, "#pending-tasks .task-card")

    target_card = None
    for card in task_cards:
        card_text = card.text
        if "Original Title" in card_text and "Original description" in card_text:
            target_card = card
            break

    assert target_card is not None, "Could not find the created task card to edit."

    edit_button = target_card.find_element(
        By.CSS_SELECTOR, 'button[data-action="edit"]'
    )
    edit_button.click()

    wait_for_text(browser, By.ID, "form-title", "Edit Task")

    title_input = browser.find_element(By.ID, "title")
    description_input = browser.find_element(By.ID, "description")
    status_select = Select(browser.find_element(By.ID, "status"))
    submit_btn = browser.find_element(By.ID, "submit-btn")

    title_input.clear()
    title_input.send_keys("Updated Title")
    description_input.clear()
    description_input.send_keys("Updated description")
    status_select.select_by_value("done")
    submit_btn.click()

    wait_for_text(browser, By.ID, "done-tasks", "Updated Title")
    wait_for_text(browser, By.ID, "done-tasks", "Updated description")

    done_column = browser.find_element(By.ID, "done-tasks")
    assert "Updated Title" in done_column.text
    assert "Updated description" in done_column.text


def test_user_can_change_task_status_from_card(browser):
    open_app(browser)

    create_task(
        browser,
        title="Move Status Task",
        description="Will be moved from pending to in progress",
        status="pending",
    )

    wait_for_text(browser, By.ID, "pending-tasks", "Move Status Task")

    task_cards = browser.find_elements(By.CSS_SELECTOR, "#pending-tasks .task-card")

    target_card = None
    for card in task_cards:
        card_text = card.text
        if (
            "Move Status Task" in card_text
            and "Will be moved from pending to in progress" in card_text
        ):
            target_card = card
            break

    assert (
        target_card is not None
    ), "Could not find the created task card to change status."

    status_select = Select(
        target_card.find_element(By.CSS_SELECTOR, 'select[data-action="status"]')
    )
    status_select.select_by_value("in_progress")

    wait_for_text(browser, By.ID, "in_progress-tasks", "Move Status Task")
    wait_for_text(
        browser, By.ID, "in_progress-tasks", "Will be moved from pending to in progress"
    )

    in_progress_column = browser.find_element(By.ID, "in_progress-tasks")
    assert "Move Status Task" in in_progress_column.text
    assert "Will be moved from pending to in progress" in in_progress_column.text


def test_user_can_delete_task_from_ui(browser):
    open_app(browser)

    create_task(
        browser,
        title="Delete Me",
        description="This task will be removed",
        status="pending",
    )

    wait_for_text(browser, By.ID, "pending-tasks", "Delete Me")

    task_cards = browser.find_elements(By.CSS_SELECTOR, "#pending-tasks .task-card")

    target_card = None
    for card in task_cards:
        card_text = card.text
        if "Delete Me" in card_text and "This task will be removed" in card_text:
            target_card = card
            break

    assert target_card is not None, "Could not find the created task card to delete."

    delete_button = target_card.find_element(
        By.CSS_SELECTOR, 'button[data-action="delete"]'
    )
    delete_button.click()

    WebDriverWait(browser, 10).until(
        lambda driver: "Delete Me"
        not in driver.find_element(By.ID, "pending-tasks").text
    )

    pending_column = browser.find_element(By.ID, "pending-tasks")
    assert "Delete Me" not in pending_column.text
    assert "This task will be removed" not in pending_column.text


def test_user_can_cancel_edit_mode(browser):
    open_app(browser)

    create_task(
        browser,
        title="Task To Cancel Edit",
        description="This task will enter edit mode",
        status="pending",
    )

    wait_for_text(browser, By.ID, "pending-tasks", "Task To Cancel Edit")

    task_cards = browser.find_elements(By.CSS_SELECTOR, "#pending-tasks .task-card")

    target_card = None
    for card in task_cards:
        card_text = card.text
        if (
            "Task To Cancel Edit" in card_text
            and "This task will enter edit mode" in card_text
        ):
            target_card = card
            break

    assert (
        target_card is not None
    ), "Could not find the created task card to enter edit mode."

    edit_button = target_card.find_element(
        By.CSS_SELECTOR, 'button[data-action="edit"]'
    )
    edit_button.click()

    wait_for_text(browser, By.ID, "form-title", "Edit Task")

    cancel_button = browser.find_element(By.ID, "cancel-edit-btn")
    cancel_button.click()

    wait_for_text(browser, By.ID, "form-title", "Create Task")
    wait_for_text(browser, By.ID, "feedback", "Edit cancelled.")

    assert browser.find_element(By.ID, "task-id").get_attribute("value") == ""
    assert browser.find_element(By.ID, "title").get_attribute("value") == ""
    assert browser.find_element(By.ID, "description").get_attribute("value") == ""
    assert (
        Select(
            browser.find_element(By.ID, "status")
        ).first_selected_option.get_attribute("value")
        == "pending"  
    )
