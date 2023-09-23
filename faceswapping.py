from flask import Flask, render_template, request #importing flask
import tkinter as tk
from tkinter import ttk, filedialog  #for Progressbar
from tkinter import messagebox
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime 
import os

# Flask constructor

# Mention custom folder name
# app = Flask(__name__, template_folder='templates', static_folder='static')

# @app.route('/', methods =["GET", "POST"])
# def file_path():
#     global image_path, video_path
#     if request.method == "POST":
#        # getting input with name = image-path in HTML form
#        image_path = request.form.get("image-path")
#        # getting input with name = video-path in HTML form
#        video_path = request.form.get("video-path")
#     #    return "Your name is " + video_path + "  "  + image_path # test if it returns the paths

#     return render_template("main.html")
 
# if __name__=='__main__':
#    app.run(debug=True)

#call the file_path() to access the global variable inside of it
# file_path()
# abs_path_image = image_path
# abs_path_video = video_path
# print(abs_path_image)
# print(abs_path_video)

#testing remove this after
abs_path_image = "C:/Users/LIM/Desktop/AI ECard/static/barak1.png"
abs_path_video = "C:/Users/LIM/Desktop/AI ECard/static/Teacher.mov"

# Load the input image for face swapping
input_image = cv2.imread(abs_path_image, -1)

# Initialize MediaPipe face detection and facial landmark detection models
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh

# Initialize video capture/input
cap = cv2.VideoCapture(abs_path_video)  # Replace "assets/Thankyou-Compass.mov" with the path to your video file

# Initialize the global variable to keep track of the incrementing number
output_file_number = 1

# Count the total number of frames in the video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Function to perform face swapping
def face_swap(frame, input_image):
    # Convert the input image to RGB
    input_image_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)

    # Detect faces in the input image
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        input_image_results = face_detection.process(input_image_rgb)
        if not input_image_results.detections:
            return frame

    # Convert the video frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the video frame
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        frame_results = face_detection.process(frame_rgb)
        if not frame_results.detections:
            return frame
 
        # Get the bounding box coordinates for the first detected face in the video frame
        frame_face = frame_results.detections[0].location_data.relative_bounding_box

    # Extract the face region from the video frame
    frame_height, frame_width, _ = frame.shape
    xmin = int(frame_face.xmin * frame_width)
    ymin = int(frame_face.ymin * frame_height)
    xmax = int((frame_face.xmin + frame_face.width) * frame_width)
    ymax = int((frame_face.ymin + frame_face.height) * frame_height)
    face_region = frame[ymin:ymax, xmin:xmax]
   
    
    # Resize the input image to match the size of the face region 
    input_image_resized = cv2.resize(input_image, (face_region.shape[1], face_region.shape[0]), interpolation=cv2.INTER_AREA)
    
    #----------
    top = ymin
    left = xmin
    small_foreground = input_image_resized
    fg_b, fg_g, fg_r, fg_a = cv2.split(small_foreground)
    # Make the range 0...1 instead of 0...255
    fg_a = fg_a / 255.0
    # Multiply the RGB channels with the alpha channel
    label_rgb = cv2.merge([fg_b * fg_a, fg_g * fg_a, fg_r * fg_a])  

    result = frame.copy()

    # Work on a part of the background only
    height, width = small_foreground.shape[0], small_foreground.shape[1]
    part_of_bg = result[top:top + height, left:left + width, :]
    # Same procedure as before: split the individual channels
    bg_b, bg_g, bg_r = cv2.split(part_of_bg)
    # Merge them back with opposite of the alpha channel
    part_of_bg = cv2.merge([bg_b * (1 - fg_a), bg_g * (1 - fg_a), bg_r * (1 - fg_a)])
    
    cv2.add(label_rgb, part_of_bg, part_of_bg)
    #----------
     # Perform the face swapping by replacing the face region in the video frame with the input image 
    frame[top:top + height, left:left + width, :] = part_of_bg

    return frame

