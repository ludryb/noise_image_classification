import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedStyle
import threading


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()

        self.title("Классификация изображений для заповедника")
        self.minsize(600, 300)
        self.resizable(width=False, height=False)

        style = ThemedStyle(self)
        style.set_theme("arc") 

        self.iconbitmap("icon.ico")  

        self.input_folder = None
        self.output_folder = None

        self.create_widgets()

    def create_widgets(self):
        header_label = ttk.Label(self, text="Классификация изображений для заповедника", font=("Arial", 16))
        header_label.pack(pady=20)

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.folder_label = ttk.Label(input_frame, text="", font=("Tahoma", 12))
        self.folder_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        choose_input_button = ttk.Button(input_frame, text="Выбрать папку с изображениями", command=self.get_input_folder)
        choose_input_button.grid(row=1, column=0, pady=10, padx=5, sticky="w")

        self.output_folder_label = ttk.Label(input_frame, text="", font=("Tahoma", 12))
        self.output_folder_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        choose_output_button = ttk.Button(input_frame, text="Выбрать папку для вывода данных", command=self.get_output_folder)
        choose_output_button.grid(row=3, column=0, pady=10, padx=5, sticky="w")

        classify_button = ttk.Button(self, text="Классифицировать изображения", command=self.classification)
        classify_button.pack(pady=20)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack()
        self.progress_label = ttk.Label(self, text="", font=("Tahoma", 12))
        self.progress_label.pack()

    def get_input_folder(self):
        self.input_folder = filedialog.askdirectory()
        self.folder_label.config(text=f"Изображения загружаются из папки:\n{self.input_folder}")

    def get_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.output_folder_label.config(text=f"Изображения выгружаются в папку:\n{self.output_folder}")

    def classification(self):
        if self.output_folder is not None and self.input_folder is not None:
            self.progress_label.config(text="Классификация изображений в процессе...")
            self.progress["value"] = 0
            self.progress["maximum"] = 100

            # Создайте новый поток для классификации изображений, передавая self как аргумент
            classification_thread = threading.Thread(target=self.process_images, args=(self,))
            classification_thread.start()

    
    def process_images(self, root):
        try:
            # Код классификации

            for i in range(1, 101):
                root.progress["value"] = i
                root.update_idletasks()

            # Обновление текстового поля
            root.progress_label.config(text="Классификация завершена")
            messagebox.showinfo("Завершено", "Классификация изображений завершена!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    root = Root()
    root.mainloop()

root = Root()
root.mainloop()