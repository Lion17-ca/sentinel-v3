# managers/log_manager.py

import logging

class LogManager:
    def __init__(self, file_manager, encryption_manager, log_filename="log_chiffre.txt"):
        """
        Gère l'ajout, la lecture, l'effacement et l'export des logs.
        """
        self.file_manager = file_manager
        self.encryption_manager = encryption_manager
        self.log_filename = log_filename

    def add_log(self, text):
        enc = self.encryption_manager.encrypt(text)
        if enc:
            self.file_manager.append_file(self.log_filename, enc + "\n")
            return enc
        return None

    def get_logs(self):
        c = self.file_manager.read_file(self.log_filename)
        if c:
            return c.splitlines()
        return []

    def clear_logs(self):
        if self.file_manager.delete_file(self.log_filename):
            logging.info("Logs effacés.")
            return True
        logging.error("Erreur lors de l'effacement des logs.")
        return False

    def export_logs(self, path, encrypted=False):
        logs = self.get_logs()
        if not logs:
            return False
        try:
            with open(path, "w") as f:
                for line in logs:
                    if encrypted:
                        f.write(line + "\n")
                    else:
                        dec = self.encryption_manager.decrypt(line)
                        f.write(dec + "\n")
            logging.info(f"Logs exportés vers {path}.")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des logs: {e}")
            return False

    def search_in_logs(self, search_term):
        if not search_term:
            return []
        logs = self.get_logs()
        results = []
        for line in logs:
            dec = self.encryption_manager.decrypt(line)
            if search_term.lower() in dec.lower():
                results.append(dec)
        return results
