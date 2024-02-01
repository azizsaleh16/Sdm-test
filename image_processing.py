import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime
import os

class ImageProcessing:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing")

        self.db_connection = mysql.connector.connect(
            host= "127.0.0.1",
            user= "root",
            passwd= "1234",
            database= "image_processing")
        self.cursor = self.db_connection.cursor()

        self.image_path = tk.StringVar()
        self.transformation_var = tk.StringVar()

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0)
        ttk.Button(self.main_frame, text="Select Image", command=self.select_image).grid(row=0, column=0, pady=10)
        ttk.Button(self.main_frame, text="History", command=self.show_history_page).grid(row=0, column=1, pady=10)
        ttk.Label(self.main_frame, text="Choose Transformation:").grid(row=1, column=0, pady=5)
        self.transformation_dropdown = ttk.Combobox(self.main_frame, textvariable=self.transformation_var, values=["Flipping", "Rotation", "Cropping"])
        self.transformation_dropdown.grid(row=1, column=1, pady=5)
        self.transformation_dropdown.bind("<<ComboboxSelected>>", self.show_argument_field)     
        self.processed_image_label = ttk.Label(self.main_frame)
        self.processed_image_label.grid(row=5, column=0, columnspan=2, pady=10)

    def show_history_page(self):
        self.history_frame = ttk.Frame(self.root, padding="10")
        self.history_frame.grid(row=0, column=0)
        ttk.Label(self.history_frame, text="Choose by Transformation:").grid(row=0, column=2, pady=10)
        self.show_history_table()
        self.filter_dropdown = ttk.Combobox(self.history_frame, values=["All", "Flipping", "Rotation", "Cropping"])
        self.filter_dropdown.grid(row=0, column=1, pady=5)
        self.filter_dropdown.bind("<<ComboboxSelected>>", self.show_history_table)
        self.history_table = ttk.Treeview(self.history_frame, columns=("id","Source Image", "Transformation", "Argument", "Destination Image", "Date of Creation"))
        self.history_table.grid(row=1, column=0, columnspan=5, pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.image_path.set(file_path)
            self.display_image(file_path)

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)
        label = ttk.Label(self.main_frame, image=img)
        label.image = img
        label.grid(row=5, column=0, columnspan=2, pady=10)

    def show_argument_field(self, event):
        selected_transformation = self.transformation_var.get()
        if selected_transformation == "Flipping":
            ttk.Label(self.main_frame, text="Choose options").grid(row=4, column=0, pady=5)
            selected_option = tk.StringVar()
            self.transformation_dropdown = ttk.Combobox(self.main_frame, textvariable=selected_option, values=["vertically", "horizontally"])
            self.transformation_dropdown.grid(row=4, column=1, pady=10)
            self.apply_button = ttk.Button(self.main_frame, text="Apply", command=lambda: self.flip_image(selected_option.get()))
            self.apply_button.grid(row=0, column=3, columnspan=2, pady=10)
        elif selected_transformation == "Rotation":
            degree = tk.IntVar()
            ttk.Label(self.main_frame, text="Enter Rotation degree:").grid(row=3, column=0, pady=10)
            self.degree_entry = ttk.Entry(self.main_frame, textvariable=degree)
            self.degree_entry.grid(row=3, column=1, pady=10)
            self.apply_button = ttk.Button(self.main_frame, text="Apply", command=lambda: self.rotate_image(degree.get()))
            self.apply_button.grid(row=0, column=3, columnspan=2, pady=10)
        elif selected_transformation == "Cropping":
            x1y1 = tk.IntVar()
            x1y2 = tk.IntVar()
            x2y1 = tk.IntVar()
            x2y2 = tk.IntVar()
            ttk.Label(self.main_frame, text="Enter Top Left point(X1Y1):").grid(row=3, column=0, pady=5)
            ttk.Label(self.main_frame, text="Enter Top Right point(X1Y2):").grid(row=3, column=2, pady=5)
            ttk.Label(self.main_frame, text="Enter Bottom Left point(X2Y1):").grid(row=4, column=0, pady=5)
            ttk.Label(self.main_frame, text="Enter Bottom Right Point (X2, Y2):").grid(row=4, column=2, pady=5)
            self.x1y1_entry = ttk.Entry(self.main_frame, textvariable=x1y1)
            self.x1y1_entry.grid(row=3, column=1, pady=5, sticky=tk.W)
            self.x1y2_entry = ttk.Entry(self.main_frame, textvariable=x1y2)
            self.x1y2_entry.grid(row=3, column=3, pady=5, sticky=tk.W)
            self.x2y1_entry = ttk.Entry(self.main_frame, textvariable=x2y1)
            self.x2y1_entry.grid(row=4, column=1, pady=5, sticky=tk.W)
            self.x2y2_entry = ttk.Entry(self.main_frame, textvariable=x2y2)
            self.x2y2_entry.grid(row=4, column=3, pady=5, sticky=tk.W)
            self.apply_button = ttk.Button(self.main_frame, text="Apply", command=lambda: self.crop_image(x1y1.get(), x1y2.get(), x2y1.get(), x2y2.get()))
            self.apply_button.grid(row=0, column=3, columnspan=2, pady=10)

    def flip_image(self, flip_option):
        image_path = self.image_path.get()
        img = Image.open(image_path)
        if flip_option == "vertically":
            img = img.flip()
        else:
            img = img.mirror()
        self.image_processing(img, "Flipping", flip_option)

    def rotate_image(self, degree):
        image_path = self.image_path.get()
        img = Image.open(image_path)
        img = img.rotate(degree)
        self.image_processing(img, "Rotation", str(degree))

    def crop_image(self, x1y1, x1y2, x2y1, x2y2):
        image_path = self.image_path.get()
        img = Image.open(image_path)
        img = img.crop((x1y1, x1y2, x2y1, x2y2))
        self.image_processing(img, "Cropping", f"({x1y1}, {x1y2}), ({x2y1}, {x2y2})")

    def image_processing(self, img, transformation, arguments):
        self.save_image(img)
        output_image_path = os.path.join("results", "output_image.jpg")
        self.save_to_database(self.image_path.get(), transformation, arguments, output_image_path)
        self.display_image(output_image_path)

    def save_image(self, img):
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(os.path.join("results", "output_image.jpg"))

    def save_to_database(self, source_image, transformation, arguments, destination_image):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO image (source_image, transformation, arguments, destination_image, creation_date) VALUES (%s, %s, %s, %s, %s)"
        values = (source_image, transformation, arguments, destination_image, current_time)
        self.cursor.execute(query, values)
        self.db_connection.commit()
        self.update_history_table()

    def show_history_table(self, event=None):
        filter_value = self.filter_dropdown.get()
        if filter_value == "All":
            query = "SELECT * FROM image ORDER BY creation_date DESC"
        else:
            query = "SELECT * FROM image WHERE transformation=%s ORDER BY creation_date DESC"
            self.cursor.execute(query, (filter_value,))
        records = self.cursor.fetchall()
        for record in records:
            self.history_table.insert("", "end", values=record)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessing(root)
    root.mainloop()
