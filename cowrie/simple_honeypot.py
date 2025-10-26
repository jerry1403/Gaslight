#!/usr/bin/env python3
"""
SSH Honeypot with LLM Integration
"""
import asyncio
import asyncssh
import logging
import json
import inspect
import requests
import os

LLM_API = os.environ.get('LLM_API', 'http://llm:8000/respond')

#######################Logging################################

#BasicLog
logging.basicConfig(filename='/cowrie/var/log/honeypot.log', level=logging.INFO)

class SessionLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs

#JsonFullLog
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelno,
            'ip': getattr(record, 'ip', None),
            'port': getattr(record, 'port', None),
            'username': getattr(record, 'username', None),
            'password': getattr(record, 'password', None),
            'command': getattr(record, 'command', None),
            'message': record.getMessage(),
        }
        return json.dumps(log_record)

logger = logging.getLogger()
json_file_handler = logging.FileHandler('/cowrie/var/log/flamepot.json')
json_file_handler.setFormatter(JsonFormatter())
logger.addHandler(json_file_handler)
logger = logging.getLogger()

#CommandLog
def log_command(ip, command):
    command_logger.info(f'{ip} | {command}')

command_logger = logging.getLogger('cmd_logger')
command_logger.setLevel(logging.INFO)
handler = logging.FileHandler('/cowrie/var/log/command.logs')
formatter = logging.Formatter('%(asctime)s  %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
handler.setFormatter(formatter)
command_logger.addHandler(handler)

#MetadataLog
def log_session_metadata(conn, username, password, process=None):
    ip, port = conn.get_extra_info('peername')[:2]
    client_version = conn.get_extra_info('version')
    subsystem = getattr(process, 'subsystem', None) if process else None
    command = getattr(process, 'command', None) if process else None

    session_logger = SessionLoggerAdapter(
        logger,
        {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password,
            "client_version": client_version,
            "subsystem": subsystem,
            "command": command,
        }
    )
    session_logger.info("Session metadata logged")

###########################LLM Integration###########################
async def get_llm_response(command):
    """Get response from LLM API"""
    try:
        response = requests.post(
            LLM_API,
            json={"command": command},
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            llm_response = data.get("response", "").strip()
            if llm_response:
                return llm_response
        
        return f"bash: {command}: command not found"
        
    except requests.exceptions.Timeout:
        return f"bash: {command}: command not found"
    except requests.exceptions.ConnectionError:
        return f"bash: {command}: command not found"
    except Exception as e:
        return f"bash: {command}: command not found"

###########################Server###########################
class HoneypotSSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self.conn = conn  # Store connection reference
        peername, port = conn.get_extra_info('peername')
        self.logger = SessionLoggerAdapter(
            logger,
            {
                "ip": peername,
                "port": port,
                "username": None,
                "password": None,
                "client_version": conn.get_extra_info('version'),
                "subsystem": None,
                "command": None,
            }
        )
        conn.session_logger = self.logger
        self.logger.info(f'Connection from {peername}')

    def connection_lost(self, exc):
        self.logger.info(f'Connection lost from {self.logger.extra.get("ip")}')

    def begin_auth(self, username):
        return True  # allow all users

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        self.logger.extra['username'] = username
        self.logger.extra['password'] = password
        self.logger.info(f'Login attempt: {username}/{password}')

        # Accept common honeypot credentials immediately
        valid_creds = [
            ('root', 'root'), ('root', '123456'), ('root', 'password'),
            ('admin', 'admin'), ('admin', 'password'), ('admin', '123456'),
            ('ubuntu', 'ubuntu'), ('user', 'user'), ('pi', 'raspberry'),
            ('guest', 'guest'), ('test', 'test')
        ]
        
        if (username, password) in valid_creds:
            return True
        
        # Accept ANY credentials after a short delay to seem realistic
        # This makes the honeypot more attractive to attackers
        return True

async def handle_connection(proc):
    logger = getattr(proc._conn, "session_logger", None)
    username = proc.get_extra_info('username')
    ip = proc._conn.get_extra_info('peername')[0]
    if logger:
        logger.extra['username'] = username
    
    # Send welcome message
    proc.stdout.write(f'Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.4.0-74-generic x86_64)\n\n')
    proc.stdout.write(' * Documentation:  https://help.ubuntu.com\n')
    proc.stdout.write(' * Management:     https://landscape.canonical.com\n')
    proc.stdout.write(' * Support:        https://ubuntu.com/advantage\n\n')
    proc.stdout.write(f'Last login: Sat Oct 26 10:30:15 2024 from {ip}\n')
    await proc.stdout.drain()

    while not proc.stdin.at_eof():
        proc.stdout.write(f"{username}@ubuntu-server:~$ ")
        await proc.stdout.drain()
        cmd = await proc.stdin.readline()
        if not cmd:
            break
        command = cmd.strip()
        
        if not command:
            continue
            
        log_command(ip, command)
        if logger:
            logger.extra['command'] = command
            logger.info(f'Command from {username}: {command}')
            logger.extra['command'] = None

        # Handle special commands
        if command in ["exit", "logout", "quit"]:
            proc.stdout.write("logout\n")
            await proc.stdout.drain()
            break
        elif command == "clear":
            proc.stdout.write("\033[2J\033[H")
            await proc.stdout.drain()
            continue
        
        # Get LLM response
        try:
            llm_response = await get_llm_response(command)
            proc.stdout.write(f"{llm_response}\n")
            await proc.stdout.drain()
        except Exception as e:
            proc.stdout.write(f"bash: {command}: command not found\n")
            await proc.stdout.drain()

    proc.exit(0)

async def start_pot():
    # Wait for LLM service
    print("Waiting for LLM service...")
    while True:
        try:
            response = requests.get("http://llm:8000/", timeout=5)
            if response.status_code == 200:
                print("LLM service is ready!")
                break
        except:
            pass
        await asyncio.sleep(2)
    
    print("Starting SSH honeypot server on port 2222")
    await asyncssh.create_server(
        HoneypotSSHServer,
        '', 2222,
        server_host_keys=['ssh_host_key'],
        process_factory=handle_connection
    )
    print("SSH honeypot server started successfully")

try:
    asyncio.get_event_loop().run_until_complete(start_pot())
    asyncio.get_event_loop().run_forever()
except (OSError, asyncssh.Error) as exc:
    print(f'Error starting server: {exc}')
    logging.exception(f"Exception in connection handler: {exc}")