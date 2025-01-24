import tkinter as tk
import time
from pyrf24 import RF24, RF24_PA_MAX, RF24_250KBPS, RF24Network, RF24NetworkHeader

# Impostazione dei pin per Raspberry Pi
radio = RF24(22, 0)  # Pin CE (22) e CSN (0)
network = RF24Network(radio)

address = 0  # Indirizzo del master (nodo 0)

uidList = []

studentsList = [] #3
teachersList = [] #1
specialsList = [] #2


# Funzione per inviare messaggi al nodo slave
def send_message(data, slave_address):
    header = RF24NetworkHeader(slave_address)
    network.write(header, data.encode())
    print(f"Sent message: {data}")


def receive_message():
    network.update()
    if network.available():
        header, payload = network.read()  
        print(f"Received message from node {header.from_node}: {payload.hex()}")

        return [header.from_node, list(payload)]
    else:
        return False

# Funzione per svuotare i buffer FIFO prima di inviare o ricevere
def flush_buffers():
    radio.flush_tx()
    radio.flush_rx() 
    print("[i] Buffers flushed (TX and RX)")



def setup():
    if radio.begin():
        print("[i] - Master unit initialized")
    network.begin(90, address)  # Canale 90, nodo 0
    radio.setPALevel(RF24_PA_MAX)
    radio.setDataRate(RF24_250KBPS)
    radio.setChannel(100)  # Canale 100




def loop():
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
                        print(f"[+] - uid dal nodo {headerFromNode} aggiunto: {''.join(format(x, '02x') for x in uid)}")

                        print(int(category))
                        
                        if int(category) == 1:
                            print("categoria docenti\n\n")
                            teachersList.append(uid)
                        elif int(category) == 2:
                            print("categoria invalidi\n\n")
                            specialsList.append(uid)
                        elif int(category) == 3:
                            print("categoria studenti\n\n")
                            studentsList.append(uid)
                        else:
                            print("formato invalido. UID aggiunto solo alla lista principale\n\n")


                    else:
                        print("[i] - tag già registrato")
                else:
                    if uid in teachersList:
                        print(f"!!! docente al nodo {headerFromNode} !!!")
                    elif uid in specialsList:
                        print(f"!!! invalido al nodo {headerFromNode} !!!")
                    elif uid in studentsList:
                        print(f"!!! studente al nodo {headerFromNode} !!!")
                    else:
                        print("[i] - tag non registrato")
            else:
                print("[!] Payload vuoto.")

# Main program
if __name__ == "__main__":
    setup()
    loop()