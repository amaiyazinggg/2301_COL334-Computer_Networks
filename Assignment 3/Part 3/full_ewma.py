import socket
import threading
import time
import hashlib
import matplotlib.pyplot as plt

MAX_SIZE = 2048
FORMAT = "utf-8"

# Connect to vayu via server_socket
host = "10.17.7.218"
# host = "vayu.iitd.ac.in"
# host = "127.0.0.1"
port = 9802
lhost = "127.0.0.1"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def ensure_correctness():
	for i in range(10):
	    server_socket.settimeout(0.01)
	    try:
	        data, server_address = server_socket.recvfrom(MAX_SIZE)
	        response = data.decode()
	        # print(response)
	        return response
	        
	    except socket.timeout:
	        print("CHECK")
	time.sleep(0.1)

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
	        
def calculate_rtt():
	start = time.time()
	count = 0
	rtt = 0.03
	alpha = 0.4
	times = 0
	i = 0
	while(1):
		message = f"Offset: {i}\nNumBytes: 1448\n\n"
		server_socket.sendto(message.encode(), (host, port))
		sent_dict[i//1448] = [time.time() - start_time]
		server_socket.settimeout(0.03)
	    
		try:
			data, server_address = server_socket.recvfrom(MAX_SIZE)
			response = data.decode()
			count += 1
	        
			
			k = 1448
			t = int(int(response.split()[1])/1448)
			response_dict[t] = time.time() - start_time
			found_arr[t] = 1
			if (t == dict_size - 1):
				k = TOT_BYTES%1448
				
			print(f"Received {t}")

			if response.split('\n')[2] == 'Squished':
				print("SQUISH ALERT")
				
			lines_dict[t] = response[-k:]

			if (count == 5):
				start = time.time()
				time.sleep(rtt)
	        	
			if (count == 10):
				rtt = (1-alpha)*rtt + alpha*(time.time() - start)
				print(f"rtt {rtt}")
				time.sleep(rtt)
				start = time.time()
				count = 6
				times += 1
				if (times == 10):
					return rtt
	        
		except socket.timeout:
		    print("SENDING AGAIN")
		    
		i += 1448
	
	        
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
	# write_to_files()
	        
# Function for writing the data to the files
def write_to_files():
	sent_file = open("NewTrace/SENT_TIME_17.txt", 'w')
	response_file = open("NewTrace/RESPONSE_TIME_17.txt", 'w')
	burst_file = open("NewTrace/burst_TIME_17.txt", 'w')
	rtt_file = open("NewTrace/rtt_TIME_17.txt", "w")

	for i in range(dict_size):
	    sent_file.write(f"Offset: {i*1448} Time: \n{sent_dict[i]}\n")
	    response_file.write(f"Offset: {i*1448} Time: {response_dict[i]}\n")
	for i in burstsize.keys():
	    burst_file.write(f"BurstSize: {burstsize[i]} Time: {i}\n")
	for i in rtt_change.keys():
		rtt_file.write(f"RTT: {rtt_change[i]} Time: {i}\n")
	    
def aimd(ind_list, last_time):
	
	global cwnd
	global rtt
	global max_cwnd
	
	while(1):
		rec = 0
		for i in ind_list:
			if found_arr[i]:
				rec += 1
				
		if time.time() - last_time > rtt or (rec == len(ind_list) and rec > 1):
			if rec == 0:
				if host == lhost:
					rtt *= 1.05
				else:
					rtt *= 1.01
			elif rec == 1:
				rtt = rtt
			elif rec == 2:
				rtt = 0.1*(time.time() - last_time) + 0.9*rtt
			else:
				rtt = 0.2*(time.time() - last_time) + 0.8*rtt
				
			rtt_change[time.time() - start_time] = rtt
			 
			print(f"RTT is {rtt}")
			count = len(ind_list)
			for index in ind_list:
				if found_arr[index] == 1:
					count -= 1
			if count >= 0.2 * cwnd:
				cwnd *= 0.5
				cwnd = int(max(cwnd, 1))
				burstsize[time.time() - start_time] = cwnd
				print("congestion window size reduced to ", cwnd)
			else:
				cwnd = min(cwnd+1, max_cwnd)
				burstsize[time.time() - start_time] = cwnd
				print("congestion window size increased to ", cwnd)
			return
	 
def request_lines(server_socket):
	global cwnd
	global rtt
	global index
	global inflight
	global MAX_SIZE
	global last_ind
	
	run = True
	flag = True
	

	while(run):
		count = 0
		last_time = time.time()
		last_ind = []
		while (count < cwnd):
			if len(lines_dict) == dict_size:
				run = False
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
				server_socket.sendto(message.encode(), (host, port))
				print(f"REQUEST SENT {index}")
				if flag:
					sent_dict[index] = [time.time() - start_time]
				else:
					sent_dict[index] += [time.time() - start_time]
					
				last_ind.append(index)
				count += 1
				# inflight += 1
			index += 1
			
		# call the function here
		# aimd_thread = threading.Thread(target=aimd, args=(last_ind, last_time))
		# aimd_thread.start()
		aimd(last_ind, last_time)
		# time.sleep(rtt)
				
		# while(1):
		# 	if (time.time() - last_time) > rtt:
		# 		print("INFLIGHT ", inflight)
		# 		if inflight >= 0.2 * cwnd:
		# 			print("Congestion Window Size Reduced")
		# 			cwnd *= 0.5
		# 			cwnd = int(cwnd)
		# 			cwnd = max(cwnd, 1)
		# 			inflight = 0
		# 		else:
		# 			print("Congestion Window Size Increased")
		# 			cwnd = min(cwnd+1, max_cwnd)
		# 			cwnd += 1
		# 			inflight = 0
		# 		break
	return
	
def receive_lines(server_socket):
	global cwnd
	global rtt
	global index
	global inflight
	global MAX_SIZE
	global last_ind
	
	while(1):
		if len(lines_dict) == dict_size:
			break
			
		server_socket.settimeout(0.5)
		try:
			data, server_address = server_socket.recvfrom(MAX_SIZE)
			response = data.decode()
			t = int(int(response.split()[1])/1448)
			response_dict[t] = time.time() - start_time
			print(f"RESPONSE RECEIVED {t}")
			# print(t)
			
			found_arr[t] = 1
			k = 1448
			
			if (t == dict_size - 1):
				k = TOT_BYTES%1448

			if response.split('\n')[2] == 'Squished':
				print("SQUISH ALERT")
				max_cwnd = cwnd - 1
				
			lines_dict[t] = response[-k:]
			# if t in last_ind:
			# 	inflight -= 1
			
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

rtt_change = {}
sent_dict = {}
response_dict = {}
burstsize = {}

lines_dict = {}
dict_size = int((TOT_BYTES+1447)/1448)
print(dict_size, " ", TOT_BYTES)


cwnd = 5
rtt = 0.01
index = 0
last_ind = index
inflight = 0
found_arr = [0 for i in range(dict_size)]
max_cwnd = 1000
sent_time = {}
ensure_correctness()
# rtt = calculate_rtt()
print(f"RTT is {rtt}")

sending_thread = threading.Thread(target=request_lines, args=(server_socket, ))
receiving_thread = threading.Thread(target=receive_lines, args=(server_socket, ))
sending_thread.start()
receiving_thread.start()


