import sqlite3
import sqlite_utils

class DatabaseManager:
    def __init__(self, db_name="orion.db"):
        self.db_name = db_name
        self.db = None

    def connect(self):
        try:
            self.db = sqlite_utils.Database(self.db_name)
        except sqlite3.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            raise

    def disconnect(self):
        if self.db:
            self.db.close()

    def create_vector_table(self, table_name, dimension):
        try:
            self.connect()
            if self.db is None:
                raise Exception("Veritabanı bağlantısı kurulamadı.")
            self.db.create_table(table_name, {
                "id": int,
                "content": str,
                "embedding": str  # Vektörleri metin olarak saklayacağız (örneğin, "[0.1, 0.2, 0.3]")
            }, pk="id")
            self.disconnect()
        except Exception as e:
            print(f"Tablo oluşturma hatası: {e}")
            raise

    def add_data(self, table_name, content, embedding):
        try:
            self.connect()
            if self.db is None:
                raise Exception("Veritabanı bağlantısı kurulamadı.")
            data = {
                "content": content,
                "embedding": str(embedding)  # Vektörü metin olarak sakla
            }
            self.db[table_name].insert(data)
            self.disconnect()
        except Exception as e:
            print(f"Veri ekleme hatası: {e}")
            raise

    def search_vector(self, table_name, query_embedding, top_k=5):
        try:
            self.connect()
            if self.db is None:
                raise Exception("Veritabanı bağlantısı kurulamadı.")
            # Vektör araması için daha karmaşık bir yöntem gerekebilir,
            # çünkü sqlite_utils doğrudan vektör aramayı desteklemez.
            # Bu örnekte, sadece içeriğe göre FTS araması yapıyoruz.
            results = [] # Geçici olarak boş liste döndürüyoruz
            self.disconnect()
            return results
        except Exception as e:
            print(f"Vektör arama hatası: {e}")
            raise

    def is_indexed(self, table_name, column_name):
        try:
            self.connect()
            if self.db is None:
                raise Exception("Veritabanı bağlantısı kurulamadı.")
            
            # Sütunun indekslenip indekslenmediğini kontrol et
            index_info = self.db.execute(f"PRAGMA index_info('{table_name}_{column_name}_idx')").fetchone()
            self.disconnect()
            return index_info is not None
        except Exception as e:
            print(f"Indeks kontrol hatası: {e}")
            return False

    def execute_query(self, query):
        try:
            self.connect()
            if self.db is None:
                raise Exception("Veritabanı bağlantısı kurulamadı.")
            
            # SQL sorgusunu çalıştır ve sonuçları döndür
            cursor = self.db.execute(query)
            results = cursor.fetchall()
            self.disconnect()
            return results
        except Exception as e:
            print(f"Sorgu çalıştırma hatası: {e}")
            raise

# TODO: Voice Agent (Text-to-speech, Bark/TTS) optimizasyonu ve entegrasyonu yapılacak.
#       - Gerekirse yeni bir sınıf veya modül olarak ekleyin.
#       - API veya CLI üzerinden erişim için fonksiyonlar ekleyin.
#       - Testler ve hata yönetimi eklemeyi unutmayın.

# Örnek Kullanım:
if __name__ == '__main__':
    db_manager = DatabaseManager()
    try:
        db_manager.create_vector_table("my_table", 3) # Boyutu 3 olan bir vektör tablosu oluştur
        db_manager.add_data("my_table", "örnek veri", [0.1, 0.2, 0.3])
        db_manager.add_data("my_table", "başka bir örnek veri", [0.4, 0.5, 0.6])

        arama_sonucu = db_manager.search_vector("my_table", "örnek")
        print("Arama Sonuçları:")
        for sonuc in arama_sonucu:
            print(f"ID: {sonuc['id']}, İçerik: {sonuc['content']}")

        # is_indexed fonksiyonunu test et
        is_indexed = db_manager.is_indexed("my_table", "content")
        print(f"content sütunu indekslenmiş mi: {is_indexed}")

        # execute_query fonksiyonunu test et
        sorgu = "SELECT * FROM my_table"
        sonuclar = db_manager.execute_query(sorgu)
        print("Sorgu Sonuçları:")
        for sonuc in sonuclar:
            print(sonuc)

        # Veritabanı dosyasını sil (test amaçlı)
        import os
        db_manager.disconnect()
        os.remove("orion.db")
        print("Veritabanı dosyası silindi.")

    except Exception as e:
        print(f"Hata oluştu: {e}")