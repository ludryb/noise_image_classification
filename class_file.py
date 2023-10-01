import tkinter as tk
from tkinter import filedialog as fd
import os
import pandas as pd

import torch
import torchvision.transforms as transforms
from tqdm import tqdm
from PIL import Image, ImageFile
import shutil
import requests
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import torch


ImageFile.LOAD_TRUNCATED_IMAGES = True
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

class Root(ThemedTk):
    def __init__(self):
        super(Root, self).__init__()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.animals_model = self.load_model('animals.pt')
        self.noise_model = self.load_model('noise.pt')

        self.set_theme("arc")  # Устанавливаем тему arc из библиотеки ttkthemes

        self.title("Классификация изображений для заповедника")
        self.minsize(600, 300)
        self.resizable(width=True, height=True)  # Разрешаем изменение размера окна

        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        header_label = ttk.Label(header_frame, text="Классификация изображений для заповедника", font=("Arial", 16))
        header_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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
        self.progress.pack(pady=5)

        self.progress_label = ttk.Label(self, text="", font=("Tahoma", 12))
        self.progress_label.pack(pady=5)


    def load_model(self, model_name):
        try:
            return torch.jit.load(model_name, map_location=self.device)
        except:
            url = f"http://b98766hs.beget.tech/zoo/{model_name}"
            response = requests.get(
                url,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
            )
            downloading_progress_bar = tqdm(
                desc=f"Downloading model {model_name}",
                total=int(response.headers.get('content-length', 0)),
                unit='iB',
                unit_scale=True
            )
            with open(model_name, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        downloading_progress_bar.update(len(chunk))
                        file.write(chunk)
            return torch.jit.load(model_name, map_location=self.device)

    def get_input_folder(self):
        self.input_folder = fd.askdirectory()
        self.choice_folder_with_images_label.config(text=f"Изображения загружаются из папки:\n{self.input_folder}")

    def get_output_folder(self):
        self.output_folder = fd.askdirectory()
        self.choice_output_folder_label.config(text=f"Результат выгружается в папку:\n{self.output_folder}")
    
    def classification(self):
        if self.output_folder is not None and self.input_folder is not None:
            if not os.path.exists(self.output_folder + '/images_with_animals'):
                os.makedirs(self.output_folder + '/images_with_animals')
            if not os.path.exists(self.output_folder + '/images_without_animals'):
                os.makedirs(self.output_folder + '/images_without_animals')
            if not os.path.exists(self.output_folder + '/broken_images'):
                os.makedirs(self.output_folder + '/broken_images')
            self.files = {}
            self.get_files(self.input_folder)
            if not os.path.exists(self.output_folder + '/tmp_files'):
                os.makedirs(self.output_folder + '/tmp_files')
            for file in tqdm(self.files, desc="Reparing files"):
                if not os.path.exists(self.output_folder + '/tmp_files' + self.files[file]['file_path'].replace(self.input_folder, '').replace(self.files[file]['file_name'], '')):
                    os.makedirs(self.output_folder + '/tmp_files' + self.files[file]['file_path'].replace(self.input_folder, '').replace(self.files[file]['file_name'], ''))
                Image.open(self.files[file]['file_path']).save(self.output_folder + '/tmp_files' + self.files[file]['file_path'].replace(self.input_folder, ''))
            self.save_csv()
            tqdm.pandas(desc="Noise prediction")
            self.data['broken'] = self.data['filenames'].progress_apply(self.do_predict_noise)
            tqdm.pandas(desc="Empty prediction")
            self.data['empty'] = self.data.progress_apply(self.do_predict_empty, axis=1)
            tqdm.pandas(desc="Animal prediction")
            self.data['animal'] = self.data.progress_apply(lambda x: 1 if x['broken'] == 0 and x['empty'] == 0 else 0, axis=1)
            tqdm.pandas(desc="Moving files")
            self.data.progress_apply(self.move_files, axis=1)
            self.data.to_csv(self.output_folder + '/submission.csv', index=False)
            shutil.rmtree(self.output_folder + '/tmp_files')
    
    def get_files(self, PATH):
        for file in os.listdir(PATH):
            if os.path.isdir(f"{PATH}/{file}"):
                self.get_files(f"{PATH}/{file}")
            else:
                self.files[len(self.files)] = {}
                self.files[len(self.files) - 1]['file_path'] = f"{PATH}/{file}"
                self.files[len(self.files) - 1]['file_name'] = f"{file}"
    
    def save_csv(self):
        file_paths = [self.files[file]['file_path'] for file in self.files]
        file_names = [self.files[file]['file_name'] for file in self.files]
        file_relative_path = [self.files[file]['file_path'].replace(self.input_folder, '') for file in self.files]
        data = {
#            'file_paths':file_paths,
            'file_names':file_names,
            'filenames':file_relative_path,
            'broken':[0] * len(file_paths),
            'empty':[0] * len(file_paths),
            'animal':[0] * len(file_paths)
        }
        self.data = pd.DataFrame(data)
    
    def do_predict_noise(self, PATH):
        transform = transforms.Compose([
            transforms.Resize((64,64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        _, predicted = torch.max(self.noise_model(transform(Image.open(self.output_folder + '/tmp_files' + PATH)).unsqueeze(0)), 1)
        return int(predicted[0])
    
    def do_predict_empty(self, row):
        if row['broken']:
            return 0
        PATH = row['filenames']
        transform = transforms.Compose([
            transforms.Resize((64,64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        _, predicted = torch.max(self.animals_model(transform(Image.open(self.output_folder + '/tmp_files' + PATH)).unsqueeze(0)), 1)
        return int(predicted[0])
    
    def move_files(self, row):
        if row['broken']:
            shutil.move(self.output_folder + '/tmp_files' + row['filenames'], self.output_folder + '/broken_images/' + row['file_names'])
        if row['empty']:
            shutil.move(self.output_folder + '/tmp_files' + row['filenames'], self.output_folder + '/images_without_animals/' + row['file_names'])
        if row['animal']:
            shutil.move(self.output_folder + '/tmp_files' + row['filenames'], self.output_folder + '/images_with_animals/' + row['file_names'])

root = Root()
root.mainloop()