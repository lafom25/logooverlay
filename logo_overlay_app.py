import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os
import re
import threading

class LogoOverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gắn Logo vào Video (By Ly Han)")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.input_file = ""
        self.output_folder = ""
        self.format_var = tk.StringVar(value="MP4")
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file
        ttk.Label(main_frame, text="File đầu vào:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(main_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, pady=5)
        
        # Output folder
        ttk.Label(main_frame, text="Thư mục đầu ra:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Định dạng đầu ra", padding="10")
        format_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Radiobutton(format_frame, text="MXF", variable=self.format_var, value="MXF").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(format_frame, text="MP4", variable=self.format_var, value="MP4").pack(side=tk.LEFT, padx=20)
        
        # Button gắn logo
        self.process_btn = ttk.Button(main_frame, text="Gắn Logo", command=self.process_video)
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="Tiến độ: 0%", font=("Arial", 10, "bold"))
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Status textbox
        ttk.Label(main_frame, text="Trạng thái:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.status_text = tk.Text(main_frame, height=6, width=60, wrap=tk.WORD)
        self.status_text.grid(row=6, column=0, columnspan=3, pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, command=self.status_text.yview)
        scrollbar.grid(row=6, column=3, sticky=(tk.N, tk.S))
        self.status_text.config(yscrollcommand=scrollbar.set)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Chọn file video đầu vào",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.mxf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file = filename
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Chọn thư mục đầu ra")
        if folder:
            self.output_folder = folder
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            
    def update_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def update_progress(self, percent):
        self.progress_label.config(text=f"Tiến độ: {percent}%")
        self.root.update()
        
    def process_video(self):
        # Kiểm tra input
        if not self.input_file or not os.path.exists(self.input_file):
            messagebox.showerror("Lỗi", "Vui lòng chọn file đầu vào!")
            return
            
        if not self.output_folder or not os.path.exists(self.output_folder):
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đầu ra!")
            return
            
        # Kiểm tra logo.png
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if not os.path.exists(logo_path):
            messagebox.showerror("Lỗi", "Không tìm thấy file logo.png trong thư mục chương trình!")
            return
            
        # Kiểm tra ffmpeg.exe
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        if not os.path.exists(ffmpeg_path):
            messagebox.showerror("Lỗi", "Không tìm thấy file ffmpeg.exe trong thư mục chương trình!")
            return
            
        # Reset status
        self.status_text.delete(1.0, tk.END)
        self.update_progress(0)
        self.process_btn.config(state="disabled")
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self.run_ffmpeg, args=(ffmpeg_path, logo_path))
        thread.daemon = True
        thread.start()
        
    def run_ffmpeg(self, ffmpeg_path, logo_path):
        try:
            # Tạo tên file output
            input_basename = os.path.splitext(os.path.basename(self.input_file))[0]
            format_ext = self.format_var.get().lower()
            output_file = os.path.join(self.output_folder, f"{input_basename}_logo.{format_ext}")
            
            # Tạo lệnh ffmpeg
            if self.format_var.get() == "MXF":
                cmd = [
                    ffmpeg_path,
                    "-i", self.input_file,
                    "-i", logo_path,
                    "-filter_complex", "[0:v]overlay=0:0[v_out]",
                    "-map", "[v_out]",
                    "-map", "0:a",
                    "-f", "mxf",
                    "-c:v", "mpeg2video",
                    "-pix_fmt", "yuv422p",
                    "-profile:v", "422",
                    "-flags", "+ilme+ildct",
                    "-top", "1",
                    "-s", "1920x1080",
                    "-r", "25",
                    "-aspect", "16:9",
                    "-b:v", "25M",
                    "-minrate", "25M",
                    "-maxrate", "25M",
                    "-bufsize", "2M",
                    "-g", "15",
                    "-bf", "2",
                    "-c:a", "pcm_s24le",
                    "-ar", "48000",
                    "-ac", "2",
                    "-y",
                    output_file
                ]
            else:  # MP4
                cmd = [
                    ffmpeg_path,
                    "-i", self.input_file,
                    "-i", logo_path,
                    "-filter_complex", "[0:v][1:v]overlay=0:0",
                    "-c:v", "libx264",
                    "-crf", "23",
                    "-preset", "fast",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-y",
                    output_file
                ]
            
            self.update_status(f"Bắt đầu xử lý file: {os.path.basename(self.input_file)}")
            self.update_status(f"Định dạng đầu ra: {self.format_var.get()}")
            
            # Chạy ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Đọc duration từ stderr
            duration = None
            for line in process.stderr:
                if "Duration:" in line and not duration:
                    match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if match:
                        h, m, s = match.groups()
                        duration = int(h) * 3600 + int(m) * 60 + float(s)
                
                # Cập nhật progress
                if duration and "time=" in line:
                    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if match:
                        h, m, s = match.groups()
                        current_time = int(h) * 3600 + int(m) * 60 + float(s)
                        percent = min(int((current_time / duration) * 100), 99)
                        self.update_progress(percent)
            
            process.wait()
            
            if process.returncode == 0:
                self.update_progress(100)
                self.update_status("✓ Hoàn thành thành công!")
                self.update_status(f"File đầu ra: {output_file}")
                messagebox.showinfo("Thành công", "Gắn logo thành công!")
            else:
                self.update_status("✗ Có lỗi xảy ra trong quá trình xử lý!")
                messagebox.showerror("Lỗi", "Gắn logo thất bại!")
                
        except Exception as e:
            self.update_status(f"✗ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            
        finally:
            self.process_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogoOverlayApp(root)
    root.mainloop()