import random
import urllib.parse

# --- LISTA MAESTRA DE CARPETAS ---
# Esta es la lista que me proporcionaste.
SONG_FOLDER_NAMES = [
    "A Familiar Room - Aaron Cherof",
    "Bromeliad - Aaron Cherof",
    "Crescent Dunes - Aaron Cherof",
    "Echo in the Wind - Aaron Cherof",
    "Featherfall - Aaron Cherof",
    "Precipice - Aaron Cherof",
    "Puzzlebox - Aaron Cherof",
    "Relic - Aaron Cherof",
    "Watcher - Aaron Cherof",
    "Alpha - C418",
    "Aria Math - C418",
    "Axolotl - C418",
    "Ballad of the Cats - C418",
    "Beginning 2 - C418",
    "Beginning - C418",
    "Biome Fest - C418",
    "Blind Spots - C418",
    "Blocks - C418",
    "Cat - C418",
    "Chirp - C418",
    "Chris - C418",
    "Clark - C418",
    "Concrete Halls - C418",
    "Danny - C418",
    "Dead Voxel - C418",
    "Death - C418",
    "Dog - C418",
    "Door - C418",
    "Dragon Fish - C418",
    "Dreiton - C418",
    "Droopy Likes Ricochet - C418",
    "Droopy Likes Your Face - C418",
    "Dry Hands - C418",
    "Eleven - C418",
    "Excuse - C418",
    "Far - C418",
    "Flake - C418",
    "Floating Trees - C418",
    "Haggstrom - C418",
    "Haunt Muskie - C418",
    "Intro - C418",
    "Key - C418",
    "Ki - C418",
    "Kyoto - C418",
    "Living Mice - C418",
    "Mall - C418",
    "Mellohi - C418",
    "Mice on Venus - C418",
    "Minecraft - C418",
    "Moog City 2 - C418",
    "Moog City - C418",
    "Mutation - C418",
    "Oxygène - C418",
    "Shuniji - C418",
    "Stal - C418",
    "Strad - C418",
    "Subwoofer Lullaby - C418",
    "Sweden - C418",
    "Taswell - C418",
    "The End - C418",
    "Thirteen - C418",
    "Wait - C418",
    "Ward - C418",
    "Warmth - C418",
    "Wet Hands - C418",
    "Équinoxe - C418",
    "An Ordinary Day - Kumi Tanioka",
    "Comforting Memories - Kumi Tanioka",
    "Floating Dream - Kumi Tanioka",
    "komorebi - Kumi Tanioka",
    "pokopoko - Kumi Tanioka",
    "yakusoku - Kumi Tanioka",
    "Aerie - Lena Raine",
    "Ancestry - Lena Raine",
    "Chrysopoeia - Lena Raine",
    "Creator (Music Box Version) - Lena Raine",
    "Creator - Lena Raine",
    "Deeper - Lena Raine",
    "Eld Unknown - Lena Raine",
    "Endless - Lena Raine",
    "Firebugs - Lena Raine",
    "Infinite Amethyst - Lena Raine",
    "Labyrinthine - Lena Raine",
    "Left to Bloom - Lena Raine",
    "One More Day - Lena Raine",
    "otherside - Lena Raine",
    "Pigstep (Mono Mix) - Lena Raine",
    "Pigstep (Stereo Mix) - Lena Raine",
    "Rubedo - Lena Raine",
    "So Below - Lena Raine",
    "Stand Tall - Lena Raine",
    "Wending - Lena Raine",
    "Below and Above - Minecraft",
    "Broken Clocks - Minecraft",
    "Fireflies - Minecraft",
    "Lilypad - Minecraft",
    "O's Piano - Minecraft",
    "Tears - Minecraft",
    "Minecraft Lava Chicken (Original Game Soundtrack) - Minecraft",
    "Five - Samuel Åberg"
]

