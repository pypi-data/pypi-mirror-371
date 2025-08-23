# src/race.py

import pandas as pd
import requests
import warnings
from .codes import FLAG_CODE
from .caching import load_df, save_df


#https://cf.nascar.com/cacher/2023/2/5314/lap-times.json

class Race:
    def __init__(self, year, series_id,race_id=None,live=False):
        # Initialize race metadata
        self.year = year
        self.live = live
        self.series_id = series_id
        self.race_id = race_id
        self.entrants = None
        self.superspeedway = None
        self.winner = None
        self.data = {}

        # Practice and Qualifying.
        # This may be moved
        self.practice_data = pd.DataFrame()
        self.qualifying_data = pd.DataFrame()

        # Race Data
        self.name = None
        self.laps = None
        self.pit_stops = None
        self.events = None
        self.results = None
        self.cautions = None
        self.lead_changes = None
        self.lead_change_data = None
        self.start_time = None
        self.race_time = None
        self.end_time = None
        self.distance = None
        self.lap_count = None
        self.drivers = pd.DataFrame()
        self.driver_stats_advanced = pd.DataFrame()

        # Stage Results. Currently shows only the top 10
        self.stage_1_results = None
        self.stage_2_results = None
        self.stage_3_results = None
        self.s1_lap_count = None
        self.s2_lap_count = None
        self.s3_lap_count = None

        # Initialize the race data
        self.fetch_laps()
        self.get_pit_stops()
        self.fetch_events()
        self.get_race_data()
        self.get_driver_stats()
        self.get_advanced_driver_stats()


    def get_race_data(self):
        """
        Fetch data for the race
        """
        if not self.live:
            cached_results = load_df("results", year=self.year, series_id=self.series_id, race_id=self.race_id)
            cached_cautions = load_df("cautions", year=self.year, series_id=self.series_id, race_id=self.race_id)
            cached_lead_changes = load_df("lead_changes", year=self.year, series_id=self.series_id, race_id=self.race_id)
            cached_stage1 = load_df("stage_1_results", year=self.year, series_id=self.series_id, race_id=self.race_id)
            cached_stage2 = load_df("stage_2_results", year=self.year, series_id=self.series_id, race_id=self.race_id)
            cached_stage3 = load_df("stage_3_results", year=self.year, series_id=self.series_id, race_id=self.race_id)

            if cached_results is not None:
                self.results = cached_results
            if cached_cautions is not None:
                self.cautions = cached_cautions
            if cached_lead_changes is not None:
                self.lead_changes = len(cached_lead_changes) - 1 if not cached_lead_changes.empty else 0
                self.lead_change_data = cached_lead_changes

            if cached_stage1 is not None:
                self.stage_1_results = cached_stage1
            if cached_stage2 is not None:
                self.stage_2_results = cached_stage2
            if cached_stage3 is not None:
                self.stage_3_results = cached_stage3

            if (
                cached_results is not None
                and cached_cautions is not None
                and cached_lead_changes is not None
                and cached_stage1 is not None
                and cached_stage2 is not None
                and cached_stage3 is not None
            ):
                 print(f'Loading data from Cache for: {self.year}-{self.series_id}-{self.race_id}')
                 return
            
            url = f"https://cf.nascar.com/cacher/{self.year}/{self.series_id}/{self.race_id}/weekend-feed.json"
            print(f'Fetching data for Year:{self.year} Series: {self.series_id} Race: {self.race_id}')
        else:
            url = f"https://cf.nascar.com/cacher/live/series_{self.series_id}/{self.race_id}/weekend-feed.json"
            print(f'Loading live data for: Year:{self.year} Series: {self.series_id} Race: {self.race_id}')

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            try:
                weekend = data.get('weekend_race', [])[0]
                weekend_runs = data.get('weekend_runs', [])
            except:
                weekend = {}
                weekend_runs = []

            self.race_time = weekend.get('total_race_time')
            self.distance = weekend.get('scheduled_distance')
            self.lap_count = weekend.get('scheduled_laps')
            self.s1_lap_count = weekend.get('stage_1_laps')
            self.s2_lap_count = weekend.get('stage_2_laps')
            self.s3_lap_count = weekend.get('stage_3_laps')
            self.entrants = weekend.get('number_of_cars_in_field')
            self.superspeedway = weekend.get('restrictor_plate')

            
            results = weekend.get('results', [])
            caution_segments = weekend.get('caution_segments', [])
            leaders = weekend.get('race_leaders', [])
            stages = weekend.get('stage_results', [])

            driver_res = []
            caution_rows = []
            leader_list = []
            stage_1 = []
            stage_2 = []
            stage_3 = []

            for i in results:
                driver_res.append({
                    'driver_id': i.get('driver_id'),
                    'driver': i.get('driver_fullname'),
                    'driver_number': i.get('car_number'),
                    'manufacturer': i.get('car_make'),
                    'sponsor': i.get('sponsor'),
                    'team': i.get('team_name'),
                    'team_id': i.get('team_id'),
                    'qualifying_order': i.get('qualifying_order'),
                    'qualifying_position': i.get('qualifying_position'),
                    'qualifying_speed': i.get('qualifying_speed'),
                    'starting_position': i.get('starting_position'),
                    'finishing_position': i.get('finishing_position'),                    
                    'laps_completed': i.get('laps_completed'),
                    'points': i.get('points_earned'),
                    'playoff_points': i.get('playoff_points_earned'),
                })
            self.results = pd.DataFrame(driver_res)
            if not self.live:
                save_df("results", self.results, year=self.year, series_id=self.series_id, race_id=self.race_id)

            for i in caution_segments:
                caution_rows.append({
                    'start_lap': i.get('start_lap'),
                    'end_lap': i.get('end_lap'),
                    'caution_type': i.get('reason'),
                    'comment': i.get('comment'),
                    'flag_state': i.get('flag_state'),
                })

            self.cautions = pd.DataFrame(caution_rows) if caution_rows else pd.DataFrame()
            self.cautions['Flag'] = self.cautions['flag_state'].map(FLAG_CODE) if not self.cautions.empty else None
            self.cautions['duration'] = self.cautions['end_lap'] - self.cautions['start_lap'] if not self.cautions.empty else None
            
            if not self.live:
                save_df("cautions", self.cautions, year=self.year, series_id=self.series_id, race_id=self.race_id)
            for i in leaders:
                leader_list.append({
                    'start_lap': i.get('start_lap'),
                    'end_lap': i.get('end_lap'),
                    'driver_name': None,
                    'car_number': i.get('car_number')
                })

            try:
                self.lead_changes = len(leader_list) - 1 if leader_list else 0
                self.lead_change_data = pd.DataFrame(leader_list) if leader_list else pd.DataFrame()
                self.lead_change_data['driver_name'] = self.lead_change_data['car_number'].map(self.results.set_index('driver_number')['driver']) if not self.lead_change_data.empty else None
                if not self.live:
                    save_df("lead_changes", self.lead_change_data, year=self.year, series_id=self.series_id, race_id=self.race_id)
            except Exception as e:
                print(f"Error processing lead changes: {e}")
            
            for i in stages:
                if i.get('stage_number') == 1:
                    for j in i.get('results', []):
                        stage_1.append({
                            'driver_id': j.get('driver_id'),
                            'driver_name': j.get('driver_fullname'),
                            'car_number': j.get('car_number'),
                            'position': j.get('finishing_position'),
                            'stage_points': j.get('stage_points'),
                        })
                elif i.get('stage_number') == 2:
                    for j in i.get('results', []):
                        stage_2.append({
                            'driver_id': j.get('driver_id'),
                            'driver_name': j.get('driver_fullname'),
                            'car_number': j.get('car_number'),
                            'position': j.get('finishing_position'),
                            'stage_points': j.get('stage_points'),
                        })
                elif i.get('stage_number') == 3:
                    for j in i.get('results', []):
                        stage_3.append({
                            'driver_id': j.get('driver_id'),
                            'driver_name': j.get('driver_fullname'),
                            'car_number': j.get('car_number'),
                            'position': j.get('finishing_position'),
                            'stage_points': j.get('stage_points'),
                        })

            self.stage_1_results = pd.DataFrame(stage_1) if stage_1 else pd.DataFrame()
            self.stage_2_results = pd.DataFrame(stage_2) if stage_2 else pd.DataFrame()
            self.stage_3_results = pd.DataFrame(stage_3) if stage_3 else pd.DataFrame()

            if not self.live:
                save_df('stage_1_results', self.stage_1_results, year=self.year, series_id=self.series_id, race_id=self.race_id)
                save_df('stage_2_results', self.stage_2_results, year=self.year, series_id=self.series_id, race_id=self.race_id)
                save_df('stage_3_results', self.stage_3_results, year=self.year, series_id=self.series_id, race_id=self.race_id)

            # Process weekend runs (practice and qualifying)
            for run in weekend_runs:
                name = (run.get('run_name') or '').lower()
                if 'practice' in name:
                    df = self.get_practice_results(run)
                    if 'practice 1' in name:
                        df['practice_number'] = 1
                    elif 'practice 2' in name:
                        df['practice_number'] = 2
                    elif 'practice 3' in name:
                        df['practice_number'] = 3
                    elif 'final practice' in name:
                        df['practice_number'] = 4
                    self.practice_data = pd.concat([self.practice_data, df], ignore_index=True) if not self.practice_data.empty else df
                elif 'pole qualifying' in name:
                    df = self.get_qualifying_results(run)
                    if 'round 1' in name:
                        df['qualifying_round'] = 1
                    elif 'final round' in name:
                        df['qualifying_round'] = 2
                    else:
                        df['qualifying_round'] = None
                    self.qualifying_data = pd.concat([self.qualifying_data, df], ignore_index=True) if not self.qualifying_data.empty else df
            if not self.live:
                if not self.practice_data.empty:
                    save_df("practice", self.practice_data, year=self.year, series_id=self.series_id, race_id=self.race_id)
                if not self.qualifying_data.empty:
                    save_df("qualifying", self.qualifying_data, year=self.year, series_id=self.series_id, race_id=self.race_id)

        else:
            print(f"Failed to retrieve race data: {response.status_code}")

    def fetch_laps(self):
        """Fetch lap times for the specified race ID."""
        if not self.live:
            cached = load_df("laps", year=self.year, series_id=self.series_id, race_id=self.race_id)
            if cached is not None:
                self.laps = cached
                return
        
        if self.live:
            url = f"https://cf.nascar.com/cacher/live/series_{self.series_id}/{self.race_id}/lap-times.json"
        else:
            url = f"https://cf.nascar.com/cacher/{self.year}/{self.series_id}/{self.race_id}/lap-times.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.data = data
            lap_times = []
            
            for i in data['laps']:
                driver = i.get('FullName')
                number = i.get('Number')
                manufacturer = i.get('Manufacturer')
                for j in i.get('Laps', []):
                    lap_times.append({
                        'Driver': driver,
                        'Number': number,
                        'Manufacturer': manufacturer,
                        'Lap': j.get('Lap'),
                        'lap_time': j.get('LapTime'),
                        'lap_speed': j.get('LapSpeed'),
                        'position': j.get('RunningPos'),
                    })
            self.laps = pd.DataFrame(lap_times)
            self.laps['Lap'] = pd.to_numeric(self.laps['Lap'], errors='coerce').astype('Int64')
            self.laps['lap_time'] = pd.to_timedelta(self.laps['lap_time'], errors='coerce')
            self.laps['lap_speed'] = pd.to_numeric(self.laps['lap_speed'], errors='coerce')

            # Save the DataFrame to cache
            if not self.live:
                save_df("laps", self.laps, year=self.year, series_id=self.series_id, race_id=self.race_id)
        else:
            print(f"Failed to retrieve lap data: {response.status_code}")
            print(f"url: {url}")

    def get_pit_stops(self):
        """Get pit stop information for the race."""
        if not self.live:
            cached_pit_stops = load_df("pit_stops", year=self.year, series_id=self.series_id, race_id=self.race_id)
            if cached_pit_stops is not None:
                self.pit_stops = cached_pit_stops
                return
            url = f"https://cf.nascar.com/cacher/{self.year}/{self.series_id}/{self.race_id}/live-pit-data.json"
        if self.live:
            url = f"https://cf.nascar.com/cacher/live/series_{self.series_id}/{self.race_id}/live-pit-data.json"
            
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            stops = []
            for i in data:
                stops.append({
                    'Driver': i.get('driver_name'),
                    'Lap': i.get('lap_count'),
                    'Manufacturer': i.get('vehicle_manufacturer'),
                    'pit_in_flag_status': i.get('pit_in_flag_status'),
                    'pit_out_flag_status': i.get('pit_out_flag_status'),
                    'pit_in_race_time': i.get('pit_in_race_time'),
                    'pit_out_race_time': i.get('pit_out_race_time'),
                    'total_duration': i.get('total_duration'),
                    'box_stop_race_time': i.get('box_stop_race_time'),
                    'box_leave_race_time': i.get('box_leave_race_time'),
                    'pit_stop_duration': i.get('pit_stop_duration'),
                    'in_travel_duration': i.get('in_travel_duration'),
                    'out_travel_duration': i.get('out_travel_duration'),
                    'pit_stop_type': i.get('pit_stop_type'),
                    'left_front_tire_changed': i.get('left_front_tire_changed'),
                    'left_rear_tire_changed': i.get('left_rear_tire_changed'),
                    'right_front_tire_changed': i.get('right_front_tire_changed'),
                    'right_rear_tire_changed': i.get('right_rear_tire_changed'),
                    'previous_lap_time': i.get('previous_lap_time'),
                    'next_lap_time': i.get('next_lap_time'),
                    'pit_in_rank': i.get('pit_in_rank'),
                    'pit_out_rank': i.get('pit_out_rank'),
                    'positions_gained_lost': i.get('positions_gained_lost'),
                })
            # store both list and a DataFrame for convenience
            self.pit_stops = pd.DataFrame(stops) if stops else pd.DataFrame()
            if not self.live:
                save_df("pit_stops", self.pit_stops, year=self.year, series_id=self.series_id, race_id=self.race_id)
        else:
            print(f"Failed to retrieve pit stop data: {response.status_code}")
            print(f"url: {url}")

    def fetch_events(self):
        """ Fetch lap events and flags"""
        if not self.live:
            cached_events = load_df("events", year=self.year, series_id=self.series_id, race_id=self.race_id)
            if cached_events is not None:
                self.events = cached_events
                return
            url = f"https://cf.nascar.com/cacher/{self.year}/{self.series_id}/{self.race_id}/lap-notes.json"
        if self.live:
            url = f"https://cf.nascar.com/cacher/live/series_{self.series_id}/{self.race_id}/lap-notes.json"
            
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            events = []
            laps = data.get('laps')
            
            for k,v in laps.items():
                for j in v:
                    events.append({
                        'Lap': k,
                        'Flag_State': j.get('FlagState'),
                        'Flag': None,
                        'note': j.get('Note'),
                        #'note_id': j.get('NoteID'),
                        'driver_ids': j.get('DriverIDs'),
                    })
            self.events = pd.DataFrame(events) if events else pd.DataFrame()
            if not self.events.empty:
                self.events['Flag'] = self.events['Flag_State'].map(FLAG_CODE)
            if not self.live:
                save_df("events", self.events, year=self.year, series_id=self.series_id, race_id=self.race_id)

        else:
            print(f"Failed to retrieve lap events: {response.status_code}")
            print(f"url: {url}")

    def get_practice_results(self, run: dict) -> pd.DataFrame:
        results = run.get('results', [])
        practice_res = []
        for i in results:
            practice_res.append({
                'driver_id': i.get('driver_id'),
                'driver_name': i.get('driver_name'),
                'manufacturer': i.get('manufacturer'),
                'position': i.get('finishing_position'),
                'lap_time': i.get('best_lap_time'),
                'speed': i.get('best_lap_speed'),
                'total_laps': i.get('laps_completed'),
                'delta_to_leader': i.get('delta_leader')
            })

        practice_data = pd.DataFrame(practice_res) if practice_res else pd.DataFrame()
        practice_data['practice_number'] = run.get('practice_number', 1)
        practice_data = practice_data.sort_values(by='position') if not practice_data.empty else pd.DataFrame()
        return practice_data

    def get_qualifying_results(self, run:dict) -> pd.DataFrame:
        results = run.get('results', [])
        quali_res = []
        for i in results:
            quali_res.append({
                'driver_id': i.get('driver_id'),
                'driver_name': i.get('driver_name'),
                'manufacturer': i.get('manufacturer'),
                'position': i.get('finishing_position'),
                'lap_time': i.get('best_lap_time'),
                'speed': i.get('best_lap_speed'),
                'total_laps': i.get('laps_completed'),
                'delta_to_leader': i.get('delta_leader')
            })
        qualifying_data = pd.DataFrame(quali_res) if quali_res else pd.DataFrame()
        qualifying_data['qualifying_round'] = None
        qualifying_data = qualifying_data.sort_values(by='position') if not qualifying_data.empty else pd.DataFrame()
        return qualifying_data

    def get_practice(self, round: int) -> pd.DataFrame:
        """Return practice data for a specific round."""
        data = self.practice_data[self.practice_data['practice_number'] == round] if not self.practice_data.empty else pd.DataFrame()
        return data

    def get_qualifying(self, round: int) -> pd.DataFrame:
        """Return qualifying data for a specific round."""
        data = self.qualifying_data[self.qualifying_data['qualifying_round'] == round] if not self.qualifying_data.empty else pd.DataFrame()
        return data
    
    def get_driver_stats(self):
        #https://cf.nascar.com/loopstats/prod/2023/2/5314.json
        #https://cf.nascar.com/cacher/live/series_2/5314/live-feed.json
        if not self.live:
            cached_driver_stats = load_df("driver_stats", year=self.year, series_id=self.series_id, race_id=self.race_id)
            if cached_driver_stats is not None:
                self.driver_stats = cached_driver_stats
                return
            
        url = f"https://cf.nascar.com/loopstats/prod/{self.year}/{self.series_id}/{self.race_id}.json"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            # Data comes in array
            drivers = data[0].get('drivers', [])
            driver_list = []
            for i in drivers:
                driver_list.append({
                    'driver_id': i.get('driver_id'),
                    'driver_name': None,
                    'start_position': i.get('start_ps'),
                    'mid_position': i.get('mid_ps'),
                    'position': i.get('ps'),
                    'closing_position': i.get('closing_ps'),
                    'closing_laps_diff': i.get('closing_laps_diff'),
                    'best_position': i.get('best_ps'),
                    'worst_position': i.get('worst_ps'),
                    'avg_position': i.get('avg_ps'),
                    'passes_green_flag': i.get('passes_gf'),
                    'passing_diff': i.get('passing_diff'),
                    'passed_green_flag': i.get('passed_gf'),
                    'quality_passes': i.get('quality_passes'),
                    'fast_laps': i.get('fast_laps'),
                    'top15_laps': i.get('top15_laps'),
                    'lead_laps': i.get('lead_laps'),
                    'laps': i.get('laps'),
                    'rating': i.get('rating'),
                })
            
            self.drivers = pd.DataFrame(driver_list) if driver_list else pd.DataFrame()
            if not self.drivers.empty and isinstance(self.results, pd.DataFrame) and not self.results.empty:
                name_map_df = (
                    self.results[['driver_id', 'driver']]
                    .dropna(subset=['driver_id', 'driver'])
                    .astype({'driver_id': 'Int64'})
                    .drop_duplicates(subset=['driver_id'], keep='first')
                )
                name_map = name_map_df.set_index('driver_id')['driver']
                self.drivers['driver_name'] = self.drivers['driver_id'].astype('Int64').map(name_map)
            if not self.live:
                save_df("driver_stats", self.drivers, year=self.year, series_id=self.series_id, race_id=self.race_id)

    def get_advanced_driver_stats(self):
        # Implement the logic to retrieve advanced driver stats
        if not self.live:
            cached_driver_stats_advanced = load_df("driver_stats_advanced", year=self.year, series_id=self.series_id, race_id=self.race_id)
            if cached_driver_stats_advanced is not None:
                self.driver_stats_advanced = cached_driver_stats_advanced
                return
            
        url = f"https://cf.nascar.com/cacher/live/series_{self.series_id}/{self.race_id}/live-feed.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Process the advanced driver stats data
            vehicles = data.get('vehicles', [])
            driver_stats_advanced = []
            for vehicle in vehicles:
                driver = vehicle.get('driver', {})
                driver_stats_advanced.append({
                    'driver_id': driver.get('driver_id'),
                    'driver_name': driver.get('full_name'),
                    'vehicle_number': vehicle.get('vehicle_number'),
                    'vehicle_manufacturer': vehicle.get('vehicle_manufacturer'),
                    'sponsor_name': vehicle.get('sponsor_name'),
                    'best_lap': vehicle.get('best_lap'),
                    'best_lap_speed': vehicle.get('best_lap_speed'),
                    'best_lap_time': vehicle.get('best_lap_time'),
                    'laps_position_improved': vehicle.get('laps_position_improved'),
                    "fastest_laps_run": vehicle.get("fastest_laps_run"),
                    'passes_made': vehicle.get('passes_made'),
                    "times_passed": vehicle.get("times_passed"),
                    'passing_differential': vehicle.get('passing_differential'),
                    "quality_passes": vehicle.get("quality_passes"),
                    'position_differential_last_10_percent': vehicle.get('position_differential_last_10_percent'),
                })
            self.driver_stats_advanced = pd.DataFrame(driver_stats_advanced)
        else:
            self.driver_stats_advanced = pd.DataFrame()