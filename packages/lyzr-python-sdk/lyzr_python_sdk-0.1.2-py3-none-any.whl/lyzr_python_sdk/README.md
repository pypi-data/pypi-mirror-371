# Lyzr Python SDK

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lyzr-python-sdk)
![PyPI](https://img.shields.io/pypi/v/lyzr-python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python client library for interacting with the Lyzr Agent API. This SDK provides a convenient and structured way to access all Lyzr API functionalities, including managing agents, tools, providers, workflows, and handling inference requests.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Core Features](#core-features)
- [API Reference](#api-reference)
  - [Agents](#agents)
  - [Inference](#inference)
  - [Tools](#tools)
  - [Providers](#providers)
  - [Workflows](#workflows)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Installation

Install the package using pip:

```bash
pip install lyzr-python-sdk
```

## Quick Start

```python
from lyzr_python_sdk import LyzrAgentAPI
import os

# Initialize the client
api_key = os.environ.get("LYZR_AGENT_API_KEY")
client = LyzrAgentAPI(api_key=api_key)

# Get all agents
agents = client.agents.get_agents()
print(f"Found {len(agents)} agents")

# Chat with an agent
chat_response = client.inference.chat({
    "user_id": "user@example.com",
    "agent_id": "your-agent-id",
    "message": "Hello! How can you help me?"
})
print(chat_response)
```

## Authentication

The SDK requires a Lyzr API key for authentication. You can obtain your API key from the Lyzr dashboard.

```python
# Method 1: Environment variable (recommended)
import os
api_key = os.environ.get("LYZR_AGENT_API_KEY")
client = LyzrAgentAPI(api_key=api_key)

# Method 2: Direct initialization
client = LyzrAgentAPI(api_key="your-api-key-here")

# Method 3: Custom base URL
client = LyzrAgentAPI(
    api_key="your-api-key",
    base_url="https://your-custom-endpoint.com"
)
```

## Core Features

- **Agent Management**: Create, update, delete, and manage AI agents
- **Chat & Inference**: Real-time and asynchronous chat capabilities
- **Tool Integration**: Connect external APIs and services
- **Provider Management**: Manage AI model providers and credentials
- **Workflow Automation**: Create and execute automated workflows
- **Streaming Support**: Real-time response streaming
- **Async Operations**: Background task processing

## API Reference

### Agents

Manage your AI agents with full CRUD operations.

#### `get_agents()`
Get all agents associated with your API key.

```python
agents = client.agents.get_agents()
```

#### `create_agent(agent_config: dict)`
Create a new agent.

```python
agent_config = {
    "name": "My Assistant",
    "system_prompt": "You are a helpful assistant",
    "environment_id": "env-123"
}
agent = client.agents.create_agent(agent_config)
```

#### `get_agent(agent_id: str)`
Get details of a specific agent.

```python
agent = client.agents.get_agent("agent-123")
```

#### `update_agent(agent_id: str, agent_config: dict)`
Update an existing agent.

```python
update_config = {
    "name": "Updated Assistant",
    "system_prompt": "You are an expert assistant"
}
result = client.agents.update_agent("agent-123", update_config)
```

#### `delete_agent(agent_id: str)`
Delete an agent.

```python
result = client.agents.delete_agent("agent-123")
```

### Inference

Handle AI inference operations including chat, streaming, and async tasks.

#### `chat(chat_request: dict)`
Chat with an agent synchronously.

```python
chat_request = {
    "user_id": "user@example.com",
    "agent_id": "agent-123",
    "message": "Hello, how can you help me?",
    "session_id": "session-456"  # Optional
}
response = client.inference.chat(chat_request)
```

#### `stream_chat(chat_request: dict)`
Stream chat responses in real-time.

```python
chat_request = {
    "user_id": "user@example.com",
    "agent_id": "agent-123",
    "message": "Tell me a story"
}
response = client.inference.stream_chat(chat_request)

# Process streaming response
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

#### `task(chat_request: dict)`
Create an asynchronous chat task.

```python
task = client.inference.task({
    "user_id": "user@example.com",
    "agent_id": "agent-123",
    "message": "Analyze this data"
})
task_id = task["task_id"]
```

#### `task_status(task_id: str)`
Check the status of an asynchronous task.

```python
status = client.inference.task_status("task-123")
if status["status"] == "completed":
    print(f"Result: {status['result']}")
```

### Tools

Manage external tool integrations and API connections.

#### `get_tools()`
Get all available tools.

```python
tools = client.tools.get_tools()
```

#### `create_tool(tool_data: dict)`
Create a new tool from an OpenAPI schema.

```python
tool_data = {
    "tool_set_name": "weather-api",
    "openapi_schema": {...},  # Your OpenAPI schema
    "default_headers": {"Authorization": "Bearer token"}
}
tool = client.tools.create_tool(tool_data)
```

#### `execute_tool(tool_id: str, path: str, method: str, params: dict)`
Execute a tool with specified parameters.

```python
result = client.tools.execute_tool(
    tool_id="tool-123",
    path="/api/weather",
    method="GET",
    params={"city": "New York"}
)
```

### Providers

Manage AI model providers and their credentials.

#### `get_providers(provider_type: str)`
Get providers by type.

```python
llm_providers = client.providers.get_providers("llm")
```

#### `create_provider(provider_body: dict)`
Create a new provider.

```python
provider_body = {
    "vendor_id": "openai",
    "type": "llm",
    "form": {
        "api_key": "your-openai-key"
    }
}
provider = client.providers.create_provider(provider_body)
```

### Workflows

Create and execute automated workflows.

#### `list_workflows()`
List all workflows.

```python
workflows = client.workflow.list_workflows()
```

#### `execute_workflow(flow_id: str, input_data: dict)`
Execute a workflow with input data.

```python
input_data = {
    "data_source": "file.csv",
    "parameters": {"threshold": 0.8}
}
result = client.workflow.execute_workflow("workflow-123", input_data)
```

## Examples

### Complete Agent Workflow

```python
from lyzr_python_sdk import LyzrAgentAPI
import os

# Initialize client
client = LyzrAgentAPI(api_key=os.environ.get("LYZR_AGENT_API_KEY"))

# Create an agent
agent = client.agents.create_agent({
    "name": "Data Analyst",
    "system_prompt": "You are an expert data analyst",
    "environment_id": "env-123"
})

# Chat with the agent
response = client.inference.chat({
    "user_id": "analyst@company.com",
    "agent_id": agent["agent_id"],
    "message": "Analyze the sales trends"
})

print(f"Agent response: {response['response']}")
```

### Async Task Processing

```python
# Create a long-running task
task = client.inference.task({
    "user_id": "user@example.com",
    "agent_id": "agent-123",
    "message": "Generate a comprehensive report"
})

# Check status periodically
import time
while True:
    status = client.inference.task_status(task["task_id"])
    if status["status"] == "completed":
        print(f"Task completed: {status['result']}")
        break
    elif status["status"] == "failed":
        print(f"Task failed: {status['result']}")
        break
    time.sleep(2)
```

## Error Handling

The SDK raises exceptions for API errors. Always wrap API calls in try-catch blocks:

```python
try:
    agents = client.agents.get_agents()
except Exception as e:
    print(f"Error fetching agents: {e}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://docs.lyzr.ai](https://docs.lyzr.ai)
- **GitHub Issues**: [https://github.com/LyzrCore/lyzr-python/issues](https://github.com/LyzrCore/lyzr-python/issues)
- **Email**: support@lyzr.ai