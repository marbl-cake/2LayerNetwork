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
        self.ordinaryList = []  # Categoria 3
        self.emergencyList = []  # Categoria 1
        self.disabilitiesList = []  # Categoria 2
        
        # Inizializza subito la radio
        self.setup()

    def send_message(self, data, slave_address):
        header = RF24NetworkHeader(slave_address)
        self.network.write(header, data.encode())
        print(f"Sent message: {data}")

    def receive_message(self):
        try:
            self.network.update()
            if self.network.available():
                header, payload = self.network.read()
                print(f"Received message from node {header.from_node}: {payload.hex()}")
                return [header.from_node, list(payload)]
            return False
        except Exception as e:
            print(f"Error in receive_message: {e}")
            return False

    def flush_buffers(self):
        try:
            self.radio.flush_tx()
            self.radio.flush_rx()
            print("[i] Buffers flushed (TX and RX)")
        except Exception as e:
            print(f"Error flushing buffers: {e}")

    def setup(self):
        try:
            if not self.radio.begin():
                raise RuntimeError("Radio hardware not responding!")
                
            self.network.begin(90, self.address)  # Canale 90, nodo 0
            self.radio.setPALevel(RF24_PA_MAX)
            self.radio.setDataRate(RF24_250KBPS)
            self.radio.setChannel(100)  # Canale 100
            print("[i] - Master unit initialized")
            return True
        except Exception as e:
            print(f"Error in setup: {e}")
            return False

class ListaConteggiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Inizializza la radio come attributo separato
        self.radio_handler = Radio()
        
        self.title("Contatore Elementi per Liste")
        
        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        self.font_text = ("Helvetica", 15)
        self.font_numbers = ("Helvetica", 150)
        self.font_message = ("Helvetica", 20)  # Font per i messaggi
        
        self.total_uids_text = tk.StringVar()
        
        upperframe = tk.Frame(self, bg='lightblue', border=2)
        middleframe = tk.Frame(self, bg='lightgray', border=2)
        messageframe = tk.Frame(self, bg='white', border=2)  # Nuovo frame per i messaggi
        lowerframe = tk.Frame(self, bg='lightgreen', border=2)
        
        self.grid_rowconfigure(0, weight=1)    # Upper frame
        self.grid_rowconfigure(1, weight=1)    # Middle frame
        self.grid_rowconfigure(2, weight=2)    # Message frame
        self.grid_rowconfigure(3, weight=4)    # Lower frame
        self.grid_columnconfigure(0, weight=1)
        
        upperframe.grid(column=0, row=0, sticky="nsew", padx=2, pady=2)
        middleframe.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        messageframe.grid(column=0, row=2, sticky="nsew", padx=2, pady=2)  # Aggiungi message frame
        lowerframe.grid(column=0, row=3, sticky="nsew", padx=2, pady=2)
        
        self.create_upper(upperframe)
        self.create_middle(middleframe)
        self.create_message_area(messageframe)  # Nuovo metodo
        self.create_bottom(lowerframe)
        
        self.update_numbers()
        
        # Avvia il loop di aggiornamento
        self.after(100, self.action)

    def update_numbers(self):
        self.total_uids_text.set(f"Registered UIDs: {len(self.radio_handler.uidList)}")
        self.number_ordinary.set(f"{len(self.radio_handler.ordinaryList)}")
        self.number_emergency.set(f"{len(self.radio_handler.emergencyList)}")
        self.number_disabilities.set(f"{len(self.radio_handler.disabilitiesList)}")

    def create_upper(self, frame: tk.Frame):
        label_total_uids = tk.Label(
            frame,
            textvariable=self.total_uids_text,
            font=self.font_text,
            bg=frame.cget('bg')
        )
        label_total_uids.pack(pady=10, fill=tk.BOTH, expand=True)

    def create_middle(self, frame: tk.Frame):
        label_ordinary = tk.Label(
            frame,
            text="Ordinary People",
            font=self.font_text,
            bg=frame.cget('bg')
        )

        label_emergency = tk.Label(
            frame,
            text="Emergency Squad People",
            font=self.font_text,
            bg=frame.cget('bg')
        )

        label_disabilities = tk.Label(
            frame,
            text="People with Disabilities",
            font=self.font_text,
            bg=frame.cget('bg')
        )

        label_ordinary.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        label_emergency.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        label_disabilities.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)

    def create_bottom(self, frame: tk.Frame):
        self.number_ordinary = tk.StringVar()
        self.number_emergency = tk.StringVar()
        self.number_disabilities = tk.StringVar()

        number_ordinary = tk.Label(
            frame,
            textvariable=self.number_ordinary,
            font=self.font_numbers,
            bg=frame.cget('bg')
        )

        number_emergency = tk.Label(
            frame,
            textvariable=self.number_emergency,
            font=self.font_numbers,
            bg=frame.cget('bg')
        )

        number_disabilities = tk.Label(
            frame,
            textvariable=self.number_disabilities,
            font=self.font_numbers,
            bg=frame.cget('bg')
        )

        number_ordinary.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        number_emergency.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)
        number_disabilities.pack(side=tk.LEFT, pady=5, fill=tk.Y, expand=True)

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
        return "break"

    def toggle_fullscreen(self, event=None):
        current_state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current_state)
        return "break"

    def show_message(self, message, duration=None):  # duration non viene più usato
        self.message_label.config(text=message)
        
    def create_message_area(self, frame: tk.Frame):
        self.message_label = tk.Label(
            frame,
            text="",  # Inizialmente vuoto
            font=self.font_message,
            bg=frame.cget('bg'),
            justify=tk.CENTER,
            wraplength=800  # Imposta la larghezza massima del testo
        )
        self.message_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def action(self):
        try:
            # Controlla se ci sono messaggi da ricevere
            payloadWithHeader = self.radio_handler.receive_message()
            
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
                        if uid not in self.radio_handler.uidList:
                            self.radio_handler.uidList.append(uid)
                            print(f"[+] - UID dal nodo {headerFromNode} aggiunto: {''.join(format(x, '02x') for x in uid)}")
                            
                            if int(category) == 1:
                                print("Categoria: Docenti")
                                self.radio_handler.emergencyList.append(uid)
                            elif int(category) == 2:
                                print("Categoria: Invalidi")
                                self.radio_handler.disabilitiesList.append(uid)
                            elif int(category) == 3:
                                print("Categoria: Studenti")
                                self.radio_handler.ordinaryList.append(uid)
                            else:
                                print("Formato invalido. UID aggiunto solo alla lista principale.")
                            
                            self.update_numbers()
                        else:
                            print("[i] - Tag già registrato")
                    else:
                        if uid in self.radio_handler.emergencyList:
                            self.show_message(f"EMERGENCY SQUAD MEMBER AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                        elif uid in self.radio_handler.disabilitiesList:
                            self.show_message(f"PERSON WITH DISABILITIES AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                        elif uid in self.radio_handler.ordinaryList:
                            self.show_message(f"STUDENT AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                        else:
                            self.show_message("Not registered tag")
                        self.update_numbers()
                else:
                    print("[!] Payload vuoto.")
        except Exception as e:
            print(f"Error in action loop: {e}")
        
        # Programma il prossimo aggiornamento
        self.after(100, self.action)

if __name__ == "__main__":
    app = ListaConteggiApp()
    app.mainloop()