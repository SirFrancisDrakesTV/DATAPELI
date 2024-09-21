import tkinter as tk
from tkinter import messagebox, filedialog
import json
import requests
from PIL import Image, ImageTk
import io
import os
import obswebsocket
import obswebsocket.requests

class OBSPanel:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Configuración del Plugin Película OBS")
        self.ventana.geometry("800x800")

        # Frame para configuración
        self.config_frame = tk.Frame(self.ventana, bg="#e6f7ff", padx=10, pady=10)
        self.config_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.config_frame, text="Configuración", font=("Arial", 16), bg="#e6f7ff").grid(row=0, column=0, columnspan=2)

        # API Key de TMDB
        tk.Label(self.config_frame, text="API Key de TMDB:").grid(row=1, column=0, sticky=tk.W)
        self.tmdb_entry = tk.Entry(self.config_frame)
        self.tmdb_entry.grid(row=1, column=1, sticky=tk.EW)
        self.tmdb_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.tmdb_status_light.grid(row=1, column=2)
        tk.Button(self.config_frame, text="Probar API", command=self.probar_api).grid(row=1, column=3, pady=5)

        # Campos para WebSocket
        tk.Label(self.config_frame, text="IP del Servidor WebSocket:").grid(row=2, column=0, sticky=tk.W)
        self.ip_entry = tk.Entry(self.config_frame)
        self.ip_entry.grid(row=2, column=1, sticky=tk.EW)
        self.websocket_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.websocket_status_light.grid(row=2, column=2)

        tk.Label(self.config_frame, text="Puerto WebSocket:").grid(row=3, column=0, sticky=tk.W)
        self.puerto_entry = tk.Entry(self.config_frame)
        self.puerto_entry.grid(row=3, column=1, sticky=tk.EW)

        tk.Label(self.config_frame, text="Contraseña WebSocket:").grid(row=4, column=0, sticky=tk.W)
        self.contraseña_entry = tk.Entry(self.config_frame, show='*')
        self.contraseña_entry.grid(row=4, column=1, sticky=tk.EW)

        # Fuente VLC
        tk.Label(self.config_frame, text="Fuente VLC en OBS:").grid(row=5, column=0, sticky=tk.W)
        self.vlc_source_entry = tk.Entry(self.config_frame)
        self.vlc_source_entry.grid(row=5, column=1, sticky=tk.EW)
        self.vlc_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.vlc_status_light.grid(row=5, column=2)
        tk.Button(self.config_frame, text="Probar VLC", command=self.probar_vlc).grid(row=5, column=3, pady=5)

        # Webhook Discord
        tk.Label(self.config_frame, text="Webhook Discord:").grid(row=6, column=0, sticky=tk.W)
        self.discord_entry = tk.Entry(self.config_frame)
        self.discord_entry.grid(row=6, column=1, sticky=tk.EW)
        self.discord_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.discord_status_light.grid(row=6, column=2)
        tk.Button(self.config_frame, text="Probar Discord", command=self.probar_discord).grid(row=6, column=3, pady=5)

        # Usuario Instagram
        tk.Label(self.config_frame, text="Usuario Instagram:").grid(row=7, column=0, sticky=tk.W)
        self.instagram_user_entry = tk.Entry(self.config_frame)
        self.instagram_user_entry.grid(row=7, column=1, sticky=tk.EW)
        self.instagram_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.instagram_status_light.grid(row=7, column=2)
        tk.Button(self.config_frame, text="Probar Instagram", command=self.probar_instagram).grid(row=7, column=3, pady=5)

        # Usuario Twitter
        tk.Label(self.config_frame, text="Usuario Twitter:").grid(row=8, column=0, sticky=tk.W)
        self.twitter_user_entry = tk.Entry(self.config_frame)
        self.twitter_user_entry.grid(row=8, column=1, sticky=tk.EW)
        self.twitter_status_light = tk.Label(self.config_frame, text="●", fg="red", bg="#e6f7ff")
        self.twitter_status_light.grid(row=8, column=2)
        tk.Button(self.config_frame, text="Probar Twitter", command=self.probar_twitter).grid(row=8, column=3, pady=5)

        # Ruta para guardar archivos
        tk.Label(self.config_frame, text="Ruta para guardar archivos:").grid(row=9, column=0, sticky=tk.W)
        self.ruta_entry = tk.Entry(self.config_frame)
        self.ruta_entry.grid(row=9, column=1, sticky=tk.EW)
        tk.Button(self.config_frame, text="Seleccionar Carpeta", command=self.seleccionar_carpeta).grid(row=9, column=3)

        # Botones para conectar y desconectar
        tk.Button(self.config_frame, text="Conectar WebSocket", command=self.conectar_websocket).grid(row=10, column=0, pady=5)
        tk.Button(self.config_frame, text="Desconectar WebSocket", command=self.desconectar_websocket).grid(row=10, column=1, pady=5)

        # Indicadores de conexión
        self.websocket_status = tk.Label(self.config_frame, text="WebSocket: Desconectado", fg="red", bg="#e6f7ff")
        self.websocket_status.grid(row=11, column=0, columnspan=2, sticky=tk.W)

        # Indicador de estado de la fuente VLC
        self.vlc_status = tk.Label(self.config_frame, text="VLC: Desconectado", fg="red", bg="#e6f7ff")
        self.vlc_status.grid(row=15, column=0, columnspan=2, sticky=tk.W)

        # Frame para búsqueda de películas
        self.search_frame = tk.Frame(self.ventana)
        self.search_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        tk.Label(self.search_frame, text="Buscar Película/Serie:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W)
        self.pelicula_entry = tk.Entry(self.search_frame)
        self.pelicula_entry.grid(row=0, column=1, sticky=tk.EW)
        self.pelicula_entry.bind("<Return>", lambda event: self.buscar_peliculas(self.pelicula_entry.get()))

        tk.Button(self.search_frame, text="Buscar", command=lambda: self.buscar_peliculas(self.pelicula_entry.get())).grid(row=0, column=2)

        # Opciones de tipo de búsqueda
        self.tipo_var = tk.StringVar(value="movie")
        tk.Radiobutton(self.search_frame, text="Película", variable=self.tipo_var, value="movie").grid(row=0, column=3, sticky=tk.W)
        tk.Radiobutton(self.search_frame, text="Serie", variable=self.tipo_var, value="tv").grid(row=0, column=4, sticky=tk.W)

        # Botón para modo automático
        tk.Button(self.search_frame, text="Modo Automático", command=self.modo_automatico).grid(row=0, column=5)

        # Frame para resultados con scrollbar
        self.resultados_frame = tk.Frame(self.search_frame)
        self.resultados_frame.grid(row=1, column=0, columnspan=6, sticky=tk.EW)

        self.resultados_listbox = tk.Listbox(self.resultados_frame, height=15)
        self.resultados_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.resultados_listbox.bind("<<ListboxSelect>>", self.seleccionar_pelicula)

        scrollbar = tk.Scrollbar(self.resultados_frame, command=self.resultados_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.resultados_listbox.config(yscrollcommand=scrollbar.set)

        # Frame para mostrar la información de la película
        self.info_frame = tk.Frame(self.ventana, padx=10, pady=10)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        tk.Label(self.info_frame, text="Información de la Película/Serie", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self.poster_label = tk.Label(self.info_frame, text="Carátula aquí")
        self.poster_label.grid(row=1, column=0, rowspan=4, sticky=tk.W)

        tk.Label(self.info_frame, text="Título:").grid(row=1, column=1, sticky=tk.W)
        self.titulo_label = tk.Label(self.info_frame, text="Título aquí")
        self.titulo_label.grid(row=1, column=2, sticky=tk.W)

        tk.Label(self.info_frame, text="Año:").grid(row=2, column=1, sticky=tk.W)
        self.ano_label = tk.Label(self.info_frame, text="Año aquí")
        self.ano_label.grid(row=2, column=2, sticky=tk.W)

        tk.Label(self.info_frame, text="Director:").grid(row=3, column=1, sticky=tk.W)
        self.director_label = tk.Label(self.info_frame, text="Director aquí")
        self.director_label.grid(row=3, column=2, sticky=tk.W)

        tk.Label(self.info_frame, text="Sinopsis:").grid(row=4, column=1, sticky=tk.W)
        self.sinopsis_label = tk.Label(self.info_frame, text="Sinopsis aquí")
        self.sinopsis_label.grid(row=4, column=2, sticky=tk.W)

        # Ejecutar la aplicación
        self.ventana.mainloop()

    def guardar_informacion_pelicula(self, data):
        ruta = self.ruta_entry.get()
        if not os.path.exists(ruta):
            os.makedirs(ruta)

        archivo = os.path.join(ruta, f"{data['title']}.json")
        with open(archivo, "w") as f:
            json.dump(data, f)

    def guardar_configuracion(self):
        configuracion = {
            "tmdb_api_key": self.tmdb_entry.get(),
            "ip_websocket": self.ip_entry.get(),
            "puerto_websocket": self.puerto_entry.get(),
            "contraseña_websocket": self.contraseña_entry.get(),
            "discord_webhook": self.discord_entry.get(),
            "instagram_user": self.instagram_user_entry.get(),
            "instagram_pass": self.instagram_pass_entry.get(),
            "twitter_user": self.twitter_user_entry.get(),
            "twitter_pass": self.twitter_pass_entry.get(),
            "vlc_source": self.vlc_source_entry.get(),
            "ruta_guardado": self.ruta_entry.get(),
        }
        with open("configuracion.json", "w") as f:
            json.dump(configuracion, f)
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_entry.delete(0, tk.END)
            self.ruta_entry.insert(0, carpeta)

    def conectar_websocket(self):
        ip = self.ip_entry.get()
        puerto = self.puerto_entry.get()
        contraseña = self.contraseña_entry.get()
        try:
            self.cliente = obswebsocket.obsws(ip, int(puerto), contraseña)
            self.cliente.connect()
            self.websocket_status.config(text="WebSocket: Conectado", fg="green")
            self.websocket_status_light.config(fg="green")
        except Exception:
            self.websocket_status.config(text="WebSocket: Desconectado", fg="red")
            self.websocket_status_light.config(fg="red")
            messagebox.showerror("Error", "No se pudo conectar al WebSocket.")

    def desconectar_websocket(self):
        try:
            self.cliente.disconnect()
            self.websocket_status.config(text="WebSocket: Desconectado", fg="red")
            self.websocket_status_light.config(fg="red")
        except Exception:
            messagebox.showerror("Error", "No se pudo desconectar del WebSocket.")

    def probar_api(self):
        api_key = self.tmdb_entry.get()
        if api_key:
            test_url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=es-ES"
            response = requests.get(test_url)
            if response.status_code == 200:
                self.tmdb_status_light.config(fg="green")
                messagebox.showinfo("Conexión API", "Conexión a la API de TMDB exitosa.")
            else:
                self.tmdb_status_light.config(fg="red")
                messagebox.showerror("Conexión API", f"Error al conectar a la API: {response.status_code}")
        else:
            self.tmdb_status_light.config(fg="red")
            messagebox.showerror("Conexión API", "Por favor, ingresa una API Key válida.")

    def probar_discord(self):
        discord_webhook = self.discord_entry.get()
        if discord_webhook:
            self.discord_status_light.config(fg="green")
        else:
            self.discord_status_light.config(fg="red")

    def probar_instagram(self):
        instagram_user = self.instagram_user_entry.get()
        instagram_pass = self.instagram_pass_entry.get()
        if instagram_user and instagram_pass:
            self.instagram_status_light.config(fg="green")
        else:
            self.instagram_status_light.config(fg="red")

    def probar_twitter(self):
        twitter_user = self.twitter_user_entry.get()
        twitter_pass = self.twitter_pass_entry.get()
        if twitter_user and twitter_pass:
            self.twitter_status_light.config(fg="green")
        else:
            self.twitter_status_light.config(fg="red")

    def probar_vlc(self):
        vlc_source = self.vlc_source_entry.get()
        if vlc_source:
            self.vlc_status_light.config(fg="green")
        else:
            self.vlc_status_light.config(fg="red")

    def buscar_peliculas(self, query):
        tipo = self.tipo_var.get()
        api_key = self.tmdb_entry.get()
        search_url = f"https://api.themoviedb.org/3/search/{tipo}?api_key={api_key}&query={query}&language=es-ES"
        response = requests.get(search_url)

        if response.status_code == 200:
            data = response.json()
            self.resultados_listbox.delete(0, tk.END)
            if data.get("results"):
                for pelicula in data["results"]:
                    titulo = pelicula["title"] if tipo == "movie" else pelicula["name"]
                    self.resultados_listbox.insert(tk.END, f"{titulo} ({pelicula['release_date'][:4]})")
            else:
                messagebox.showwarning("No encontrado", "No se encontraron resultados.")
        else:
            messagebox.showerror("Error", f"Error al buscar: {response.status_code}")

    def seleccionar_pelicula(self, event):
        try:
            seleccion = self.resultados_listbox.curselection()[0]
            pelicula = self.resultados_listbox.get(seleccion)
            titulo = pelicula.split(" (")[0]
            tipo = self.tipo_var.get()
            self.cargar_info_pelicula(titulo, tipo)
        except IndexError:
            pass

    def cargar_info_pelicula(self, titulo, tipo):
        api_key = self.tmdb_entry.get()
        search_url = f"https://api.themoviedb.org/3/search/{tipo}?api_key={api_key}&query={titulo}&language=es-ES"
        search_response = requests.get(search_url)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("results"):
                pelicula_id = search_data["results"][0]["id"]
                info_url = f"https://api.themoviedb.org/3/{tipo}/{pelicula_id}?api_key={api_key}&language=es-ES"
                info_response = requests.get(info_url)
                if info_response.status_code == 200:
                    data = info_response.json()
                    self.titulo_label.config(text=data.get("title", ""))
                    self.ano_label.config(text=data.get("release_date", "").split("-")[0])
                    
                    # Obtener el director de los créditos
                    credits_url = f"https://api.themoviedb.org/3/{tipo}/{pelicula_id}/credits?api_key={api_key}&language=es-ES"
                    credits_response = requests.get(credits_url)
                    if credits_response.status_code == 200:
                        credits_data = credits_response.json()
                        directors = [person['name'] for person in credits_data['crew'] if person['job'] == 'Director']
                        self.director_label.config(text=", ".join(directors) if directors else "Desconocido")
                    else:
                        self.director_label.config(text="Desconocido")

                    self.sinopsis_label.config(text=data.get("overview", ""))

                    # Guardar información de la película
                    self.guardar_informacion_pelicula(data)

                    # Mostrar el poster
                    poster_url = f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}"
                    if poster_url:
                        img_data = requests.get(poster_url).content
                        img = Image.open(io.BytesIO(img_data))
                        img = img.resize((150, 225), Image.ANTIALIAS)
                        photo = ImageTk.PhotoImage(img)
                        self.poster_label.config(image=photo)
                        self.poster_label.image = photo
                    else:
                        self.poster_label.config(text="No hay carátula disponible", image='', compound=tk.CENTER)
                else:
                    messagebox.showerror("Error", f"Error al obtener información: {info_response.status_code}")
            else:
                messagebox.showwarning("No encontrado", "No se encontró información para la película seleccionada.")
        else:
            messagebox.showerror("Error", f"Error al buscar la película: {search_response.status_code}")

    def modo_automatico(self):
        messagebox.showinfo("Modo Automático", "Modo automático activado (implementa tu lógica aquí).")

# Ejecutar la aplicación
app = OBSPanel()
