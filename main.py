"""
Daily Occurrence Report Application
-----------------------------------

Author: Zeeshan Nasir
Version: 0.3

This application allows the user to fill out a Daily Occurrence Report form. The user can
enter details such as the incident description, actions taken, and officer name, as well as
upload an image to be included in the report. The data is stored in an SQLite database and
a non-editable PDF report is generated with all the entered information, including the image.

"""

import base64
import io
import os
import sqlite3
import sys
##################   NEw code ############################
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog, Label, Toplevel

from PIL import Image, ImageTk
from reportlab.lib import utils
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Version of the application
APP_VERSION = "0.3"
TRIAL_DAYS = 10  # Trial period
LICENSE_KEY = "FULLACCESS1234"  # Hardcoded license key for full access
TRIAL_FILE = 'trial_info.json'



# Function to correctly resolve file paths, useful when bundling with PyInstaller
def resource_path(relative_path):
    """ Get the absolute path to resource, works for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Set up paths for resources
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = resource_path('images/liberty-london-ico.ico')
db_path = os.path.join(current_dir, 'occurrence_reports.db')  # Database file

# Create the application window
root = tk.Tk()
root.title(f"Daily Occurrence Form - Version {APP_VERSION}")
root.geometry("1000x900")

# Check the trial status
def check_trial():
    """Check if the trial period has expired or if a license key is needed."""
    if os.path.exists(TRIAL_FILE):
        # Load the trial information
        with open(TRIAL_FILE, 'rb') as f:
            encoded_data = f.read()
            # Ensure proper padding before decoding
            missing_padding = len(encoded_data) % 4
            if missing_padding:
                encoded_data += b'=' * (4 - missing_padding)
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            install_date_str, license_key_entered = decoded_data.split(',')

        install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
        current_date = datetime.now()

        if license_key_entered == 'True':
            return  # License key has already been entered; no need for further checks

        # Calculate the number of days since installation
        days_since_install = (current_date - install_date).days

        if days_since_install > TRIAL_DAYS:
            # Trial expired, prompt for license key
            entered_key = ask_for_license_key()
            if entered_key == LICENSE_KEY:
                # Save license key entered in the trial file
                trial_data = f"{install_date_str},True"
                encoded_data = base64.b64encode(trial_data.encode('utf-8'))
                with open(TRIAL_FILE, 'wb') as f:
                    f.write(encoded_data)
                custom_messagebox("License Activated", "Thank you! The license has been activated.", "info")
            else:
                custom_messagebox("Invalid License", "The license key is incorrect. Exiting the application.", "error")
                root.quit()  # Quit Tkinter main loop
                sys.exit()  # Forcefully close the program
        else:
            remaining_days = TRIAL_DAYS - days_since_install
            custom_messagebox("Trial Mode", f"You have {remaining_days} days left in your trial.", "info")
    else:
        # First time run: Save the installation date
        install_date = datetime.now()
        trial_data = f"{install_date.strftime('%Y-%m-%d')},False"
        encoded_data = base64.b64encode(trial_data.encode('utf-8'))
        with open(TRIAL_FILE, 'wb') as f:
            f.write(encoded_data)

        custom_messagebox("Trial Mode", f"You have {TRIAL_DAYS} days trial period.", "info")

#License key prompt
def ask_for_license_key():
    """Prompt the user for a license key."""
    key_prompt = tk.Toplevel(root)
    key_prompt.title("License Key Required")
    key_prompt.geometry("400x200")
    center_window(key_prompt)

    tk.Label(key_prompt, text="Please enter your license key:", font=("Arial", 12)).pack(pady=10)
    key_entry = tk.Entry(key_prompt, font=("Arial", 12))
    key_entry.pack(pady=5)

    # Create a container to hold the entered key
    entered_key = tk.StringVar()

    def submit_key():
        # Store the entered key in the variable before destroying the window
        entered_key.set(key_entry.get())
        key_prompt.destroy()

    submit_button = tk.Button(key_prompt, text="Submit", command=submit_key, font=("Arial", 12))
    submit_button.pack(pady=10)

    key_prompt.transient(root)
    key_prompt.grab_set()
    root.wait_window(key_prompt)

    return entered_key.get()  # Return the value of the entered key

# Function to center the app window
def center_window(window):
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    window.geometry(f'{window_width}x{window_height}+{x}+{y}')


# Center the main window
center_window(root)

# Set custom window icon
root.iconbitmap(icon_path)


# Custom Message Box function
def custom_messagebox(title, message, type="info"):
    box = Toplevel(root)
    box.title(title)
    box.geometry("400x200")
    center_window(box)

    message_label = tk.Label(box, text=message, font=("Arial", 12), wraplength=350, padx=10, pady=10)
    message_label.pack(pady=20)

    ok_button = tk.Button(box, text="OK", command=box.destroy, font=("Arial", 12))
    ok_button.pack(pady=10)

    box.transient(root)
    box.grab_set()
    root.wait_window(box)


# Load the top logo for the app
logo_image_path = resource_path('images/liberty-london.png')
logo_image = Image.open(logo_image_path)
logo_image = logo_image.resize((200, 50), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)

# Create a frame for the top logo
logo_frame = tk.Frame(root)
logo_frame.pack(pady=10)

# Add the top logo to the frame, centered
logo_label = tk.Label(logo_frame, image=logo_photo)
logo_label.pack(side=tk.TOP, anchor='center')

# Create a frame for the form fields
form_frame = tk.Frame(root)
form_frame.pack(pady=20)

# Initialize variable to store multiple image data
image_data_list = []
image_preview_label = None  # Label to display the preview images


# Function to open a file dialog to select multiple images
def select_image():
    global image_data_list, image_preview_label
    image_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg"),
            ("JPEG files", "*.jpeg"),
            ("All image files", "*.png *.jpg *.jpeg")
        ]
    )
    if image_paths:
        try:
            image_data_list = []
            for image_path in image_paths:
                image = Image.open(image_path).convert('RGB')
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                image_data_list.append(img_byte_arr.getvalue())

            image_preview = ImageTk.PhotoImage(Image.open(image_paths[0]).resize((200, 150)))
            if image_preview_label:
                image_preview_label.config(image=image_preview)
                image_preview_label.image = image_preview
            else:
                image_preview_label = Label(root, image=image_preview)
                image_preview_label.image = image_preview
                image_preview_label.pack(pady=10)

            custom_messagebox("Images Selected", f"{len(image_paths)} images have been stored.", "info")
        except Exception as e:
            custom_messagebox("Image Error", f"Error processing the images: {str(e)}", "error")
    else:
        custom_messagebox("No Image", "No image was selected.", "error")


# Create or connect to the SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# # Check if the 'category' column exists, and add it if not
# try:
#     c.execute("SELECT category FROM reports LIMIT 1")
# except sqlite3.OperationalError:
#     c.execute("ALTER TABLE reports ADD COLUMN category TEXT")

# Create a table with the crime reference number, category, and image column as BLOB
c.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        ref_number TEXT,
        date TEXT,
        time TEXT,
        reported_by TEXT,
        incident_details TEXT,
        action_taken TEXT,
        crime_ref_number TEXT,
        cctv_link TEXT,
        officer_name TEXT,
        category TEXT,
        image BLOB
    )
""")

