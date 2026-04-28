import json
import requests
import uuid
import sys
import threading
import time

API_URL = "http://127.0.0.1:8000/api/v1/chat/stream"
SESSION_ID = str(uuid.uuid4())

class LoadingSpinner:
    """A background thread that prints a spinner while waiting for network I/O."""
    def __init__(self, message="Thinking..."):
        self.spinner_chars = "|/-\\"
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        while self.running:
            # \r returns the carriage to the start of the line to overwrite it
            sys.stdout.write(f"\r{self.spinner_chars[i % len(self.spinner_chars)]} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

        # Clear the line completely when stopped
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        # Daemon threads exit automatically when the main program exits
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

def main():
    print("===========================================================")
    print("🛡️  Life Insurance Support Assistant (Type 'exit' to quit)")
    print("===========================================================\n")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            payload = {
                "session_id": SESSION_ID,
                "message": user_input
            }

            # Initialize and start the spinner
            spinner = LoadingSpinner("Searching knowledge base...")
            spinner.start()

            first_token_received = False

            with requests.post(API_URL, json=payload, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]

                            if data_str == "[DONE]":
                                break

                            try:
                                data_json = json.loads(data_str)

                                # The moment we get our first piece of data, kill the spinner
                                if not first_token_received:
                                    spinner.stop()
                                    print("Agent: ", end="", flush=True)
                                    first_token_received = True

                                if "token" in data_json:
                                    print(data_json["token"], end="", flush=True)
                                elif "error" in data_json:
                                    print(f"\n[Error: {data_json['error']}]")
                            except json.JSONDecodeError:
                                pass

            print() # Add a final newline when the stream finishes

        except requests.exceptions.ConnectionError:
            print("\n[Connection Error: Ensure your app server (uvicorn app:app) is running!]")
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()