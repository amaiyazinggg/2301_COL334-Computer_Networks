# 2301_COL334-Computer_Networks
Assignments for the undergraduate course on Computer Networks (COL334/COL672) at IIT Delhi, Fall Semester 2023

## Assignment 1
- Experimenting with tools such as traceroute, nmap, wireshark, ifconfig, ping etc

## Assignment 2
- A server was setup to which each client could connect to download parts of the file.
- Each group (of 4 members) had to write a client program and run it on multiple devices (up to four
devices) which can collaborate amongst themselves to exchange distinct parts of the file each of them
have received and reassemble the entire file.

## Assignment 3
- Aim was to implement a TCP-like protocol for reliable data transfer, with congestion
control-like mechanisms to not overwhelm the network yet obtain high throughput.
- A UDP server was setup which had a leaky bucket filter to mimic congestion.
- Aim was to download the entire file quickly but while minimising penalty at the same time.
