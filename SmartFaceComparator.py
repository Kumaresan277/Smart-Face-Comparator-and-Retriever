import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import face_recognition
import shutil
import threading

class FaceComparator:

    def __init__(self, master):
        self.master = master
        self.master.title("Smart Face Comparator")
        self.master.geometry("900x700")
        self.selected_image_paths = set()
        self.image_labels = []
        self.stop_comparison = False
        self.encoding_cache = {}

        self.create_header()
        self.create_gallery_container()

    def create_header(self):
        header_frame = tk.Frame(self.master, bg="#2a2d36", pady=10)
        header_frame.pack(fill="x")

        title_label = tk.Label(header_frame, text="Smart Face Comparator", font=("Arial", 20, "bold"), fg="white", bg="#2a2d36")
        title_label.pack(pady=5)

        button_frame = tk.Frame(header_frame, bg="#2a2d36")
        button_frame.pack()

        self.select_folder_button = tk.Button(button_frame, text="Select Folder", command=self.select_folder, bg="#4CAF50", fg="white", width=15)
        self.select_folder_button.pack(side="left", padx=5)

        self.compare_button = tk.Button(button_frame, text="Compare Faces", command=self.start_comparison_thread, bg="#2196F3", fg="white", width=15)
        self.compare_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Comparison", command=self.stop_comparison_process, bg="#f44336", fg="white", width=15)
        self.stop_button.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(header_frame, orient='horizontal', length=300, mode='determinate')
        self.progress.pack(pady=5)

    def create_gallery_container(self):
        self.gallery_frame = tk.Frame(self.master)
        self.gallery_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.gallery_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(self.gallery_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.image_folder = folder
            self.image_files = [f for f in os.listdir(folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.encoding_cache.clear()
            self.display_gallery()

    def display_gallery(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.image_labels = []
        for idx, file in enumerate(self.image_files):
            path = os.path.join(self.image_folder, file)
            img = Image.open(path).resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(self.scrollable_frame, image=photo, borderwidth=2, relief="solid", highlightthickness=0)
            label.image = photo
            label.grid(row=idx // 4, column=idx % 4, padx=10, pady=10)

            label.bind('<Button-1>', lambda e, idx=idx: self.toggle_selection(idx))
            self.image_labels.append(label)

    def toggle_selection(self, index):
        file_path = os.path.join(self.image_folder, self.image_files[index])
        label = self.image_labels[index]

        if file_path in self.selected_image_paths:
            self.selected_image_paths.remove(file_path)
            label.config(highlightthickness=0, highlightbackground="white")
        else:
            self.selected_image_paths.add(file_path)
            label.config(highlightthickness=4, highlightbackground="red")

    def start_comparison_thread(self):
        self.stop_comparison = False
        thread = threading.Thread(target=self.compare_faces)
        thread.start()

    def stop_comparison_process(self):
        self.stop_comparison = True

    def encode_image(self, path):
        if path in self.encoding_cache:
            return self.encoding_cache[path]

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            self.encoding_cache[path] = encodings[0]
            return encodings[0]
        return None

    def compare_faces(self):
        if len(self.selected_image_paths) < 1:
            messagebox.showinfo("Info", "Please select at least one image to compare against the folder.")
            return

        self.progress['value'] = 0
        self.progress['maximum'] = len(self.image_files)
        self.master.update_idletasks()

        selected_encodings = []
        for path in self.selected_image_paths:
            encoding = self.encode_image(path)
            if encoding is not None:
                selected_encodings.append((path, encoding))

        if not selected_encodings:
            messagebox.showinfo("Info", "No faces found in selected images.")
            self.progress['value'] = 0
            return

        remaining_files = [os.path.join(self.image_folder, f) for f in self.image_files]
        matched_images = set()

        for sel_path, sel_encoding in selected_encodings:
            next_remaining_files = []

            for path in remaining_files:
                if self.stop_comparison:
                    messagebox.showinfo("Stopped", "Comparison was stopped by the user.")
                    self.progress['value'] = 0
                    return

                target_encoding = self.encode_image(path)
                if target_encoding is not None:
                    result = face_recognition.compare_faces([sel_encoding], target_encoding)[0]
                    if result:
                        matched_images.add(path)
                    else:
                        next_remaining_files.append(path)
                else:
                    next_remaining_files.append(path)

                self.progress['value'] += 1
                self.master.update_idletasks()

            remaining_files = next_remaining_files

        self.progress['value'] = 0
        self.master.update_idletasks()

        if matched_images:
            self.show_matched_window(list(matched_images))
            messagebox.showinfo("Success", "Comparison completed!")
        else:
            messagebox.showinfo("Results", "No matches found.")

    def show_matched_window(self, matched_images):
        win = tk.Toplevel(self.master)
        win.title("Matched Images")
        win.geometry("650x650")

        header = tk.Label(win, text="Matched Images", font=("Arial", 16, "bold"), fg="white", bg="#4CAF50")
        header.pack(fill="x")

        frame = tk.Frame(win, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, path in enumerate(matched_images):
            img = Image.open(path).resize((220, 220), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(scrollable_frame, image=photo, borderwidth=1, relief="solid")
            label.image = photo
            label.grid(row=idx // 5, column=idx % 5, padx=10, pady=10)

        button_frame = tk.Frame(win, pady=10)
        button_frame.pack()

        tk.Button(button_frame, text="Copy", command=lambda: self.copy_images(matched_images), bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Move", command=lambda: self.move_images(matched_images), bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Share", command=self.share_placeholder, bg="#FFC107", fg="white", width=12).pack(side="left", padx=5)

    def copy_images(self, images):
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if destination:
            for path in images:
                shutil.copy(path, destination)
            messagebox.showinfo("Copied", "Images copied successfully.")

    def move_images(self, images):
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if destination:
            for path in images:
                shutil.move(path, destination)
            messagebox.showinfo("Moved", "Images moved successfully.")

    def share_placeholder(self):
        messagebox.showinfo("Share", "Share functionality is under development.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceComparator(root)
    root.mainloop()
