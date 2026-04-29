import json
import requests
import uuid
import sys
import threading
import time

from config import settings

SESSION_ID = str(uuid.uuid4())


class LoadingSpinner:
    """Manages a background thread to display a dynamic UI during network I/O."""

    def __init__(self):
        self.spinner_chars = "|/-\\"
        self.messages = [
            "Analyzing query context...",
            "Searching local knowledge base...",
            "Retrieving insurance policy schemas...",
            "Synthesizing response...",
        ]
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        msg_idx = 0
        while self.running:
            if i > 0 and i % 15 == 0:
                if msg_idx < len(self.messages) - 1:
                    msg_idx += 1

            current_msg = self.messages[msg_idx]
            sys.stdout.write(
                f"\r{self.spinner_chars[i % len(self.spinner_chars)]} {current_msg}"
                + " " * 10
            )
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


def main():
    print("=================================================================")
    print(" Life Insurance Support Assistant API Client v1.0")
    print(" Session Status: Active")
    print(" Instructions: Enter your query below. Type 'exit' to disconnect.")
    print("=================================================================\n")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("\n[System] Disconnecting from server... Session terminated.")
                break

            if not user_input.strip():
                continue

            payload = {"session_id": SESSION_ID, "message": user_input}

            spinner = LoadingSpinner()
            spinner.start()

            first_token_received = False

            with requests.post(
                settings.api_stream_url, json=payload, stream=True
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]

                            if data_str == "[DONE]":
                                break

                            try:
                                data_json = json.loads(data_str)

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

            print()

        except requests.exceptions.ConnectionError:
            print(
                "\n[System Error] Connection refused. Ensure the backend server is running."
            )
            break
        except KeyboardInterrupt:
            print("\n\n[System] Process interrupted by user. Session terminated.")
            break


if __name__ == "__main__":
    main()
