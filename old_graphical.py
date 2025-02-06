from datetime import datetime
import tkinter as tk
import threading  # Per eseguire il loop principale in un thread separato
from pyrf24 import RF24, RF24_PA_MAX, RF24_250KBPS, RF24Network, RF24NetworkHeader

# Impostazione dei pin per Raspberry Pi
radio = RF24(22, 0)  # Pin CE (22) e CSN (0)
network = RF24Network(radio)

address = 0  # Indirizzo del master (nodo 0)

# Liste per gli UID
uidList = []
studentsList = []  # Categoria 3
teachersList = []  # Categoria 1
specialsList = []  # Categoria 2

# Funzione per inviare messaggi al nodo slave
def send_message(data, slave_address):
    header = RF24NetworkHeader(slave_address)  # Crea un header per il pacchetto
    network.write(header, data.encode())  # Invia i dati al nodo slave
    print(f"Sent message: {data}")

# Funzione per ricevere messaggi dal nodo slave
def receive_message():
    network.update()
    if network.available():
        header, payload = network.read()  # Leggi i dati
        print(f"Received message from node {header.from_node}: {payload.hex()}")

        # Restituisci i dati come una lista [header_from_node, payload]
        return [header.from_node, list(payload)]
    else:
        return False

# Funzione per svuotare i buffer FIFO prima di inviare o ricevere
def flush_buffers():
    radio.flush_tx()  # Svuota il buffer di trasmissione
    radio.flush_rx()  # Svuota il buffer di ricezione
    print("[i] Buffers flushed (TX and RX)")

# Inizializzazione del nodo master
def setup():
    if radio.begin():
        print("[i] - Master unit initialized")
          # Inizializza la radio
    network.begin(90, address)  # Canale 90, nodo 0
    radio.setPALevel(RF24_PA_MAX)
    radio.setDataRate(RF24_250KBPS)
    radio.setChannel(100)  # Canale 100

# Funzione di loop principale
def loop(app):
    while True:
        # Controlla se ci sono messaggi da ricevere
        payloadWithHeader = receive_message()

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
                    if uid not in uidList:
                        uidList.append(uid)
                        print(f"[+] - UID dal nodo {headerFromNode} aggiunto: {''.join(format(x, '02x') for x in uid)}")

                        if int(category) == 1:
                            print("Categoria: Docenti")
                            teachersList.append(uid)
                        elif int(category) == 2:
                            print("Categoria: Invalidi")
                            specialsList.append(uid)
                        elif int(category) == 3:
                            print("Categoria: Studenti")
                            studentsList.append(uid)
                        else:
                            print("Formato invalido. UID aggiunto solo alla lista principale.")

                        # Aggiorna i conteggi nell'interfaccia grafica
                        app.aggiorna_numeri()
                    else:
                        print("[i] - Tag già registrato")
                else:
                    # Sovrascrivi il testo nella finestra principale
                    if uid in teachersList:
                        app.update_message(f"TEACHER AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    elif uid in specialsList:
                        app.update_message(f"SPECIAL NEEDING AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    elif uid in studentsList:
                        app.update_message(f"STUDENT AT NODE {headerFromNode}\nUID: {uid}\n{datetime.now()}")
                    else:
                        app.update_message("Not registered tag")
            else:
                print("[!] Payload vuoto.")

# Modifica della classe ListaConteggiApp
class ListaConteggiApp:
    def __init__(self, root, uidList, studentsList, teachersList, specialsList):
        self.root = root
        self.root.title("Contatore Elementi per Liste")

        self.uidList = uidList
        self.studentsList = studentsList
        self.teachersList = teachersList
        self.specialsList = specialsList

        # Imposta la finestra a tutto schermo
        self.root.attributes("-fullscreen", True)
        self.root.bind("<F11>", self.toggle_fullscreen)  # Tasto F11 per attivare/disattivare fullscreen
        self.root.bind("<Escape>", self.exit_fullscreen)  # Tasto Escape per uscire dal fullscreen
        self.root.bind("<Configure>", self.resize_text)  # Evento per ridimensionare il testo

        # Variabili per visualizzare i conteggi
        self.lista1_count = tk.StringVar()
        self.lista2_count = tk.StringVar()
        self.lista3_count = tk.StringVar()
        self.lista4_count = tk.StringVar()

        # Frame principale per contenere i widget
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Font di base (sarà aggiornato dinamicamente)
        self.default_font_size = 16
        self.font = ("Helvetica", self.default_font_size)

        # Etichette per visualizzare i conteggi
        self.label_lista1 = tk.Label(self.main_frame, textvariable=self.lista1_count, font=self.font)
        self.label_lista1.pack(pady=10, fill=tk.BOTH, expand=True)

        self.label_lista2 = tk.Label(self.main_frame, textvariable=self.lista2_count, font=self.font)
        self.label_lista2.pack(pady=10, fill=tk.BOTH, expand=True)

        self.label_lista3 = tk.Label(self.main_frame, textvariable=self.lista3_count, font=self.font)
        self.label_lista3.pack(pady=10, fill=tk.BOTH, expand=True)

        self.label_lista4 = tk.Label(self.main_frame, textvariable=self.lista4_count, font=self.font)
        self.label_lista4.pack(pady=10, fill=tk.BOTH, expand=True)

        # Etichetta per il messaggio in tempo reale
        self.label_message = tk.Label(self.main_frame, text="", font=("Helvetica", 20), fg="red")
        self.label_message.pack(pady=20, fill=tk.BOTH, expand=True)

        # Inizializzazione dei numeri all'avvio
        self.aggiorna_numeri()

    def aggiorna_numeri(self):
        self.lista1_count.set(f"Registered UIDs: {len(self.uidList)}")
        self.lista2_count.set(f"Teachers: {len(self.teachersList)}")
        self.lista3_count.set(f"Students: {len(self.studentsList)}")
        self.lista4_count.set(f"Special needings: {len(self.specialsList)}")

    def resize_text(self, event):
        new_font_size = max(12, int(event.width / 50))
        self.font = ("Helvetica", new_font_size)
        self.label_lista1.config(font=self.font)
        self.label_lista2.config(font=self.font)
        self.label_lista3.config(font=self.font)
        self.label_lista4.config(font=self.font)
        self.label_message.config(font=("Helvetica", new_font_size + 4))

    def update_message(self, message):
        # Aggiorna il messaggio in tempo reale
        self.label_message.config(text=message)

    def toggle_fullscreen(self, event=None):
        current_state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current_state)
        return "break"

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)
        return "break"

# Main program
if __name__ == "__main__":
    setup()  # Imposta la radio e la rete

    # Configura l'interfaccia grafica
    root = tk.Tk()
    app = ListaConteggiApp(root, uidList, studentsList, teachersList, specialsList)

    # Esegui il loop principale in un thread separato per non bloccare l'interfaccia grafica
    thread = threading.Thread(target=loop, args=(app,), daemon=True)
    thread.start()

    # Avvia l'interfaccia grafica
    root.mainloop()