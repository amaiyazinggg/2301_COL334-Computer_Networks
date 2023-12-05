import socket
import threading
import sys
import time

MAX_SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# f = open("Slave.txt", "w")
# f.close()
# f = open("Vayu.txt", "w")
# f.close()

NUM_DEVICES = 0

def check_host_server(address, port): # Function for checking connection with vayu
    timeout = 40
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    print ("Attempting to connect to %s on port %s" % (address, port))
    try:
        s.connect((address, port))
        return "Connected to %s on port %s" % (address, port)
    except socket.error as error:
        return "Connection to %s on port %s failed: %s" % (address, port, error)
    finally:
        s.close()
        
def reset_server(sockets): # Function for performing session reset
    sockets.sendall(b'SESSION RESET\n')
    message_ok = sockets.recv(MAX_SIZE)
    
def submit(socket, no_of_lines): # Function for submitting finally
	socket.sendall(b"SUBMIT\n")
	socket.sendall(b"amaiya@col334-672\n")
	lines_text = str(no_of_lines) + "\n"
	socket.sendall(b"1000\n")
	
	for i in range(no_of_lines):
		num_text = str(i) + "\n"
		socket.sendall(num_text.encode())
		curr_line = new_received_lines[i] + "\n"
		socket.sendall(curr_line.encode())
		
	submission_message = socket.recv(MAX_SIZE).decode(FORMAT)
	submission_details = submission_message.split()
	print(submission_message)
	print("TIME TAKEN: ", (int(submission_details[-1]) - int(submission_details[-3][:-1]))/1000, "s")
	
def distribute(receiver_socket, data):
	for sockets in slave_connections:
		if (sockets != receiver_socket):
			try:
				sockets.sendall(data)
			except:
				try:
					slave_connections.remove(sockets)
				except:
					next

count = 0
no_of_lines = 1000
new_received_lines = {}
new_received_time = {}
received_bool = [-1 for i in range(no_of_lines)]

def write_time(filename):
	print("Writing to File")
	with open (filename, 'a') as file:
		times = list(new_received_time.values())
		times.sort()
		for time in times:
			file.write(str(time)+'\n')
	print("Finished writing to File")
	
	
def handle_client(conn, addr, server_socket):
	print(f"[NEW CONNECTION] {addr} started.")
	global slave_connections
	
	response = conn.makefile("r", encoding="utf-8", newline="\n")
	while True:
		try:
			# while not submitted:
				
			if len(new_received_lines) == no_of_lines:
				print("Master Process Completed 1")
				return
				
			myline = response.readline()
			mydata = response.readline()
			line_no = int(myline)
			line = mydata.split("\n")[0]

			# f = open("Slave.txt", "a")
			# f.write(str(line_no) + '\n')
			# f.write(line + '\n')
			# f.close()
			
			# if len(new_received_lines) in range (50, 53):
			# 	print("Attempting Close")
			# 	conn.shutdown()
			# 	conn.close()
				# server_socket = None
				
			if (received_bool[line_no] == -1):
				print("Received from Slave")
				
				new_received_lines[line_no] = line
				new_received_time[line_no] = time.time() - start

				print(len(new_received_lines))
				received_bool[line_no] = 1
				
				message = myline + mydata
				try:
					distribute(conn, message.encode())
				except:
					print("dc")
					
		except:
			if len(new_received_lines) == no_of_lines:
				print("Master Process Completed 1")
				return
				
			print(f"Disconnected from Client {addr}")
			# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# server_socket.bind(addr)
			slave_connections.remove(conn)
			server_socket.listen()
			conn, addr = server_socket.accept()
			response = conn.makefile("r", encoding="utf-8", newline="\n")
			slave_connections += [conn]
			
			print("Socket added")
		# return
		
		
sent_data = {}	
received_data = {}

def buffer_distribution(conn):
	while True:
		for i in range(no_of_lines):
			if (i in received_data.keys()):
				# print("Hi ", i)
				if sent_data[conn][i] == -1:
					conn.sendall(received_data[i])
					sent_data[conn][i] = 1
		 
    
def runner(server_socket):
	print("RUNNER ACTIVATED")
	global slave_connections
	while True:
		try:
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
					print("Received from Vayu")
					
					# f = open("Vayu.txt", "a")
					# f.write(str(line_no) + '\n')
					# f.write(line + '\n')
					# f.close()
					
					new_received_lines[line_no] = line
					new_received_time[line_no] = time.time() - start
					print(len(new_received_lines))
					received_bool[line_no] = 1
					
					# try:
					distribute(server_socket, data) # Distribute to everyone
				
			# if len(new_received_lines) in range (230, 232):
			# 	server_socket.close()
			# 	server_socket = None

			if len(new_received_lines) == no_of_lines:
				print("Master Process Completed 2")
				submit(server_socket, no_of_lines)
				# write_time("4run2.txt")
				# submitted = True
				
				for sockets in slave_connections:
					try:
						sockets.sendall(b"EM")
					except:
						continue

				return
			
		except:
			print("Disconnected from Vayu")
			disconnected = True
			
			while disconnected:
				try:
					# time.sleep(5)
					server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					server_socket.connect((host, port))
					disconnected = False
				except:
					next
					
			print("Reconnected to Vayu")
				

			
submitted = False
# Start listening on Server_Socket
server_port = 12905
server = socket.gethostbyname(socket.gethostname())
print(server)
print(socket.gethostname())
addr = ("10.194.36.209", server_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(addr)
server_socket.listen()
print(f"[LISTENING] Server is listening on {server}")

# Connect to VAYU via vayu_socket
host = "10.17.7.218"

port = 9803
vayu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

slave_connections = []
slave_threads = []
sending_threads = []


start = 0
if NUM_DEVICES == 0:
	vayu_socket.connect((host, port))
	reset_server(vayu_socket)
	vayu_thread = threading.Thread(target = runner, args=(vayu_socket,))
	vayu_thread.start()
	start = time.time()
else:
	while True:
		conn, addr = server_socket.accept()
		print(f"[NEW CONNECTION] {addr} established.")
		slave_connections += [conn]
		thread = threading.Thread(target=handle_client, args=(conn, addr, server_socket))
		
		# sending_thread = threading.Thread(target=buffer_distribution, args = (conn, server_socket))
		# sending_thread.start()
		
		slave_threads += [thread]
		# sending_threads += [sending_thread]
		# thread.start()
		
		sent_data[conn] = [-1 for i in range(no_of_lines)]
		
		if len(slave_connections) == NUM_DEVICES:
			for sockets in slave_connections:
				sockets.sendall(b"ACK")
			print("Both ACK sent")
			break
			
			
	syn_acks = 0
	while True:
		for sockets in slave_connections:
			data = sockets.recv(MAX_SIZE)
			if data.decode(FORMAT) == "SYNACK":
				print("One SYNACK received")
				syn_acks += 1
				
		if syn_acks == NUM_DEVICES:
			for thread in slave_threads:
				thread.start()
				
			print("All SYN-ACK received")
			
			for sockets in slave_connections:
				sockets.sendall(b"FIN")
				
			print("All FIN sent")
			vayu_socket.connect((host, port))
			vayu_thread = threading.Thread(target = runner, args=(vayu_socket,))
			reset_server(vayu_socket)
			start = time.time()
			vayu_thread.start()
			break



# # server_socket.close()