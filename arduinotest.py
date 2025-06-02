import network
import socket
from machine import Pin
import time

# Configure LED on D4 (GPIO2)
led = Pin(2, Pin.OUT)
led_state = False  # Initial state

# Wi-Fi credentials
SSID = 'YOUR_SSID'
PASSWORD = 'YOUR_PASSWORD'

# Connect to Wi-Fi
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

# Wait for connection
while not sta.isconnected():
    time.sleep(1)

print('Connected. IP:', sta.ifconfig()[0])

# HTML response
def webpage(state):
    button_state = "ON" if state else "OFF"
    button_color = "#4CAF50" if state else "#f44336"
    return f"""
    <html>
        <head>
            <title>ESP8266 Toggle</title>
            <style>
                body {{ font-family: Arial; text-align: center; padding: 50px; }}
                button {{
                    background-color: {button_color};
                    border: none;
                    color: white;
                    padding: 20px 40px;
                    font-size: 24px;
                    cursor: pointer;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <h1>ESP8266 LED Control</h1>
            <p>LED is <strong>{button_state}</strong></p>
            <form action="/toggle">
                <button type="submit">Toggle</button>
            </form>
        </body>
    </html>
    """

# Start server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

while True:
    conn, addr = s.accept()
    print('Client connected from', addr)
    request = conn.recv(1024).decode()

    # Check for toggle
    if '/toggle' in request:
        led_state = not led_state
        led.value(led_state)

    response = webpage(led_state)
    conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    conn.send(response)
    conn.close()
