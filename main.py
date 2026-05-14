import customtkinter as ctk
from PIL import Image
from io import BytesIO
import requests


class PokedexApp(ctk.CTk):
    API_URL = "https://pokeapi.co/api/v2/pokemon/{}"

    THEMES = {
        "Vermelho Clássico": {
            "window": "#1b0c0f", "container": "#290a10", "header": "#3b1118",
            "body": "#26080d", "panel": "#1d0a11", "screen": "#2d0d14",
            "stats": "#2a1118", "footer": "#3b1118", "text": "#f5e0d7",
            "secondary": "#ffd9d2", "accent": "#d32f2f", "accent_hover": "#eb423f",
            "border": "#80232d",
        },
        "Azul Clássico": {
            "window": "#08131f", "container": "#10213a", "header": "#152741",
            "body": "#0f1d33", "panel": "#12203a", "screen": "#18304d",
            "stats": "#172645", "footer": "#172a46", "text": "#d9e8f2",
            "secondary": "#b8d8ff", "accent": "#1f6fdc", "accent_hover": "#3b83ee",
            "border": "#1d4c85",
        },
        "Amarelo Clássico": {
            "window": "#2b210d", "container": "#3c2f14", "header": "#4d381a",
            "body": "#3f311c", "panel": "#463f24", "screen": "#503f24",
            "stats": "#4a3b1f", "footer": "#4e3720", "text": "#fff1d3",
            "secondary": "#ffe6a8", "accent": "#d1a92e", "accent_hover": "#efc132",
            "border": "#7f6c32",
        },
        "Preto Metálico": {
            "window": "#0f1012", "container": "#18191d", "header": "#202228",
            "body": "#16181d", "panel": "#1b1c22", "screen": "#23262e",
            "stats": "#1f2128", "footer": "#21242d", "text": "#e6e8ef",
            "secondary": "#bfc5d2", "accent": "#d32f2f", "accent_hover": "#f04b4b",
            "border": "#444b5b",
        },
    }

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Pokédex")
        self.geometry("980x640")
        self.resizable(False, False)
        self.center_window()

        try:
            self.iconbitmap("icon.ico")
        except Exception:
            pass

        self.current_theme = "Vermelho Clássico"
        self.theme_colors = self.THEMES[self.current_theme]

        self.current_id = 1
        self.current_pokemon_name = ""
        self.pokemon_image = None

        self.evolution_list = []
        self.evolution_index = 0

        self.variety_list = []
        self.current_variety = None
        self.is_shiny = False

        self.create_interface()
        self.apply_theme()
        self.fetch_pokemon(self.current_id)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_interface(self):
        self.container = ctk.CTkFrame(self, fg_color=self.theme_colors["container"], corner_radius=24, border_width=1, border_color=self.theme_colors["border"])
        self.container.pack(fill="both", expand=True, padx=16, pady=16)

        self.header_frame = ctk.CTkFrame(self.container, fg_color=self.theme_colors["header"], corner_radius=18, border_width=1, border_color=self.theme_colors["border"])
        self.header_frame.pack(fill="x", padx=16, pady=(16, 10))

        self.top_bar = ctk.CTkFrame(self.header_frame, fg_color=self.theme_colors["accent"], height=6, corner_radius=3)
        self.top_bar.grid(row=0, column=0, columnspan=5, sticky="ew", padx=18, pady=(12, 10))

        self.title_label = ctk.CTkLabel(self.header_frame, text="Pokédex", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.theme_colors["text"])
        self.title_label.grid(row=1, column=0, sticky="w", padx=(18, 12), pady=(0, 16))

        self.theme_label = ctk.CTkLabel(self.header_frame, text="Tema:", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.theme_colors["secondary"])
        self.theme_label.grid(row=1, column=1, sticky="e", padx=(0, 4), pady=(0, 16))

        self.theme_menu = ctk.CTkOptionMenu(self.header_frame, values=list(self.THEMES.keys()), width=160, corner_radius=12, fg_color=self.theme_colors["panel"], button_color=self.theme_colors["accent"], button_hover_color=self.theme_colors["accent_hover"], dropdown_fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"], command=self.change_theme)
        self.theme_menu.set(self.current_theme)
        self.theme_menu.grid(row=1, column=2, padx=(0, 10), pady=(0, 16), sticky="e")

        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Nome ou número do Pokémon", width=280, height=38, corner_radius=12, border_width=1, border_color=self.theme_colors["border"], fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"])
        self.search_entry.grid(row=1, column=3, padx=8, pady=(0, 16), sticky="ew")
        self.search_entry.bind("<Return>", self.on_enter_search)

        self.search_button = ctk.CTkButton(self.header_frame, text="Buscar", width=120, corner_radius=12, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.on_search_click)
        self.search_button.grid(row=1, column=4, padx=(8, 18), pady=(0, 16))
        self.header_frame.grid_columnconfigure(3, weight=1)

        self.body_frame = ctk.CTkFrame(self.container, fg_color=self.theme_colors["body"], corner_radius=18, border_width=1, border_color=self.theme_colors["border"])
        self.body_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.left_frame = ctk.CTkFrame(self.body_frame, fg_color=self.theme_colors["panel"], corner_radius=18)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(18, 12), pady=18)

        self.image_frame = ctk.CTkFrame(self.left_frame, fg_color=self.theme_colors["screen"], corner_radius=18, height=360, width=360, border_width=1, border_color=self.theme_colors["border"])
        self.image_frame.pack(padx=16, pady=16, fill="both", expand=True)

        self.screen_indicator = ctk.CTkLabel(self.image_frame, text="●   ●   ●", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.theme_colors["secondary"])
        self.screen_indicator.place(relx=0.55, rely=0.08, anchor="center")

        self.image_label = ctk.CTkLabel(self.image_frame, text="Carregando...", text_color=self.theme_colors["text"])
        self.image_label.place(relx=0.5, rely=0.55, anchor="center")

        self.variety_title = ctk.CTkLabel(self.left_frame, text="Formas / versões", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.theme_colors["secondary"])
        self.variety_title.pack(anchor="w", padx=18, pady=(0, 6))

        self.variety_menu = ctk.CTkOptionMenu(self.left_frame, values=["Padrão"], width=320, corner_radius=12, fg_color=self.theme_colors["stats"], button_color=self.theme_colors["accent"], button_hover_color=self.theme_colors["accent_hover"], dropdown_fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"], command=self.on_variety_change)
        self.variety_menu.set("Padrão")
        self.variety_menu.pack(padx=16, pady=(0, 16), fill="x")

        self.right_frame = ctk.CTkFrame(self.body_frame, fg_color=self.theme_colors["panel"], corner_radius=18)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 18), pady=18)

        self.name_label = ctk.CTkLabel(self.right_frame, text="Nome do Pokémon", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.theme_colors["text"])
        self.name_label.pack(anchor="w", padx=22, pady=(24, 6))

        self.number_label = ctk.CTkLabel(self.right_frame, text="#000", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.theme_colors["secondary"])
        self.number_label.pack(anchor="w", padx=22, pady=(0, 18))

        self.stats_frame = ctk.CTkFrame(self.right_frame, fg_color=self.theme_colors["stats"], corner_radius=18, border_width=1, border_color=self.theme_colors["border"])
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 18))

        self.type_label = ctk.CTkLabel(self.stats_frame, text="Tipo: —", font=ctk.CTkFont(size=14), text_color=self.theme_colors["text"], anchor="w")
        self.type_label.pack(fill="x", padx=16, pady=(16, 8))

        self.height_label = ctk.CTkLabel(self.stats_frame, text="Altura: — m", font=ctk.CTkFont(size=14), text_color=self.theme_colors["text"], anchor="w")
        self.height_label.pack(fill="x", padx=16, pady=4)

        self.weight_label = ctk.CTkLabel(self.stats_frame, text="Peso: — kg", font=ctk.CTkFont(size=14), text_color=self.theme_colors["text"], anchor="w")
        self.weight_label.pack(fill="x", padx=16, pady=(4, 16))

        abilities_frame = ctk.CTkFrame(self.right_frame, fg_color=self.theme_colors["stats"], corner_radius=18, border_width=1, border_color=self.theme_colors["border"])
        abilities_frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        abilities_title = ctk.CTkLabel(abilities_frame, text="Habilidades", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.theme_colors["text"])
        abilities_title.pack(anchor="w", padx=16, pady=(16, 8))

        self.abilities_label = ctk.CTkLabel(abilities_frame, text="—", font=ctk.CTkFont(size=14), text_color=self.theme_colors["secondary"], wraplength=380, justify="left")
        self.abilities_label.pack(fill="both", padx=16, pady=(0, 16), expand=True)

        self.footer_frame = ctk.CTkFrame(self.container, fg_color=self.theme_colors["footer"], corner_radius=18, border_width=1, border_color=self.theme_colors["border"])
        self.footer_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.prev_button = ctk.CTkButton(self.footer_frame, text="Anterior", width=110, corner_radius=16, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.on_previous)
        self.prev_button.pack(side="left", padx=(20, 6), pady=14)

        self.prev_evolution_button = ctk.CTkButton(self.footer_frame, text="⬅ Evolução", width=120, corner_radius=16, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.on_previous_evolution)
        self.prev_evolution_button.pack(side="left", padx=6, pady=14)

        self.shiny_button = ctk.CTkButton(self.footer_frame, text="Shiny ✨: OFF", width=120, corner_radius=16, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.toggle_shiny)
        self.shiny_button.pack(side="left", padx=6, pady=14)

        self.next_button = ctk.CTkButton(self.footer_frame, text="Próximo", width=110, corner_radius=16, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.on_next)
        self.next_button.pack(side="right", padx=(6, 20), pady=14)

        self.next_evolution_button = ctk.CTkButton(self.footer_frame, text="Evolução ➜", width=120, corner_radius=16, fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"], command=self.on_next_evolution)
        self.next_evolution_button.pack(side="right", padx=6, pady=14)

        self.status_label = ctk.CTkLabel(self.footer_frame, text="", font=ctk.CTkFont(size=14), text_color=self.theme_colors["secondary"], anchor="center")
        self.status_label.pack(fill="x", padx=12, pady=(12, 8))

        self.body_frame.grid_columnconfigure(0, weight=1)
        self.body_frame.grid_columnconfigure(1, weight=1)

    def change_theme(self, value: str):
        if value in self.THEMES:
            self.current_theme = value
            self.apply_theme()

    def apply_theme(self):
        self.theme_colors = self.THEMES[self.current_theme]
        self.configure(fg_color=self.theme_colors["window"])
        self.container.configure(fg_color=self.theme_colors["container"], border_color=self.theme_colors["border"])
        self.header_frame.configure(fg_color=self.theme_colors["header"], border_color=self.theme_colors["border"])
        self.body_frame.configure(fg_color=self.theme_colors["body"], border_color=self.theme_colors["border"])
        self.left_frame.configure(fg_color=self.theme_colors["panel"])
        self.image_frame.configure(fg_color=self.theme_colors["screen"], border_color=self.theme_colors["border"])
        self.right_frame.configure(fg_color=self.theme_colors["panel"])
        self.stats_frame.configure(fg_color=self.theme_colors["stats"], border_color=self.theme_colors["border"])
        self.footer_frame.configure(fg_color=self.theme_colors["footer"], border_color=self.theme_colors["border"])
        self.top_bar.configure(fg_color=self.theme_colors["accent"])

        labels = [
            self.title_label, self.name_label, self.type_label, self.height_label, self.weight_label
        ]
        for label in labels:
            label.configure(text_color=self.theme_colors["text"])

        secondary_labels = [self.theme_label, self.number_label, self.abilities_label, self.status_label, self.screen_indicator, self.variety_title]
        for label in secondary_labels:
            label.configure(text_color=self.theme_colors["secondary"])

        self.search_entry.configure(border_color=self.theme_colors["border"], fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"])
        self.theme_menu.configure(fg_color=self.theme_colors["panel"], button_color=self.theme_colors["accent"], button_hover_color=self.theme_colors["accent_hover"], dropdown_fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"])
        self.variety_menu.configure(fg_color=self.theme_colors["stats"], button_color=self.theme_colors["accent"], button_hover_color=self.theme_colors["accent_hover"], dropdown_fg_color=self.theme_colors["panel"], text_color=self.theme_colors["text"])

        buttons = [self.search_button, self.prev_button, self.next_button, self.prev_evolution_button, self.next_evolution_button, self.shiny_button]
        for button in buttons:
            button.configure(fg_color=self.theme_colors["accent"], hover_color=self.theme_colors["accent_hover"])

    def on_search_click(self):
        query = self.search_entry.get().strip()
        if query:
            self.is_shiny = False
            self.fetch_pokemon(query)
        else:
            self.show_status("Digite o nome ou número do Pokémon.")

    def on_enter_search(self, event):
        self.on_search_click()

    def on_previous(self):
        if self.current_id > 1:
            self.is_shiny = False
            self.fetch_pokemon(self.current_id - 1)
        else:
            self.show_status("Este é o primeiro Pokémon da Pokédex.")

    def on_next(self):
        self.is_shiny = False
        self.fetch_pokemon(self.current_id + 1)

    def fetch_species_data(self, pokemon_data):
        species_url = pokemon_data.get("species", {}).get("url")
        if not species_url:
            return None
        response = requests.get(species_url, timeout=8)
        response.raise_for_status()
        return response.json()

    def fetch_evolution_chain(self, pokemon_data):
        try:
            species_data = self.fetch_species_data(pokemon_data)
            if not species_data:
                raise ValueError("Sem species data")

            evolution_url = species_data["evolution_chain"]["url"]
            response = requests.get(evolution_url, timeout=8)
            response.raise_for_status()
            evolution_data = response.json()

            evolutions = []

            def walk_chain(chain):
                evolutions.append(chain["species"]["name"])
                for evolution in chain.get("evolves_to", []):
                    walk_chain(evolution)

            walk_chain(evolution_data["chain"])

            self.evolution_list = evolutions
            current_species_name = pokemon_data.get("species", {}).get("name", pokemon_data.get("name", ""))
            self.evolution_index = self.evolution_list.index(current_species_name) if current_species_name in self.evolution_list else 0

        except Exception:
            self.evolution_list = []
            self.evolution_index = 0

    def fetch_varieties(self, pokemon_data):
        try:
            species_data = self.fetch_species_data(pokemon_data)
            if not species_data:
                raise ValueError("Sem species data")

            self.variety_list = [item["pokemon"]["name"] for item in species_data.get("varieties", [])]
            if not self.variety_list:
                self.variety_list = [pokemon_data["name"]]

            values = [self.format_pokemon_name(name) for name in self.variety_list]
            self.variety_menu.configure(values=values)

            current_name = pokemon_data.get("name", "")
            if current_name in self.variety_list:
                self.current_variety = current_name
                self.variety_menu.set(self.format_pokemon_name(current_name))
            else:
                self.current_variety = self.variety_list[0]
                self.variety_menu.set(self.format_pokemon_name(self.current_variety))

        except Exception:
            self.variety_list = [pokemon_data.get("name", "")]
            self.current_variety = pokemon_data.get("name", "")
            self.variety_menu.configure(values=[self.format_pokemon_name(self.current_variety)])
            self.variety_menu.set(self.format_pokemon_name(self.current_variety))

    def on_previous_evolution(self):
        if not self.evolution_list:
            self.show_status("Este Pokémon não possui evoluções conhecidas.")
            return

        if self.evolution_index > 0:
            self.evolution_index -= 1
            self.is_shiny = False
            self.fetch_pokemon(self.evolution_list[self.evolution_index])
        else:
            self.show_status("Este é o primeiro estágio da evolução.")

    def on_next_evolution(self):
        if not self.evolution_list:
            self.show_status("Este Pokémon não possui evoluções conhecidas.")
            return

        if self.evolution_index < len(self.evolution_list) - 1:
            self.evolution_index += 1
            self.is_shiny = False
            self.fetch_pokemon(self.evolution_list[self.evolution_index])
        else:
            self.show_status("Este é o estágio final da evolução.")

    def toggle_shiny(self):
        self.is_shiny = not self.is_shiny
        self.shiny_button.configure(text=f"Shiny ✨: {'ON' if self.is_shiny else 'OFF'}")
        self.fetch_pokemon(self.current_pokemon_name or self.current_id, update_varieties=False)

    def on_variety_change(self, selected_value):
        selected_name = self.unformat_pokemon_name(selected_value)
        if selected_name in self.variety_list:
            self.is_shiny = False
            self.fetch_pokemon(selected_name, update_varieties=False)

    def fetch_pokemon(self, identifier, update_varieties=True):
        self.show_status("Buscando dados...")
        try:
            response = requests.get(self.API_URL.format(str(identifier).lower()), timeout=8)
            if response.status_code == 200:
                data = response.json()
                self.update_display(data, update_varieties=update_varieties)
            elif response.status_code == 404:
                self.show_status("Pokémon não encontrado. Tente outro nome ou número.")
            else:
                self.show_status("Erro ao consultar a PokéAPI. Tente novamente mais tarde.")
        except requests.exceptions.RequestException:
            self.show_status("Falha de conexão. Verifique sua internet e tente novamente.")

    def update_display(self, data, update_varieties=True):
        self.current_id = data.get("id", self.current_id)
        self.current_pokemon_name = data.get("name", str(self.current_id))

        self.fetch_evolution_chain(data)
        if update_varieties:
            self.fetch_varieties(data)

        name = self.format_pokemon_name(data.get("name", "?"))
        number = data.get("id", 0)
        types = [item["type"]["name"].capitalize() for item in data.get("types", [])]
        height = data.get("height", 0) / 10
        weight = data.get("weight", 0) / 10
        abilities = [item["ability"]["name"].replace("-", " ").capitalize() for item in data.get("abilities", [])]

        self.name_label.configure(text=name)
        self.number_label.configure(text=f"#{number:03d}")
        self.type_label.configure(text=f"Tipo: {', '.join(types) if types else '—'}")
        self.height_label.configure(text=f"Altura: {height:.1f} m")
        self.weight_label.configure(text=f"Peso: {weight:.1f} kg")
        self.abilities_label.configure(text="\n".join(abilities) if abilities else "—")

        sprites = data.get("sprites", {})
        official_artwork = sprites.get("other", {}).get("official-artwork", {})

        if self.is_shiny:
            image_url = official_artwork.get("front_shiny") or sprites.get("front_shiny")
        else:
            image_url = official_artwork.get("front_default") or sprites.get("front_default")

        if image_url:
            self.load_image_from_url(image_url)
        else:
            self.image_label.configure(text="Imagem não disponível", image=None)
            self.pokemon_image = None

        self.shiny_button.configure(text=f"Shiny ✨: {'ON' if self.is_shiny else 'OFF'}")
        self.search_entry.delete(0, ctk.END)
        self.search_entry.insert(0, str(number))
        self.show_status("Pokémon carregado com sucesso.")

    def load_image_from_url(self, url):
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGBA")

            max_size = (280, 280)
            image.thumbnail(max_size, Image.LANCZOS)

            canvas = Image.new("RGBA", max_size, (0, 0, 0, 0))
            offset = ((max_size[0] - image.width) // 2, (max_size[1] - image.height) // 2)
            canvas.paste(image, offset, image)

            self.pokemon_image = ctk.CTkImage(light_image=canvas, size=max_size)
            self.image_label.configure(image=self.pokemon_image, text="")
        except requests.exceptions.RequestException:
            self.image_label.configure(text="Erro ao carregar imagem", image=None)
            self.pokemon_image = None

    def show_status(self, message: str):
        self.status_label.configure(text=message)

    @staticmethod
    def format_pokemon_name(name: str):
        return name.replace("-", " ").title()

    @staticmethod
    def unformat_pokemon_name(name: str):
        return name.replace(" ", "-").lower()


if __name__ == "__main__":
    app = PokedexApp()
    app.mainloop()
