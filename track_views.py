import requests
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

USERNAME = "vatsalunadkat"
DATA_FILE = "view_data.json"
GRAPH_FILE = "view_graph.svg"

def get_current_views():
    """Fetch current view count from the badge"""
    url = f"https://komarev.com/ghpvc/?username={USERNAME}"
    try:
        response = requests.get(url)
        # The badge is an SVG, parse the count from it
        svg_content = response.text
        # Extract number from SVG text (format varies, look for the count)
        import re
        match = re.search(r'>(\d+)</text>', svg_content)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Error fetching views: {e}")
    return None

def load_data():
    """Load historical data"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"history": []}

def save_data(data):
    """Save historical data"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_daily_views(history):
    """Calculate daily views from cumulative counts"""
    daily_views = []
    for i in range(1, len(history)):
        prev = history[i-1]
        curr = history[i]
        daily = curr['count'] - prev['count']
        daily_views.append({
            'date': curr['date'],
            'views': max(0, daily)  # Ensure non-negative
        })
    return daily_views

def generate_graph(daily_views):
    """Generate SVG graph of last 15 days"""
    if len(daily_views) < 2:
        print("Not enough data to generate graph yet")
        return
    
    # Get last 15 days
    recent = daily_views[-15:] if len(daily_views) >= 15 else daily_views
    
    dates = [datetime.fromisoformat(d['date']) for d in recent]
    views = [d['views'] for d in recent]
    
    # Create figure
    plt.figure(figsize=(12, 4))
    plt.plot(dates, views, marker='o', linewidth=2, markersize=6, 
             color='#2ea44f', markerfacecolor='#2ea44f')
    
    # Formatting
    plt.xlabel('Date', fontsize=10)
    plt.ylabel('Daily Views', fontsize=10)
    plt.title('GitHub Profile Views (Last 15 Days)', fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    plt.xticks(rotation=45)
    
    # Tight layout
    plt.tight_layout()
    
    # Save as SVG
    plt.savefig(GRAPH_FILE, format='svg', bbox_inches='tight')
    print(f"Graph saved to {GRAPH_FILE}")

def main():
    # Get current views
    current_views = get_current_views()
    if current_views is None:
        print("Failed to fetch current views")
        return
    
    print(f"Current views: {current_views}")
    
    # Load existing data
    data = load_data()
    
    # Add new entry
    today = datetime.now().strftime("%Y-%m-%d")
    data['history'].append({
        'date': today,
        'count': current_views,
        'timestamp': datetime.now().isoformat()
    })
    
    save_data(data)
    print(f"Data saved with {len(data['history'])} entries")
    
    # generate graph
    daily_views = calculate_daily_views(data['history'])
    if daily_views:
        generate_graph(daily_views)
    
    # Print
    if daily_views:
        print(f"\nLast 5 days:")
        for entry in daily_views[-5:]:
            print(f"  {entry['date']}: {entry['views']} views")

if __name__ == "__main__":
    main()