#The server for a simple web server using a reliable datagram protocol
#uses sockets and UDP packets
import socket
import sys
import os
import time 

def create_header(header_code, request_list,address,clientsocket,headers,port,val2):
    #print the headers to both the server and client files based on what the 
    #header code is and what the connection header is
    
    if header_code == 400:
        if address == 'h2':
            address = '10.10.1.100'
        clientsocket.send(bytes('\r\nHTTP/1.0 400 Bad Request\r\n\r', encoding='utf8'))
        clientsocket.send(bytes('Connection:close\n', encoding='utf8'))
        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y", time.localtime())
        print('{now}: '.format(now=timeval),end='')
        print('{address}'.format(address = val2[0]),end='')
        print(':{address}'.format(address = val2[1]),end='')
        print(' ' + request_list[0],end='')
        print(' ' + request_list[1], end='')
        print(' ' + request_list[2].replace('\n', ''), end='')
        print('; HTTP/1.0 400 Bad Request')
        
    elif header_code == 404:
        if address == 'h2':
            address = '10.10.1.100'
        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y", time.localtime())
        print('{now}: '.format(now=timeval),end='')
        print('{address}'.format(address=val2[0]),end='')
        print(':{address}'.format(address = val2[1]),end='')
        print(' ' + request_list[0].replace('\r',''),end='')
        print(' ' + request_list[1], end='')
        print(' ' + request_list[2].replace('\n', ''), end='')
        print('; HTTP/1.0 404 Not Found')
       
    else:
        if address == 'h2':
            address = '10.10.1.100'
        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y", time.localtime())
        print('{now}: '.format(now=timeval),end='')
        print('{address}'.format(address = val2[0]),end='')
        print(':{address}'.format(address = val2[1]),end='')
        print(' ' + request_list[0].replace('\r',''),end='')
        print(' ' + request_list[1], end='')
        print(' ' + request_list[2].replace('\n', ''), end='')
        print('; HTTP/1.0 200 OK')
        
