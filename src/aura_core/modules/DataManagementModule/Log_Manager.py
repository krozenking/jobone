import logging
import os
import datetime

# Loglama şemasını tanımla
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Orion log dizini
ORION_LOGS_DIR = 'orion_logs'
ERROR_ARCHIVE_DIR = os.path.join(ORION_LOGS_DIR, 'error_archive')

def setup_logging():
    """
    Loglama ayarlarını yapılandırır.
    """
    # Orion log dizinini oluştur
    if not os.path.exists(ORION_LOGS_DIR):
        os.makedirs(ORION_LOGS_DIR)

    # Hata arşivi dizinini oluştur
    if not os.path.exists(ERROR_ARCHIVE_DIR):
        os.makedirs(ERROR_ARCHIVE_DIR)

    # Temel loglama ayarlarını yapılandır
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def archive_error_log(log_message):
    """
    Hata loglarını arşivler.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"error_{timestamp}.log"
    log_filepath = os.path.join(ERROR_ARCHIVE_DIR, log_filename)

    try:
        with open(log_filepath, 'w', encoding='utf-8') as log_file:
            log_file.write(log_message)
        logging.info(f"Hata logu arşivlendi: {log_filepath}")
    except Exception as e:
        logging.error(f"Hata logu arşivlenirken hata oluştu: {e}")

def process_log(log_message, log_level=logging.INFO):
    """
    Log mesajını işler ve uygun şekilde kaydeder.
    """
    if log_level == logging.ERROR:
        logging.error(log_message)
        archive_error_log(log_message)
    else:
        logging.info(log_message)

if __name__ == '__main__':
    # Loglama ayarlarını yapılandır
    setup_logging()

    # Örnek log mesajları
    process_log("Sistem başlatıldı.")
    process_log("Bir uyarı oluştu.", log_level=logging.WARNING)
    process_log("Bir hata oluştu!", log_level=logging.ERROR)