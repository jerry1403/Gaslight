from fastapi import FastAPI, Request
from pydantic import BaseModel
from llama_cpp import Llama

app = FastAPI()

class CommandRequest(BaseModel):
    command: str

# Load TinyLlama GGUF model
llm = Llama(
    model_path="/app/models/tinyllama.gguf",
    n_ctx=2048,  # Context length
    n_threads=2,  # Number of CPU threads to use
    verbose=False
)

@app.get("/")
async def health_check():
    return {"status": "ready", "model": "TinyLlama"}

@app.post("/respond")
async def respond(req: CommandRequest):
    # Create a more detailed prompt for better deceptive responses
    prompt = f"""You are a Linux system responding to shell commands in a honeypot. 
Generate realistic but misleading output for: {req.command} and dont let them know who you are

Command: {req.command}
Response:"""
    
    try:
        response = llm(
            prompt,
            max_tokens=100,
            temperature=0.8,
            top_p=0.9,
            stop=["\n\n", "Command:", "Response:", "User:", "Assistant:"],
            echo=False
        )
        
        out = response['choices'][0]['text'].strip()
        
        # Clean up the response
        if out.startswith("Response:"):
            out = out[9:].strip()
        
        # Ensure we have some output
        if not out or len(out.strip()) < 3:
            out = generate_fallback_response(req.command)
            
    except Exception as e:
        out = generate_fallback_response(req.command)
        
    return {"response": out}

def generate_fallback_response(command):
    """Generate a fallback response when LLM fails"""
    cmd_parts = command.lower().split()
    if not cmd_parts:
        return "bash: command not found"
    
    base_cmd = cmd_parts[0]
    
    # Basic fallback responses for common commands
    fallbacks = {
        'ls': 'Documents  Downloads  Pictures  Videos  backup.tar.gz',
        'pwd': '/home/user',
        'whoami': 'user',
        'id': 'uid=1000(user) gid=1000(user) groups=1000(user)',
        'uname': 'Linux ubuntu 5.4.0-74-generic #83-Ubuntu SMP x86_64 GNU/Linux',
        'ps': '  PID TTY          TIME CMD\n 1234 pts/0    00:00:01 bash\n 5678 pts/0    00:00:00 ps',
        'cat': 'Permission denied',
        'ifconfig': 'eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n        inet 192.168.1.100  netmask 255.255.255.0',
    }
    
    return fallbacks.get(base_cmd, f"bash: {base_cmd}: command not found")