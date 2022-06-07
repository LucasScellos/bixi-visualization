'''
Take real time data from Bixi json

Save data in severals .csv
'''

import json
import os
from queue import Queue
import threading
import time
import pandas as pd
import urllib.request
import datetime as dt
import keyboard

# Number of collected data to create a .csv
NB_ROWS_CSV = 100 

# Get new data every 20 seconds
TIME_BETWEEN_COLLECT = 20

# Collect time. If negative or null, infinite collect
COLLECT_TIME = 0

# CSV Prefix
RESULT_PATH = "Sniffer Data"


class BixiSniffer:
    def __init__(self, result_path: str, nb_rows_csv: int, time_between_collect: int, collect_time: int) -> None:
        self.result_path = result_path
        if not self.result_path in os.listdir():
            os.makedirs(os.path.join(self.result_path, "Available Bikes"))
            os.mkdir(os.path.join(self.result_path, "Available eBikes"))

        self.nb_rows_csv = nb_rows_csv
        self.nb_csv = 1

        self.time_between_collect = time_between_collect
        self.collect_time = collect_time

        # Manage thread sync with a queue
        self.nb_rows_queue = Queue()
        self.sniffer_on = False
        self.get_and_save_thread = threading.Thread(
            target=self.get_and_save_data, args=(self.nb_rows_queue,),daemon=True)
        self.sniffer_thread = threading.Thread(target=self.sniffer)

        # Init dataframe columns
        df_bikes, df_ebikes = self.get_data()
        self.df_available_bikes_original = pd.DataFrame(
            columns=df_bikes.columns)
        self.df_available_ebikes_original = pd.DataFrame(
            columns=df_ebikes.columns)

        self.df_available_bikes = self.df_available_bikes_original.copy()
        self.df_available_ebikes = self.df_available_ebikes_original.copy()
        print("Press SPACE to abord acquisition (will save incomplete data) ...")
        
    def query_station_status(self, bixi_url="https://gbfs.velobixi.com/gbfs/fr/station_status.json"):
        with urllib.request.urlopen(bixi_url) as data_url:
            data = json.loads(data_url.read().decode())

        df = pd.DataFrame(data['data']['stations'])
        # drop inactive stations
        # TODO Check if necessary, problems with columns if a merge is needed ???
        df = df[df.is_renting == 1]
        df = df[df.is_returning == 1]
        df = df.drop_duplicates(['station_id', 'last_reported'])
        df.last_reported = df.last_reported.map(
            lambda x: dt.datetime.utcfromtimestamp(x))
        df['time'] = data['last_updated']
        df.time = df.time.map(lambda x: dt.datetime.utcfromtimestamp(x))
        df = df.set_index('time')
        # Add convert to Montreal time
        df.index = df.index.tz_localize('UTC').tz_convert('America/Montreal')

        return df

    def get_data(self):
        df = self.query_station_status()
        df_bikes = pd.pivot_table(
            df, columns='station_id', index='time', values='num_bikes_available')
        df_ebikes = pd.pivot_table(
            df, columns='station_id', index='time', values='num_ebikes_available')
        return df_bikes, df_ebikes

    def get_and_save_data(self, nb_rows_queue: Queue):
        '''
        Get each data, accumulate and save to .csv
        '''
        while self.sniffer_on:
            # Wait for nb_rows
            nb_rows = nb_rows_queue.get()

            # Get data
            df_bikes, df_ebikes = self.get_data()

            # Concat dataframe
            self.df_available_bikes = pd.concat(
                [self.df_available_bikes, df_bikes])
            self.df_available_ebikes = pd.concat(
                [self.df_available_ebikes, df_ebikes])

            # Save csv if nb_rows is enough
            if nb_rows == self.nb_rows_csv:
                self.df_available_bikes.to_csv(os.path.join(
                    self.result_path, "Available Bikes", f"Available_Bikes_{str(self.nb_csv).zfill(3)}.csv"))
                self.df_available_ebikes.to_csv(os.path.join(
                    self.result_path, "Available eBikes", f"Available_eBikes_{str(self.nb_csv).zfill(3)}.csv"))
                self.nb_csv += 1

                # Reset DataFrames
                self.df_available_bikes = self.df_available_bikes_original.copy()
                self.df_available_ebikes = self.df_available_ebikes_original.copy()
        print("Get and save data thread stopped")

    def start_sniffer(self):
        self.sniffer_on = True
        
        # Start loop thread and get_and_save thread
        self.sniffer_thread.start()
        self.get_and_save_thread.start()
        
        # Wait for pressing keyboard or end of time...
        while self.sniffer_on:
            if keyboard.is_pressed("space"):
                # Passing sniffer_on to False will end other threads
                self.sniffer_on=False
            time.sleep(0.01)
        
        # Save data to csv if not empty
        if len(self.df_available_bikes):
            self.df_available_bikes.to_csv(os.path.join(
                self.result_path, "Available Bikes", f"Available_Bikes_{str(self.nb_csv).zfill(3)}.csv"))
            self.df_available_ebikes.to_csv(os.path.join(
                self.result_path, "Available eBikes", f"Available_eBikes_{str(self.nb_csv).zfill(3)}.csv"))
            self.nb_csv += 1


    def sniffer(self):
        nb_rows = 0
        start_time = time.perf_counter()
        print("Starting Bixi Sniffer..")

        while self.sniffer_on:
            # Loop that manage nb_rows and therefore the thread and saving to csv
            nb_rows += 1

            # Put nb_rows to queue: execute func in thread
            self.nb_rows_queue.put(nb_rows)

            current_time = time.perf_counter()-start_time
            # Print information
            print(
                f"Time since beggining : {dt.timedelta(seconds=int(current_time))} | Current number of csv files : {self.nb_csv} | Number of rows for current csv : {nb_rows}")

            # Reset nb_rows if equals to desired rows number is csv
            if nb_rows == self.nb_rows_csv:
                nb_rows = 0

            # Stop condition if collect_time > 0
            if self.collect_time > 0:
                print(
                    f"Remaining time: {int(self.collect_time-current_time)} s")
                if current_time > self.collect_time:
                    break

            # Wait for new collect
            time.sleep(self.time_between_collect)

        self.sniffer_on = False
        print("Sniffer stopped successfully !")


if __name__ == "__main__":
    sniffer = BixiSniffer(RESULT_PATH, NB_ROWS_CSV,
                          TIME_BETWEEN_COLLECT, COLLECT_TIME)

    # Test initializing dataframes

    # print(sniffer.df_available_bikes_original)
    # print(sniffer.df_available_ebikes_original)

    # Test sniffing
    sniffer.start_sniffer()
