# Gaslighted - LLM-Powered SSH Honeypot

A deceptive SSH honeypot that uses a local TinyLlama model to generate realistic but misleading responses to attacker commands.

## Architecture

- **SSH Honeypot** (`flamepot/`): Accepts SSH connections and captures attacker commands
- **LLM Service** (`llm/`): TinyLlama model that generates deceptive responses
- **Logging**: All interactions are logged for analysis

## Quick Start

1. **Place your GGUF model**: Put your TinyLlama GGUF file in the `llm/` directory
2. **Update model path**: Edit `llm/Dockerfile` to match your GGUF filename
3. **Deploy**: Run `docker compose up -d`

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

### Generated
- `logs/` - Runtime logs and captured interactions

## Usage

The honeypot runs on port 2222. Attackers can connect using common credentials:
- `root:root`, `admin:admin`, `ubuntu:ubuntu`, etc.

All commands are sent to the LLM for processing, creating realistic but deceptive responses.

## Monitoring

View real-time activity:
```bash
# All logs
docker compose logs -f

# Command logs only  
docker compose logs -f cowrie

# LLM responses
docker compose logs -f llm
```

## Security Note

This is for authorized security research and testing only. Ensure proper network isolation and legal compliance.