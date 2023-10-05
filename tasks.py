from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1,
    )
    open_robot_order_website()
    orders = get_orders()
    place_orders(orders)
    archive_receipts()

def open_robot_order_website():
    """Opens the robot order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads the orders file, reads it as a table, and returns the result"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = Tables().read_table_from_csv("orders.csv")
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")

def fill_the_form(order_details):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()

    page.select_option("#head", order_details["Head"])
    page.check("#id-body-" + order_details["Body"])
    page.fill("#root > div > div.container > div > div.col-sm-7 > form > div:nth-child(3) > input", str(order_details["Legs"]))
    #page.fill("[placeholder=Enter the part number for the legs]", str(order_details["Legs"]))
    page.fill("#address", order_details["Address"])

def place_orders(orders):
    """ """
    page = browser.page()

    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        submit_order()
        order_number = order["Order number"]
        pdf_file = store_receipt_as_pdf(order_number)
        screenshot = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
        page.click("#order-another")

def preview_robot():
    """ """
    page = browser.page()
    page.click("preview")

def submit_order():
    """Submit the order"""
    page = browser.page()
    page.click("#order")
    condition = page.locator("div.alert-danger").is_visible()
    while condition:
        page.click("#order")
        condition = page.locator("div.alert-danger").is_visible()
    
def store_receipt_as_pdf(order_number):
    """Export the receipt to a pdf file"""
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_path = "output/receipts/receipt_" + order_number + ".pdf"
    pdf.html_to_pdf(receipt, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Take a screenshot of the receipt"""
    page = browser.page()
    screenshot_path = "output/screenshots/screenshot_" + order_number + ".png"
    page.screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the robot screenshot to the receipt PDF file"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip('output/receipts', 'output/receipts.zip')