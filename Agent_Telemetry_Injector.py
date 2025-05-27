# Agent_Telemetry_Injector.py
import logging
import threading
import time

class AgentTelemetryInjector:
    def __init__(self, log_manager, agents, interval=60):
        """
        Ajanlardan ve bileşenlerden telemetri verilerini toplar ve Log_Manager'a iletir.

        Args:
            log_manager: Log_Manager örneği.
            agents: İzlenecek ajanların listesi.
            interval: Metrik toplama aralığı (saniye).
        """
        self.log_manager = log_manager
        self.agents = agents
        self.interval = interval
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()

    def collect_metrics(self):
        """
        Ajanlardan performans metriklerini ve operasyonel verileri toplar.
        """
        metrics = {}
        for agent in self.agents:
            try:
                # Ajanın metrik toplama metodunu çağır
                agent_metrics = agent.get_metrics()
                metrics[agent.__class__.__name__] = agent_metrics
            except Exception as e:
                self.logger.error(f"Ajan metrikleri toplanamadı {agent.__class__.__name__}: {e}")
        return metrics

    def send_metrics(self, metrics):
        """
        Toplanan metrikleri Log_Manager'a iletir.

        Args:
            metrics: Toplanan metriklerin sözlüğü.
        """
        try:
            self.log_manager.log_telemetry(metrics)
            self.logger.info("Telemetri verileri Log_Manager'a gönderildi.")
        except Exception as e:
            self.logger.error(f"Telemetri verileri Log_Manager'a gönderilemedi: {e}")

    def run(self):
        """
        Metrik toplama ve gönderme işlemini periyodik olarak çalıştırır.
        """
        self.logger.info("Telemetri enjektörü çalışıyor...")
        while not self.stop_event.is_set():
            metrics = self.collect_metrics()
            self.send_metrics(metrics)
            time.sleep(self.interval)
        self.logger.info("Telemetri enjektörü durduruldu.")

    def start(self):
        """
        Telemetri enjektörünü başlatır.
        """
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True  # Arka planda çalışmasını sağlar
        self.thread.start()

    def stop(self):
        """
        Telemetri enjektörünü durdurur.
        """
        self.stop_event.set()
        self.thread.join()


if __name__ == '__main__':
    # Örnek kullanım
    logging.basicConfig(level=logging.INFO)
    from Database_Manager import DatabaseManager  # Örnek olarak DatabaseManager'ı kullanıyoruz
    from Environment_Monitoring_Agent import EnvironmentMonitoringAgent

    # Log_Manager örneği oluştur (örnek olarak DatabaseManager'ı kullanıyoruz)
    log_manager = DatabaseManager()

    # İzlenecek ajanların listesi
    agents = [
        EnvironmentMonitoringAgent(log_manager),
        # Diğer ajanları buraya ekleyebilirsiniz
    ]

    # Telemetri enjektörü örneği oluştur
    telemetry_injector = AgentTelemetryInjector(log_manager, agents, interval=10)

    # Telemetri enjektörünü başlat
    telemetry_injector.start()

    # 30 saniye çalıştır
    time.sleep(30)

    # Telemetri enjektörünü durdur
    telemetry_injector.stop()