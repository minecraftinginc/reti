import asyncio
import json
import websockets
import datetime

film_connections = {}

async def send_message(websocket, cod_film, username, message):
    payload = {'action': 'message', 'cod_film': cod_film, 'username': username, 'message': message}
    await websocket.send(json.dumps(payload))

async def save_to_file(cod_film, username, message):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    filename = f'chat_log{cod_film}.txt'
    with open(filename, 'a') as file:
        file.write(f'{username} {timestamp} {message}\n')

async def handle_connection(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            username = data.get('username', 'UnknownUser')
            cod_film = data.get('cod_film', None)

            if data['action'] == 'join':
                if cod_film not in film_connections:
                    film_connections[cod_film] = set()

                film_connections[cod_film].add(websocket)

            elif data['action'] == 'message':
                message = data['message']
                await save_to_file(cod_film, username, message)
                await asyncio.gather(
                    *[send_message(ws, cod_film, username, message) for ws in film_connections.get(cod_film, set())]
                )

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed: {websocket.remote_address}")
    finally:
        for cod_film, connections in film_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del film_connections[cod_film]

start_server = websockets.serve(handle_connection, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
