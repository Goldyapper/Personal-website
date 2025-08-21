from flask import Blueprint, render_template, request
from collections import defaultdict, OrderedDict
from datetime import datetime
import requests, re
from station_info import station_ids, line_colors

tube_bp = Blueprint("tube", __name__)

def extract_platform_number(name):
    match = re.search(r'\d+', name)
    return int(match.group()) if match else float('inf')

@tube_bp.route("/tube")
def tube():
    station_name = request.args.get('station', 'Acton Town')
    stop_point_ids = station_ids.get(station_name, '940GZZLUACT')
    if isinstance(stop_point_ids, str):
        stop_point_ids = [stop_point_ids]

    arrivals = []
    for i, stop_point_id in enumerate(stop_point_ids):
        try:
            arrival_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}/Arrivals"
            response = requests.get(arrival_url)
            response.raise_for_status()
            arrivals += response.json()

            if i == 0:
                station_name_url = f"https://api.tfl.gov.uk/StopPoint/{stop_point_id}"
                station_name_response = requests.get(station_name_url)
                station_name_response.raise_for_status()
                station_name = station_name_response.json()
                station_name = station_name.get("commonName", station_name)
                station_name = station_name.replace("Underground Station", "").strip()

        except Exception as e:
            print(f"Error: {e}")
            station_name = "Unknown Station"
            platforms = {}
            fetched_time = "Unknown Time"

        arrivals.sort(key=lambda x: x['timeToStation'])
        fetched_time = datetime.now().strftime('%H:%M:%S')

        platforms = defaultdict(list)
        seen = set()

        for arrival in arrivals:
            platform = arrival.get("platformName")
            if not platform:
                continue
            destination = arrival.get("destinationName", "Check front of train").replace("Underground Station", "").strip()
            if destination == station_name:
                destination = "Terminating here"

            line = arrival.get("lineName", "").lower()
            if not line:
                continue

            rounded_minutes = arrival.get("timeToStation", 0) // 30
            key = (destination.lower(), line, rounded_minutes)
            if key in seen:
                continue
            seen.add(key)

            direction_match = re.search(r'(Northbound|Southbound|Eastbound|Westbound)', platform, re.IGNORECASE)
            direction = direction_match.group(1) if direction_match else "Unknown"
            number_match = re.search(r'Platform\s+(\w+)', platform)
            platform_number = number_match.group(1) if number_match else platform.strip()

            if direction and direction != "Unknown":
                platform_label = f"Platform {platform_number} - {direction} -"
            else:
                platform_label = f"Platform {platform_number} -"

            platforms[platform_label].append({
                "destination": destination,
                "minutes": arrival.get("timeToStation",0)//60,
                "line": line
            })

        sorted_platforms = sorted(platforms.items(), key=lambda item: (
            0 if re.match(r'Platform \d+', item[0]) else 1,
            int(re.search(r'Platform (\d+)', item[0]).group(1)) if re.match(r'Platform \d+', item[0]) else item[0]
        ))
        platforms = OrderedDict(sorted_platforms)

    return render_template("tube.html", platforms=platforms, station_name=station_name,fetched_time=fetched_time, station_list=list(station_ids.keys()),line_colors=line_colors)
