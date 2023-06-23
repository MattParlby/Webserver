import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine

# Configuration
SSID = 'wifi_name'
PASSWORD = 'wifi_password'
PORT = 80


def connect_to_wifi(ssid, password):
    """Connect to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        print('Waiting for connection...')
        sleep(1)
    
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def create_socket(ip, port):
    """Create a socket and bind it to the specified IP address and port."""
    address = (ip, port)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection


def generate_webpage(temperature, state):
    """Generate the HTML webpage with temperature and LED state information."""
    html = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <font size="15">
        <form action="./lighton">
        <input type="submit" value="Light on" style="height:90px; width:200px" />
        </form>
        <form action="./lightoff">
        <input type="submit" value="Light off" style="height:90px; width:200px" />
        </form>
        <p>LED is {state}</p>
        <p>Temperature is {temperature}</p>
        </font> 
        </body>
        </html>
        """
    return str(html)


def serve_requests(connection):
    """Serve incoming HTTP requests and control the LED based on the request."""
    state = 'OFF'
    pico_led.off()
    temperature = 0
    
    while True:
        client, addr = connection.accept()
        request = client.recv(1024).decode('utf-8')
        request_path = request.split()[1]
        
        if request_path == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request_path == '/lightoff?':
            pico_led.off()
            state = 'OFF'
        
        temperature = pico_temp_sensor.temp
        html = generate_webpage(temperature, state)
        client.send(html.encode('utf-8'))
        client.close()


def main():
    try:
        ip = connect_to_wifi(SSID, PASSWORD)
        connection = create_socket(ip, PORT)
        serve_requests(connection)
    except KeyboardInterrupt:
        machine.reset()


if __name__ == '__main__':
    main()
