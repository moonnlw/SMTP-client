import socket
import ssl
import base64
import sys

host_addr = 'smtp.yandex.ru'
port = 465
user_name = sys.argv[1]
password = sys.argv[2]


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data


def read_config():
    all_content = []
    with open("cfg.txt", 'r') as f:
        for line in f:
            content = line.split()
            all_content.append(content)
    return all_content


def make_content():
    all_content = read_config()
    msg = ""
    for content in all_content:
        disposition = content[0]
        filename = content[2]
        exstension = filename.split(".")[1]

        file_type = f"{content[1]}/{exstension}"
        if content[1] == "document":
            file_type = f"text/plain"

        msg += f"--{boundary}\n"
        msg += f'Content-Disposition: {disposition}; filename="{filename}"\n'
        msg += 'Content-Transfer-Encoding: base64\n'
        msg += f'Content-Type: {file_type}; name="{filename}"\n\n'

        with open(filename, "rb") as f:
            content = f.read()

        base64content = base64.b64encode(content).decode()

        msg += base64content + "\n\n"
        msg += f"--{boundary}\n"
    print(msg)
    return msg


with open("headers.txt") as f:
    f.readline()
    reciever = f.readline().split(" ")[1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    client = ssl.wrap_socket(client)
    print(client.recv(1024))  # smtp сервер отсылает сообщение клиенту первый
    print(request(client, f'ehlo {user_name}'))
    base64login = base64.b64encode(user_name.encode()).decode()
    base64password = base64.b64encode(password.encode()).decode()

    print(request(client, 'AUTH LOGIN'))
    print(request(client, base64login))
    print(request(client, base64password))

    print(request(client, f'MAIL FROM:<{user_name}@yandex.ru>'))
    print(request(client, f'RCPT TO:{reciever}'))
    print(request(client, 'DATA'))
    boundary = "random_boundary"

    with open("headers.txt") as f:
        s = f.read() + "\n" + f'Content-Type: multipart/mixed; boundary={boundary}\n\n'

    with open('msg.txt', 'r') as file:
        msg = s + f"--{boundary}\n"
        msg += "Content-Type: text/plain\n\n"
        msg += file.read() + '\n'
        msg += make_content()
        msg += "."

    print(request(client, msg))
    print(msg)
