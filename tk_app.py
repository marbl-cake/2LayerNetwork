import tkinter as tk
from datetime import datetime



class ListaConteggiApp(tk.Tk):


    def __init__(self):
        super().__init__()

        self.title('Contatore Elementi per Liste')

        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)


        self.font_text = ("Helvetica", 25)
        self.font_numbers = ("Helvetica", 150)

        self.total_uids_text = tk.StringVar()

        upperframe = tk.Frame(self, bg='blue', border=2)
        middleframe = tk.Frame(self, bg='lightgray', border=2)
        lowerframe = tk.Frame(self, bg='red', border=2)

        self.grid_rowconfigure(0, weight=2) 
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=6)
        self.grid_columnconfigure(0, weight=1)

        upperframe.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        middleframe.grid(column=0, row=1, sticky="nsew",  padx=2, pady=2)
        lowerframe.grid(column=0, row=2, sticky="nsew",  padx=2, pady=2)

        self.create_upper(upperframe)
        self.create_middle(middleframe)
        self.create_bottom(lowerframe)

        self.update_numbers()

        self.after(3000, lambda : self.show_message(f"TEACHER AT NODE {0}\nUID: {0}\n{datetime.now()}"))

    def update_numbers(self):
        self.total_uids_text.set(f"Registered UIDs: {len([])}")
        self.number_ordinary.set(f"{len([])}")
        self.number_emergency.set(f"{len([])}")
        self.number_disabilities.set(f"{len([])}")


    def create_upper(self, frame:tk.Frame):
        label_total_uids = tk.Label(
            frame,
            textvariable =  self.total_uids_text,
            font = self.font_text,
            bg=frame.cget('bg')
        )
        label_total_uids.pack(pady=10, fill=tk.BOTH, expand=True)

    
    def create_middle(self, frame: tk.Frame):

        label_ordinary = tk.Label(
            frame,
            text = "Ordinary People",
            font = self.font_text,
            bg = frame.cget('bg')
        )

        label_emergency = tk.Label(
            frame,
            text = "Emergency Squad People",
            font = self.font_text,
            bg = frame.cget('bg')
        )

        label_disabilities = tk.Label(
            frame,
            text = "People with Disabilities",
            font = self.font_text,
            bg = frame.cget('bg')
        )

        label_ordinary.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        label_emergency.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        label_disabilities.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)



    def create_bottom(self, frame:tk.Frame):
        
        self.number_ordinary = tk.StringVar()
        self.number_emergency = tk.StringVar()
        self.number_disabilities = tk.StringVar()

        number_ordinary = tk.Label(
            frame,
            textvariable = self.number_ordinary,
            font = self.font_numbers,
            bg = frame.cget('bg')
        )

        number_emergency = tk.Label(
            frame,
            textvariable = self.number_emergency,
            font = self.font_numbers,
            bg = frame.cget('bg')
        )

        number_disabilities = tk.Label(
            frame,
            textvariable = self.number_disabilities,
            font = self.font_numbers,
            bg = frame.cget('bg')
        )

        number_ordinary.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        number_emergency.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        number_disabilities.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)


    def exit_fullscreen(self, event:tk.Event = None):
        self.attributes("-fullscreen", False)
        return "break"
    

    def toggle_fullscreen(self, event:tk.Event = None):
        current_state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current_state)
        return "break"
    

    def show_message(self, message, duration=1000):
       
        popup = tk.Toplevel(self)
        
        popup.title("Message")
        
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()

        popup_width = parent_width // 2
        popup_height = parent_height // 2
        popup_x = parent_x + (parent_width - popup_width) // 2
        popup_y = parent_y + (parent_height - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        popup.config(bg=self.cget('bg'))
        
        label = tk.Label(popup, text=message, font=self.font_text, bg=popup.cget('bg'))
        label.pack(expand=True, fill=tk.BOTH)
        
        popup.after(duration, popup.destroy)


if __name__ == "__main__":
    lista = ListaConteggiApp()
    lista.mainloop()