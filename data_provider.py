import datetime as dt
import json
import random
import threading
import time
from typing import cast

import numpy as np
import pandas as pd
import Pyro5.api


@Pyro5.api.expose
class DataProvider:
    def __init__(self):
        self.data_lock = threading.Lock()
        self.ticks_df = pd.DataFrame(columns=["timestamp", "bid", "ask"])
        self.running = True

        # Start background threads for tick generation and data dumping
        self.tick_thread = threading.Thread(target=self.generate_ticks)
        self.dump_thread = threading.Thread(target=self.dump_ticks)
        self.tick_thread.start()
        self.dump_thread.start()

    def generate_ticks(self):
        """Generates tick data every 0.1-0.3 seconds and appends to the DataFrame."""
        if len(self.ticks_df) > 1000:
            self.ticks_df = self.ticks_df.tail(1000)
        while self.running:
            time.sleep(random.uniform(0.1, 0.3))
            timestamp = dt.datetime.now(tz=dt.timezone.utc)
            bid = np.random.uniform(100, 105)
            ask = bid + np.random.uniform(0, 1)
            with self.data_lock:
                new_tick = pd.DataFrame(
                    {"timestamp": [timestamp], "bid": [bid], "ask": [ask]}
                )
                if len(self.ticks_df) > 0:
                    self.ticks_df = cast(
                        pd.DataFrame,
                        pd.concat([self.ticks_df, new_tick], ignore_index=True),
                    )
                else:
                    self.ticks_df = new_tick

    def dump_ticks(self):
        """Dumps the DataFrame to a CSV file every 10 seconds."""
        while self.running:
            time.sleep(10)
            with self.data_lock:
                if not self.ticks_df.empty:
                    filename = dt.datetime.now(dt.timezone.utc).strftime(
                        "ticks_%Y%m%d_%H%M%S.csv"
                    )
                    self.ticks_df.to_csv(filename, index=False)

    def get_ticks(self):
        """Returns a JSON message with at most 100 samples from the DataFrame."""
        with self.data_lock:
            df = self.ticks_df.tail(100).copy()
        print(f"get_ticks returned {len(df)} ticks!")
        json_data = df.to_json(orient="records", date_format="iso")
        return json_data

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
        self.running = False
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
        daemon.requestLoop()
    finally:
        # Ensure we shutdown the threads
        provider.shutdown()


if __name__ == "__main__":
    main()
