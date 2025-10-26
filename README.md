# Gaslighted - LLM-Powered SSH Honeypot

A deceptive SSH honeypot that uses a local TinyLlama model to generate realistic but misleading responses to attacker commands.

## Architecture

- **SSH Honeypot** (`flamepot/`): Accepts SSH connections and captures attacker commands
- **LLM Service** (`llm/`): TinyLlama model that generates deceptive responses
- **Logging**: All interactions are logged for analysis

## Installation

1. **Download tinyllama** - https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/blob/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
2. **Place your GGUF model**: Put your TinyLlama GGUF file in the `llm/` directory
3. **Update model path**: Edit `llm/Dockerfile` to match your GGUF filename
4. **Deploy**: Run `docker compose up -d`

## Files

### Core Components
- `docker-compose.yml` - Service orchestration
- `cowrie/simple_honeypot.py` - Main SSH honeypot implementation
- `cowrie/entrypoint.sh` - Honeypot startup script
- `cowrie/Dockerfile` - Honeypot container build
- `llm/main.py` - LLM API service
- `llm/requirements.txt` - LLM service dependencies  
- `llm/Dockerfile` - LLM container build
- `llm/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` - Local LLM model

### Logs
- `logs/` - Runtime logs and captured interactions
- `flamepot.json/` - Records logs in JSON format to be ingested into SIEM for visualization
## Usage

The honeypot runs on port 2222 (Can be configured to 22 for irl scenario). Attackers can connect using common credentials:
- `root:root`, `admin:admin`, `ubuntu:ubuntu`, etc.

All commands are sent to the LLM for processing, creating realistic but deceptive responses.

## Monitoring

View real-time activity:
```bash
# All logs
docker compose logs -f

# Command logs only  
docker compose logs -f flamepot

# LLM responses
docker compose logs -f llm
```


