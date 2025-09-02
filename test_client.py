#!/usr/bin/env python3

import socket
import struct
import time

def create_bind_transceiver_pdu(system_id="smppclient1", password="password"):
    """Create a BIND_TRANSCEIVER PDU"""
    command_id = 0x00000009  # BIND_TRANSCEIVER
    command_status = 0x00000000
    sequence_number = 1
    
    # Body: system_id + password + system_type + interface_version + addr_ton + addr_npi + address_range
    body = system_id.encode('ascii') + b'\x00'  # system_id (null-terminated)
    body += password.encode('ascii') + b'\x00'  # password (null-terminated)
    body += b'\x00'  # system_type (null-terminated)
    body += struct.pack('!B', 0x34)  # interface_version (3.4)
    body += struct.pack('!B', 0x00)  # addr_ton
    body += struct.pack('!B', 0x00)  # addr_npi
    body += b'\x00'  # address_range (null-terminated)
    
    command_length = 16 + len(body)  # Header (16 bytes) + body
    
    # Create PDU header
    header = struct.pack('!IIII', command_length, command_id, command_status, sequence_number)
    
    return header + body

def create_unbind_pdu():
    """Create an UNBIND PDU"""
    command_id = 0x00000006  # UNBIND
    command_status = 0x00000000
    sequence_number = 2
    command_length = 16  # Header only
    
    return struct.pack('!IIII', command_length, command_id, command_status, sequence_number)

def parse_pdu_header(data):
    """Parse PDU header"""
    if len(data) < 16:
        return None
    
    command_length, command_id, command_status, sequence_number = struct.unpack('!IIII', data[:16])
    return {
        'command_length': command_length,
        'command_id': command_id,
        'command_status': command_status,
        'sequence_number': sequence_number
    }

def test_smpp_connection():
    """Test SMPP connection to the simulator"""
    try:
        # Connect to SMPP simulator
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print("Connecting to SMPP simulator on localhost:2779...")
        sock.connect(('localhost', 2779))
        print("Connected successfully!")
        
        # Send BIND_TRANSCEIVER
        bind_pdu = create_bind_transceiver_pdu("smppclient1", "password")
        print(f"Sending BIND_TRANSCEIVER PDU ({len(bind_pdu)} bytes)...")
        sock.send(bind_pdu)
        
        # Receive BIND_TRANSCEIVER_RESP
        response = sock.recv(1024)
        header = parse_pdu_header(response)
        if header:
            print(f"Received response: command_id=0x{header['command_id']:08x}, status=0x{header['command_status']:08x}")
            if header['command_id'] == 0x80000009:  # BIND_TRANSCEIVER_RESP
                if header['command_status'] == 0:
                    print("BIND successful!")
                else:
                    print(f"BIND failed with status: 0x{header['command_status']:08x}")
            else:
                print(f"Unexpected response command_id: 0x{header['command_id']:08x}")
        
        # Wait a moment
        time.sleep(1)
        
        # Send UNBIND
        unbind_pdu = create_unbind_pdu()
        print(f"Sending UNBIND PDU ({len(unbind_pdu)} bytes)...")
        sock.send(unbind_pdu)
        
        # Receive UNBIND_RESP
        response = sock.recv(1024)
        header = parse_pdu_header(response)
        if header:
            print(f"Received response: command_id=0x{header['command_id']:08x}, status=0x{header['command_status']:08x}")
            if header['command_id'] == 0x80000006:  # UNBIND_RESP
                print("UNBIND successful!")
        
        sock.close()
        print("Connection closed.")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing SMPP Simulator Connection...")
    success = test_smpp_connection()
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")