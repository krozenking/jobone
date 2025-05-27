import time
import random
import Log_Manager

class EnvironmentMonitoringAgent:
    def __init__(self, log_manager):
        self.log_manager = log_manager

    def collect_environmental_data(self):
        # Burada çevresel verileri toplamak için sensörlerden veya API'lerden veri çekilebilir.
        # Şimdilik rastgele değerler üretelim.
        temperature = random.randint(15, 30)  # 15-30 derece arası sıcaklık
        humidity = random.randint(40, 80)  # %40-%80 arası nem
        pressure = random.randint(980, 1020)  # 980-1020 hPa arası basınç

        data = {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure
        }
        return data

    def run(self):
        while True:
            environmental_data = self.collect_environmental_data()
            self.log_manager.process_log(f"Environmental Data: {environmental_data}")
            time.sleep(60)  # Her 60 saniyede bir veri topla

    def get_metrics(self):
        """
        Performans metriklerini ve operasyonel verileri döndürür.
        """
        return self.collect_environmental_data()

if __name__ == '__main__':
    # Loglama ayarlarını yapılandır
    Log_Manager.setup_logging()

    # Log_Manager örneğini oluştur
    log_manager = Log_Manager

    # EnvironmentMonitoringAgent örneğini oluştur
    agent = EnvironmentMonitoringAgent(log_manager)
    agent.run()