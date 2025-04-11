#!/usr/bin/env python3
"""
QGIS MCP Client - Simple client to connect to the QGIS MCP server
"""

import socket
import json
import argparse
import sys

class QgisMCPClient:
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Connect to the QGIS MCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error connecting to server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send_command(self, command_type, params=None):
        """Send a command to the server and get the response"""
        if not self.socket:
            print("Not connected to server")
            return None
        
        # Create command
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Send the command
            self.socket.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive the response
            response_data = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                
                # Try to decode as JSON to see if it's complete
                try:
                    json.loads(response_data.decode('utf-8'))
                    break  # Valid JSON, we have the full message
                except json.JSONDecodeError:
                    continue  # Keep receiving
            
            # Parse and return the response
            return json.loads(response_data.decode('utf-8'))
            
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            return None
    
    def ping(self):
        """Simple ping command to check server connectivity"""
        return self.send_command("ping")
    
    def get_qgis_info(self):
        """Get QGIS information"""
        return self.send_command("get_qgis_info")
    
    def get_project_info(self):
        """Get current project information"""
        return self.send_command("get_project_info")
    
    def execute_code(self, code):
        """Execute arbitrary PyQGIS code"""
        return self.send_command("execute_code", {"code": code})
    
    def add_vector_layer(self, path, name=None, provider="ogr"):
        """Add a vector layer to the project"""
        params = {
            "path": path,
            "provider": provider
        }
        if name:
            params["name"] = name
            
        return self.send_command("add_vector_layer", params)
    
    def add_raster_layer(self, path, name=None, provider="gdal"):
        """Add a raster layer to the project"""
        params = {
            "path": path,
            "provider": provider
        }
        if name:
            params["name"] = name
            
        return self.send_command("add_raster_layer", params)
    
    def get_layers(self):
        """Get all layers in the project"""
        return self.send_command("get_layers")
    
    def remove_layer(self, layer_id):
        """Remove a layer from the project"""
        return self.send_command("remove_layer", {"layer_id": layer_id})
    
    def zoom_to_layer(self, layer_id):
        """Zoom to a layer's extent"""
        return self.send_command("zoom_to_layer", {"layer_id": layer_id})
    
    def get_layer_features(self, layer_id, limit=10):
        """Get features from a vector layer"""
        return self.send_command("get_layer_features", {"layer_id": layer_id, "limit": limit})
    
    def execute_processing(self, algorithm, parameters):
        """Execute a processing algorithm"""
        return self.send_command("execute_processing", {
            "algorithm": algorithm,
            "parameters": parameters
        })
    
    def save_project(self, path=None):
        """Save the current project"""
        params = {}
        if path:
            params["path"] = path
            
        return self.send_command("save_project", params)
    
    def load_project(self, path):
        """Load a project"""
        return self.send_command("load_project", {"path": path})
    
    def render_map(self, path, width=800, height=600):
        """Render the current map view to an image"""
        return self.send_command("render_map", {
            "path": path,
            "width": width,
            "height": height
        })


def print_json(data):
    """Imprime datos JSON formateados"""
    print(json.dumps(data, indent=2))

def main():
    # Conectar al servidor QGIS MCP
    client = QgisMCPClient(host='localhost', port=9876)
    if not client.connect():
        print("No se pudo conectar al servidor QGIS MCP")
        return
    
    try:
        # Verificar conexión con ping
        print("Verificando conexión...")
        response = client.ping()
        if response and response.get("status") == "success":
            print("Conexión exitosa")
        else:
            print("Error de conexión")
            return
        
        # Obtener información de QGIS
        print("\nInformación de QGIS:")
        qgis_info = client.get_qgis_info()
        print_json(qgis_info)
        
        # Load project
        print("\nLoad project")
        load_project = client.load_project("C:/Users/jjsan/OneDrive/Consultoria/Finalizados/electoral_maps/thailand_2007/thailand_2007.qgz")
        print_json(load_project)

        # Obtener información del proyecto actual
        print("\nInformación del proyecto:")
        project_info = client.get_project_info()
        print_json(project_info)

        # Zoom to layer
        print("\nZoom to first layer")
        first_layer = project_info["result"]["layers"][0]["id"]
        zoom_layer = client.zoom_to_layer(first_layer)
        print_json(zoom_layer)

        # Render Map to file
        print("\nRendering image")
        render_map = client.render_map("C:/Users/jjsan/OneDrive/Consultoria/Finalizados/electoral_maps/thailand_2007/map.png")
        print_json(render_map)
        
    except Exception:
        print("Error ejecutando comandos")

if __name__ == "__main__":
    main()