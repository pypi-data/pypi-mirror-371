# WebSocketTool Plugin for FastPluggy

The WebSocketTool plugin provides real-time WebSocket communication capabilities for FastPluggy applications. It enables bidirectional communication between the server and clients, supports message broadcasting, targeted messaging, and integrates with the task worker system for real-time task monitoring.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [API Reference](#api-reference)
- [Integration with Other Modules](#integration-with-other-modules)
    - [Tasks Worker Integration](#tasks-worker-integration)
- [WebSocket Integration](#websocket-integration)
    - [Connecting to WebSocket](#connecting-to-websocket)
    - [Registering Backend Message Handlers](#registering-backend-message-handlers)
    - [Registering Event Hooks](#registering-event-hooks)
    - [Frontend Integration](#frontend-integration)
    - [Naming Convention for Message Types](#naming-convention-for-message-types)
    - [Using AsyncWidget [WIP]](#using-asyncwidget-wip)
- [Advanced Usage and Troubleshooting](#advanced-usage-and-troubleshooting)
- [License](#license)

## Installation

### Requirements

- FastPluggy framework >=0.0.3
- UI Tools plugin >=0.0.3

### Quick Start & Installation 

```bash
pip install fastpluggy-websocket-tool
```

## Configuration

The WebSocketTool plugin can be configured through the `WebSocketSettings` class:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `max_queue_size` | int | 10000 | Maximum size of the message queue |
| `enable_heartbeat` | bool | True | Enable heartbeat mechanism to monitor connection health |
| `heartbeat_interval` | int | 30 | Seconds between heartbeat pings |
| `heartbeat_timeout` | int | 60 | Seconds before a connection is considered timed out |


## Core Components

For detailed information about the core components of the WebSocketTool plugin, including the ConnectionManager, WebSocketMessage, and AsyncWidget classes, see the [Core Components Documentation](docs/core_components.md).

## API Reference

For detailed information about the WebSocket API endpoints and interfaces, see the [API Reference Documentation](docs/api_reference.md).

## Integration with Other Modules

### Tasks Worker Integration

The WebSocketTool plugin integrates with the Tasks Worker module to provide real-time monitoring of task execution, streaming of task logs, and task completion notifications.

For detailed information about the Tasks Worker integration, see the [Tasks Worker Integration Documentation](docs/tasks_worker_integration.md).

## WebSocket Integration

The WebSocketTool plugin provides a powerful handler registry system that allows you to easily register handlers for both frontend and backend WebSocket messages. This simplifies the integration of WebSocket functionality into your application.

For detailed information about the handler registry system, see the [Handler Registry Documentation](docs/websocket_handlers.md).


### Registering Backend Message Handlers

Backend message handlers process messages received from clients. Here's how to register them:

```python
from fastpluggy.fastpluggy import FastPluggy
from typing import Dict, Any

# Define a handler function for a specific message type
async def handle_chat_message(client_id: str, data: Dict[str, Any]):
    """Handler for chat messages from clients"""
    print(f"Received chat from {client_id}: {data.get('content')}")

    # You can access the WebSocket manager to send responses
    manager = FastPluggy.get_global("ws_manager")

    # Process the message and potentially send a response
    # ...

# Get the WebSocket manager
ws_manager = FastPluggy.get_global("ws_manager")

# Register the handler for the "chat.message" message type
ws_manager.register_handler("chat.message", handle_chat_message)
```

### Registering Event Hooks

You can register hooks for WebSocket events:

```python
from fastpluggy.fastpluggy import FastPluggy
from fastpluggy_plugin.websocket_tool.schema.ws_message import WebSocketMessage

# Define hook functions
async def on_client_connected(client_id: str):
    """Called when a client connects"""
    print(f"Client connected: {client_id}")

    # Send a welcome message
    manager = FastPluggy.get_global("ws_manager")
    welcome_msg = WebSocketMessage(
        type="system.welcome",
        content=f"Welcome {client_id}!",
        meta={"event": "connected"}
    )
    await manager.send_to_client(welcome_msg, client_id)

# Get the WebSocket manager
ws_manager = FastPluggy.get_global("ws_manager")

# Register the hook
ws_manager.add_hook("client_connected", on_client_connected)
```


### Frontend Integration

To handle WebSocket messages in the frontend, include the websocket-client.js file in your HTML:

```html
<script src="/static/websocket-client.js"></script>
```

This file provides:
- `WebSocketRegistry`: A registry for WebSocket message handlers
- `safeRegisterHandler`: A function to safely register handlers even if the registry isn't loaded yet

Here's how to use these features:

```javascript

// Register handlers for specific message types using safeRegisterHandler
// This works even if WebSocketRegistry isn't loaded yet
safeRegisterHandler("chat.message", (data) => {
    displayChatMessage(data.content, data.meta);
});

// Send a message to the backend
function sendChatMessage(message) {
    socket.send(JSON.stringify({
        type: "chat.message",  // This will be handled by the registered "chat.message" handler
        content: message,
        meta: {
            timestamp: Date.now(),
            user: "current_user"
        }
    }));
}

// Example usage
document.getElementById('send-button').addEventListener('click', () => {
    const messageInput = document.getElementById('message-input');
    sendChatMessage(messageInput.value);
    messageInput.value = '';
});
```

The `safeRegisterHandler` function ensures that your handlers are registered even if the WebSocketRegistry is loaded after your code runs. It's the recommended way to register handlers in the frontend.

### Naming Convention for Message Types

To avoid conflicts between different plugins, it's recommended to use a namespaced approach for message types:

```
<plugin_name>.<action_or_event>
```

For example:
- `chat.message` - For chat messages
- `user.login` - For user login events
- `data.request` - For data requests

This ensures that handlers from different plugins don't accidentally override each other.

For more detailed information about message types and naming conventions, see the [WebSocket Message Types Documentation](docs/ws.md).

### Using AsyncWidget [WIP]

The AsyncWidget feature allows for asynchronous loading of UI components, improving the responsiveness of your application by rendering complex components in the background.

**Note:** This feature is currently a Work In Progress (WIP) and not fully implemented yet.

For detailed information about the AsyncWidget feature, including usage examples, current status, and planned improvements, see the [AsyncWidget Documentation](docs/async_widget.md).

## Advanced Usage and Troubleshooting

For detailed information about advanced usage, health monitoring, and troubleshooting, see the [Advanced Usage Documentation](docs/advanced_usage.md).

## License

This plugin is licensed under the same license as the FastPluggy framework.
