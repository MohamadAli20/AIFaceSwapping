import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2, os
import mediapipe as mp
import numpy as np
import datetime, time, subprocess, webbrowser 

class InputFrame(tk.Frame):
    def __init__(self, parent, switch_frame_callback):
        super().__init__(parent)
        self.switch_frame_callback = switch_frame_callback

        self.configure(bg="#F0F0F0")  # Set a light background color

        label = tk.Label(self, text="Upload Media File:", font=("Helvetica", 18, "bold"))
        label.pack(pady=10)

        self.image_file_path = tk.StringVar()
        self.video_file_path = tk.StringVar()

        self.recent_files = []

        self.image_label = tk.Label(self, text="Image File:", font=("Helvetica", 15))
        self.image_label.pack()

        self.image_frame = tk.Frame(self, bg="#F0F0F0")
        self.image_frame.pack(fill="x", padx=30, pady=10)  # Increased height

        self.image_entry = tk.Entry(self.image_frame, 
                                    textvariable=self.image_file_path, 
                                    state='readonly', bd=2,
                                    width=75, font=("Helvetica", 15))
        self.image_entry.grid(row=0, column=2, padx=20, pady=10, columnspan=3, rowspan=2)

        self.image_browse_button = tk.Button(self.image_frame, 
                                             text="Browse Image", 
                                             command=self.browse_image_file, 
                                             bg="#4472C4", fg="white", 
                                             activebackground="#5A8ACF", 
                                             height=1, width=18, 
                                             font=("Helvetica",11))
        self.image_browse_button.grid(row=0, column=6, padx=5, columnspan=2, rowspan=2)

        self.image_clear_button = tk.Button(self.image_frame, 
                                            text="Clear", 
                                            command=self.clear_image_entry, 
                                            bg="#E74C3C", fg="white", 
                                            activebackground="#EF665F",
                                            height=1, width=18, 
                                            font=("Helvetica",11))
        self.image_clear_button.grid(row=0, column=8, padx=5, columnspan=2, rowspan=2)

        self.video_label = tk.Label(self, text="Video File:", font=("Helvetica", 15))
        self.video_label.pack()

        self.video_frame = tk.Frame(self, bg="#F0F0F0")
        self.video_frame.pack(fill="x", padx=30, pady=(0, 10))  # Increased height

        self.video_entry = tk.Entry(self.video_frame, 
                                    textvariable=self.video_file_path, 
                                    state='readonly', width=75, bd=2,
                                    font=("Helvetica", 15))  # Increased entry height
        self.video_entry.grid(row=0, column=2, padx=20, pady=10, columnspan=3, rowspan=2)

        self.video_browse_button = tk.Button(self.video_frame, 
                                             text="Browse Video", 
                                             command=self.browse_video_file, 
                                             bg="#4472C4", fg="white", 
                                             activebackground="#5A8ACF",
                                             height=1, width=18, 
                                             font=("Helvetica",11))
        self.video_browse_button.grid(row=0, column=6, padx=5, columnspan=2, rowspan=2)

        self.video_clear_button = tk.Button(self.video_frame, text="Clear", 
                                            command=self.clear_video_entry, 
                                            bg="#E74C3C", fg="white", 
                                            activebackground="#EF665F",
                                            height=1, width=18, 
                                            font=("Helvetica",11))
        self.video_clear_button.grid(row=0, column=8, padx=5, columnspan=2, rowspan=2)

        self.recent_files_label = tk.Label(self, text="Recent Uploads:", font=("Helvetica", 15))
        self.recent_files_label.pack()

        self.recent_files_frame = tk.Frame(self, bg="#F0F0F0")
        self.recent_files_frame.pack(fill="x", pady=(0, 20))  # Increased height

        # Create a border for the listbox only when it's not empty
        self.listbox_frame = tk.Frame(self.recent_files_frame, 
                                      bg="white", bd=2 if self.recent_files else 0, 
                                      relief="solid")
        self.listbox_frame.pack(padx=30, pady=15)
        
        # Create the listbox and scrollbar
        self.recent_files_listbox = tk.Listbox(self.listbox_frame, 
                                               selectmode=tk.SINGLE, 
                                               width=170, height=10, 
                                               font=("Helvetica",11))  # Increased height
        self.recent_files_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.recent_files_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.recent_files_listbox.config(yscrollcommand=scrollbar.set)

        self.load_recent_files()  # Load recent files from file
        self.update_recent_files_listbox()  # Update the listbox with recent files

        self.button_frame = tk.Frame(self.recent_files_frame, bg="#F0F0F0")
        self.button_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.recall_button = tk.Button(self.button_frame, 
                                       text="Recall Recent Upload", 
                                       command=self.recall_recent_upload, 
                                       bg="#218DEF", fg="white", 
                                       activebackground="#4DA0F7",
                                       height=1, width=18, 
                                       font=("Helvetica",11))
        self.recall_button.pack(side="left", padx=30, pady=5)  # Uniform button size

        self.select_button = tk.Button(self.button_frame, text="Select", 
                                       command=self.select_files, 
                                       bg="#27AE60", fg="white", 
                                       activebackground="#33C26D",
                                       height=1, width=18, 
                                       font=("Helvetica",11))
        self.select_button.pack(side="left", padx=30, pady=5)  # Uniform button size

        self.select_button = tk.Button(self.button_frame, text="Clear Recent Upload", 
                                       command=self.clear_recent, 
                                       bg="#E74C3C", fg="white", 
                                       activebackground="#EF665F",
                                       height=1, width=18, 
                                       font=("Helvetica",11))
        self.select_button.pack(side="left", padx=30, pady=5)  # Uniform button size

        # Adjust the submit button alignment
        button_submit = tk.Button(self, text="Submit", 
                                  command=self.switch_to_output_frame, 
                                  font=("Helvetica", 18, "bold"), 
                                  bg="#34495E", fg="white", 
                                  activebackground="#4A648C",
                                  height=1, width=22)
        button_submit.pack(side="bottom", pady=(0, 60))

    def clear_image_entry(self):
        self.image_file_path.set("")

    def clear_video_entry(self):
        self.video_file_path.set("")

    def clear_recent(self):
        self.recent_files_listbox.delete(0, tk.END)
        self.recent_files = []

    def load_recent_files(self):
        try:
            with open('recent_files.txt', 'r') as file:
                self.recent_files = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            self.recent_files = []

    def update_recent_files_listbox(self):
        self.recent_files_listbox.delete(0, tk.END)
        for file_path in self.recent_files:
            self.recent_files_listbox.insert(tk.END, file_path)

    def recall_recent_upload(self):
        self.load_recent_files()  # Load recent files from file
        self.update_recent_files_listbox()  # Update the listbox with recent files
        selected_index = self.recent_files_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_file = self.recent_files[selected_index]
            if selected_file.endswith(".png"):
                self.image_file_path.set(selected_file)
                self.video_file_path.set("")  # Clear the video path
            else:
                self.video_file_path.set(selected_file)
                self.image_file_path.set("")  # Clear the image path

    def select_files(self):
        image_path = self.image_file_path.get()
        video_path = self.video_file_path.get()
        if image_path:
            self.image_label.config(text=f"Image Path: {image_path}")
        if video_path:
            self.video_label.config(text=f"Video Path: {video_path}")

    def switch_to_output_frame(self):
        image_path = self.image_file_path.get()
        video_path = self.video_file_path.get()

        if not image_path and not video_path:
            response = messagebox.askquestion("Empty Entries", "The entries are empty. Would you like to view the list of output paths?", icon="warning")
            if response == "yes":
                self.switch_frame_callback(OutputFrame, None, None)  # Pass None for image_path and video_path
        else:
            self.switch_frame_callback(OutputFrame, image_path, video_path)


    def browse_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if file_path:
            self.add_recent_file(file_path)
            self.image_file_path.set(file_path)

    def browse_video_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")])
        if file_path:
            self.add_recent_file(file_path)
            self.video_file_path.set(file_path)

    def add_recent_file(self, file_path):
        self.recent_files.append(file_path)
        self.save_recent_files()  # Save recent files to file
        self.update_recent_files_listbox()  # Update the listbox with recent files

    def save_recent_files(self):
        with open('recent_files.txt', 'w') as file:
            for file_path in self.recent_files:
                file.write(file_path + '\n')

    def update_recent_files_listbox(self):
        self.recent_files_listbox.delete(0, tk.END)
        for file_path in self.recent_files:
            self.recent_files_listbox.insert(tk.END, file_path)

    def select_files(self):
        selected_index = self.recent_files_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_file = self.recent_files[selected_index]
            if selected_file.endswith(".png"):
                self.image_file_path.set(selected_file)
            else:
                self.video_file_path.set(selected_file)