# --- (NUEVO) LISTA MAESTRA DE NOMBRES DE MP3 ---
# Esta lista DEBE tener el mismo orden y número de elementos que SONG_FOLDER_NAMES
SONG_MP3_FILENAMES = [
    "Aaron Cherof, Minecraft - A Familiar Room.mp3",
    "Aaron Cherof, Minecraft - Bromeliad.mp3",
    "Aaron Cherof, Minecraft - Crescent Dunes.mp3",
    "Aaron Cherof, Minecraft - Echo in the Wind.mp3",
    "Aaron Cherof, Minecraft - Featherfall.mp3",
    "Aaron Cherof, Minecraft - Precipice.mp3",
    "Aaron Cherof, Minecraft - Puzzlebox.mp3",
    "Aaron Cherof, Minecraft - Relic.mp3",
    "Aaron Cherof, Minecraft - Watcher.mp3",
    "C418 - Alpha.mp3",
    "C418 - Aria Math.mp3",
    "C418 - Axolotl.mp3",
    "C418 - Ballad of the Cats.mp3",
    "C418 - Beginning 2.mp3",
    "C418 - Beginning.mp3",
    "C418 - Biome Fest.mp3",
    "C418 - Blind Spots.mp3",
    "C418 - Blocks.mp3",
    "C418 - Cat.mp3",
    "C418 - Chirp.mp3",
    "C418 - Chris.mp3",
    "C418 - Clark.mp3",
    "C418 - Concrete Halls.mp3",
    "C418 - Danny.mp3",
    "C418 - Dead Voxel.mp3",
    "C418 - Death.mp3",
    "C418 - Dog.mp3",
    "C418 - Door.mp3",
    "C418 - Dragon Fish.mp3",
    "C418 - Dreiton.mp3",
    "C418 - Droopy Likes Ricochet.mp3",
    "C418 - Droopy Likes Your Face.mp3",
    "C418 - Dry Hands.mp3",
    "C418 - Eleven.mp3",
    "C418 - Excuse.mp3",
    "C418 - Far.mp3", # Corregido de tu lista (C418)
    "C418 - Flake.mp3",
    "C418 - Floating Trees.mp3",
    "C418 - Haggstrom.mp3",
    "C418 - Haunt Muskie.mp3",
    "C418 - Intro.mp3",
    "C418 - Key.mp3",
    "C418 - Ki.mp3",
    "C418 - Kyoto.mp3",
    "C418 - Living Mice.mp3",
    "C418 - Mall.mp3",
    "C418 - Mellohi.mp3",
    "C418 - Mice on Venus.mp3",
    "C418 - Minecraft.mp3",
    "C418 - Moog City 2.mp3",
    "C418 - Moog City.mp3",
    "C418 - Mutation.mp3",
    "C418 - Oxygène.mp3",
    "C418 - Shuniji.mp3",
    "C418 - Stal.mp3",
    "C418 - Strad.mp3",
    "C418 - Subwoofer Lullaby.mp3",
    "C418 - Sweden.mp3",
    "C418 - Taswell.mp3",
    "C418 - The End.mp3",
    "C418 - Thirteen.mp3",
    "C418 - Wait.mp3",
    "C418 - Ward.mp3",
    "C418 - Warmth.mp3",
    "C418 - Wet Hands.mp3",
    "C418 - Équinoxe.mp3",
    "Kumi Tanioka, Minecraft - An Ordinary Day.mp3",
    "Kumi Tanioka, Minecraft - Comforting Memories.mp3",
    "Kumi Tanioka, Minecraft - Floating Dream.mp3",
    "Kumi Tanioka, Minecraft - komorebi.mp3",
    "Kumi Tanioka, Minecraft - pokopoko.mp3",
    "Kumi Tanioka, Minecraft - yakusoku.mp3",
    "Lena Raine, Minecraft - Aerie.mp3",
    "Lena Raine, Minecraft - Ancestry.mp3",
    "Lena Raine, Minecraft - Chrysopoeia.mp3",
    "Lena Raine, Minecraft - Creator (Music Box Version).mp3",
    "Lena Raine, Minecraft - Creator.mp3",
    "Lena Raine, Minecraft - Deeper.mp3",
    "Lena Raine, Minecraft - Eld Unknown.mp3",
    "Lena Raine, Minecraft - Endless.mp3",
    "Lena Raine, Minecraft - Firebugs.mp3",
    "Lena Raine, Minecraft - Infinite Amethyst.mp3",
    "Lena Raine, Minecraft - Labyrinthine.mp3",
    "Lena Raine, Minecraft - Left to Bloom.mp3",
    "Lena Raine, Minecraft - One More Day.mp3",
    "Lena Raine, Minecraft - otherside.mp3",
    "Lena Raine, Minecraft - Pigstep (Mono Mix).mp3",
    "Lena Raine, Minecraft - Pigstep (Stereo Mix).mp3",
    "Lena Raine, Minecraft - Rubedo.mp3",
    "Lena Raine, Minecraft - So Below.mp3",
    "Lena Raine, Minecraft - Stand Tall.mp3",
    "Lena Raine, Minecraft - Wending.mp3",
    "Minecraft, Amos Roddy - Below and Above.mp3",
    "Minecraft, Amos Roddy - Broken Clocks.mp3",
    "Minecraft, Amos Roddy - Fireflies.mp3",
    "Minecraft, Amos Roddy - Lilypad.mp3",
    "Minecraft, Amos Roddy - O's Piano.mp3",
    "Minecraft, Amos Roddy - Tears.mp3",
    "Minecraft, Hyper Potions - Minecraft_ Lava Chicken (Original Game Soundtrack).mp3",
    "Samuel Åberg, Minecraft - Five.mp3"
]


