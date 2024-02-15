import tkinter as tk
from tkinter import ttk
from threading import Thread
import socket
import time
import os
from PIL import ImageTk, Image

myip = socket.gethostbyname(socket.gethostname())
port = 4444
row = 1
server_running=True

root = tk.Tk()

def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
    if event:
        at_bottom = event.height >= canvas.bbox("all")[3]
        if at_bottom:
            canvas.unbind_all("<MouseWheel>")
        else:
            canvas.bind_all("<MouseWheel>", on_mousewheel)

def start_server():
    global myip, server, clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((myip, port))
    server.listen()
    
    clients = set()
    connected_ips = set()
        
    def check_connections():
        while True:
            try:
                for client in clients:
                    client[0].send("ping".encode())
                    client[0].recv(1024).decode() #pong
            except ConnectionResetError:
                client[0].close()
                print(client[1]+" disconnected!")
                client[4].grid_remove()
                client[5].grid_remove()
                client[6].grid_remove()
                client[7].grid_remove()
                clients.remove(client)
                connected_ips.remove(client[1])
            except ConnectionAbortedError:
                break
            except OSError:
                break
            time.sleep(0.75)
    
    def m_client(client):
        global root_clients, row, canvas
        print(client)
        client.send("ip".encode())
        ipclient = client.recv(1024).decode()
        client.send("user".encode())
        userclient = client.recv(1024).decode()
        statusclient = True
        
        def shutdown():
            print("shutdown")
            client.send("shutdown".encode())
            print(client.recv(1024).decode())
            client.close()
            client_info[4].grid_remove()
            client_info[5].grid_remove()
            client_info[6].grid_remove()
            client_info[7].grid_remove()
            clients.remove(client_info)
            connected_ips.remove(client_info[1])
            
        if ipclient not in connected_ips:
            connected_ips.add(ipclient)
            ipcliententry = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
            ipcliententry.insert(0, ipclient)
            ipcliententry.config(state="readonly")
            ipcliententry.grid(row=row, column=0)
            
            usercliententry = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
            usercliententry.insert(0, userclient)
            usercliententry.config(state="readonly")
            usercliententry.grid(row=row, column=1)
    
            statuscliententry = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
            statuscliententry.insert(0, "Online" if statusclient == True else "Offline")
            statuscliententry.config(state="readonly")
            statuscliententry.grid(row=row, column=2)
            
            shutdown_button=ttk.Button(root_clients, text="Shutdown", width=27, command=shutdown)
            shutdown_button.grid(row=row, column=3, sticky="w")
            
            row += 1
            
            client_info = tuple([client, ipclient, userclient, statusclient, ipcliententry, usercliententry, statuscliententry, shutdown_button])
            clients.add(client_info)
            
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        else:
            client.close()
    
    Thread(target=check_connections).start()
    
    while server_running:
        client, address = server.accept()
        Thread(target=m_client, args=(client, )).start()
    
server_thread=Thread(target=start_server)
server_thread.start()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.title("Shutdowner")
root.iconbitmap("images/logo.ico")
root.geometry(f"750x500+{int(screen_width/2-375)}+{int(screen_height/2-250)}")
root.resizable(False, False)

#ip
tk.Label(root, text="IP:", font="Arial 26 bold").place(x=89, y=15)
image = Image.open("images/backip.png")
image = image.resize((len(myip) * 20, 50))
image = ImageTk.PhotoImage(image)
tk.Label(root, image=image).place(x=149, y=11)
tk.Label(root, text=str(myip), font="Arial 26 bold", fg="white", bg="#009c00").place(x=164, y=15)

def on_validate(P):
    if P.isdigit() and len(P) <= 4:
        return True
    else:
        return False

#port
tk.Label(root, text="PORT:", font="Arial 26 bold").place(x=414, y=15)
imagep = Image.open("images/backport.png")
imagep = imagep.resize((len(str(port)) * 30, 50))
imagep = ImageTk.PhotoImage(imagep)
tk.Label(root, image=imagep).place(x=534, y=11)
validate_cmd = root.register(on_validate)
port_entry = tk.Entry(root, text=str(port), font="Arial 26 bold", fg="white", bg="#ff6400", width=5, borderwidth=0, insertbackground="white", validate="key", validatecommand=(validate_cmd, "%P"), justify="center")
port_entry.insert(0, str(port))
port_entry.place(x=549, y=15)

root_ = tk.Frame(root)
root_.place(x=0, y=80)

canvas = tk.Canvas(root_, width=725, height=300, highlightthickness=0)
canvas.pack(side='left', fill='both', expand=True)

root_clients = tk.Frame(canvas)
canvas.create_window((0, 0), window=root_clients, anchor='nw')

ipcolumn = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
ipcolumn.insert(0, "IP address:")
ipcolumn.config(state="readonly")
ipcolumn.grid(row=0, column=0)

usercolumn = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
usercolumn.insert(0, "User:")
usercolumn.config(state="readonly")
usercolumn.grid(row=0, column=1)

statuscolumn = tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold")
statuscolumn.insert(0, "Status:")
statuscolumn.config(state="readonly")
statuscolumn.grid(row=0, column=2)

tk.Entry(root_clients, justify=tk.CENTER, font="Arial 12 bold", state="readonly").grid(row=0, column=3)

def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
    at_bottom = event.height >= canvas.bbox("all")[3]
    if at_bottom:
        canvas.unbind_all("<MouseWheel>")
    else:
        canvas.bind_all("<MouseWheel>", on_mousewheel)

canvas.bind('<Configure>', update_scrollregion)

scrollbar = tk.Scrollbar(root_, orient='vertical', command=canvas.yview)
scrollbar.pack(side='right', fill='y')

canvas.config(yscrollcommand=scrollbar.set)

def on_mousewheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), 'units')

canvas.bind_all("<MouseWheel>", on_mousewheel)

def close_window():
    global clients
    for clt in clients:
        try:
            clt[0].close()
        except:
            pass
    os._exit(0)

root.protocol("WM_DELETE_WINDOW", close_window)
root.mainloop()
