import requests
import json
import os
from datetime import datetime, timedelta

USERNAME = "vatsalunadkat"
DATA_FILE = "view_data.json"
GRAPH_FILE = "view_graph.svg"

def get_current_views():
    """Fetch current view count from the badge"""
    url = f"https://komarev.com/ghpvc/?username={USERNAME}"
    try:
        response = requests.get(url)
        svg_content = response.text
        print(f"Fetched SVG content (first 500 chars): {svg_content[:500]}")
        
        # The count appears in text elements after "Profile views"
        # Look for numbers with optional commas in text elements
        import re
        
        # Find all text elements with numbers (including commas)
        pattern = r'<text[^>]*>([0-9,]+)</text>'
        matches = re.findall(pattern, svg_content)
        
        print(f"Found text elements: {matches}")
        
        # The view count is the number that appears (not "Profile views")
        for match in matches:
            # Remove commas and try to convert to int
            cleaned = match.replace(',', '')
            if cleaned.isdigit():
                count = int(cleaned)
                print(f"Found count: {count}")
                return count
        
        print("Could not find view count in SVG")
    except Exception as e:
        print(f"Error fetching views: {e}")
        import traceback
        traceback.print_exc()
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
            'views': max(0, daily)
        })
    return daily_views

def generate_interactive_svg(daily_views):
    """Generate modern interactive SVG graph with dark theme"""
    if len(daily_views) < 2:
        print("Not enough data to generate graph yet")
        return
    
    # Get last 15 days
    recent = daily_views[-15:] if len(daily_views) >= 15 else daily_views
    
    dates = [datetime.fromisoformat(d['date']) for d in recent]
    views = [d['views'] for d in recent]
    
    # SVG dimensions and padding
    width = 800
    height = 300
    padding_left = 60
    padding_right = 40
    padding_top = 40
    padding_bottom = 60
    
    chart_width = width - padding_left - padding_right
    chart_height = height - padding_top - padding_bottom
    
    # Calculate scales
    max_views = max(views) if views else 1
    min_views = 0  # Always start from 0
    view_range = max_views - min_views if max_views != min_views else 1
    
    # Add 10% padding to top
    max_views_padded = max_views + (view_range * 0.1)
    
    def scale_x(index):
        return padding_left + (index / (len(dates) - 1)) * chart_width if len(dates) > 1 else padding_left + chart_width / 2
    
    def scale_y(value):
        return padding_top + chart_height - ((value - min_views) / (max_views_padded - min_views)) * chart_height
    
    # GitHub dark theme colors
    bg_color = "#0d1117"
    grid_color = "#21262d"
    text_color = "#8b949e"
    line_color = "#58a6ff"
    gradient_start = "#58a6ff"
    gradient_end = "#1f6feb"
    point_color = "#58a6ff"
    point_hover = "#79c0ff"
    
    # Start SVG
    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:{gradient_start};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{gradient_end};stop-opacity:1" />
        </linearGradient>
        <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{gradient_start};stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:{gradient_start};stop-opacity:0.05" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <style>
            .tooltip {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
                font-size: 12px;
                fill: #ffffff;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            }}
            .tooltip-bg {{
                fill: #1f6feb;
                rx: 6;
                filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
            }}
            .data-point {{
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .data-point:hover {{
                r: 6;
            }}
            .data-point:hover + .tooltip {{
                opacity: 1;
            }}
            .grid-line {{
                stroke: {grid_color};
                stroke-width: 1;
                stroke-dasharray: 4, 4;
            }}
            .axis-text {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
                font-size: 11px;
                fill: {text_color};
            }}
            .title-text {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                fill: #c9d1d9;
            }}
            .line-path {{
                fill: none;
                stroke: url(#lineGradient);
                stroke-width: 2.5;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}
            .area-path {{
                fill: url(#areaGradient);
            }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="{bg_color}" rx="8"/>
    
    <!-- Title -->
    <text x="{width/2}" y="25" text-anchor="middle" class="title-text">GitHub Profile Views</text>
    
'''
    
    # Grid lines (horizontal)
    grid_lines = 4
    for i in range(grid_lines + 1):
        y = padding_top + (chart_height / grid_lines) * i
        value = max_views_padded - ((max_views_padded - min_views) / grid_lines) * i
        svg += f'    <line x1="{padding_left}" y1="{y}" x2="{width - padding_right}" y2="{y}" class="grid-line"/>\n'
        svg += f'    <text x="{padding_left - 10}" y="{y + 4}" text-anchor="end" class="axis-text">{int(value)}</text>\n'
    
    # Area under line
    area_points = f"M {padding_left} {padding_top + chart_height} "
    for i, value in enumerate(views):
        x = scale_x(i)
        y = scale_y(value)
        area_points += f"L {x} {y} "
    area_points += f"L {scale_x(len(views) - 1)} {padding_top + chart_height} Z"
    svg += f'    <path d="{area_points}" class="area-path"/>\n'
    
    # Line path
    line_points = " ".join([f"{'M' if i == 0 else 'L'} {scale_x(i)} {scale_y(value)}" for i, value in enumerate(views)])
    svg += f'    <path d="{line_points}" class="line-path"/>\n'
    
    # Data points with tooltips
    for i, (date, value) in enumerate(zip(dates, views)):
        x = scale_x(i)
        y = scale_y(value)
        date_str = date.strftime("%b %d")
        
        # Tooltip group
        tooltip_text = f"{date_str}: {value} views"
        tooltip_width = len(tooltip_text) * 7 + 20
        tooltip_x = x - tooltip_width / 2
        tooltip_y = y - 40
        
        # Adjust tooltip position if it goes off screen
        if tooltip_x < 5:
            tooltip_x = 5
        if tooltip_x + tooltip_width > width - 5:
            tooltip_x = width - tooltip_width - 5
        
        svg += f'''    <g class="data-point-group">
        <circle cx="{x}" cy="{y}" r="4" fill="{point_color}" class="data-point" filter="url(#glow)"/>
        <g class="tooltip">
            <rect x="{tooltip_x}" y="{tooltip_y}" width="{tooltip_width}" height="28" class="tooltip-bg"/>
            <text x="{tooltip_x + tooltip_width/2}" y="{tooltip_y + 18}" text-anchor="middle">{tooltip_text}</text>
        </g>
    </g>
'''
    
    # X-axis labels
    step = max(1, len(dates) // 8)
    for i in range(0, len(dates), step):
        x = scale_x(i)
        date_str = dates[i].strftime("%m/%d")
        svg += f'    <text x="{x}" y="{height - padding_bottom + 20}" text-anchor="middle" class="axis-text">{date_str}</text>\n'
    
    # Y-axis label
    svg += f'    <text x="20" y="{height/2}" text-anchor="middle" transform="rotate(-90 20 {height/2})" class="axis-text">Daily Views</text>\n'
    
    svg += '</svg>'
    
    # Save SVG
    with open(GRAPH_FILE, 'w') as f:
        f.write(svg)
    print(f"Interactive graph saved to {GRAPH_FILE}")

def main():
    # Get current views
    current_views = get_current_views()
    if current_views is None:
        print("Failed to fetch current views")
        return
    
    print(f"Current views: {current_views}")
    
    # Load existing data
    data = load_data()
    
    # Add today's entry
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if we already have today's entry
    if data['history'] and data['history'][-1]['date'] == today:
        print(f"Updating today's entry")
        data['history'][-1] = {
            'date': today,
            'count': current_views,
            'timestamp': datetime.now().isoformat()
        }
    else:
        data['history'].append({
            'date': today,
            'count': current_views,
            'timestamp': datetime.now().isoformat()
        })
    
    # Save data
    save_data(data)
    print(f"Data saved with {len(data['history'])} entries")
    
    # Calculate and generate graph
    daily_views = calculate_daily_views(data['history'])
    if daily_views:
        generate_interactive_svg(daily_views)
    
    # Print summary
    if daily_views:
        print(f"\nLast 5 days:")
        for entry in daily_views[-5:]:
            print(f"  {entry['date']}: {entry['views']} views")

if __name__ == "__main__":
    main()