# --- (ELIMINADO) ---
# MP3_FILENAME_EXCEPTIONS ya no es necesario.


class MusicLibrary:
    """
    Clase que maneja la lógica de CONSTRUIR la información de la
    biblioteca de música desde una lista estática de carpetas.
    
    NO reproduce música, solo genera la lista de reproducción.
    """
    
    def __init__(self, gitlab_raw_url):
        """
        Inicializa la biblioteca de música.
        
        :param gitlab_raw_url: La URL base "raw" de tu proyecto.
                               Ej: "https://gitlab.com/Kewz4/kewz-launcher/-/raw/main"
        """
        self.base_raw_url = gitlab_raw_url
        self.playlist = [] # Aquí se guardará la lista de diccionarios de canciones
        print("MusicLibrary (GitLab) inicializada con lista estática.")
        
        self._build_playlist_from_list()
        self.shuffle_playlist() # Mezclamos la lista al inicio

    def _build_playlist_from_list(self):
        """
        Construye la playlist internamente a partir de las listas globales emparejadas.
        """
        self.playlist = []
        
        # (NUEVO) Validar que las listas coincidan en tamaño
        if len(SONG_FOLDER_NAMES) != len(SONG_MP3_FILENAMES):
            print("="*50)
            print("ERROR CRÍTICO: ¡Las listas de carpetas y de MP3 no coinciden!")
            print(f"Número de carpetas: {len(SONG_FOLDER_NAMES)}")
            print(f"Número de archivos MP3: {len(SONG_MP3_FILENAMES)}")
            print("Por favor, asegúrate de que ambas listas en 'music_player.py' tengan exactamente el mismo número de elementos.")
            print("="*50)
            return # No construir la playlist

        # (NUEVO) Iterar usando 'zip' para emparejar carpeta con su mp3
        for folder_name, mp3_filename in zip(SONG_FOLDER_NAMES, SONG_MP3_FILENAMES):
            try:
                # 1. (NUEVO) Extraer Artista y Título desde el nombre del MP3
                # Esta es ahora la fuente de verdad para el texto mostrado
                mp3_name_no_ext = mp3_filename[:-4] # Quitar ".mp3"
                mp3_parts = mp3_name_no_ext.rsplit(' - ', 1)
                
                if len(mp3_parts) == 2:
                    final_artist = mp3_parts[0].strip() # Ej: "Lena Raine, Minecraft"
                    final_title = mp3_parts[1].strip()  # Ej: "Aerie"
                else:
                    # Fallback si el nombre del MP3 no tiene " - "
                    final_title = mp3_name_no_ext 
                    final_artist = "Artista Desconocido"
                    print(f"  -> ADVERTENCIA: Nombre de MP3 ('{mp3_filename}') no tiene ' - '. Título: '{final_title}'")

                # 2. Construir las URLs finales
                # Usar folder_name para la ruta de la carpeta
                safe_folder_path = urllib.parse.quote(f"songs/{folder_name}")
                # Usar mp3_filename para la ruta del archivo
                safe_mp3_filename = urllib.parse.quote(mp3_filename)
                
                # La URL de la carátula siempre es 'cover.jpg' (no necesita quote)
                cover_url = f"{self.base_raw_url}/{safe_folder_path}/cover.jpg"
                mp3_url = f"{self.base_raw_url}/{safe_folder_path}/{safe_mp3_filename}"
                
                # 3. Añadir el diccionario final a nuestra lista
                self.playlist.append({
                    "title": final_title,    # El título correcto (ej: "Aerie")
                    "artist": final_artist,  # El artista correcto (ej: "Lena Raine, Minecraft")
                    "src": mp3_url,          # El JS espera 'src'
                    "cover": cover_url       # El JS espera 'cover'
                })
                
            except Exception as e:
                print(f"Advertencia: No se pudo procesar la carpeta '{folder_name}'. Error: {e}")
        
        print(f"Éxito: Se construyó una lista de {len(self.playlist)} canciones.")

    def get_playlist(self):
        """
        Devuelve la lista de reproducción completa (lista de diccionarios).
        La lista ya puede estar mezclada si se llamó a shuffle_playlist().
        :return: (list)
        """
        return self.playlist
        
    def shuffle_playlist(self):
        """
        Reordena aleatoriamente la lista de reproducción.
        """
        if self.playlist:
            random.shuffle(self.playlist)
            print("Lista de reproducción mezclada.")

