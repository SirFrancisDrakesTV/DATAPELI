import tkinter as tk
from tkinter import messagebox, filedialog
import json
import requests
from PIL import Image, ImageTk
import io
import os

class OBSPanel:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Configuración del Plugin Película OBS")
        self.ventana.geometry("800x600")

        # Frame para configuración con un fondo de color
        self.config_frame = tk.Frame(self.ventana, bg="#e6f7ff", padx=10, pady=10)
        self.config_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.config_frame, text="Configuración", font=("Arial", 16), bg="#e6f7ff").grid(row=0, column=0, columnspan=2)

        tk.Label(self.config_frame, text="API Key de OMDb:").grid(row=1, column=0, sticky=tk.W)
        self.omdb_entry = tk.Entry(self.config_frame)
        self.omdb_entry.grid(row=1, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Usuario de Twitter:").grid(row=2, column=0, sticky=tk.W)
        self.twitter_user_entry = tk.Entry(self.config_frame)
        self.twitter_user_entry.grid(row=2, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Contraseña de Twitter:").grid(row=3, column=0, sticky=tk.W)
        self.twitter_pass_entry = tk.Entry(self.config_frame, show='*')
        self.twitter_pass_entry.grid(row=3, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Usuario de Instagram:").grid(row=4, column=0, sticky=tk.W)
        self.instagram_user_entry = tk.Entry(self.config_frame)
        self.instagram_user_entry.grid(row=4, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Contraseña de Instagram:").grid(row=5, column=0, sticky=tk.W)
        self.instagram_pass_entry = tk.Entry(self.config_frame, show='*')
        self.instagram_pass_entry.grid(row=5, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Webhook de Discord:").grid(row=6, column=0, sticky=tk.W)
        self.discord_webhook_entry = tk.Entry(self.config_frame)
        self.discord_webhook_entry.grid(row=6, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Ruta de Guardado:").grid(row=7, column=0, sticky=tk.W)
        self.ruta_entry = tk.Entry(self.config_frame)
        self.ruta_entry.grid(row=7, column=1, sticky=tk.EW)
        
        tk.Button(self.config_frame, text="Seleccionar Carpeta", command=self.seleccionar_carpeta).grid(row=7, column=2)

        tk.Button(self.config_frame, text="Guardar Configuración", command=self.guardar_configuracion).grid(row=8, column=0, columnspan=3, pady=(10, 0))

        # Frame para la búsqueda y resultados
        self.search_frame = tk.Frame(self.ventana)
        self.search_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        tk.Label(self.search_frame, text="Buscar Película/Serie:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W)
        self.pelicula_entry = tk.Entry(self.search_frame)
        self.pelicula_entry.grid(row=0, column=1, sticky=tk.EW)
        self.pelicula_entry.bind("<Return>", lambda event: self.buscar_peliculas())

        tk.Button(self.search_frame, text="Buscar", command=self.buscar_peliculas).grid(row=0, column=2)

        # Opciones de tipo de búsqueda
        self.tipo_var = tk.StringVar(value="movie")
        tk.Radiobutton(self.search_frame, text="Película", variable=self.tipo_var, value="movie").grid(row=0, column=3, sticky=tk.W)
        tk.Radiobutton(self.search_frame, text="Serie", variable=self.tipo_var, value="series").grid(row=0, column=4, sticky=tk.W)

        # Frame para resultados con scrollbar
        self.resultados_frame = tk.Frame(self.search_frame)
        self.resultados_frame.grid(row=1, column=0, columnspan=5, sticky=tk.EW)

        self.resultados_listbox = tk.Listbox(self.resultados_frame, height=15)
        self.resultados_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.resultados_listbox.bind("<<ListboxSelect>>", self.seleccionar_pelicula)

        scrollbar = tk.Scrollbar(self.resultados_frame, command=self.resultados_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.resultados_listbox.config(yscrollcommand=scrollbar.set)

        # Frame para mostrar la información de la película
        self.info_frame = tk.Frame(self.ventana, padx=10, pady=10)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        tk.Label(self.info_frame, text="Información de la Película/Serie", font=("Arial", 16)).grid(row=0, column=0, columnspan=2)

        tk.Label(self.info_frame, text="Carátula:").grid(row=1, column=0)
        self.poster_label = tk.Label(self.info_frame, text="(Aquí se mostrará la carátula)")
        self.poster_label.grid(row=1, column=1)

        tk.Label(self.info_frame, text="Título:").grid(row=2, column=0, sticky=tk.W)
        self.titulo_label = tk.Label(self.info_frame, text="Título aquí")
        self.titulo_label.grid(row=2, column=1, sticky=tk.W)

        tk.Label(self.info_frame, text="Año:").grid(row=3, column=0, sticky=tk.W)
        self.ano_label = tk.Label(self.info_frame, text="Año aquí")
        self.ano_label.grid(row=3, column=1, sticky=tk.W)

        tk.Label(self.info_frame, text="Director:").grid(row=4, column=0, sticky=tk.W)
        self.director_label = tk.Label(self.info_frame, text="Director aquí")
        self.director_label.grid(row=4, column=1, sticky=tk.W)

        tk.Label(self.info_frame, text="Sinopsis:").grid(row=5, column=0, sticky=tk.W)
        self.sinopsis_label = tk.Label(self.info_frame, text="Sinopsis aquí", wraplength=400, justify="left")
        self.sinopsis_label.grid(row=5, column=1, sticky=tk.W)

        # Botones para modos
        tk.Button(self.ventana, text="Modo Normal", command=self.modo_normal).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self.ventana, text="Modo Automático", command=self.modo_automatico).pack(side=tk.LEFT, padx=10)

        self.resultados = []  # Para almacenar los resultados de la búsqueda

        # Configuración de columnas para que se expandan
        self.config_frame.columnconfigure(1, weight=1)
        self.search_frame.columnconfigure(1, weight=1)

    def mostrar_panel(self):
        self.ventana.mainloop()

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_entry.delete(0, tk.END)
            self.ruta_entry.insert(0, ruta)

    def guardar_configuracion(self):
        configuracion = {
            'OMDB_API_KEY': self.omdb_entry.get(),
            'Twitter_User': self.twitter_user_entry.get(),
            'Twitter_Pass': self.twitter_pass_entry.get(),
            'Instagram_User': self.instagram_user_entry.get(),
            'Instagram_Pass': self.instagram_pass_entry.get(),
            'Discord_Webhook': self.discord_webhook_entry.get(),
            'Ruta_Guardado': self.ruta_entry.get(),
        }
        with open('config.json', 'w') as f:
            json.dump(configuracion, f, indent=4)
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")

    def buscar_peliculas(self):
        pelicula = self.pelicula_entry.get()
        api_key = self.omdb_entry.get()
        tipo = self.tipo_var.get()

        url = f"http://www.omdbapi.com/?s={pelicula}&apikey={api_key}&type={tipo}"
        response = requests.get(url)

        if response.status_code == 200:
            datos = response.json()
            if datos['Response'] == "True":
                self.resultados = datos['Search']
                self.mostrar_resultados()
            else:
                messagebox.showerror("Error", "Película o serie no encontrada.")
        else:
            messagebox.showerror("Error", "No se pudo conectar a OMDb.")

    def mostrar_resultados(self):
        self.resultados_listbox.delete(0, tk.END)

        for resultado in self.resultados:
            titulo = f"{resultado['Title']} ({resultado['Year']})"
            self.resultados_listbox.insert(tk.END, titulo)

    def seleccionar_pelicula(self, event):
        seleccion = self.resultados_listbox.curselection()

        if seleccion:
            indice = seleccion[0]
            pelicula_seleccionada = self.resultados[indice]
            self.buscar_detalles_pelicula(pelicula_seleccionada['imdbID'])

    def buscar_detalles_pelicula(self, imdb_id):
        api_key = self.omdb_entry.get()
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            datos = response.json()
            self.mostrar_info_pelicula(datos)
        else:
            messagebox.showerror("Error", "No se pudo conectar a OMDb para obtener los detalles de la película/serie.")

    def mostrar_info_pelicula(self, datos):
        self.titulo_label.config(text=datos.get('Title', 'No disponible'))
        self.director_label.config(text=datos.get('Director', 'No disponible'))
        self.ano_label.config(text=datos.get('Year', 'No disponible'))

        # Traducir la sinopsis al español
        sinopsis = datos.get('Plot', 'No disponible')
        sinopsis_es = self.traducir_a_espanol(sinopsis)
        self.sinopsis_label.config(text=sinopsis_es)

        # Guardar información en archivos
        self.guardar_info_en_archivos(datos, sinopsis_es)

        self.mostrar_poster(datos.get('Poster', ''))

    def traducir_a_espanol(self, texto):
        url = f"https://api.mymemory.translated.net/get?q={texto}&langpair=en|es"
        response = requests.get(url)
        if response.status_code == 200:
            datos = response.json()
            return datos['responseData']['translatedText']
        return texto  # Retorna el texto original si no se pudo traducir

    def mostrar_poster(self, url):
        try:
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))
            image = image.resize((200, 300), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)

            self.poster_label.config(image=photo)
            self.poster_label.image = photo  # Mantener referencia
        except Exception as e:
            self.poster_label.config(text="No se pudo cargar la imagen.")

    def guardar_info_en_archivos(self, datos, sinopsis_es):
        ruta_guardado = self.ruta_entry.get()
        if not os.path.exists(ruta_guardado):
            messagebox.showerror("Error", "La ruta de guardado no existe.")
            return

        # Guardar la información en archivos de texto
        with open(os.path.join(ruta_guardado, "sinopsis.txt"), 'w', encoding='utf-8') as f:
            f.write(f"Sinopsis: {sinopsis_es}\n")  # Guardar la sinopsis traducida

        with open(os.path.join(ruta_guardado, "titulo.txt"), 'w', encoding='utf-8') as f:
            f.write(f"Título: {datos.get('Title', 'No disponible')}\n")  # Guardar el título

        with open(os.path.join(ruta_guardado, "director.txt"), 'w', encoding='utf-8') as f:
            f.write(f"Director: {datos.get('Director', 'No disponible')}\n")  # Guardar el director

        with open(os.path.join(ruta_guardado, "ano.txt"), 'w', encoding='utf-8') as f:
            f.write(f"Año: {datos.get('Year', 'No disponible')}\n")  # Guardar el año

        # Guardar la carátula
        poster_url = datos.get('Poster', '')
        if poster_url:
            try:
                response = requests.get(poster_url)
                if response.status_code == 200:
                    with open(os.path.join(ruta_guardado, "caratula.jpg"), 'wb') as img_file:
                        img_file.write(response.content)
            except Exception as e:
                messagebox.showerror("Error", "No se pudo guardar la carátula.")

    def modo_normal(self):
        messagebox.showinfo("Modo", "Modo Normal Activado")

    def modo_automatico(self):
        messagebox.showinfo("Modo", "Modo Automático Activado")

# Inicializa el panel
obs_panel = OBSPanel()
obs_panel.mostrar_panel()