# Function to clean text fields by removing newlines or unwanted characters
def clean_text(text):
    return text.replace('\n', ' ').replace('\r', '').strip()


# Function to get the last reference number saved in the database
def get_last_reference_number():
    c.execute("SELECT ref_number FROM reports ORDER BY rowid DESC LIMIT 1")
    last_ref = c.fetchone()
    if last_ref:
        return last_ref[0]  # Return as is
    else:
        return ""  # Return an empty string if no reference number is found


# Function to create the PDF report
def create_report_pdf(ref_number, date, time, reported_by, incident_details, action_taken, crime_ref_number, cctv_link,
                      officer_name, category, image_data_list):
    # Get save path
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save Report As"
    )

    # Debugging: Check the path in a message box or print statement
    if not save_path:
        custom_messagebox("Cancelled", "No path was selected, PDF save operation cancelled.", "info")
        return None

    # Print or message box the selected path (for debugging)
    print(f"Selected path: {save_path}")
    custom_messagebox("Save Path", f"Saving PDF to: {save_path}", "info")

    try:
        # Begin creating the PDF file
        pdf = canvas.Canvas(save_path, pagesize=A4)
        pdf.setTitle("Daily Occurrence Report")

        page_width, page_height = A4
        content_y = 700  # Starting point for content
        left_margin = 30  # Left margin for text placement

        # Add the top image (for PDF: liberty logo)
        # Use the resource_path function to reference the image
        pdf_image_path = resource_path('images/pdf_image.jpg')  # Use resource_path for the image

        try:
            pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)
        except Exception as e:
            custom_messagebox("Error", f"Failed to add image to the PDF: {str(e)}", "error")

        # pdf_image_path = 'images/pdf_image.jpg'  # Assuming the path is correctly set
        # pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)

        pdf.setFont("Helvetica-Bold", 18)
        text = "Daily Occurrence Report"
        text_width = pdf.stringWidth(text, "Helvetica-Bold", 18)
        x_position = (page_width - text_width) / 2
        pdf.drawString(x_position, 750, text)

        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0, 0, 0)  # Set font color to black

        # Add the report details with wrapping
        def wrap_text(pdf, text, max_width, content_y):
            wrapped_lines = utils.simpleSplit(text, 'Helvetica', 10, max_width)
            for line in wrapped_lines:
                if content_y < 150:  # Check if we need a new page
                    pdf.showPage()
                    content_y = 700  # Reset content_y for the new page below the top border
                    # Redraw the logo on the new page
                    pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)
                    pdf.setFont("Helvetica", 10)  # Reset text font size
                    pdf.setFillColorRGB(0, 0, 0)  # Set text color to black
                pdf.drawString(left_margin, content_y, line)
                content_y -= 15  # Move down after each line to avoid overlapping text
            return content_y

        # Draw report details in bold maroon color
        def draw_bold_maroon_text(pdf, text, x, y):
            pdf.setFont("Helvetica-Bold", 12)
            pdf.setFillColorRGB(0.5, 0, 0)  # Set color to maroon
            pdf.drawString(x, y, text)
            pdf.setFont("Helvetica", 10)  # Reset to normal text settings
            pdf.setFillColorRGB(0, 0, 0)  # Reset color to black

        # Simplified drawing of report details
        def draw_field(pdf, title, value, content_y):
            if content_y < 150:  # Check if we need a new page
                pdf.showPage()
                content_y = 700  # Reset content_y for the new page below the top border
                # Redraw the logo on the new page
                pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)
            draw_bold_maroon_text(pdf, title, left_margin, content_y)
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0, 0, 0)  # Set text color to black
            pdf.drawString(left_margin + 5 + pdf.stringWidth(title, "Helvetica-Bold", 12), content_y,
                           clean_text(value))  # Keep the value on the same line with minimal spacing
            return content_y - 25

        # Generate the PDF report
        content_y = draw_field(pdf, "Reference Number:", ref_number, content_y)
        content_y = draw_field(pdf, "Date:", date, content_y)
        content_y = draw_field(pdf, "Time:", time, content_y)
        content_y = draw_field(pdf, "Reported By:", reported_by, content_y)

        # Wrap long text fields for Details of Incident and Action Taken
        content_y -= 10

        draw_bold_maroon_text(pdf, "Details of Incident:", left_margin, content_y)
        content_y -= 15
        content_y = wrap_text(pdf, clean_text(incident_details), 500, content_y)
        content_y -= 15  # Extra space after the title

        draw_bold_maroon_text(pdf, "Action Taken:", left_margin, content_y)
        content_y -= 15
        content_y = wrap_text(pdf, clean_text(action_taken), 500, content_y)
        content_y -= 15  # Extra space after the title

        draw_bold_maroon_text(pdf, "Crime Reference Number:", left_margin, content_y)
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0, 0, 0)  # Set text color to black
        pdf.drawString(left_margin + 5 + pdf.stringWidth("Crime Reference Number:", "Helvetica-Bold", 12), content_y,
                       clean_text(crime_ref_number))
        content_y -= 23

        # Wrap long text for CCTV Footage Link and add hyperlink support
        if cctv_link:
            # Step 1: Clean and format the CCTV link
            absolute_cctv_path = os.path.abspath(clean_text(cctv_link))  # Get the absolute path
            formatted_link = f"file:///{absolute_cctv_path.replace('\\', '/')}"  # Format for Windows paths

            # Step 2: Add the text "CCTV Footage Link:" with the same maroon color and formatting
            draw_bold_maroon_text(pdf, "CCTV Footage Link:", left_margin, content_y)
            content_y -= 15  # Adjusted spacing after the title

            pdf.setFont("Helvetica", 10)  # Set text font size
            pdf.setFillColorRGB(0, 0, 0)  # Set text color to black

            # Step 3: Draw the clickable link text
            link_x = left_margin # + 150  # Position the link to the right of the label
            pdf.drawString(link_x, content_y, clean_text(cctv_link))  # Display the link text

            # Step 4: Calculate link width and create the clickable link area
            link_width = pdf.stringWidth(clean_text(cctv_link), "Helvetica", 10)
            pdf.linkURL(
                formatted_link,  # The formatted local file link
                (link_x, content_y - 5, link_x + link_width, content_y + 10),  # Define the clickable area
                relative=0  # Relative positioning
            )

            content_y -= 20  # Extra space after the clickable link
        else:
            # No CCTV link provided, so just display that information
            draw_bold_maroon_text(pdf, "CCTV Footage Link:", left_margin, content_y)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(left_margin + 150, content_y, "Not provided")
            content_y -= 20

        content_y = draw_field(pdf, "Officer Reporting Full Name:", officer_name, content_y)

        # Add the category field to the PDF
        content_y = draw_field(pdf, "Category:", category, content_y)

        # Move content_y down after the text content to create space for images
        content_y -= 115  # Increase spacing to ensure images are below the text

        # Add images to the PDF (if image_data_list is not empty)
        if image_data_list:
            try:
                # Set passport size dimensions for the images
                image_width = 100
                image_height = 120
                space_between_images = 10  # Add space between each image

                images_per_row = 4  # Number of images per row
                x_offset = left_margin  # Reset the x_offset to start from the left

                for index, image_data in enumerate(image_data_list):
                    if content_y < 200:  # Check if we need a new page
                        pdf.showPage()
                        content_y = 700  # Reset content_y for the new page below the top border
                        # Redraw the logo on the new page
                        pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)
                        x_offset = left_margin  # Reset x_offset for the new page

                    image = Image.open(io.BytesIO(image_data))
                    temp_image_path = os.path.join(os.getcwd(), f'temp_image_{index}.jpg')
                    image.save(temp_image_path, 'JPEG')

                    # Draw the image
                    pdf.drawImage(temp_image_path, x_offset, content_y, width=image_width, height=image_height)

                    # Increment the x_offset for the next image in the row
                    x_offset += image_width + space_between_images

                    # If 4 images have been placed, move to the next row
                    if (index + 1) % images_per_row == 0:
                        content_y -= image_height + space_between_images  # Move down to start the new row
                        x_offset = left_margin  # Reset the x_offset to start the new row

                    # Check if the images are near the bottom of the page and move to a new page if necessary
                    if content_y < 100:
                        pdf.showPage()  # Create a new page
                        content_y = 780  # Reset the content_y for the new page
                        # Redraw the logo on the new page
                        pdf.drawImage(pdf_image_path, 230, 780, width=150, height=50)
                        x_offset = left_margin  # Reset x_offset for the new page

                    # Clean up: remove the temporary image file
                    os.remove(temp_image_path)

            except Exception as e:
                print(f"Error adding image: {e}")
                custom_messagebox("Error", f"Failed to add image to the PDF: {e}", "error")

        # Add the generated timestamp at the bottom of the page
        pdf.setFont("Helvetica", 10)
        timestamp = datetime.now().strftime("%d-%m-%Y at %H:%M:%S")
        timestamp_text = f"Generated on: {timestamp} (UK GMT)"
        timestamp_width = pdf.stringWidth(timestamp_text, "Helvetica", 10)
        pdf.drawString((page_width - timestamp_width) / 2, 30, timestamp_text)

        pdf.save()
        return save_path

    except Exception as e:
        custom_messagebox("Error", f"Failed to save the PDF: {str(e)}", "error")
        return None

