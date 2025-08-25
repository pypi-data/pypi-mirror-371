from scapy.all import ARP, Ether, srp

def arp_scan(target_ip):
    """Perform ARP scan on the target IP range"""
    # Create an ARP request packet
    arp_request = ARP(pdst=target_ip)
    # Create an Ethernet frame to encapsulate the ARP request
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcasting to all devices

    # Combine the Ethernet frame and ARP request packet
    arp_request_packet = ether_frame / arp_request

    # Send the packet and receive the response
    result = srp(arp_request_packet, timeout=3, verbose=False)[0]

    # List to store the discovered devices
    devices_list = []

    # Parse the response and extract IP and MAC addresses
    for sent, received in result:
        devices_list.append({"ip": received.psrc, "mac": received.hwsrc})

    return devices_list

def print_scan_results(devices_list):
    """Print the scan results in a formatted table"""
    print("IP Address\t\tMAC Address")
    print("-----------------------------------------")
    for device in devices_list:
        print(f"{device['ip']}\t\t{device['mac']}") 

def main():
    """Main function for command-line usage"""
    target_ip = input("Enter the target IP range (e.g., 192.168.1.0/24): ")
    print(f"Scanning {target_ip}...")
    devices_list = arp_scan(target_ip)
    print_scan_results(devices_list)

if __name__ == "__main__":
    main()