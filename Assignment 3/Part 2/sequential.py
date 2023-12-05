import socket
import threading
import time
import hashlib
import matplotlib.pyplot as plt

MAX_SIZE = 2048
FORMAT = "utf-8"

# Connect to vayu via server_socket
host = "10.17.51.115"
# host = "127.0.0.1"
# host = "vayu.iitd.ac.in"
port = 9801

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending message to receive total bytes to receive
def get_size():
	message = "SendSize\nReset\n\n"
	while(1):
	    server_socket.sendto(message.encode(), (host, port))
	    server_socket.settimeout(0.05)
	    
	    try:
	        data, server_address = server_socket.recvfrom(MAX_SIZE)
	        response = data.decode()
	        # print(response)
	        return response
	        
	    except socket.timeout:
	        print("SENDING AGAIN")
	        
# Function for submitting the MD5 hash to the server
def submit():
	full_data = ""
	for i in range(dict_size):
	    full_data += lines_dict[i]

	# print(full_data)
	# print(lines_dict[dict_size-1])

	md5_hash = hashlib.md5()
	md5_hash.update(full_data.encode())
	md5_hex = md5_hash.hexdigest()

	message = f"Submit: amaiom@team\nMD5: {md5_hex}\n\n"
	for i in range(10):
	    server_socket.sendto(message.encode(), (host, port))
	    server_socket.settimeout(0.05)
	    
	    try:
	        data, server_address = server_socket.recvfrom(MAX_SIZE)
	        response = data.decode()
	        print(response)
	        # break
	    except socket.timeout:
	        print("SENDING RESULT AGAIN")
    
	write_to_files()
	        
# Function for writing the data to the files
def write_to_files():
	sent_file = open("SENT_TIME_05.txt", 'w')
	response_file = open("RESPONSE_TIME_05.txt", 'w')
	rate_file = open("RATE_TIME_05.txt", 'w')

	for i in range(dict_size):
	    sent_file.write(f"Offset: {i*1448} Time: \n{sent_dict[i]}\n")
	    response_file.write(f"Offset: {i*1448} Time: {response_dict[i]}\n")
	for i in windowsize.keys():
	    rate_file.write(f"Rate: {windowsize[i]} Time: {i}\n")
         
	 
def request_lines(server_socket):
	global cwnd
	global rtt
	# global index
	global inflight
	global MAX_SIZE
	global last_ind
	
	run = True
	index = 0
	flag = True
	while(1):
		count = 0
		last_time = time.time()
		last_ind = index
		
		if len(lines_dict) == dict_size:
			break
				
		if index >= dict_size:
			index = 0
			flag = False
				
		if found_arr[index] == 0:
			offset = index*1448
			k = 1448
			if (index == dict_size-1):
				k = TOT_BYTES%1448
			sent_time[index] = time.time()
			message = f"Offset: {offset}\nNumBytes: {k}\n\n"
			last_time = time.time()
			if flag:
				sent_dict[index] = [time.time() - start_time]
			else:
				sent_dict[index] += [time.time() - start_time]
			server_socket.sendto(message.encode(), (host, port))
			# print(f"REQUEST SENT {index}")

			time.sleep(1/cwnd)

		index += 1
	return
	
def receive_lines(server_socket):
	global cwnd
	global rtt
	# global index
	global inflight
	global MAX_SIZE
	global last_ind
	
	# index = 0
	count = 0
	twenty_ind = 1
	flag = False
	max_cwnd = 1000*cwnd
	while(1):
		if len(lines_dict) == dict_size:
			break
			
		server_socket.settimeout(rtt)
		try:
			data, server_address = server_socket.recvfrom(MAX_SIZE)
			response = data.decode()
			t = int(int(response.split()[1])/1448)
			response_dict[t] = time.time() - start_time
			print(f"RESPONSE RECEIVED {t}")
			count += 1
			
			print(f"WINDOW SIZE: {cwnd}")

			
			if (t >= twenty_ind*20):
				flag = True
				twenty_ind = t//20 + 1
			
			if flag:
				count -= 1
				if count < 15:
					max_cwnd = cwnd
				cwnd = max(cwnd * ((count + 3)/ 20), cwnd * 0.5)
				cwnd = min(max_cwnd, cwnd)
				count = 1
				flag = False
				windowsize[time.time() - start_time] = cwnd
			
			found_arr[t] = 1
			k = 1448
			
			if (t == dict_size - 1):
				k = TOT_BYTES%1448

			if response.split('\n')[2] == 'Squished':
				print("SQUISH ALERT")
				
			lines_dict[t] = response[-k:]
			
		except socket.timeout:
			print("NO RESPONSE RECEIVED")
			
	submit()
	server_socket.close()
	return

# Receive total bytes from the server
response = get_size()
TOT_BYTES = int((response.split('\n')[0]).split()[1])
print(TOT_BYTES)

start_time = time.time()

sent_dict = {}
response_dict = {}
windowsize = {}

lines_dict = {}
dict_size = int((TOT_BYTES+1447)/1448)

cwnd = 300
rtt = 0.1
# index = 0
# last_ind = index
inflight = 0
found_arr = [0 for i in range(dict_size)]
max_cwnd = 1000
sent_time = {}

sending_thread = threading.Thread(target=request_lines, args=(server_socket, ))
receiving_thread = threading.Thread(target=receive_lines, args=(server_socket, ))

receiving_thread.start()
sending_thread.start()