class OutputFrame(tk.Frame):
    def __init__(self, parent, switch_frame_callback, image_path, video_path):
        super().__init__(parent)
        self.switch_frame_callback = switch_frame_callback
        self.image_path = image_path
        self.video_path = video_path

        self.configure(bg="#F0F0F0")  # Set a light background color

        # Create a frame to hold the canvas and progress bar
        canvas_frame = tk.Frame(self, bg="#F0F0F0")
        canvas_frame.pack(side="right", padx=30, pady=(0, 50))

        # Create a canvas for displaying the media
        self.canvas = tk.Canvas(canvas_frame, width=640, height=480, bg="#16558F", bd=3, relief="solid")
        self.canvas.pack()

        
        # Create a frame to hold the buttons
        button_frame = tk.Frame(canvas_frame, bg="#F0F0F0")
        button_frame.pack(side="bottom", padx=(0, 0), pady=(20, 0))

        # Create a "Back to Input" button
        back_button = tk.Button(button_frame, text="Back", 
                                command=self.switch_to_input_frame,
                                bg="#4472C4", fg="white", 
                                activebackground="#5A8ACF", 
                                height=1, width=18, 
                                font=("Helvetica",11))
        back_button.pack(side="left", padx=30)

        # Create the "Generate Face Swap" button
        self.generate_button = tk.Button(button_frame, text="Generate",
                                        command=self.setup_and_start_face_swapping,
                                        bg="#2467EC", fg="white",
                                        activebackground="#4DA0F7",
                                        height=1, width=18,
                                        font=("Helvetica", 11))
        self.generate_button.pack(side="left", padx=30)

        # Create a "Save Video" button
        self.save_button = tk.Button(button_frame, text="Save Video", 
                                     command=self.save_video,
                                     bg="#4472C4", fg="white", 
                                     activebackground="#5A8ACF", 
                                     height=1, width=18, 
                                     font=("Helvetica",11))
        self.save_button.pack(side="right", padx=30)
        
        self.progress_running = False  # Flag to track if progress is running

        # Progress bar Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Horizontal.TProgressbar", thickness=20, 
                        thicknessunit='pixels', background='#16558F', 
                        troughcolor='#b0b0b0', troughrelief='flat', 
                        bordercolor='#b0b0b0')

        self.progress_bar = ttk.Progressbar(canvas_frame,style="Horizontal.TProgressbar", 
                                            orient="horizontal", mode="determinate", length=650)
        self.progress_bar.pack(side="bottom", padx=(50, 50), pady=(0, 10))  # Align to the canvas and set the same width

        # # Start the face swapping process
        # self.setup_and_start_face_swapping()
        
        # Create a frame to hold the table and scrollbar
        table_frame = tk.Frame(self, bg="#16558F", bd=2, relief="solid")
        table_frame.pack(side="left", padx=(30, 10), pady=(20, 100), fill="y")

        # Create a scrollbar for the table
        scrollbar = tk.Scrollbar(table_frame, orient="vertical")

        # Create a table to display saved output files
        self.table = ttk.Treeview(table_frame, columns=("Title", "Path"),
                                  show="headings", selectmode="browse",
                                  yscrollcommand=scrollbar.set,
                                  height=10)
        self.table.heading("Title", text="File")
        self.table.heading("Path", text="Path")
        self.table.pack(fill="y", side="left")

        scrollbar.config(command=self.table.yview)
        scrollbar.pack(side="right", fill="y")

        # Load saved output files from file
        self.load_saved_output_files()
        self.update_output_table()  # Update the table with saved output files

        # Bind hover events to show tooltip and "Double Click to Open" note
        self.table.bind("<Motion>", self.on_table_hover)
        self.table.bind("<Leave>", self.on_table_leave)
        self.table.bind("<Double-1>", self.open_file_explorer)

        self.tooltip = None

            
    def switch_to_input_frame(self):
        self.switch_frame_callback(InputFrame, self.output_files)

    def setup_and_start_face_swapping(self):
        if not self.image_path or not self.video_path:
            messagebox.showerror("Missing Input", "Both image and video paths are required for face swapping.")
            self.save_button.config(state="disabled")
            self.generate_button.config(state="disabled")
            return
        
        else:
            # Initialize MediaPipe face detection and facial landmark detection models
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_face_mesh = mp.solutions.face_mesh

            # Load the input image for face swapping
            self.input_image_path = self.image_path
            self.input_image = cv2.imread(self.input_image_path, -1)

            # Initialize video capture/input
            # self.video_path = self.video_path
            self.cap = cv2.VideoCapture(self.video_path)
            
            # Initialize the VideoWriter object
            self.frame_width = int(self.cap.get(3))
            self.frame_height = int(self.cap.get(4))
            self.size = (self.frame_width, self.frame_height)
            self.result = cv2.VideoWriter('output_video.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, self.size)

            # Start the face swapping process
            self.start_face_swapping()

    
    def update_progress_bar(self):
        progress = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.cap.get(cv2.CAP_PROP_FRAME_COUNT) * 100
        self.progress_bar["value"] = progress

    def start_face_swapping(self):
        def process_frame():
            self.progress_running = True
            self.save_button.config(state="disabled") 
            self.generate_button.config(state="disabled") 
            ret, frame = self.cap.read()
            if ret:
                swapped_frame = self.face_swap(frame, self.input_image)
                self.result.write(swapped_frame)
                self.display_frame_on_canvas(swapped_frame)
                self.update_progress_bar()  # Update the progress bar
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.result.release()
                    self.progress_running = False
                    self.save_button.config(state="normal")  # Enable the "Save Video" button
                    self.generate_button.config(state="normal")  # Enable the "Generate" button
                else:
                    self.after(1, process_frame)

        process_frame()   


    def save_video(self):
        self.result.release()  # Release the VideoWriter

        # Prompt the user to enter a filename
        save_filename = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
        if save_filename:
            # Wait for a short period to ensure the VideoWriter is fully released
            time.sleep(0.5)

            # Move the saved file to the specified location
            saved_filepath = os.path.join(os.getcwd(), "output_video.avi")
            new_filepath = os.path.join(save_filename)
            os.rename(saved_filepath, new_filepath)

            # Add the saved file to the listbox
            self.add_saved_output_file(new_filepath)
            self.update_output_table()  # Update the table with saved output files

            # Display a message dialog box
            message = f"File saved successfully:\n{new_filepath}"
            messagebox.showinfo("File Saved", message)

        self.switch_frame_callback(InputFrame)  # Switch back to the input frame

    def add_saved_output_file(self, file_path):
        self.output_files.append(file_path)
        self.save_output_files()  # Save output files to file

    def update_output_table(self):
        self.table.delete(*self.table.get_children())
        for file_path in self.output_files:
            self.table.insert("", "end", values=(os.path.basename(file_path), file_path))

            # Bind the double-click event to open the file explorer
            self.table.bind("<Double-1>", self.open_file_explorer)

    def open_folder_in_file_explorer(self, folder_path):
        webbrowser.open(folder_path)
    
    def open_file_explorer(self, event):
        selected_item = self.table.selection()[0]
        file_path = self.table.item(selected_item, "values")[1]  # Get the second column value (file path)
        folder_path = os.path.dirname(file_path)
        self.open_folder_in_file_explorer(folder_path)


    def save_output_files(self):
        with open('output_files.txt', 'w') as file:
            for file_path in self.output_files:
                file.write(file_path + '\n')

    def load_saved_output_files(self):
        try:
            with open('output_files.txt', 'r') as file:
                self.output_files = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            self.output_files = []

    def on_table_hover(self, event):
        row = self.table.identify_row(event.y)
        if row:
            file_path = self.table.item(row, "values")[1]
            note = "Double Click to Open"
            tooltip_text = f"{file_path}\n{note}"
            self.show_tooltip(event, tooltip_text)  # Pass the event as an argument

    def on_table_leave(self, event):
        self.hide_tooltip()

    def show_tooltip(self, event, text):
        if self.tooltip is None:
            x, y, _, _ = self.table.bbox(self.table.identify_row(event.y))
            x += self.table.winfo_rootx() + 25
            y += self.table.winfo_rooty() + 25
            self.tooltip = tk.Toplevel(self.table)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=text, background="#FFFFE0", relief="solid", borderwidth=1)
            label.pack()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    
    def display_frame_on_canvas(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def face_swap(self, frame, input_image):
        # Convert the input image to RGB
        input_image_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
        # Detect faces in the input image
        with self.mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            input_image_results = face_detection.process(input_image_rgb)
            if not input_image_results.detections:
                return frame

        # Convert the video frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the video frame
        with self.mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            frame_results = face_detection.process(frame_rgb)
            if not frame_results.detections:
                return frame

            # Get the bounding box coordinates for the first detected face in the video frame
            frame_face = frame_results.detections[0].location_data.relative_bounding_box

        # Convert the video frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Extract the face region from the video frame
        frame_height, frame_width, _ = frame.shape
        xmin = int(frame_face.xmin * frame_width)
        ymin = int(frame_face.ymin * frame_height)
        xmax = int((frame_face.xmin + frame_face.width) * frame_width)
        ymax = int((frame_face.ymin + frame_face.height) * frame_height)
        face_region = frame[ymin:ymax, xmin:xmax]

        # Resize the input image to match the size of the face region
        input_image_resized = cv2.resize(input_image, (face_region.shape[1], face_region.shape[0]), interpolation=cv2.INTER_AREA)

        # Create a mask for the input image with a transparent background
        input_mask = input_image_resized[:, :, 3] / 255.0
        
        # Apply the input image over the face region using the mask
        for c in range(0, 3):
            frame[ymin:ymax, xmin:xmax, c] = frame[ymin:ymax, xmin:xmax, c] * (1 - input_mask) + input_image_resized[:, :, c] * input_mask
        
        return frame

 
class MainApp(tk.Tk):
    

    def __init__(self):
        super().__init__()
        self.title("Face Swapping GUI")
        self.geometry("1920x1080")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.output_files = []  # Initialize the list of output files

        self.frames = {}
        self.current_frame = None

        self.add_frame(InputFrame)  # Pass only the frame class, without additional arguments

    def add_frame(self, frame_class):
        new_frame = frame_class(self.container, self.switch_frame)  # Pass the output_files argument
        if self.current_frame:
            self.current_frame.pack_forget()
        new_frame.pack(fill="both", expand=True)
        self.current_frame = new_frame

    def switch_frame(self, frame_class, *args):
        if frame_class == OutputFrame:
            new_frame = frame_class(self.container, self.switch_frame, *args)
        else:
            new_frame = frame_class(self.container, self.switch_frame)
        if self.current_frame:
            self.current_frame.pack_forget()
        new_frame.pack(fill="both", expand=True)
        self.current_frame = new_frame

        
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
