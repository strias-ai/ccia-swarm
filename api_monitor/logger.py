import logging
import datetime

class Logger:
    def __init__(self, log_file='web_monitoring.log', level=logging.INFO):
        # Configurar el nivel de registro y el formato del mensaje
        logging.basicConfig(filename=log_file, level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    def log_info(self, message):
        """Registrar un mensaje de información."""
        logging.info(message)

    def log_warning(self, message):
        """Registrar un mensaje de advertencia."""
        logging.warning(message)

    def log_error(self, message):
        """Registrar un mensaje de error."""