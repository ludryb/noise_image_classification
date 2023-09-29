import tensorflow as tf
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
import requests
from tqdm import tqdm
import os


class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()

        self.title("Классификация изображений для заповедника")
        self.minsize(500, 200)
        self.resizable(width=False, height=False)
        self.choice_folder_with_images_label = tk.Label(self, text="Выберите папку с фотографиями", font=("Tahoma", 16))
        self.choice_folder_with_images_label.pack()
        self.choice_folder_with_images_button = tk.Button(
            self,
            text="Выбрать папку с изображениями",
            command=self.get_input_folder,
            font=("Tahoma", 12)
        )
        self.choice_folder_with_images_button.pack()
        self.choice_output_folder_label = tk.Label(self, text="Выберите папку для вывода результатов", font=("Tahoma", 16))
        self.choice_output_folder_label.pack()
        self.choice_output_folder_button = tk.Button(
            self,
            text="Выбрать папку для вывода данных",
            command=self.get_output_folder,
            font=("Tahoma", 12)
        )
        self.choice_output_folder_button.pack()
        self.classification_button = tk.Button(
            self,
            text="Классифицировать изображения",
            command=self.classification,
            font=("Tahoma", 12)
        )
        self.classification_button.pack()

    def get_input_folder(self):
        self.input_folder = fd.askdirectory()
        self.choice_folder_with_images_label.config(text=f"Изображения загружаются из папки:\n{self.input_folder}")

    def get_output_folder(self):
        self.output_folder = fd.askdirectory()
        self.choice_output_folder_label.config(text=f"Изображения выгружаются в папку:\n{self.output_folder}")
    
    def classification(self):
        if self.output_folder is not None and self.input_folder is not None:
            if not os.path.exists(self.output_folder + '/images_with_animals'):
                os.makedirs(self.output_folder + '/images_with_animals')
            if not os.path.exists(self.output_folder + '/images_without_animals'):
                os.makedirs(self.output_folder + '/images_without_animals')
            if not os.path.exists(self.output_folder + '/broken_images'):
                os.makedirs(self.output_folder + '/broken_images')


root = Root()
root.mainloop()
