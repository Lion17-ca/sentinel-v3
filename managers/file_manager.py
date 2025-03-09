# managers/file_manager.py

import os
import logging

class FileManager:
    def __init__(self, app_folder=".securetype"):
        """
        Gère la création d'un dossier d'application et propose des méthodes
        de lecture/écriture/effacement de fichiers.
        """
        self.app_folder = os.path.join(os.path.expanduser("~"), app_folder)
        try:
            os.makedirs(self.app_folder, exist_ok=True)
        except Exception as e:
            logging.error(f"Erreur lors de la création du dossier d'application: {e}")

    def get_file_path(self, filename):
        return os.path.join(self.app_folder, filename)

    def read_file(self, filename, binary=False):
        path = self.get_file_path(filename)
        mode = "rb" if binary else "r"
        if os.path.exists(path):
            try:
                with open(path, mode) as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Erreur de lecture du fichier {filename}: {e}")
        return None

    def write_file(self, filename, content, binary=False):
        path = self.get_file_path(filename)
        mode = "wb" if binary else "w"
        try:
            with open(path, mode) as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Erreur d'écriture dans le fichier {filename}: {e}")

    def append_file(self, filename, content, binary=False):
        path = self.get_file_path(filename)
        mode = "ab" if binary else "a"
        try:
            with open(path, mode) as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Erreur d'ajout dans le fichier {filename}: {e}")

    def delete_file(self, filename):
        path = self.get_file_path(filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du fichier {filename}: {e}")
        return False
