import json
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

CONFIG_FILE = "progress.json"  # 进度存储文件

class PDFReader:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 阅读器")
        self.root.geometry("800x600")

        self.canvas = tk.Label(root)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.btn_open = tk.Button(root, text="打开 PDF", command=self.open_pdf)
        self.btn_open.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_prev = tk.Button(root, text="上一页", command=self.prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_next = tk.Button(root, text="下一页", command=self.next_page)
        self.btn_next.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_save = tk.Button(root, text="保存进度", command=self.save_progress)
        self.btn_save.pack(side=tk.LEFT, padx=10, pady=5)

        self.doc = None
        self.page_num = 0
        self.file_path = None  # 记录 PDF 路径
        self.scale = 1.0  # 初始化缩放比例

        # 绑定鼠标滚轮事件来放大和缩小页面
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.file_path = file_path
            self.page_num = self.load_progress(file_path)  # 加载上次进度
            self.display_page()

    def display_page(self):
        if self.doc:
            page = self.doc[self.page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(self.scale, self.scale))  # 使用缩放矩阵调整页面大小
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # 获取页面的实际尺寸并根据比例调整图像大小
            new_width = int(pix.width)
            new_height = int(pix.height)

            img = img.resize((new_width, new_height), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.config(image=self.tk_img)

    def next_page(self):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.display_page()

    def prev_page(self):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.display_page()

    def save_progress(self):
        """保存当前 PDF 的阅读进度"""
        if self.file_path:
            progress_data = self.load_all_progress()
            progress_data[self.file_path] = self.page_num  # 存储当前页码
            with open(CONFIG_FILE, "w") as f:
                json.dump(progress_data, f)
            print(f"已保存进度：{self.page_num}")

    def load_progress(self, file_path):
        """加载已存储的阅读进度"""
        progress_data = self.load_all_progress()
        return progress_data.get(file_path, 0)

    def load_all_progress(self):
        """加载所有 PDF 的进度"""
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # 文件不存在时返回空字典

    def on_mouse_wheel(self, event):
        """鼠标滚轮事件：放大或缩小页面"""
        if event.delta > 0:  # 鼠标滚轮向上，放大
            self.scale *= 1.1  # 放大 10%
        else:  # 鼠标滚轮向下，缩小
            self.scale /= 1.1  # 缩小 10%
        self.display_page()  # 更新页面显示

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReader(root)
    root.mainloop()