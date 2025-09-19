import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import pandas as pd
from reportlab.pdfgen import canvas

class LJKScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LJK Scanner")
        self.root.minsize(800, 600)

        self.correct_answers = []
        self.score_per_question = 10
        self.detected_answers = []
        self.loaded_cv2_image = None

        self.benar = 0
        self.salah = 0
        self.skor_akhir = 0

        self.data_siswa = {"nama": "", "kelas": "", "mapel": ""}

        self.build_gui()

    def build_gui(self):
        self.header = tk.Label(self.root, text="📝 LJK SCANNER", font=("Arial", 20, "bold"), bg="#0d47a1", fg="white", pady=10)
        self.header.pack(fill="x")

        self.tabs = ttk.Notebook(self.root)
        self.tab_kunci = ttk.Frame(self.tabs)
        self.tab_scan = ttk.Frame(self.tabs)
        self.tab_hasil = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_kunci, text="Kunci Jawaban")
        self.tabs.add(self.tab_scan, text="Scan LJK")
        self.tabs.add(self.tab_hasil, text="Hasil")

        self.tabs.pack(fill="both", expand=True)

        self.build_tab_kunci()
        self.build_tab_scan()
        self.build_tab_hasil()

    def build_tab_kunci(self):
        ttk.Label(self.tab_kunci, text="Kunci Jawaban (pisahkan dengan koma):").pack(pady=10)
        self.kunci_entry = ttk.Entry(self.tab_kunci, width=70)
        self.kunci_entry.pack()

        ttk.Label(self.tab_kunci, text="Skor per Soal:").pack(pady=10)
        self.skor_spinbox = ttk.Spinbox(self.tab_kunci, from_=1, to=100, width=10)
        self.skor_spinbox.set(self.score_per_question)
        self.skor_spinbox.pack()

        ttk.Button(self.tab_kunci, text="Simpan Kunci", command=self.input_kunci_jawaban).pack(pady=10)

    def build_tab_scan(self):
        form = ttk.Frame(self.tab_scan, padding=10)
        form.pack(fill="x")

        self.nama_entry = self.create_labeled_entry(form, "Nama Siswa")
        self.kelas_entry = self.create_labeled_entry(form, "Kelas")
        self.mapel_entry = self.create_labeled_entry(form, "Mata Pelajaran")

        btn_frame = ttk.Frame(self.tab_scan)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="📷 Pindai LJK", command=self.load_image).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🔄 Simpan Data", command=self.update_data_siswa).pack(side="left", padx=10)

        self.canvas = tk.Canvas(self.tab_scan, width=600, height=400, bg="#e0e0e0")
        self.canvas.pack(pady=10)

    def build_tab_hasil(self):
        self.result_text = tk.Text(self.tab_hasil, height=20, width=90, font=("Courier", 10))
        self.result_text.pack(padx=20, pady=10)

        btns = ttk.Frame(self.tab_hasil)
        btns.pack(pady=10)

        ttk.Button(btns, text="✅ Koreksi", command=self.process_image).pack(side="left", padx=10)
        ttk.Button(btns, text="💾 Simpan Excel", command=self.simpan_hasil_excel).pack(side="left", padx=10)
        ttk.Button(btns, text="🖨️ Simpan PDF", command=self.cetak_laporan_pdf).pack(side="left", padx=10)

    def create_labeled_entry(self, parent, label_text):
        ttk.Label(parent, text=label_text).pack(anchor="w")
        entry = ttk.Entry(parent, width=60)
        entry.pack(fill="x", pady=5)
        return entry

    def update_data_siswa(self):
        self.data_siswa["nama"] = self.nama_entry.get()
        self.data_siswa["kelas"] = self.kelas_entry.get()
        self.data_siswa["mapel"] = self.mapel_entry.get()
        messagebox.showinfo("Data Siswa", "Data disimpan.")

    def input_kunci_jawaban(self):
        kunci_text = self.kunci_entry.get()
        if kunci_text:
            self.correct_answers = [x.strip().upper() for x in kunci_text.split(',')]
            try:
                self.score_per_question = int(self.skor_spinbox.get())
            except:
                self.score_per_question = 10
            messagebox.showinfo("Kunci Jawaban", f"{len(self.correct_answers)} kunci disimpan.")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not path:
            return
        self.loaded_cv2_image = cv2.imread(path)
        if self.loaded_cv2_image is None:
            messagebox.showerror("Gagal", "Gambar tidak dapat dimuat.")
            return
        img = cv2.cvtColor(self.loaded_cv2_image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (600, 400))
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.image = img_tk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.detect_answers()

    def detect_answers(self):
        self.detected_answers.clear()
        if self.loaded_cv2_image is None:
            return
        gray = cv2.cvtColor(self.loaded_cv2_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            ratio = w / float(h)
            area = cv2.contourArea(cnt)
            if 1000 < area < 10000 and 0.8 < ratio < 1.2:
                boxes.append((x, y, w, h))
        boxes = sorted(boxes, key=lambda b: (b[1] // 10 * 10, b[0]))
        for (x, y, w, h) in boxes:
            roi = thresh[y:y+h, x:x+w]
            total = w * h
            fill = cv2.countNonZero(roi)
            filled = fill / total > 0.5
            self.detected_answers.append("X" if filled else "-")

    def process_image(self):
        if not self.correct_answers or not self.detected_answers:
            messagebox.showwarning("Perhatian", "Kunci atau jawaban tidak lengkap.")
            return
        self.benar = 0
        self.salah = 0
        hasil = []
        for i in range(min(len(self.correct_answers), len(self.detected_answers))):
            key = self.correct_answers[i]
            ans = self.detected_answers[i]
            if ans == key:
                self.benar += 1
                hasil.append(f"{i+1:02}: {ans} ✔️")
            else:
                self.salah += 1
                hasil.append(f"{i+1:02}: {ans} ❌")
        self.skor_akhir = self.benar * self.score_per_question
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Nama  : {self.data_siswa['nama']}\n")
        self.result_text.insert(tk.END, f"Kelas : {self.data_siswa['kelas']}\n")
        self.result_text.insert(tk.END, f"Mapel : {self.data_siswa['mapel']}\n\n")
        self.result_text.insert(tk.END, "\n".join(hasil))
        self.result_text.insert(tk.END, f"\n\nBenar: {self.benar}\nSalah: {self.salah}\nSkor Akhir: {self.skor_akhir}")

    def simpan_hasil_excel(self):
        if not self.detected_answers:
            messagebox.showwarning("Kosong", "Tidak ada hasil untuk disimpan.")
            return
        data = {
            "Nama": [self.data_siswa["nama"]],
            "Kelas": [self.data_siswa["kelas"]],
            "Mapel": [self.data_siswa["mapel"]],
            "Benar": [self.benar],
            "Salah": [self.salah],
            "Skor": [self.skor_akhir],
            "Jawaban": [",".join(self.detected_answers)]
        }
        df = pd.DataFrame(data)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("Sukses", "Disimpan ke Excel.")

    def cetak_laporan_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return
        c = canvas.Canvas(path)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 800, "LAPORAN KOREKSI LJK")
        c.setFont("Helvetica", 12)
        c.drawString(100, 770, f"Nama  : {self.data_siswa['nama']}")
        c.drawString(100, 750, f"Kelas : {self.data_siswa['kelas']}")
        c.drawString(100, 730, f"Mapel : {self.data_siswa['mapel']}")
        c.drawString(100, 710, f"Benar : {self.benar}")
        c.drawString(100, 690, f"Salah : {self.salah}")
        c.drawString(100, 670, f"Skor  : {self.skor_akhir}")
        c.save()
        messagebox.showinfo("Sukses", "Laporan PDF berhasil disimpan.")

def main():
    root = tk.Tk()
    app = LJKScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
