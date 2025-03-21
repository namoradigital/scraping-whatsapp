from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re  # Import untuk mencari pola nomor telepon

# Konfigurasi Chrome dan Selenium
options = Options()
options.add_argument("--user-data-dir=./chrome-data")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Pastikan path ChromeDriver benar
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# Buka WhatsApp Web
driver.get("https://web.whatsapp.com")

# Tunggu pengguna untuk scan QR Code
input("Tekan ENTER setelah login ke WhatsApp Web...")  

def get_group_numbers(group_name):
    """ Mengambil semua nomor dari grup dengan metode baru berdasarkan teks halaman """
    try:
        wait = WebDriverWait(driver, 15)

        print("🔍 Mencari grup...")
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
        search_box.clear()
        search_box.send_keys(group_name)
        time.sleep(3)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//header//span[@title]")))
            print("✅ Grup ditemukan!")
        except:
            print("❌ Grup tidak ditemukan, pastikan namanya benar!")
            return []

        print("📌 Mencoba membuka Info Grup...")

        try:
            header = wait.until(EC.presence_of_element_located((By.XPATH, "//header")))
            header.click()
            print("✅ Header grup berhasil diklik!")
            time.sleep(5)  # Tunggu agar Info Grup terbuka sepenuhnya

        except Exception as e:
            print(f"⚠️ Gagal mengklik header grup: {e}")
            return []

        print("📜 Mengambil teks dari halaman grup...")

        # Ambil seluruh teks dari halaman
        page_text = driver.find_element(By.TAG_NAME, "html").text

        # Gunakan regex untuk mencari semua nomor WhatsApp
        numbers = re.findall(r'\+62\s?\d{2,3}-?\d{3,4}-?\d{3,4}', page_text)
        numbers = [num.replace(" ", "").replace("-", "") for num in numbers]  # Format ulang nomor

        print(f"📋 Ditemukan {len(numbers)} nomor dalam grup.")

        return numbers
    except Exception as e:
        print(f"❌ Terjadi kesalahan umum: {e}")
        return []

# Input nama grup dari pengguna
group_name = input("Masukkan nama grup: ")
numbers = get_group_numbers(group_name)

# Simpan ke dalam file CSV
if numbers:
    with open("nomor_whatsapp.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nomor WhatsApp"])
        for number in numbers:
            writer.writerow([number])

    print(f"✅ Nomor berhasil disimpan dalam 'nomor_whatsapp.csv'.")
else:
    print("⚠️ Tidak ada nomor yang ditemukan atau terjadi kesalahan.")

# Tutup browser
driver.quit()