def generate_button_clicked():
    # Read a frame from the video capture
    ret, frame = cap.read()
    if ret:
        # Perform face swapping on the frame
        swapped_frame = face_swap(frame, input_image)
        
        swapped_frame_resized = cv2.resize(swapped_frame, (blue_frame_width, blue_frame_height))

        swapped_frame_rgb = cv2.cvtColor(swapped_frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to ImageTk format
        img = Image.fromarray(swapped_frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        
        # Display the image in the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.img_tk = img_tk
        
        # Call this function again after 10 milliseconds
        root.after(10, generate_button_clicked)

generated_frames = []

# GUI window
root = tk.Tk()
root.title("Face Swapping GUI")

# Size of the frame
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
frame_width = screen_width
frame_height = screen_height

# Main Frame
frame = tk.Frame(root, width=frame_width, height=frame_height)
frame.pack()

# Center Frame with a blue background 
blue_frame_width = frame_width // 2
blue_frame_height = frame_height // 2
blue_frame = tk.Frame(frame, bg="#16558F", width=blue_frame_width, height=blue_frame_height, padx=10)
blue_frame.pack(pady=20)

# Canvas inside the blue frame to display video output
canvas = tk.Canvas(blue_frame, bg="#16558F", width=blue_frame_width, height=blue_frame_height)
canvas.pack()

def on_close():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Loading bar Style
style = ttk.Style()
style.theme_use('default')
style.configure("Horizontal.TProgressbar", thickness=20, thicknessunit='pixels', background='#16558F', troughcolor='#b0b0b0', troughrelief='flat', bordercolor='#b0b0b0')

loading_bar = ttk.Progressbar(frame, style="Horizontal.TProgressbar", orient="horizontal", mode="determinate", length=blue_frame_width, maximum=100)
loading_bar.pack()

# For face swapping and updating the canvas
def generate_and_update(progress):
    # Read a frame from the video capture
    ret, frame = cap.read()
    if ret:
        # Perform face swapping on the frame
        swapped_frame = face_swap(frame, input_image)
        
        swapped_frame_resized = cv2.resize(swapped_frame, (blue_frame_width, blue_frame_height))

        swapped_frame_rgb = cv2.cvtColor(swapped_frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to ImageTk format
        img = Image.fromarray(swapped_frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        
        # Display the image in the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.img_tk = img_tk
        
        # Increment the progress bar
        progress += 1
        loading_bar['value'] = progress

        # Append the generated frame to the list
        generated_frames.append(swapped_frame_resized)
        
        # Check if the face swapping is done
        if progress >= total_frames:
            # Face swapping is done, hide the loading bar
            loading_bar.pack_forget()
            return
        else:
            # Call this function again after 10 milliseconds with updated progress
            root.after(10, generate_and_update, progress)

def save_button_clicked():
    global generated_frames, output_file_number

    if generated_frames:
        # Create the output folder if it doesn't exist
        output_folder = "output_frames"
        os.makedirs(output_folder, exist_ok=True)

        # Get the current date and time as the file name
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        # Define the output file name with the current date and time
        output_filename = os.path.join(output_folder, f"output_video_{current_datetime_str}.mp4") # change from avi to mp4 since video element don't support avi format to display

        # Set the video codec and frame rate (adjust as needed)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 30.0
        output_video = cv2.VideoWriter(output_filename, fourcc, fps, (blue_frame_width, blue_frame_height))

        # Save each frame to the output video file
        for frame in generated_frames:
            output_video.write(frame)

        # Release the video writer and clear the list of generated frames
        output_video.release()
        generated_frames.clear()

       

        # Show a success message box
        success_message = f"Video successfully saved as '{output_filename}'"
        messagebox.showinfo("Save Successful", success_message)

        # Update the column bar with the latest content
        populate_column_bar()

        #debug , remove this after testing
        print(output_filename)

# Generate button click handler
def generate_button_clicked():
    loading_bar['value'] = 0  # Reset the loading bar
    loading_bar.pack()  # Show the loading bar
    root.update()  # Update the GUI to show the loading bar
    generate_and_update(0)
    
# Dummy frame for back and generate buttons alignment
dummy_frame = tk.Frame(frame, width=frame_width // 2, height=50)
dummy_frame.pack()

# Back button
def back_button_clicked():
    # back button for upload part, for now, close function
    on_close()

back_button = tk.Button(dummy_frame, text="Back", command=back_button_clicked, bg="#16558F", fg="white", padx=15, pady=5)
back_button.grid(row=0, column=0, padx=(10, 10), pady=(30, 30)) 

# Generate button
generate_button = tk.Button(dummy_frame, text="Generate", command=generate_button_clicked, bg="#16558F", fg="white", padx=15, pady=5)
generate_button.grid(row=0, column=2, padx=(10, 10), pady=(30, 30))  

# Save button
save_button = tk.Button(dummy_frame, text="Save", command=save_button_clicked, bg="#16558F", fg="white", padx=15, pady=5)
save_button.grid(row=0, column=4, padx=(10, 10), pady=(30, 30)) 

def populate_column_bar():
    output_folder = "output_frames"
    if not os.path.exists(output_folder):
        return

    column_bar.delete(*column_bar.get_children())  # Clear the column bar

    # Get the list of files in the output folder
    file_list = os.listdir(output_folder)

    # Add each file name to the column bar
    for filename in file_list:
        file_path = os.path.join(output_folder, filename)
        column_bar.insert("", "end", values=(filename, file_path))

# Column bar
column_bar_frame = tk.Frame(frame, bg="#16558F", width=frame_width // 2, height=blue_frame_height, padx=10)
column_bar_frame.pack(side=tk.LEFT, pady=20, padx=(20, 0))

# Add a scrollbar to the column bar
column_bar_scrollbar = ttk.Scrollbar(column_bar_frame)
column_bar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create the Treeview widget for the column bar
column_bar = ttk.Treeview(column_bar_frame, columns=("File Name", "File Path"), show="headings", selectmode="browse", yscrollcommand=column_bar_scrollbar.set)
column_bar.pack(expand=True, fill=tk.BOTH)

# Set the column headings
column_bar.heading("File Name", text="File Name")
column_bar.heading("File Path", text="File Path")

# Add the scrollbar to the Treeview
column_bar_scrollbar.config(command=column_bar.yview)

# Populate the column bar with the content of the output_frames folder
populate_column_bar()

# Run the main event loop
root.mainloop()
