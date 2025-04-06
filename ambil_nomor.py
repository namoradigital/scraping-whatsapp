import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re
import threading
import os

class WhatsAppExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Group Number Extractor")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.group_name = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.numbers_count = tk.IntVar(value=0)
        self.driver = None
        self.is_running = False
        
        # GUI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)
        
        ttk.Label(header_frame, text="WhatsApp Group Number Extractor", 
                 font=("Helvetica", 14, "bold")).pack()
        
        ttk.Label(header_frame, text="Extract phone numbers from WhatsApp groups", 
                 font=("Helvetica", 10)).pack(pady=5)
        
        # Main Content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill=tk.X)
        
        # Group Name Input
        ttk.Label(main_frame, text="Group Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        group_entry = ttk.Entry(main_frame, textvariable=self.group_name, width=40)
        group_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=15)
        
        self.start_btn = ttk.Button(button_frame, text="Start Extraction", command=self.start_extraction)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status, foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Label(results_frame, text="Numbers Found:").pack(side=tk.LEFT)
        ttk.Label(results_frame, textvariable=self.numbers_count).pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(self.root, text="Activity Log")
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def log_message(self, message, color="black"):
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_extraction(self):
        if not self.group_name.get():
            messagebox.showerror("Error", "Please enter a group name")
            return
            
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status.set("Running...")
        self.log_message("Starting extraction process...", "blue")
        
        # Run extraction in a separate thread
        threading.Thread(target=self.run_extraction, daemon=True).start()
        
    def stop_extraction(self):
        self.is_running = False
        self.status.set("Stopped")
        self.log_message("Process stopped by user", "red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def run_extraction(self):
        try:
            # Initialize Chrome driver
            options = Options()
            options.add_argument("--user-data-dir=./chrome-data")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service("/usr/local/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.log_message("Opening WhatsApp Web...", "blue")
            self.driver.get("https://web.whatsapp.com")
            
            self.log_message("Please scan QR code if needed...", "blue")
            # Wait for user to scan QR code
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            
            self.log_message("Logged in to WhatsApp Web", "green")
            
            # Get group numbers
            numbers = self.get_group_numbers(self.group_name.get())
            
            if numbers:
                self.numbers_count.set(len(numbers))
                self.log_message(f"Found {len(numbers)} numbers in the group", "green")
                
                # Save to CSV
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV Files", "*.csv")],
                    initialfile="whatsapp_numbers.csv"
                )
                
                if filename:
                    with open(filename, "w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(["Nomor WhatsApp"])
                        for number in numbers:
                            writer.writerow([number])
                    
                    self.log_message(f"Numbers saved to {filename}", "green")
                    messagebox.showinfo("Success", f"Successfully extracted {len(numbers)} numbers")
            else:
                self.log_message("No numbers found in the group", "red")
                messagebox.showinfo("Info", "No numbers found in the group")
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.is_running = False
            self.status.set("Ready")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def get_group_numbers(self, group_name):
        try:
            wait = WebDriverWait(self.driver, 15)
            numbers = []

            self.log_message(f"Searching for group: {group_name}", "blue")
            search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(3)
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//header//span[@title]")))
                self.log_message("Group found!", "green")
            except:
                self.log_message("Group not found, please check the name", "red")
                return []

            self.log_message("Opening group info...", "blue")
            try:
                header = wait.until(EC.presence_of_element_located((By.XPATH, "//header")))
                header.click()
                self.log_message("Group info opened", "green")
                time.sleep(5)
            except Exception as e:
                self.log_message(f"Failed to open group info: {e}", "red")
                return []

            self.log_message("Extracting numbers from page...", "blue")
            page_text = self.driver.find_element(By.TAG_NAME, "html").text
            numbers = re.findall(r'\+62\s?\d{2,3}-?\d{3,4}-?\d{3,4}', page_text)
            numbers = [num.replace(" ", "").replace("-", "") for num in numbers]

            return numbers
        except Exception as e:
            self.log_message(f"Error in extraction: {e}", "red")
            return []

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_extraction()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppExtractorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()