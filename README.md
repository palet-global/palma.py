
![Logo](img/palma.py.jpg)

# Palma.py

A lightweight REST API server that runs open source models `locally` or in the `cloud`. It uses `Starlette` and Hugging Face `Transformers`, with CUDA and Metal support, as well as concurrent and parallel requests.

## Description

The goal of `Palma.py` is to enable LLM inference with minimal setup via REST API using Python.
- Uses a lightweight `Starlette` implementation with no dependencies
- `Healthchecks` support for load balancer integration
- Uses Hugging Face `Transformers` library for inference
- Queue and Threads support for multiple inference requests
- Support for Apple Metal, CUDA and CPU
- Support for CPU fallback on Apple Metal

**Supported Platforms**
- MacOS
- Linux
- Windows

**Supported Models**
- LLaMA 
- LLaMA 2 
- LLaMA 3

`We need help testing more models`

### Palma.py Architecture

![Palma.py Architecture](img/palma.py_architecture.jpg)

1. **REST API:**
- The starting point where the main thread operates.

2. **Background Task Creation:**
- A background task is created when an endpoint is called and work is sent off the main thread.
- This enables concurrency as the main thread can continue processing other tasks.

3. **Shared Executor and Sub-Thread:**
- In the background task, a shared executor is instantiated.
- The shared executor creates sub-threads.
- Anything above the enviroment variable `THREADS_MAX_WORKERS` limit, will be queue.

4. **Inference in Sub-Thread:**
- The sub-threads perform inference tasks in parallel.
- This enables parallelism as multiple sub-threads run simultaneously.

## Installation

1. Clone and download this repository 

```bash
git clone https://github.com/palet-global/palma.py
cd palma.py
```
    
2. Set up your Python enviroment

```bash
# create virtual enviroment
# python3 if mac
python -m venv venv

# enter virtual enviroment
source venv/bin/activate
```

3. In the top-level directory run

```bash
pip install .
```

4. Adjust your enviroment variables
- Copy .env.example to a new file named .env
```bash
cp .env.example .env
```
- Read and update the .env file with your specific configuration
```bash
nano .env
```

## Hugging Face Setup

To run Palma.py, you need to create (or be logged into) an account on Hugging Face and log in using an access token from your account in your Python environment.

The CLI (already installed with pip) is used for models that require permission like LLama 3.

Get a token from https://huggingface.co/settings/token

Then log into Hugging Face in your Python enviroment
 
```bash
# enter virtual enviroment
source venv/bin/activate

# login to hugging face
huggingface-cli login
```

## Run

On the project directory

```bash
# enter virtual enviroment
source venv/bin/activate
  
# run server
uvicorn server:app --host 127.0.0.1 --port 8000
```
*The model will be downloaded automatically once you run the server in the virtual enviroment

## Usage

### Inference with no streaming

```shell
curl -w '\nTime: %{time_total}\n' -X POST http://127.0.0.1:8000/v0.1.0/inference \
     -H "Content-Type: application/json" \
     -d '{
           "messages": [
             {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
             {"role": "user", "content": "Whats the capital of Puerto Rico?"}
           ],
           "max_new_tokens": 256,
           "do_sample": true,
           "temperature": 0.6,
           "top_p": 0.7
         }'
```

**Response**

```json
{
    "data": "Arrrr, ye landlubber! Ye be askin' about the capital o' Puerto Rico, eh? Well, matey, I be tellin' ye it be San Juan! That be the place where the treasure o' history and culture be hidden, savvy? So hoist the colors and set a course fer San Juan, me hearty!"
}
```

### Inference with streaming

This will stream output tokens as soon they are generated using Server-Sent Events (SSE) format.

```shell
curl -N -w '\nTime: %{time_total}\n' -X POST http://127.0.0.1:8000/v0.1.0/stream \
     -H "Content-Type: application/json" \
     -d '{
           "messages": [
             {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
             {"role": "user", "content": "Whats the capital of Puerto Rico?"}
           ],
           "max_new_tokens": 256,
           "do_sample": true,
           "temperature": 0.6,
           "top_p": 0.7
         }'
```

**Response**

`<|eot_id|>` indicates the end of the streaming

```sse
data: "Arr"

data: "rr"

data: ","

data: " sh"

data: "iver"

data: " me"

data: " tim"

data: "bers"

data: "!"

data: " Ye"

data: " be"

data: " ask"

data: "in"

data: "'"

data: " about"

data: "hearty!<|eot_id|>"
```
*This reponse is just a representation of what it would look like. It is not a complete response.

## Optimizations

- Make the code `Typed Python`

## Contributing

Contributions are always welcome!

See [contributing guidelines](CONTRIBUTING.md) for ways to get started.

