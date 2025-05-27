file_path = r"C:\Users\ozy\Desktop\orion\Orion_B\venv\Lib\site-packages\bark\generation.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "checkpoint = torch.load(ckpt_path, map_location=device)" in content:
    fixed = content.replace(
        "checkpoint = torch.load(ckpt_path, map_location=device)",
        """import torch.serialization\nwith torch.serialization.safe_globals({"numpy.core.multiarray.scalar"}):\n    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)"""
    )
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed)
    print("✔️ generation.py dosyası başarıyla güncellendi.")
else:
    print("❌ Hedef kod satırı bulunamadı, muhtemelen zaten düzenlenmiş.")