import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import face_recognition
import shutil

class FaceComparator:

    def __init__(self, master):
        self.master = master
        self.master.title("Smart Face Comparator")
        self.select_folder_button = tk.Button(self.master, text="Select Folder",width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="#2a2d36", command=self.select_folder)
        self.select_folder_button.place(x=600, y=100)
   

        self.selected_image_path = tk.StringVar()
        self.selected_image_path.set("No Image Selected")

        self.image_files=[]
        self.similar_images_path=[]
        self.face_path=[]
        self.face_encodes=[]
        self.images = []
        self.image_1 = []
        self.selected_index = tk.IntVar(value=-1)
        self.selected_image_encode = []
        self.selected_image_encode_path = []
      

    def select_folder(self):
        self.image_folder = filedialog.askdirectory(title="Select Folder")
        if self.image_folder:
            self.image_files = [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
            self.create_gallery()

    #Function for make images as a gallery
    def create_gallery(self):
         #Create a Main Frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill="both", expand=1)

    #Create a Canvas
        self.my_canvas = tk.Canvas(self.main_frame)
        self.my_canvas.pack(side="left", fill="both", expand=1)

    #Add a Scrollbar To The Canvsa

        self.my_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command = self.my_canvas.yview)
        self.my_scrollbar.pack(side="right", fill="y")

    #Configure The Canvas

        self.my_canvas.configure(yscrollcommand=self.my_scrollbar.set)
        self.my_canvas.bind('<Configure>', lambda e:self.my_canvas.configure(scrollregion = self.my_canvas.bbox("all")))

    #Create Another Frame Inside the Canvas

        self.second_frame = tk.Frame(self.my_canvas)
        self.second_frame.configure(bg='blue')

    #Add that new Frame To a window in the Canvas

        self.my_canvas.create_window((0,0), window=self.second_frame, anchor="nw")
        if self.image_files:
            for i, image_file in enumerate(self.image_files):
                image_path = os.path.join(self.image_folder, image_file)
                img = Image.open(image_path)
                img = img.resize((330, 330), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                label = tk.Label(self.second_frame, image=photo)
                label.image = photo
                label.grid(row=i // 4, column=i % 4, padx=5, pady=5)

                label.bind("<Button-1>", lambda event, index=i: self.on_image_click(index))

                self.images.append(photo)

    
            select_button1 = tk.Button(self.second_frame, text="Compare",width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="#2a2d36", command=self.compare)
            select_button1.grid(row=len(self.image_files) // 4+1,column=0, columnspan=2)

            close_button = tk.Button(self.second_frame, text="Close", width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="#3697f5", command=self.close)
            close_button.grid(row=len(self.image_files) // 4+1,column=1, columnspan=10)

            selected_label = tk.Label(self.second_frame, textvariable=self.selected_image_path, width = 40, height = 1)
            selected_label.grid(row=len(self.image_files) // 4+1, column=3, columnspan=10)
     #Function for select an image
    def on_image_click(self, index):
        self.selected_index.set(index)
        self.selected_image_path.set(f"Selected Image: {os.path.join(self.image_folder, self.image_files[index])}")
        print(f"Selected Image: {os.path.join(self.image_folder, self.image_files[index])}")
        
        self.image_1.append(os.path.join(self.image_folder, self.image_files[index]))
              
     #Function to encode a face   
    def encode(self, path):
        load = face_recognition.load_image_file(path)
        encode_image = face_recognition.face_encodings(load)
        return encode_image [0]
    
   

    

        
       #Function for move a similar images  
    def move(self):

        destination_folder = filedialog.askdirectory(title = "Select Folder")
        if destination_folder:
            for image_path in self.similar_images_path:
                try:
                    _, filename = os.path.split(image_path)
                
                    destination = os.path.join(destination_folder, filename)
                    shutil.move(image_path, destination)
                    print(f"Moved {image_path} to {destination_folder}")
                except Exception as e:
            
                    print(f"Error moveing {image_path} : {e}'")
           
    #Function for copy a similar images
    def copy(self):

        destination_folder = filedialog.askdirectory(title = "Select Folder")

        if destination_folder:
            for image_path in self.similar_images_path:
                try:
                    _, filename = os.path.split(image_path)
                
                    destination = os.path.join(destination_folder, filename)
            
                    shutil.copy(image_path, destination)
                
                    print(f"copied {image_path} to {destination_folder}")
                except Exception as e:
                    print(f"Error copying {image_path} : {e}'")            

    #Function for close a window
    def close(self):
            self.master.destroy()
   
    #Function for compare an images
    def compare(self):
        print(self.image_1)
        i=1
        image_pth=[os.path.join(self.image_folder, self.image_files[i]) for i in range(len(self.image_files))]
        #if self.selected_index.get() != -1:
            #selected_image_path = os.path.join(self.image_folder, self.image_files[self.selected_index.get()])
            #print(f"Selected image path : {selected_image_path}")      

        for it in range(len(self.image_1)):
            try:
                print(self.image_1[it])
                image_encode_1 = self.encode(self.image_1[it])
                self.selected_image_encode.append(image_encode_1)
                self.selected_image_encode_path.append(self.image_1[it])
                    
                print(f"Encoding Points of Selected Image {it}", image_encode_1)
            except IndexError:
                print(f"{self.image_1[it]} This image have no face and Please select a image with a face")
                

        if self.selected_image_encode:
            for paths in range(len(image_pth)):
                try:
                    
                    image_encode_2=self.encode(image_pth[paths])
                
                    self.face_encodes.append(image_encode_2)
                    self.face_path.append(image_pth[paths])
                    print(f"encoding points of total images {paths} ", image_encode_2)

                except IndexError:
                    print(f"Skipping {image_pth[paths]} - No face detected")
                except Exception as e:
                    print(f"Error processing {image_pth[paths]} : {e}")              


            #l
            for path_of in range(len(self.selected_image_encode)):
                for encodek in range(len(self.face_encodes)):
                    is_same = face_recognition.compare_faces([self.selected_image_encode[path_of]], self.face_encodes[encodek])[0]
                    if is_same == True:
                        print(f'({i}) {self.image_1[path_of]} and {self.face_path[encodek]} are same : {is_same}')
                        i=i+1
                        #self.similar_images_path.append(image_pth[paths])
                        if self.face_path[encodek] not in self.similar_images_path:
                            self.similar_images_path.append(self.face_path[encodek])
                        
                        #finding the distance level between images
                        distance = face_recognition.face_distance([self.selected_image_encode[path_of]], self.face_encodes[encodek])
                        distance = round(distance[0] * 100)
                        print("Distance between images", distance)
                        
                        #calculating the accuracy level between images
                        accuracy = 100 - round(distance)
                        print("The images are same")
                        print(f"Accuracy Level : {accuracy}%")
       
                
                    else:
                        #print(f"{image_pth[paths]} - is not same")
                        print(f"{self.selected_image_encode_path[path_of]} and{self.face_path[encodek]} - is not same")
                               
        print("similar images path : ", self.similar_images_path)
        if self.similar_images_path:
            new_window = tk.Toplevel(self.master)
            new_window.title("Similar Images")
            new_window.geometry("500x500")
         
        #Create a Main Frame
            main_frame = tk.Frame(new_window)
            main_frame.pack(fill="both", expand=1)

        #Create a Canvas
            my_canvas = tk.Canvas(main_frame)
            my_canvas.pack(side="left", fill="both", expand=1)

        #Add a Scrollbar To The Canvsa

            my_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command = my_canvas.yview)
            my_scrollbar.pack(side="right", fill="y")

        #Configure The Canvas

            my_canvas.configure(yscrollcommand=my_scrollbar.set)
            my_canvas.bind('<Configure>', lambda e:my_canvas.configure(scrollregion = my_canvas.bbox("all")))

        #Create Another Frame Inside the Canvas

            second_frame = tk.Frame(my_canvas)
            second_frame.configure(bg='#800080')

        #Add that new Frame To a window in the Canvas

            my_canvas.create_window((0,0), window=second_frame, anchor="nw")

    
            for i, image_file in enumerate(self.similar_images_path):
            #image_path = os.path.join(image_folder, image_file)
                img = Image.open(image_file)
                img = img.resize((330, 330), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                label = tk.Label(second_frame, image=photo)
                label.image = photo
                label.grid(row=i // 4, column=i % 4, padx=5, pady=5)

            move_button = tk.Button(second_frame, text="Move",width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="#fe9037", command=self.move)
            move_button.grid(row=len(self.similar_images_path) // 4+2,column=0, columnspan=1)

            select_button = tk.Button(second_frame, text="Copy", width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="#3697f5", command=self.copy)
            select_button.grid(row=len(self.similar_images_path) // 4+2,column=0, columnspan=10)

            share_button = tk.Button(second_frame, text="Share", width=10,height=1,font=("arial",15,"bold"),bd=1,fg="#fff",bg="blue")
            share_button.grid(row=len(self.similar_images_path) // 4+2,column=3, columnspan=20)

              
    
if __name__ == "__main__":
    root = tk.Tk()
    app =FaceComparator(root)
    root.mainloop()

