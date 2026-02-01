# This program was modified by Jenny Nguyen / N01439814
import socket
import argparse
import struct  # Added for sequence number handling

def run_server(port, output_file):
    # 1. Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Bind the socket to the port (0.0.0.0 means all interfaces)
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save each received file as 'received_<ip>_<port>.jpg' based on sender.")
    sock.bind(server_address)

    # 3. Keep listening for new transfers
    try:
        while True:
            f = None
            sender_filename = None
            
            # Variables for sequencing and buffering out-of-order packets
            expected_seq = 0
            buffer = {}
            
            while True:
                data, addr = sock.recvfrom(65535)
                # Protocol: If we receive an empty packet, it means "End of File"
                if not data:
                    print(f"[*] End of file signal received from {addr}. Closing.")
                    break
                    
                # Ignore packets that are too small to contain a header
                if len(data) < 4:
                    continue
                    
                # Extract sequence number (first 4 bytes) and actual data
                seq_num = struct.unpack('!I', data[:4])[0]
                chunk = data[4:]

                # ACK: Send acknowledgment back to client
                ack_packet = struct.pack('!I', seq_num)
                sock.sendto(ack_packet, addr)
                
                if f is None:
                    print("==== Start of reception ====")
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] First packet received from {addr}. File opened for writing as '{sender_filename}'.")
                
                # Reordering logic
                if seq_num == expected_seq:
                    # This is the next expected packet - write it
                    f.write(chunk)
                    expected_seq += 1
                    
                    # Check if any buffered packets are now in order
                    while expected_seq in buffer:
                        f.write(buffer.pop(expected_seq))
                        expected_seq += 1
                        
                elif seq_num > expected_seq:
                    # Packet arrived too early - store in buffer
                    buffer[seq_num] = chunk
                else:
                    # Duplicate or old packet - ignore
                    pass
                    
                # print(f"Server received {len(data)} bytes from {addr}") # Optional: noisy
            if f:
                f.close()
            print("==== End of reception ====")
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    try:
        run_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")