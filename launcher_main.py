    def _watch_log(self, log_path):
        """Vigila 'latest.log', inicia on_top, guarda tiempo de carga y llama a fadeOut."""
        log_filename = os.path.basename(log_path)
        self._log(f"Vigilando el log: {log_filename}")
        self._log(f"Buscando línea gatillo de cierre: '{LOG_TRIGGER_LINE}'")
        self._log(f"Buscando línea gatillo de audio (x2): '{UNMUTE_TRIGGER_LINE}'")


        file_handle = None
        self.on_top_thread = None

        try:
            start_wait = time.time()
            timeout_seconds = 120
            log_found = False
            while time.time() - start_wait < timeout_seconds:
                if not self.window or self.cancel_event.is_set() or self.game_ready_event.is_set():
                    self._log("Vigilante: Ventana cerrada o cancelado/listo, deteniendo espera.")
                    return
                if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
                    log_found = True
                    break
                time.sleep(0.5)

            if not log_found:
                self._log(f"Error: Timeout ({timeout_seconds}s) esperando por '{log_filename}'.")
                if self.window:
                    try:
                        self.window.evaluate_js('returnToPlayScreen()')
                        self._show_result(False, "Error de Inicio", f"Minecraft no generó el archivo '{log_filename}' en {timeout_seconds} segundos.")
                    except Exception: pass
                return

            self._log(f"Archivo '{log_filename}' detectado. Iniciando bucle 'Siempre Encima'...")
            self.on_top_thread = threading.Thread(target=self._keep_on_top, args=(self.hwnd,), name="OnTopThread")
            self.on_top_thread.daemon = True
            self.on_top_thread.start()

            self._log("Leyendo log en tiempo real...")
            time.sleep(0.1)
            file_handle = open(log_path, 'r', encoding='utf-8', errors='ignore')
            file_handle.seek(0, os.SEEK_END)
            self._log("Monitoreando nuevas líneas en tiempo real...")

            read_start_time = time.time()
            read_timeout_seconds = 300
            trigger_lines = [LOG_TRIGGER_LINE] # Solo el trigger de ModernFix
            line_batch = []
            last_batch_time = time.time()

            unmute_trigger_count = 0 # (NUEVO) Contador para el trigger de audio

            while True:
                if not self.window or self.cancel_event.is_set() or self.game_ready_event.is_set():
                    self._log("Vigilante: Ventana cerrada, cancelado o ya listo. Deteniendo lectura.")
                    return

                try:
                    line = file_handle.readline()
                except Exception as read_err:
                    self._log(f"Error leyendo línea del log: {read_err}. Reintentando...")
                    time.sleep(0.5)
                    try:
                        if file_handle.closed:
                            self._log("Reabriendo handle del log...")
                            file_handle = open(log_path, 'r', encoding='utf-8', errors='ignore')
                            file_handle.seek(0, os.SEEK_END)
                        else:
                            current_pos = file_handle.tell()
                            file_handle.seek(current_pos)
                        self._log("Re-sincronizado con el log...")
                    except Exception as reopen_err:
                        self._log(f"Fallo al re-sincronizar/reabrir log: {reopen_err}. Deteniendo vigilancia.")
                        raise
                    continue

                if line:
                    line_strip = line.strip()
                    if not line_strip: continue

                    # (MODIFICADO) Comprobar el trigger de audio y usar un contador
                    if UNMUTE_TRIGGER_LINE in line_strip:
                        if not self.unmute_event.is_set():
                            unmute_trigger_count += 1
                            self._log(f"[UNMUTE_TRIGGER] Detectado '{UNMUTE_TRIGGER_LINE}' ({unmute_trigger_count}/2)")
                            self._update_debug_panel(unmute_count=unmute_trigger_count)
                            if unmute_trigger_count >= 2:
                                self._log("[UNMUTE_TRIGGER] Límite alcanzado. Enviando señal para reactivar audio.")
                                self.unmute_event.set()
                                self._update_debug_panel(unmute_event=True)


                    read_start_time = time.time()
                    trigger_line_found = None
                    # (MODIFICADO) Solo buscar el único trigger de cierre
                    if trigger_lines[0] in line_strip:
                        trigger_line_found = trigger_lines[0]

                    if trigger_line_found:
                        if line_batch: self._log("\n".join(line_batch)); line_batch.clear()
                        self._log(f"[LOG_TRIGGER] {line_strip}")

                        match = re.search(r'Game took ([\d\.]+) seconds', line_strip)
                        if match:
                            try:
                                game_load_time = float(match.group(1))
                                self._log(f"¡Juego cargado en {game_load_time:.2f}s!")
                                threading.Thread(target=self._save_new_launch_time, args=(game_load_time,), daemon=True).start()
                            except Exception as e:
                                self._log(f"Error al parsear tiempo de carga: {e}")

                        if self.window:
                            try:
                                self.game_ready_event.set()
                                self._update_debug_panel(gameready_event=True)
                                self.window.evaluate_js('fadeLauncherOut()')
                            except Exception as e:
                                self._log(f"Error calling fadeLauncherOut: {e}")
                        return

                    is_spam = any(keyword in line_strip for keyword in self.LOG_IGNORE_KEYWORDS)
                    if is_spam: continue

                    line_batch.append(f"[LOG_PASSTHROUGH] {line_strip}")

                current_time = time.time()
                if len(line_batch) >= 20 or (not line and current_time - last_batch_time > 0.25):
                    if line_batch: self._log("\n".join(line_batch)); line_batch.clear()
                    last_batch_time = current_time

                if not line and current_time - read_start_time > read_timeout_seconds:
                    self._log(f"Error: Timeout ({read_timeout_seconds}s) de inactividad del log esperando trigger.")
                    if self.window:
                        try:
                            self.window.evaluate_js('returnToPlayScreen()')
                            self._show_result(False, "Error de Timeout", "El juego se inició pero no respondió en 5 minutos.")
                        except Exception as e: self._log(f"Error al llamar returnToPlayScreen: {e}")
                    return

                if not line: time.sleep(0.1)

        except FileNotFoundError as e:
            self._log(f"Error crítico: Archivo de log no encontrado o inaccesible: {e}")
            if self.window:
                try:
                    self.window.evaluate_js('returnToPlayScreen()')
                    self._show_result(False, "Error de Log", f"No se encontró o no se pudo leer '{log_filename}'.")
                except: pass
        except Exception as e:
            self._log(f"Error inesperado en el vigilante de log: {e}")
            import traceback
            self._log(traceback.format_exc())
            if self.window:
                try:
                    self.window.evaluate_js('returnToPlayScreen()')
                    self._show_result(False,"Error del Vigilante", f"Ocurrió un error leyendo el log: {e}")
                except: pass
        finally:
            if file_handle:
                try: file_handle.close()
                except: pass
            self._log("Vigilante de log finalizado. Señalando a OnTopThread para que pare...")
            self.game_ready_event.set()
            if self.on_top_thread and self.on_top_thread.is_alive():
                self._log("Esperando a que OnTopThread termine...")
                self.on_top_thread.join(timeout=1.0)
                if self.on_top_thread.is_alive():
                    self._log("ADVERTENCIA: OnTopThread no terminó a tiempo.")
                else:
                    self._log("OnTopThread join() completado.")
            
            if IS_WINDOWS and self.hwnd and win32gui:
                try:
                    if win32gui.IsWindow(self.hwnd):
                        win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                except: pass
            elif self.window:
                try: self.window.on_top = False
                except: pass
            self._log("Limpieza final de _watch_log completada.")