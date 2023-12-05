import socket
import threading
import time
import hashlib
import matplotlib.pyplot as plt

MAX_SIZE = 2048
FORMAT = "utf-8"

# Connect to vayu via server_socket
# host = "vayu.iitd.ac.in"
host = "10.17.51.115"
port = 9801

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending message to receive total bytes to receive
message = "SendSize\nReset\n\n"
while(1):
    server_socket.sendto(message.encode(), (host, port))
    server_socket.settimeout(0.05)
    
    try:
        data, server_address = server_socket.recvfrom(MAX_SIZE)
        response = data.decode()
        print(response)
        break
    except socket.timeout:
        print("SENDING AGAIN")

# Receive total bytes from the server
TOT_BYTES = int((response.split('\n')[0]).split()[1])
print(TOT_BYTES)

start_time = time.time()

sent_dict = {}
response_dict = {}

lines_dict = {}
dict_size = int((TOT_BYTES+1447)/1448)

flag = False

# not_found_arr = [i for i in range(dict_size)]
not_found_arr = [0 for i in range(dict_size)]
# offset = 0
run = True
while(run):
	new_not_found = []
	for index in range(dict_size):
		if len(lines_dict.keys()) == dict_size:
			run = False
			break
		if not_found_arr[index] == 0:
			offset = index*1448
			k = 1448
			if (index == dict_size-1):
				k = TOT_BYTES%1448
			print("REQUEST SENT")
			message = f"Offset: {offset}\nNumBytes: {k}\n\n"
			server_socket.sendto(message.encode(), (host, port))
			if flag:
				sent_dict[index] += [time.time() - start_time]
			else:
				sent_dict[index] = [time.time() - start_time]
			server_socket.settimeout(0.05)
			try:
				data, server_address = server_socket.recvfrom(MAX_SIZE)
				response = data.decode()
				t = int(int(response.split()[1])/1448)
				response_dict[t] = time.time() - start_time
				# print(response)
				print("RESPONSE RECEIVED")
				# print(int(offset/1448))
				print(t)
				# print()
				# print(response[-1448:])
				lines_dict[t] = response[-k:]
				not_found_arr[t] = 1
			except socket.timeout:
				# new_not_found += [index]
				print("NO RESPONSE RECEIVED")
				
			time.sleep(0.02)
		# offset += 1448
		# offset %= TOT_BYTES + 1448
	flag = True
	# not_found_arr = new_not_found



full_data = ""
for i in range(dict_size):
    full_data += lines_dict[i]

print(full_data)

md5_hash = hashlib.md5()
md5_hash.update(full_data.encode())
md5_hex = md5_hash.hexdigest()

message = f"Submit: amaiom@team\nMD5: {md5_hex}\n\n"
while(1):
    server_socket.sendto(message.encode(), (host, port))
    server_socket.settimeout(0.05)
    
    try:
        data, server_address = server_socket.recvfrom(MAX_SIZE)
        response = data.decode()
        # print(response)
        break
    except socket.timeout:
        print("SENDING RESULT AGAIN")

# Close the UDP connection with Vayu
server_socket.close()

sent_file = open("SENT_TIME.txt", 'w')
response_file = open("RESPONSE_TIME.txt", 'w')

for i in range(dict_size):
    sent_file.write(f"Offset: {i*1448} Time: \n{sent_dict[i]}\n")
    response_file.write(f"Offset: {i*1448} Time: {response_dict[i]}\n")