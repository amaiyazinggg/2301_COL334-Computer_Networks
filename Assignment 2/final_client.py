import socket
import threading
import time

MAX_SIZE = 4096
FORMAT = "utf-8"
# f = open("Master.txt", "w")
# f.close()
# f = open("Vayu.txt", "w")
# f.close()

def check_server(address, port):
    timeout = 40
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    print("Attempting to connect to %s on port %s" % (address, port))
    try:
        s.connect((address, port))
        return "Connected to %s on port %s" % (address, port)
    except socket.error as error:
        return "Connection to %s on port %s failed: %s" % (address, port, error)
    finally:
        s.close()


def reset_server(sockets):
    sockets.sendall(b'SESSION RESET\n')
    message_ok = sockets.recv(1024)


def submit(sockets, no_of_lines):  # Function for submitting finally
    sockets.sendall(b"SUBMIT\n")
    sockets.sendall(b"amaiya@col334-672\n")
    lines_text = str(no_of_lines) + "\n"
    sockets.sendall(b"1000\n")

    for i in range(no_of_lines):
        num_text = str(i) + "\n"
        sockets.sendall(num_text.encode())
        # curr_line = received_lines[i] + "\n"
        curr_line = new_received_lines[i] + "\n"
        sockets.sendall(curr_line.encode())

    submission_message = sockets.recv(MAX_SIZE).decode(FORMAT)
    submission_details = submission_message.split()
    print(submission_message)
    print("TIME TAKEN: ", (int(submission_details[-1]) - int(submission_details[-3][:-1]))/1000, "s")


count = 0
no_of_lines = 1000
# received_lines = [-1 for i in range(no_of_lines)]
new_received_lines = {}
received_bool = [-1 for i in range(no_of_lines)]

received_data = {}
caught_list = [-1 for i in range(no_of_lines)]


def redistribution(server_socket):
    while True:
        # print("hello1")
        for i in range(no_of_lines):
            # print("hello")
            if caught_list[i] == 1:
                # print("hi")
                server_socket.sendall(received_data[i])


def handle_master(conn):
    global master_socket
    fin = master_socket.recv(MAX_SIZE)
    
    if fin.decode(FORMAT) == "FIN":
        vayu_thread.start()
        
        response = master_socket.makefile("r", encoding="utf-8", newline="\n")
        while True:
            # print("thread to on hai")
            try:
                if (len(new_received_lines) == 1000):
                    return
                    
                myline = response.readline()
                
                # print(myline)
                    
                if myline == "EM":
                    return
                
                mydata = response.readline()
                
                line_no = int(myline)
                line = mydata.split("\n")[0]

                if line_no != -1:
                    # f = open("Master.txt", "a")
                    # f.write(str(line_no) + '\n')
                    # f.write(line + "\n")
                    # f.close()
                    
                    if received_bool[line_no] == -1:
                        print("Received from Master")
                        new_received_lines[line_no] = line

                        print(len(new_received_lines))
                        received_bool[line_no] = 1
                        
                        
            except:
                print("Disconnected from Master")
                disconnected = True
            
                while disconnected:
                    try:
                        # time.sleep(5)
                        master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        master_socket.connect((master_ip, master_port))
                        response = master_socket.makefile("r", encoding="utf-8", newline="\n")
                        conn = master_socket
                        disconnected = False
                    except:
                        next
                print("Reconnected to Master")



def runner(server_socket, client_socket):
    global count
    global master_socket
    
    # global lock
    while True:
        try:
            while True:
                server_socket.sendall(b"SENDLINE\n")
                data = b""

                while True:
                    remaining_data = server_socket.recv(MAX_SIZE)
                    data += remaining_data

                    if remaining_data.decode("utf-8")[-1] == "\n":
                        break

                if not data:
                    break

                message = data.decode("utf-8")
                message_details = message.split("\n")

                line_no = int(message_details[0])
                line = message_details[1]

                if line_no != -1:
                    if received_bool[line_no] == -1:
                        messi = str(line_no) + "\n" + line + "\n"
                        try:
                            master_socket.sendall(messi.encode())
                        except:
                            pass
                        # f = open("Vayu.txt", "a")
                        # f.write(str(line_no) + '\n')
                        # f.write(line + "\n")
                        # f.close()
                        print("Received from Vayu")

                        new_received_lines[line_no] = line
                        received_data[line_no] = data
                        caught_list[line_no] = 1
                        # count += 1
                        print(len(new_received_lines))
                        received_bool[line_no] = 1

                if len(new_received_lines) == no_of_lines:
                    print("Slave Process Completed")
                    submit(server_socket, no_of_lines)
                    return
                    
        except:
            print("Disconnected from Vayu")
            disconnected = True
            
            while disconnected:
                try:
                    time.sleep(5)
                    vayu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    vayu_socket.connect((host, port))
                    server_socket = vayu_socket
                    disconnected = False
                except:
                    next
            print("Reconnected to Vayu")


# check = check_server("10.194.59.176", 11111)
# print(check)

# Connect to vayu via vayu_socket
# host = "10.17.7.134"
host = "10.17.51.115"
port = 9801
vayu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vayu_socket.connect((host, port))
reset_server(vayu_socket)
# reset_server(vayu_socket
master_ip = "10.194.36.174"
master_port = 12900
master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master_socket.connect((master_ip, master_port))
redistribution_thread = threading.Thread(target=redistribution, args=(master_socket,))
# redistribution_threadead.start()
master_thread = threading.Thread(target=handle_master, args=(master_socket,))
vayu_thread = threading.Thread(target=runner, args=(vayu_socket, master_socket))

ack = master_socket.recv(MAX_SIZE)
if ack.decode(FORMAT) == "ACK":
    master_socket.sendall(b"SYNACK")
    master_thread.start()
