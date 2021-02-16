#The client for a simple web server using a reliable datagram protocol
#uses sockets and UDP packets
import socket
import sys
import os
import time 

def intro():
    
        address = sys.argv[1]
        port = int(sys.argv[2])
        wnd_val = int(sys.argv[3])
        max_pac = int(sys.argv[4])
        wnd = wnd_val
        
        #get byte of file
        try:
            byte = os.path.getsize(sys.argv[5])
        except IOError:
            byte = 10
            
        files = [] 
        write_info = []
        read_data = []
        no_file = False
        i = 0
        twice = 1
        wnd = int(sys.argv[3])

        #set up the UDP socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #client_sock.bind(('',port))
        client_sock.settimeout(1)

        #send the initial SYN packet to the server to start the connection management
        var = sys.argv[5]
        if i == 0:
            send = 'SYN\nSequence: 0\nLength: 0\nAcknowledgment: -1\nWindow: '+ str(wnd) + '\n\n'
            client_sock.sendto(bytes(send, "utf-8"),(address, port))
            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
            print(timeval, "Send; SYN|ACK; Sequence: 0; Length: 0; Acknowledgement: -1; Window:",str(wnd))

        #until the client has sent the recieved ack pack if the pack reveived is the SYN pack 
        #send that it has been recieved and send the ack if packet gets lost timeout and send again
        while True:
            try:
                val,val2 = client_sock.recvfrom(2048)
                val = val.decode()
                data = val.split('\n')
                wnd1 = data[4].split(' ')
                wnd1 = int(wnd1[1])
                if data[0] == 'SYN|ACK':
                    timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                    print(timeval, "Receive; SYN|ACK; Sequence: 0; Length: 0; Acknowledgment: 1; Window:",wnd1)
                    break
            except socket.timeout:
                client_sock.sendto(bytes('SYN\nSequence: 0\nLength: 0\nAcknowledgment: -1\nWindow: 4096\n\n', "utf-8"),(address, port))
                timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                print(timeval, "Send; SYN|ACK; Sequence: 0; Length: 0; Acknowledgement: -1; Window:",wnd)
        
        #send the first dat packet to the server
        length = len('GET /' + var +' HTTP/1.0\nConnection:close')
        send = 'DAT|ACK\nSequence: 1\nLength: '+ str(length) + '\nAcknowledgment: 1\nWindow: '+ str(wnd) + '\n\rGET /' + var +' HTTP/1.0\nConnection:close\r\n'
        client_sock.sendto(bytes(send, "utf-8"),(address, port))
        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
        print(timeval, "Send; DAT|ACK; Sequence: 1; Length:",length,"; Acknowledgement: 1; Window:",wnd)
                
        while True:
            if byte <= -50: #if no more data to write then end the loop
                break
            else:
                try:
                    i = 0
                    val,val2 = client_sock.recvfrom(2048) #receive and split the data 
                    val = val.decode()
                    data = val.split('\n')
                    while val[i] + val[i+1] != '\n\n':
                        i += 1
                    info = val[0:i]
                    data_write = val[i+2:]
                    write_info.append(data_write)
                    data = val.split('\n')
                    if data[0] == 'FIN|ACK':
                        byte = -50
                        continue
                    payload = val.split('\n\n')
                    request = payload[1].split('\n')
                    seqno = data[1].split(' ')
                    seqno = int(seqno[1])
                    length = data[2].split(' ')
                    length = int(length[1])
                    ackno = data[3].split(' ')
                    ackno = int(ackno[1])
                    wnd1 = data[4].split(' ')
                    wnd1 = int(wnd1[1])
                    wnd = wnd_val
                    #if it is the first dat packet from the server
                    if data[0] == 'DAT|ACK' and payload[1] == 'HTTP/1.0 200 OK\nConnection: close':
                        i += 1
                        while val[i] + val[i+1] != '\n\n': #split the data again
                            i += 1
                        info = val[0:i]
                        data_write = val[i+2:]
                        read_data.append(data_write)

                        if len(read_data) >= 2 and data_write == read_data[len(read_data)-1]:
                            #send an ack if we have already received the data
                            wnd -= length
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                        else:
                            #write the data to the file and send an ack
                            pvar = 'Receive; DAT|ACK; Sequence: ' + str(seqno) + '; Length: ' + str(length) +  '; Acknowledgment: ' + str(ackno) +'; Window: ' + str(wnd1)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, pvar)
                            size = len(data_write)
                            byte -= size
                            outfile = open(sys.argv[6], 'a+')
                            outfile.write(data_write)
                            ackno1 = seqno + length
                            seqno1 = ackno
                            wnd -= length
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                    elif data[0] == 'DAT|ACK' and payload[1] == 'HTTP/1.0 404 Not Found\nConnection: close':
                        #if the file can not be found then send an ack and set byte = 0
                        no_file = True
                        length = len('HTTP/1.0 404 Not Found\nConnection: close')
                        pvar = 'Receive; DAT|ACK; Sequence: ' + str(seqno) + '; Length: ' + str(length) +  '; Acknowledgment: ' + str(ackno) +'; Window: ' + str(wnd1)
                        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                        print(timeval, pvar)
                        ackno1 = seqno + length
                        seqno1 = ackno
                        byte = 0
                        wnd -= length
                        var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                        client_sock.sendto(bytes(var, "utf-8"),(address, port))
                        var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                        print(timeval, var)
                    
                    else:
                        #the packet received was a dat that did not have a request
                        payload = val.split('\n\n')
                        request = payload[1].split('\n')
                        seqno = data[1].split(' ')
                        seqno = int(seqno[1])
                        length = data[2].split(' ')
                        length = int(length[1])
                        ackno = data[3].split(' ')
                        ackno = int(ackno[1])
                        wnd = wnd_val
                        
                        #if the data has already been read then send an ack else read it to the file
                        if len(read_data) >= 1 and data_write == read_data[len(read_data)-1]:
                            wnd -= max_pac
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                        else:    
                            pvar = 'Receive; DAT|ACK; Sequence: ' + str(seqno) + '; Length: ' + str(length) +  '; Acknowledgment: ' + str(ackno) +'; Window: ' + str(wnd1)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, pvar)
                            wnd -= length
                            size = len(data_write)
                            byte -= size
                            outfile = open(sys.argv[6], 'a+')
                            outfile.write(data_write)
                            read_data.append(data_write)
                            ackno1 = seqno + length
                            seqno1 = ackno
                            
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                            wnd += length
                except socket.timeout:
                    #if it is the first packet then resend the request to the server
                    if len(write_info) == 0:
                        send = 'DAT|ACK\nSequence: 1\nLength: '+ str(length) + '\nAcknowledgment: 1\nWindow: 4096\n\rGET /' + var +' HTTP/1.0\nConnection:close\r\n'
                        client_sock.sendto(bytes(send, "utf-8"),(address, port))
                        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                        print(timeval, "Send; DAT|ACK; Sequence: 1; Length:",length,"; Acknowledgement: 1; Window: 4096")
                    elif len(write_info) == 1: #if it is the second packet then resend the ack 
                        if payload[1] == 'HTTP/1.0 200 OK\nConnection: close':
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                        elif payload[1] == 'HTTP/1.0 404 Not Found\nConnection: close':
                            length = len('HTTP/1.0 404 Not Found\nConnection: close')
                            var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                            client_sock.sendto(bytes(var, "utf-8"),(address, port))
                            var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                            timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                            print(timeval, var)
                    else:
                        #resend the ack for the last data packet receieved
                        var = 'ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgment: ' + str(ackno1) + '\nWindow: ' + str(wnd) + '\n\n'
                        client_sock.sendto(bytes(var, "utf-8"),(address, port))
                        var = 'Send; ACK; Sequence: ' + str(seqno1) + '; Length: 0; Acknowledgment: ' + str(ackno1) + '; Window: ' + str(wnd)
                        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                        print(timeval, var)
                            
   #     if no_file == False:
         #   outfile.close()
        close = 0
            
        while True:
            try:
                #
                wnd = sys.argv[3]
                val,val2 = client_sock.recvfrom(2048)
                val = val.decode()
                data = val.split('\n')
                seqno = data[1].split(' ')
                seqno = int(seqno[1])
                length = data[2].split(' ')
                length = int(length[1])
                ackno = data[3].split(' ')
                ackno = int(ackno[1])
                wnd1 = data[4].split(' ')
                wnd1 = int(wnd1[1])

                if data[0] == 'FIN|ACK':
                    close += 1
                    if close < 2:
                        seqno1 = ackno
                        ackno1 = seqno + 1
                        timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                        print(timeval, "Receive; FIN|ACK; Sequence: {}; Length: 0; Acknowledgment: {}; Window: {}".format(seqno,ackno,wnd1))
                    header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgement: '+ str(ackno1)+'\nWindow: 4096\n\n'
                    client_sock.sendto(bytes(header, "utf-8"),(address, port))
                    timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                    print(timeval, "Send; FIN|ACK; Sequence: {}; Length: 0; Acknowledgement: {}; Window: {}".format(seqno1, ackno1,wnd_val))
                if data[0] == 'ACK':
                    timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                    print(timeval, "Receive; ACK; Sequence: {}; Length: 0; Acknowledgement: {}; Window: {}".format(seqno, ackno,wnd1))
                    break
            except socket.timeout:
                if close == 0:
                    timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                    print(timeval, "Receive; FIN|ACK; Sequence: {}; Length: 0; Acknowledgment: {}; Window: {}".format(seqno,ackno,wnd1))
                    close += 1
                header = 'FIN|ACK\nSequence: ' + str(seqno1) + '\nLength: 0\nAcknowledgement: '+ str(ackno1)+'\nWindow: '+ str(wnd) + '\n\n'
                client_sock.sendto(bytes(header, "utf-8"),(address, port))
                timeval = time.strftime("%a %b %d %H:%M:%S PDT %Y:", time.localtime())
                print(timeval, "Send; FIN|ACK; Sequence: {}; Length: 0; Acknowledgement: {}; Window: {}".format(seqno1, ackno1,wnd_val))
intro()