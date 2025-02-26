"""
WebSocket server for Polly.

This module provides a WebSocket server to handle communication
between the Raspberry Pi and the web app.
"""

import os
import json
import asyncio
import base64
import logging
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Warning: websockets not available. Using mock implementation.")
    
    # Mock websockets for development
    class MockWebSocket:
        async def send(self, message):
            print(f"WebSocket send: {message[:50]}...")
            
        async def recv(self):
            print("WebSocket recv: Mock message")
            return json.dumps({"type": "mock", "data": "Mock response"})
            
        async def wait_closed(self):
            print("WebSocket closed")
    
    class MockWebSocketServerProtocol:
        def __init__(self):
            pass
            
        @staticmethod
        async def serve(handler, host, port):
            print(f"Mock WebSocket server started on {host}:{port}")
            return MockServer()
    
    class MockServer:
        async def wait_closed(self):
            print("Server wait_closed called")
            
        def close(self):
            print("Server closed")
    
    # Replace websockets module
    websockets = type('obj', (object,), {
        'serve': MockWebSocketServerProtocol.serve,
        'WebSocketServerProtocol': MockWebSocketServerProtocol
    })


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for communication with the web app."""
    
    def __init__(self, host="0.0.0.0", port=8765):
        """
        Initialize the WebSocket server.
        
        Args:
            host: Host to bind the server to (default: "0.0.0.0")
            port: Port to bind the server to (default: 8765)
        """
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()
        self.audio_callback = None
        self.response_callback = None
        
    async def _handle_client(self, websocket, path):
        """
        Handle a client connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        client_id = id(websocket)
        logger.info(f"Client connected: {client_id}")
        
        # Add client to set
        self.clients.add(websocket)
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "info",
                "data": "Connected to Polly WebSocket server"
            }))
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON message")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "data": "Invalid JSON message"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            # Remove client from set
            self.clients.remove(websocket)
            
    async def _handle_message(self, websocket, data):
        """
        Handle a message from a client.
        
        Args:
            websocket: WebSocket connection
            data: Message data
        """
        if "type" not in data:
            logger.error("Message missing type field")
            await websocket.send(json.dumps({
                "type": "error",
                "data": "Message missing type field"
            }))
            return
            
        message_type = data["type"]
        logger.info(f"Received message of type: {message_type}")
        
        if message_type == "ping":
            # Respond to ping
            await websocket.send(json.dumps({
                "type": "pong",
                "data": data.get("data", "pong")
            }))
            
        elif message_type == "audio_response":
            # Handle audio response from web app
            if "data" not in data:
                logger.error("Audio response missing data")
                await websocket.send(json.dumps({
                    "type": "error",
                    "data": "Audio response missing data"
                }))
                return
                
            # Process audio response
            audio_data = data["data"]
            
            # If audio data is base64 encoded, decode it
            if isinstance(audio_data, str) and audio_data.startswith("data:audio"):
                # Extract the base64 part
                base64_data = audio_data.split(",")[1]
                # Decode base64
                audio_bytes = base64.b64decode(base64_data)
                
                # Save audio to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio/response_{timestamp}.wav"
                
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                    
                logger.info(f"Saved audio response to {filename}")
                
                # Call response callback if set
                if self.response_callback:
                    self.response_callback(filename)
                    
                # Send acknowledgment
                await websocket.send(json.dumps({
                    "type": "ack",
                    "data": "Audio response received"
                }))
            else:
                logger.error("Invalid audio data format")
                await websocket.send(json.dumps({
                    "type": "error",
                    "data": "Invalid audio data format"
                }))
                
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket.send(json.dumps({
                "type": "error",
                "data": f"Unknown message type: {message_type}"
            }))
            
    async def send_audio(self, audio_file):
        """
        Send audio to all connected clients.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            bool: True if audio was sent to at least one client
        """
        if not self.clients:
            logger.warning("No clients connected")
            return False
            
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return False
            
        try:
            # Read audio file
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
                
            # Encode as base64
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Create message
            message = json.dumps({
                "type": "audio",
                "data": f"data:audio/wav;base64,{audio_base64}"
            })
            
            # Send to all clients
            await asyncio.gather(
                *[client.send(message) for client in self.clients]
            )
            
            logger.info(f"Sent audio to {len(self.clients)} clients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            return False
            
    async def start(self):
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"WebSocket server started on {self.host}:{self.port}")
        
        # Keep the server running
        await self.server.wait_closed()
        
    def start_server(self, audio_callback=None, response_callback=None):
        """
        Start the WebSocket server in a new event loop.
        
        Args:
            audio_callback: Function to call when audio is received
            response_callback: Function to call when a response is received
        """
        self.audio_callback = audio_callback
        self.response_callback = response_callback
        
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start the server
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            loop.close()
            
    def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            logger.info("WebSocket server stopped")


# Example usage
if __name__ == "__main__":
    # Create and start the server
    server = WebSocketServer(host="0.0.0.0", port=8765)
    
    # Define response callback
    def on_response(filename):
        print(f"Response received: {filename}")
        
    try:
        server.start_server(response_callback=on_response)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        server.stop()