# Function to submit form data to the database and create the report PDF
def submit():
    global image_data_list, image_preview_label

    if not ref_entry.get() or not date_entry.get() or not time_entry.get():
        custom_messagebox("Error", "All fields must be filled!", "error")
        return

    try:
        date = datetime.strptime(date_entry.get(), "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError:
        custom_messagebox("Error", "Please enter the date in DD/MM/YYYY format.", "error")
        return

    time = time_entry.get()  # Use provided time directly as entered

    # Get category from dropdown or 'Other' field
    category = category_var.get()
    if category == 'Other':
        category = other_category_entry.get()

    # Handle the Crime Reference Number dropdown and text entry
    if crime_ref_var.get() == "Yes":
        crime_ref_number = crime_ref_entry.get()
        if not crime_ref_number:
            custom_messagebox("Error", "Please enter the crime reference number.", "error")
            return
    else:
        crime_ref_number = "N/A"

    # Handle the CCTV Link dropdown and text entry
    if cctv_var.get() == "Yes":
        cctv_link = cctv_entry.get()
        if not cctv_link:
            custom_messagebox("Error", "Please enter the CCTV footage link.", "error")
            return
    else:
        cctv_link = "N/A"

    # Insert the data into the database
    c.execute(
        "INSERT INTO reports (ref_number, date, time, reported_by, incident_details, action_taken, crime_ref_number, cctv_link, officer_name, category, image) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            ref_entry.get(),
            date,
            time,  # Use provided time
            reported_by_entry.get(),
            incident_text.get("1.0", tk.END),
            action_text.get("1.0", tk.END),
            crime_ref_number,
            cctv_link,
            officer_entry.get(),
            category,  # Save the selected category or 'Other' input
            image_data_list[0] if image_data_list else None
        )
    )

    conn.commit()

    # Create the PDF report
    filename = create_report_pdf(
        ref_entry.get(),
        date,
        time,  # Use provided time
        reported_by_entry.get(),
        incident_text.get("1.0", tk.END),
        action_text.get("1.0", tk.END),
        crime_ref_number,  # Crime reference number from dropdown
        cctv_link,  # CCTV Link from dropdown
        officer_entry.get(),
        category,  # Add category to PDF report
        image_data_list
    )

    if filename:
        custom_messagebox("Form Submitted", f"Thank you, the form has been submitted and saved as {filename}.", "info")
    else:
        custom_messagebox("Cancelled", "The operation was cancelled.", "info")

    result = messagebox.askquestion("Next Step", "Would you like to submit another report?", icon='question')
    if result == 'yes':
        # Clear all the fields for the next report
        ref_entry.delete(0, tk.END)
        ref_entry.insert(0, get_last_reference_number())  # Load the last reference number
        date_entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)
        reported_by_entry.delete(0, tk.END)
        incident_text.delete("1.0", tk.END)
        action_text.delete("1.0", tk.END)
        crime_ref_entry.delete(0, tk.END)
        cctv_entry.delete(0, tk.END)
        officer_entry.delete(0, tk.END)
        image_data_list.clear()
        if image_preview_label:
            image_preview_label.config(image="")
            image_preview_label.image = None
        if other_category_entry:
            other_category_entry.grid_remove()  # Hide the other category text entry box
    else:
        root.quit()


