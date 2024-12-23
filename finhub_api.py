from finhub_config_file import schema_url, schema_output_file
from finhub_config_file import FINNHUB_WS_URL, token_key, US_STOCKS
import requests
import json
import websocket


class FinhubAPI(object):
    def __init__(self):
        self.ws = None

    def fetch_schema(self):
        # Fetch the JSON schema from Finnhub's API
        try:
            # Send a GET request to the URL
            response = requests.get(schema_url)
            response.raise_for_status()  # Check for HTTP request errors
            
            # Parse the JSON content
            data = response.json()
            
            # Write the JSON data to a file
            with open(schema_output_file, "w") as file:
                json.dump(data, file, indent=4)
            
            print(f"JSON schema saved successfully to '{schema_output_file}'")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the JSON schema: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    def WebSocketConnection(self):
        # Establish a WebSocket connection to Finnhub's API
        # Create a WebSocket connection
        # websocket.enableTrace(True)
        FINNHUB_WS_URL_TOKEN = FINNHUB_WS_URL.replace('<your_token>', token_key)
        self.ws = websocket.WebSocketApp(
            FINNHUB_WS_URL_TOKEN,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        
        # Run the WebSocket
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            print("WebSocket client stopped.")
            raise
        

    def on_message(self, ws, message):
        """
        Callback function for receiving messages from the WebSocket.
        """
        data = json.loads(message)
        print("Received Message:", json.dumps(data, indent=4))

    def on_error(self, ws, error):
        """
        Callback function for handling errors.
        """
        print("WebSocket Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Callback function when the WebSocket connection is closed.
        """
        print("WebSocket closed:", close_msg)

    def on_open(self, ws):
        """
        Callback function when the WebSocket connection is opened.
        """
        print("WebSocket connection opened.")
        # Subscribe to each US stock symbol
        for symbol in US_STOCKS:
            subscribe_message = {
                "type": "subscribe",
                "symbol": symbol
            }
            self.ws.send(json.dumps(subscribe_message))
        



def main():
    try:
        # One Time Run for the Schemas files
        api = FinhubAPI()
        api.fetch_schema()

        api.WebSocketConnection()

        # WebSocket Connection
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()