# --- Bloque de prueba ---
# Este código solo se ejecuta si corres "python music_player.py" directamente.
if __name__ == "__main__":
    
    print("--- Iniciando prueba de MusicLibrary (GitLab) ---")
    
    # URL base de tu repo (la misma para todos)
    REPO_RAW_URL = "https://gitlab.com/Kewz4/kewz-launcher/-/raw/main"
    
    # Simplemente inicializar la clase ahora construye todo
    library = MusicLibrary(gitlab_raw_url=REPO_RAW_URL)
    
    playlist = library.get_playlist()
    
    if playlist:
        print(f"\nSe construyeron {len(playlist)} canciones.")
        
        print("\n--- Datos de las primeras 5 canciones (ya mezcladas) ---")
        for i, song in enumerate(playlist[:5]):
            print(f"\nCanción {i+1}:")
            print(f"  Título: {song['title']}")
            print(f"  Artista: {song['artist']}")
            print(f"  URL MP3: {song['src']}")
            print(f"  URL Cover: {song['cover']}")
            
        # Prueba específica para tu excepción
        print("\n--- Buscando la canción 'Aerie' (Prueba de Artista Múltiple) ---")
        found = False
        for song in playlist:
            if song['title'] == 'Aerie':
                print("¡Encontrada!")
                print(f"  Título: {song['title']}")
                print(f"  Artista: {song['artist']}  <-- (Debería ser 'Lena Raine, Minecraft')")
                print(f"  URL MP3: {song['src']} <-- (Debería terminar en 'Lena%20Raine%2C%20Minecraft%20-%20Aerie.mp3')")
                found = True
                break
        if not found:
            print("No se encontró 'Aerie' en la lista (puede ser por la mezcla, vuelve a ejecutar)")
            
    else:
        print("\n--- Prueba fallida ---")
        print("La lista de carpetas 'SONG_FOLDER_NAMES' está vacía o hubo un error.")