# GUI for the form fields and the image upload
tk.Label(form_frame, text="Ref Number:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
ref_entry = tk.Entry(form_frame)
ref_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
ref_entry.insert(0, get_last_reference_number())  # Load last reference number

tk.Label(form_frame, text="Date (DD/MM/YYYY):", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
date_entry = tk.Entry(form_frame)
date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(form_frame, text="Time (HH:MM:SS):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky='w')
time_entry = tk.Entry(form_frame)
time_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

tk.Label(form_frame, text="Reported By:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky='w')
reported_by_entry = tk.Entry(form_frame)
reported_by_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

tk.Label(form_frame, text="Details of Incident:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky='w')
incident_text = tk.Text(form_frame, wrap="word", width=40, height=6)
incident_text.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

tk.Label(form_frame, text="Action Taken:", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=5, sticky='w')
action_text = tk.Text(form_frame, wrap="word", width=40, height=6)
action_text.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

# Crime Reference Number dropdown
tk.Label(form_frame, text="Crime Reference Number:", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=5,
                                                                              sticky='w')
crime_ref_var = tk.StringVar()
crime_ref_options = ["Yes", "No"]
crime_ref_menu = tk.OptionMenu(form_frame, crime_ref_var, *crime_ref_options)
crime_ref_menu.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
crime_ref_entry = tk.Entry(form_frame)
crime_ref_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")
crime_ref_entry.grid_remove()  # Initially hidden

# CCTV Footage Link dropdown
tk.Label(form_frame, text="CCTV Footage Link:", font=("Arial", 12)).grid(row=8, column=0, padx=10, pady=5, sticky='w')
cctv_var = tk.StringVar()
cctv_options = ["Yes", "No"]
cctv_menu = tk.OptionMenu(form_frame, cctv_var, *cctv_options)
cctv_menu.grid(row=8, column=1, padx=10, pady=5, sticky="ew")
cctv_entry = tk.Entry(form_frame)
cctv_entry.grid(row=9, column=1, padx=10, pady=5, sticky="ew")
cctv_entry.grid_remove()  # Initially hidden

# Officer Reporting Full Name
tk.Label(form_frame, text="Officer Reporting Full Name:", font=("Arial", 12)).grid(row=10, column=0, padx=10, pady=5,
                                                                                   sticky='w')
officer_entry = tk.Entry(form_frame)
officer_entry.grid(row=10, column=1, padx=10, pady=5, sticky="ew")

# Category dropdown
tk.Label(form_frame, text="Category:", font=("Arial", 12)).grid(row=11, column=0, padx=10, pady=5, sticky='w')
category_var = tk.StringVar()
category_options = ['Arrest', 'Theft', 'Deter', 'Antisocial Behaviour', 'First Aid', 'Fire Activation', 'Suspect Package', 'Weekly Fire Bell Test', 'Other']  # Example categories
category_menu = tk.OptionMenu(form_frame, category_var, *category_options)
category_menu.grid(row=11, column=1, padx=10, pady=5, sticky="ew")

# 'Other' category entry box (hidden by default)
other_category_entry = tk.Entry(form_frame)
other_category_entry.grid(row=12, column=1, padx=10, pady=5, sticky="ew")
other_category_entry.grid_remove()  # Initially hidden

# Function to show or hide the 'Other' category entry based on selection
def show_other_category(*args):
    if category_var.get() == "Other":
        other_category_entry.grid()  # Show the text box if 'Other' is selected
    else:
        other_category_entry.grid_remove()  # Hide the text box for other selections

# Function to show or hide the crime reference number entry based on selection
def show_crime_ref_entry(*args):
    if crime_ref_var.get() == "Yes":
        crime_ref_entry.grid()  # Show the text box if 'Yes' is selected
    else:
        crime_ref_entry.grid_remove()  # Hide the text box for 'No'

# Function to show or hide the CCTV link entry based on selection
def show_cctv_entry(*args):
    if cctv_var.get() == "Yes":
        cctv_entry.grid()  # Show the text box if 'Yes' is selected
    else:
        cctv_entry.grid_remove()  # Hide the text box for 'No'

# Link the category dropdown to the show_other_category function
category_var.trace("w", show_other_category)
crime_ref_var.trace("w", show_crime_ref_entry)
cctv_var.trace("w", show_cctv_entry)

# Button to select multiple images
image_button = tk.Button(form_frame, text="Select Images", command=select_image)
image_button.grid(row=13, column=0, pady=10)

# Submit Button
submit_button = tk.Button(form_frame, text="Submit", command=submit)
submit_button.grid(row=13, column=1, pady=20, sticky="ew")

# Center the main window again after adding all widgets
center_window(root)

# Run trial check
def run_trial_check():
    check_trial()

run_trial_check()

# Run the Tkinter loop
root.mainloop()

# Close the database connection when the application closes
conn.close()
