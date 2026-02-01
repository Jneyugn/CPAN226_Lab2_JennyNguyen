# This program was modified by Jenny Nguyen / N01439814
import socket
import argparse
import time
import os
import struct

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            seq_num = 0
            while True:
                chunk = f.read(4092)
                if not chunk:
                    break

                header = struct.pack('!I', seq_num)
                packet = header + chunk

                ack_received = False
                while not ack_received:
                    sock.sendto(packet, server_address)
                    try:
                        ack_data, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack('!I', ack_data)[0]
                        if ack_seq == seq_num:
                            ack_received = True
                        else:
                            continue
                    except socket.timeout:
                        print(f"[!] Timeout for seq {seq_num}, retransmitting...")
                        continue
                
                seq_num += 1
                time.sleep(0.001)

        sock.sendto(b'', server_address)
        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)