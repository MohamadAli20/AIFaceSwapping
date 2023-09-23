import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk
import os

class VideoUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(background = 'white')
        self.root.title("Face Swapping GUI")
        self.root.geometry("1920x1080")

        self.recent_uploads = []
        self.max_recent_uploads = 30

        self.selected_file_path = None

        self.file_path_label = tk.Label(self.root, text="No video selected", wraplength=500)
        self.file_path_label.pack(pady=10)

        self.upload_button = tk.Button(self.root, 
                                       text="Upload Video", 
                                       command=self.open_and_preview_video,
                                       background="#4472C4",
                                       foreground="white",
                                       width=25,
                                       height=2)
        self.upload_button.pack(side=tk.LEFT, padx=50, pady=(450,20))

        self.preview_button = tk.Button(self.root, text="Preview Video", 
                                        command=self.preview_selected_video, 
                                        state=tk.DISABLED,
                                        background="#4472C4",
                                        foreground="white",
                                        disabledforeground="gray",
                                        width=25,
                                        height=2)
        self.preview_button.pack(side=tk.RIGHT, padx=50, pady=(450,20))

        self.recent_uploads_label = tk.Label(self.root, text="Recent Uploads:")
        self.recent_uploads_label.pack()

        self.recent_uploads_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, height=19, width=200)  
        self.recent_uploads_listbox.pack()
        self.recent_uploads_listbox.bind('<<ListboxSelect>>', self.enable_preview_button)


    def open_and_preview_video(self):
        global file_path 
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_label.config(text="Selected Video: " + file_path)
            self.recent_uploads.insert(0, file_path)
            if len(self.recent_uploads) > self.max_recent_uploads:
                self.recent_uploads.pop()

            self.update_recent_uploads_listbox()
            self.enable_preview_button()

            self.selected_file_path = file_path

    def preview_selected_video(self):
        selected_index = self.recent_uploads_listbox.curselection()[0]
        selected_video = self.recent_uploads[selected_index]
        self.preview_video(selected_video)
        self.selected_file_path = selected_video  # Set the selected file path
        self.file_path_label.config(text="Selected Video: " + selected_video)  # Update the label

    def preview_video(self, video_path):
        video_capture = cv2.VideoCapture(video_path)
        ret, frame = video_capture.read()

        if ret:
            preview_frame = tk.Toplevel()
            preview_frame.title("Video Preview")

            video_label = tk.Label(preview_frame)
            video_label.pack()

            while ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (700, 500))
                photo = ImageTk.PhotoImage(image=Image.fromarray(image))

                video_label.config(image=photo)
                video_label.image = photo

                preview_frame.update_idletasks()
                preview_frame.update()

                ret, frame = video_capture.read()

            video_capture.release()

    def update_recent_uploads_listbox(self):
        self.recent_uploads_listbox.delete(0, tk.END)
        for upload in self.recent_uploads:
            self.recent_uploads_listbox.insert(tk.END, os.path.basename(upload))
       
        #hide recent upload list when empty
        if not self.recent_uploads:
            self.recent_uploads_listbox.pack_forget()
        else:
            self.recent_uploads_listbox.pack()

    def enable_preview_button(self, event=None):
        if self.recent_uploads_listbox.curselection():
            self.preview_button.config(state=tk.NORMAL)
        else:
            self.preview_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoUploaderApp(root)
    root.mainloop()
