import csv
import json
import uuid
from datetime import datetime
from collections import defaultdict

def convert_csv_to_cubedesk_by_day(csv_file_path, output_file_path):
    # Grouping structure: { "YYYY-MM-DD": [list_of_rows] }
    daily_groups = defaultdict(list)
    
    # 1. Read and group solves by date
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # Extract only the date part (YYYY-MM-DD)
            date_str = row['Date'].split(' ')[0]
            daily_groups[date_str].append(row)

    sessions = []
    solves = []

    # 2. Process each date as a unique session
    for date_key, rows in daily_groups.items():
        session_id = str(uuid.uuid4())
        
        # Create session object for the day
        sessions.append({
            "id": session_id,
            "name": f"Solves from {date_key}",
            "created_at": f"{date_key}T00:00:00.000Z",
            "order": 0
        })

        for row in rows:
            # Parse Time (MM:SS.SSS -> float seconds)
            time_str = row['Time (MM:SS.SSS)']
            minutes, seconds = time_str.split(':')
            total_seconds = round(int(minutes) * 60 + float(seconds), 3)

            # Handle Timestamps
            dt_obj = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M')
            ended_at = int(dt_obj.timestamp() * 1000)
            started_at = ended_at - int(total_seconds * 1000)

            # Map Data Fields
            solves.append({
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "scramble": row['Scrambler'],
                "time": total_seconds,
                "raw_time": total_seconds,
                "cube_type": "333" if row['Category'] == "3x3x3" else row['Category'],
                "dnf": row['DNF (yes or no)'].lower() == 'yes',
                "plus_two": row['Penalty +2 (yes or no)'].lower() == 'yes',
                "started_at": started_at,
                "ended_at": ended_at,
                "from_timer": True,
                "inspection_time": 0,
                "is_smart_cube": False,
                "smart_put_down_time": 0
            })

    # 3. Final Export
    output_data = {
        "sessions": sessions,
        "solves": solves
    }

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

# Execution
convert_csv_to_cubedesk_by_day('cube_timer_csv.csv', 'cubedesk_grouped.txt')
print("Conversion complete! Solves grouped by unique dates.")
