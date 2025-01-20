import tkinter as tk
from datetime import datetime
from pyrf24 import RF24, RF24_PA_MAX, RF24_250KBPS, RF24Network, RF24NetworkHeader


class Radio:


    def __init__(self):

        self.radio = RF24(22, 0)  # Pin CE (22) e CSN (0)
        self.network = RF24Network(self.radio)

        self.address = 0  # Indirizzo del master (nodo 0)

        # Liste per gli UID
        self.uidList = []
        self.studentsList = []  # Categoria 3
        self.teachersList = []  # Categoria 1
        self.specialsList = []  # Categoria 2

    
    # Funzione per inviare messaggi al nodo slave
    def send_message(self, data, slave_address):
        header = RF24NetworkHeader(slave_address)  # Crea un header per il pacchetto
        self.network.write(header, data.encode())  # Invia i dati al nodo slave
        print(f"Sent message: {data}")

    
    # Funzione per ricevere messaggi dal nodo slave
    def receive_message(self):

        self.network.update()
        if self.network.available():

            header, payload = self.network.read()  # Leggi i dati
            print(f"Received message from node {header.from_node}: {payload.hex()}")

            # Restituisci i dati come una lista [header_from_node, payload]
            return [header.from_node, list(payload)]
        else:
            return False
        
    
    # Funzione per svuotare i buffer FIFO prima di inviare o ricevere
    def flush_buffers(self):
        self.radio.flush_tx()  # Svuota il buffer di trasmissione
        self.radio.flush_rx()  # Svuota il buffer di ricezione
        print("[i] Buffers flushed (TX and RX)")

    
    # Inizializzazione del nodo master
    def setup(self):
        print("[i] - Master unit initialized")
        self.radio.begin()  # Inizializza la radio
        self.network.begin(90, self.address)  # Canale 90, nodo 0
        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.setDataRate(RF24_250KBPS)
        self.radio.setChannel(100)  # Canale 100

    




class ListaConteggiApp(tk.Tk, Radio):

    def __init__(self):
        super().__init__()
        Radio.__init__(self)

        self.title("Contatore Elementi per Liste")

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

        self.after(0, self.action)


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

    
    # Funzione di loop principale
    def action(self):

        # Controlla se ci sono messaggi da ricevere
        payloadWithHeader = self.receive_message()

        if payloadWithHeader:
            headerFromNode = payloadWithHeader[0]
            payload = payloadWithHeader[1]

            if payload:
                isRfid = payload[0]
                payload.pop(0)
                uid = payload

                if not isRfid:
                    category = uid[-1]
                    uid.pop(-1)
                    if uid not in self.uidList:
                        self.uidList.append(uid)
                        print(f"[+] - UID dal nodo {headerFromNode} aggiunto: {''.join(format(x, '02x') for x in uid)}")

                        if int(category) == 1:
                            print("Categoria: Docenti")
                            self.teachersList.append(uid)

                        elif int(category) == 2:
                            print("Categoria: Invalidi")
                            self.specialsList.append(uid)

                        elif int(category) == 3:
                            print("Categoria: Studenti")
                            self.studentsList.append(uid)

                        else:
                            print("Formato invalido. UID aggiunto solo alla lista principale.")

                        # Aggiorna i conteggi nell'interfaccia grafica
                        self.update_numbers()
                    else:
                        print("[i] - Tag già registrato")
                else:
                    # Sovrascrivi il testo nella finestra principale
                    if uid in self.teachersList:
                        self.show_message(f"TEACHER AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    elif uid in self.specialsList:
                        self.show_message(f"HANDICAPPED AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    elif uid in self.studentsList:
                        self.show_message(f"STUDENT AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    else:
                        self.show_message("Not registered tag")
            else:
                print("[!] Payload vuoto.")

        self.after(0, self.action)


if __name__ == "__main__":
    root = ListaConteggiApp()
    root.mainloop()