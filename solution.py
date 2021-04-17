﻿from socket import *
import os
import sys
import struct
import time
import select
import binascii


ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise


def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0


    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2


    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff


    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.


    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    myID = os.getpid() & 0xFFFF  # Return the current process id
    #print(myID)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    #print(header)
    data = struct.pack("d", time.time())
    print("timesent: " + str(time.time()))
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end


    # So the function ending should look like this

    packet = header + data
    #print(packet)
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces
    #print("test1")

    for ttl in range(1,MAX_HOPS):
        #print("test2")
        for tries in range(TRIES):
            #print("test3")
            destAddr = gethostbyname(hostname)


            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end


            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                #print("test4")
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                #print(t)
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1 = [ttl,"*","Request timed out"]
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist2.append(tracelist1)
                    #print(tracelist1)
                    #print(tracelist2)
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                print("timereceived: " + str(timeReceived))
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1 = [ttl,"*","Request timed out"]
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist2.append(tracelist1)
                    #Fill in end
            except timeout:
                continue


            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmp_header = recvPacket[20:28]
                types, code, check_sum, packetid, seq = struct.unpack("bbHHh", icmp_header)
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    dest = gethostbyaddr(addr[0])
                    #print(dest)
                    #print(tracelist1)
                    #print(tracelist2)
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    #print("herror")
                    dest = "hostname not returnable"
                    #print(tracelist1)
                    #print(tracelist2)
                    #Fill in end


                if types == 11:
                    bytes = struct.calcsize("d")
                    #timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #print("timesent: " + str(timeSent))
                    #Fill in start
                    #You should add your responses to your lists here
                    #print("Type 11")
                    #print("%d   %.0fms %s %s" %(ttl, int(timeReceived - timeSent) *1000, addr[0], dest[0]))
                    tracelist1 = [ttl,(timeReceived - timeSent) * 1000,addr[0],dest[0]]
                    tracelist2.append(tracelist1)
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    #print("Type 3")
                    #print("%d   %.0fms %s %s" %(ttl, int(timeReceived - timeSent) *1000, addr[0], dest[0]))
                    tracelist1 = [ttl,(timeReceived - timeSent) * 1000,addr[0],dest[0]]
                    tracelist2.append(tracelist1)
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    #print("Type 0")
                    #print("%d   %.0fms %s %s" %(ttl, int(timeReceived - t) *1000, addr[0], dest[0]))
                    tracelist1 = [ttl,(timeReceived - timeSent) * 1000,addr[0],dest[0]]
                    tracelist2.append(tracelist1)
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    #print("* * * No ICMP Packets recieved.")
                    tracelist1= ["* * * No ICMP Packets recieved. Check Firewall"]
                    tracelist2.append(tracelist1)
                    #Fill in end
                break
            finally:
                mySocket.close()

    print(tracelist2)
    return tracelist2

if __name__ == '__main__':
    get_route("nyu.edu")