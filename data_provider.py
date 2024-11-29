import datetime as dt
import random
import threading

import numpy as np
import pandas as pd
import Pyro5.api

MAX_NUM_FILES = 2


@Pyro5.api.expose
class DataProvider:
    def __init__(self):
        self.num_files = 0
        self.data_lock = threading.Lock()
        self.ticks_df = pd.DataFrame(columns=["timestamp", "bid", "ask"])
        self.stop_event = threading.Event()
        # Start background threads for tick generation and data dumping
        self.tick_thread = threading.Thread(target=self.generate_ticks)
        self.dump_thread = threading.Thread(target=self.dump_ticks)
        self.tick_thread.start()
        self.dump_thread.start()

    def generate_ticks(self):
        """Generates tick data every 0.1 seconds and appends to the DataFrame."""
        while not self.stop_event.is_set():
            sleep_time = random.uniform(0.09, 0.10)
            if self.stop_event.wait(timeout=sleep_time):
                break
            timestamp = dt.datetime.now(tz=dt.timezone.utc)
            bid = np.random.uniform(100, 105)
            ask = bid + np.random.uniform(0, 1)
            with self.data_lock:
                new_tick = pd.DataFrame(
                    {"timestamp": [timestamp], "bid": [bid], "ask": [ask]}
                )
                if len(self.ticks_df) == 0:
                    self.ticks_df = new_tick
                else:
                    self.ticks_df = pd.concat(
                        [new_tick, self.ticks_df], ignore_index=True
                    )
                if len(self.ticks_df) > 1000:
                    self.ticks_df = self.ticks_df.head(1000)

    def dump_ticks(self):
        """Dumps the DataFrame to a CSV file periodically."""
        # Wait is false whenever the stop_event has been sen
        while not self.stop_event.wait(timeout=3):
            with self.data_lock:
                if not self.ticks_df.empty:
                    filename = dt.datetime.now(dt.timezone.utc).strftime(
                        "ticks_%Y%m%d_%H%M%S.csv"
                    )
                    self.ticks_df.to_csv(filename, index=False)
                    print(f"Successfully dumped the ticks to '{filename}'.")
            self.num_files += 1
            if self.num_files >= MAX_NUM_FILES:
                print(
                    "Shutdown_Reason: Automatically kills the process after creating too many files"
                    " to avoid causing issues with the OS if the process is left running in the"
                    " background for some reason."
                )
                self.stop_event.set()

    def get_ticks(self) -> str:
        """Returns a JSON message with at most 100 samples from the DataFrame."""
        with self.data_lock:
            df = self.ticks_df.head(100).copy()
        json_data = df.to_json(orient="records", date_format="iso")
        return str(json_data)

    def get_current_price(self):
        """Returns a tuple with the current bid and ask price."""
        with self.data_lock:
            if not self.ticks_df.empty:
                bid = self.ticks_df.iloc[-1]["bid"]
                ask = self.ticks_df.iloc[-1]["ask"]
            else:
                # If no ticks are available yet, generate a random price
                bid = np.random.uniform(100, 105)
                ask = bid + np.random.uniform(0, 1)
        return (float(bid), float(ask))

    def shutdown(self):
        """Stops the background threads gracefully."""
        print("Shutting down")
        self.stop_event.set()
        self.tick_thread.join()
        self.dump_thread.join()


def main():
    # Start the Pyro daemon
    daemon = Pyro5.server.Daemon()
    # Register the DataProvider class as a Pyro object
    provider = DataProvider()
    uri = daemon.register(provider)
    # Find the name server
    ns = Pyro5.api.locate_ns()
    # Register the object with a name in the name server
    ns.register("example.dataprovider", uri)
    print("DataProvider is ready. URI:", uri)
    try:
        # Start the event loop of the server to wait for calls
        daemon.requestLoop(loopCondition=lambda: not provider.stop_event.is_set())
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, shutting down.")
    finally:
        # Ensure we shutdown the threads and close the daemon
        provider.shutdown()
        daemon.close()


if __name__ == "__main__":
    main()
