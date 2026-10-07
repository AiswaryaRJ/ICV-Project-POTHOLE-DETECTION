import math

def simulate_gps_point(start_lat=37.7749, start_lon=-122.4194, elapsed_seconds=0.0, speed_kmh=30.0):
    """
    Simulates a linear GPS trajectory moving North-East at a constant speed.
    """
    speed_ms = speed_kmh / 3.6
    distance_meters = speed_ms * elapsed_seconds
    
    # 1 degree lat approx 111,000 meters
    lat_offset = (distance_meters * 0.7071) / 111000.0
    # 1 degree lon approx 111,000 * cos(lat) meters
    lon_offset = (distance_meters * 0.7071) / (111000.0 * math.cos(math.radians(start_lat)))
    
    return start_lat + lat_offset, start_lon + lon_offset

def get_gps_for_frame(frame_idx, fps, start_lat=37.7749, start_lon=-122.4194, speed_kmh=30.0, custom_gps_df=None):
    """
    Returns (lat, lon, is_simulated) for a given frame index and FPS.
    If custom_gps_df (DataFrame with 'timestamp', 'lat', 'lon') is provided, it attempts to use it.
    """
    elapsed_seconds = frame_idx / fps if fps > 0 else 0.0
    
    if custom_gps_df is not None and not custom_gps_df.empty:
        # Check if columns match
        if {'timestamp', 'lat', 'lon'}.issubset(custom_gps_df.columns):
            # Find closest timestamp
            idx = (custom_gps_df['timestamp'] - elapsed_seconds).abs().idxmin()
            lat = float(custom_gps_df.loc[idx, 'lat'])
            lon = float(custom_gps_df.loc[idx, 'lon'])
            return lat, lon, False
            
    lat, lon = simulate_gps_point(start_lat, start_lon, elapsed_seconds, speed_kmh)
    return lat, lon, True