def intro():
    headers= []
    header_code = 0
    write_info = []
    total = 1
    resend = False
    unloop = False
    many_pac = False
    k = 0
    address = sys.argv[1]
    port = int(sys.argv[2])
    wnd_size= int(sys.argv[3])
    wnd = wnd_size
    max_pac = int(sys.argv[4])
    byte = 10
    data_send = ''
    
        #set up the UDP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(('',port))
    server_sock.settimeout(1)

    while True:
        if unloop == True:
            break
        try:
            #receieve the SYN packet from the client and send back a SYN|ACK
            val,val2 = server_sock.recvfrom(2048)
            val = val.decode()
            data = val.split('\n')
            if data[0] == 'DAT|ACK':
                unloop = True
            if data[0]== 'SYN':
                
                var = 'SYN|ACK\nSequence: 0\nLength: 0\nAcknowledgment: 1\nWindow: '+ str(wnd) + '\n\n'
                server_sock.sendto(bytes(var, "utf-8"),val2)
                ackno1 = 1
                seqno1 = 1
                break
        except socket.timeout:
            var = 'SYN|ACK\nSequence: 0\nLength: 0\nAcknowledgment: 1\nWindow: '+ str(wnd) + '\n\n'
            server_sock.sendto(bytes(var, "utf-8"),(address,port))
            

    while True:
        if byte == 0 and total == 0:
            break
        else:
            try:
                if unloop == False:
                    val,val2 = server_sock.recvfrom(2048)
                    val = val.decode()
                unloop = False
                write_info.append(val)
                data = val.split('\n')
                length = data[2].split(' ')
                length = int(length[1])
                seqno = data[1].split(' ')
                seqno = int(seqno[1])
                ackno = data[3].split(' ')
                ackno = int(ackno[1])
                length1 = length
                
                if data[0]== 'DAT|ACK': #if the packet is a DAT packet
                    try:
                        headers.append(data[5])
                        headers.append(data[6])
                        request_list = data[5].split(" ")
                        file = request_list[1]
                        file = file.replace('/', '')
                        ackno1 = ackno + length
                        
                        #get the file and read the contents of it
                        open_file = open(file, 'rb')
                        byte = os.path.getsize(file)
                        contents = open_file.read()
                        request_len = len('HTTP/1.0 200 OK\nConnection: close\n\n')
                        data_send = contents[:max_pac-request_len]
                        start = max_pac-request_len
                        length1 = request_len + len(data_send)
                        byte -= len(data_send)
                        header_code = 200
                        #send the first packet with the reply to the request and some of the data
                        var = 'DAT|ACK\nSequence: '+ str(seqno) +'\nLength: '+ str(length1) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\nHTTP/1.0 200 OK\nConnection: close\n\n' + data_send.decode()
                        create_header(header_code,request_list,address,server_sock,headers,port,val2)
                        server_sock.sendto(bytes(var, "utf-8"),val2)
                    except IOError: #if the file does not exist then send the reply not found and print the correct header
                        header_code = 404
                        ackno1 = ackno + length
                        length1 = len('HTTP/1.0 404 Not Found\nConnection: close\n\n')
                        var = 'DAT|ACK\nSequence: ' + str(seqno1) + '\nLength: ' + str(length1) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\nHTTP/1.0 404 Not Found\nConnection: close\n\n'
                        create_header(header_code,request_list,address,server_sock,headers,port,val2)
                        server_sock.sendto(bytes(var, "utf-8"),val2)
                elif data[0] == 'ACK': #if the packet is an ACK packet
                    if byte <= 0: #if it is the last ACK packet set total = byte
                        total = byte
                        ackno1 = seqno
                        seqno1 = ackno
                    elif header_code == 404: #send the FIN packet if the file was not found
                        byte = 0
                        total = 0
                        ackno1 = seqno
                        seqno1 = ackno
                        header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\n'
                        server_sock.sendto(bytes(header, "utf-8"),val2)
                    else: #send the next DAT packet
                        ackno1 = seqno
                        seqno1 = ackno
                        if byte >= max_pac: #if it is the last packet
                            data_send = contents[start:max_pac+start]
                            start = start + max_pac
                            byte -= max_pac
                            var = 'DAT|ACK\nSequence: '+ str(seqno1) +'\nLength: 1024\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd)+'\n\n' + data_send.decode()
                            server_sock.sendto(bytes(var, "utf-8"),val2)
                        else:
                            data = contents[start:start+byte]
                            length = len(data)
                            byte -= byte

                            var = 'DAT|ACK\nSequence: '+ str(seqno1) +'\nLength: '+str(length) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd)+'\n\n' + data.decode()
                            server_sock.sendto(bytes(var, "utf-8"),val2)
            except socket.timeout:
                if len(write_info) == 0 or len(write_info)== 1: #if no packet is in write_info then resend the SYN packet
                    var = 'SYN|ACK\nSequence: 0\nLength: 0\nAcknowledgment: 1\nWindow: '+ str(wnd) +'\n\n'
                    server_sock.sendto(bytes(var, "utf-8"),(address,port))
                elif len(write_info) == 2: #still the first packet then resend it
                    if header_code == 404:
                        var = 'DAT|ACK\nSequence: ' + str(seqno1) + '\nLength: ' + str(length1) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd)+'\n\nHTTP/1.0 404 Not Found\nConnection: close\n\n'
                        server_sock.sendto(bytes(var, "utf-8"),val2)
                    else:
                        var = 'DAT|ACK\nSequence: '+ str(seqno) +'\nLength: '+ str(length1) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd)+'\n\nHTTP/1.0 200 OK\nConnection: close\n\n' + data_send.decode()
                        server_sock.sendto(bytes(var, "utf-8"),val2)
                else:
                    if header_code == 404:
                        header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\n'
                        server_sock.sendto(bytes(header, "utf-8"),val2)
                    else:
                        resend == True
                        var = 'DAT|ACK\nSequence: '+ str(seqno1) +'\nLength: '+str(length) + '\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\n' + data_send.decode()
                        server_sock.sendto(bytes(var, "utf-8"),val2)
                            
                

    if header_code != 404: #if the file was found then send the FIN packet
        header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\n'
        server_sock.sendto(bytes(header, "utf-8"),val2)
        open_file.close()

    while True:
        try:
            val,val2 = server_sock.recvfrom(2048)
            val = val.decode()
            data = val.split('\n')
            seqno = data[1].split(' ')
            seqno = int(seqno[1])
            length = data[2].split(' ')
            length = int(length[1])
            ackno = data[3].split(' ')
            ackno = int(ackno[1])

            if data[0] == 'FIN|ACK': #if the packet is a FIN then send an ACK 
                seqno1 = ackno
                ackno1 = seqno + 1
                head = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgement: '+ str(ackno1)+'\nWindow: '+ str(wnd) + '\n\n'
                server_sock.sendto(bytes(head, "utf-8"),val2)
                break
        except socket.timeout:
            if data[0] == 'FIN|ACK': #resend the ACK packet
                head = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgement: '+ str(ackno1)+'\nWindow: '+ str(wnd) + '\n\n'
                server_sock.sendto(bytes(head, "utf-8"),val2)
            else: #resend the FIN packet
                header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: '+ str(ackno1) + '\nWindow: '+ str(wnd) + '\n\n'
                server_sock.sendto(bytes(header, "utf-8"),val2)

time_end = time.time() + 60 * 3                
while time.time() < time_end:    #keep the server open for 3 minutes            
    intro()