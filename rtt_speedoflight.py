"""
RTT vs. Speed-of-Light
Networks Assignment — Measurement & Geography
"""

import math, time, os, requests, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import urllib.request

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TARGETS = {
    "Tokyo":        {"url": "http://www.google.co.jp",   "coords": (35.6762,  139.6503), "continent": "Asia"},
    "São Paulo":    {"url": "http://www.google.com.br",  "coords": (-23.5505, -46.6333), "continent": "S. America"},
    "Lagos":        {"url": "http://www.google.com.ng",  "coords": (6.5244,     3.3792), "continent": "Africa"},
    "Frankfurt":    {"url": "http://www.google.de",      "coords": (50.1109,    8.6821), "continent": "Europe"},
    "Sydney":       {"url": "http://www.google.com.au",  "coords": (-33.8688, 151.2093), "continent": "Oceania"},
    "Mumbai":       {"url": "http://www.google.co.in",   "coords": (19.0760,    72.8777), "continent": "Asia"},
    "London":       {"url": "http://www.google.co.uk",   "coords": (51.5074,   -0.1278), "continent": "Europe"},
    "Singapore":    {"url": "http://www.google.com.sg",  "coords": (1.3521,   103.8198), "continent": "Asia"},
}

PROBES           = 15
FIBER_SPEED_KM_S = 200_000
FIGURES_DIR      = "figures"

CONTINENT_COLORS = {
    "Asia":      "#e63946",
    "S. America":"#2a9d8f",
    "Africa":    "#e9c46a",
    "Europe":    "#457b9d",
    "Oceania":   "#a8dadc",
}

# ─────────────────────────────────────────────
# TASK 1 — MEASURE RTTs
# ─────────────────────────────────────────────

def measure_rtt(url: str, probes: int = PROBES) -> dict:
    samples = []
    lost = 0

    for i in range(probes):
        try:
            # Start timer
            start_time = time.perf_counter()
            
            # Request the page
            resp = urllib.request.urlopen(url, timeout=3)
            resp.read(1) # Grab 1 byte to ensure connection is active
            resp.close()
            
            # Stop timer and convert to ms
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            samples.append(duration)
            
        except Exception:
            # If site is unreachable or times out, increment loss
            lost += 1
        
        # Space out requests slightly
        time.sleep(0.2)

    if len(samples) == 0:
        return {"min_ms": None, "mean_ms": None, "median_ms": None,
                "loss_pct": 100.0, "samples": []}

    # Calculate stats using numpy as requested in TODO
    return {
        "min_ms": float(np.min(samples)),
        "mean_ms": float(np.mean(samples)),
        "median_ms": float(np.median(samples)),
        "loss_pct": (lost / probes) * 100,
        "samples": samples
    }


# ─────────────────────────────────────────────
# TASK 2 — HAVERSINE + INEFFICIENCY
# ─────────────────────────────────────────────

def great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in kilometers
    R = 6371.0
    
    # Need everything in radians for math functions
    r_lat1, r_lon1 = math.radians(lat1), math.radians(lon1)
    r_lat2, r_lon2 = math.radians(lat2), math.radians(lon2)
    
    # Differences
    dlat = r_lat2 - r_lat1
    dlon = r_lon2 - r_lon1
    
    # Haversine math
    a = math.sin(dlat/2)**2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_my_location() -> tuple[float, float, str]:
    """Return (lat, lon, city) for this machine's public IP."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5).json()
        lat, lon = map(float, r["loc"].split(","))
        return lat, lon, r.get("city", "Your Location")
    except Exception:
        print("Could not auto-detect location. Defaulting to Boston.")
        return 42.3601, -71.0589, "Boston"


def compute_inefficiency(results: dict, src_lat: float, src_lon: float) -> dict:
    for city in results:
        data = results[city]
        
        # 1. Get distance using city coords
        lat2, lon2 = data["coords"]
        dist = great_circle_km(src_lat, src_lon, lat2, lon2)
        data["distance_km"] = dist
        
        # 2. Theoretical min = (dist / fiber speed) * 2 (round trip) * 1000 (convert to ms)
        theor_min = (dist / FIBER_SPEED_KM_S) * 2 * 1000
        data["theoretical_min_ms"] = theor_min
        
        # 3. Ratio calculation
        if data["median_ms"] is not None:
            ratio = data["median_ms"] / theor_min
            data["inefficiency_ratio"] = ratio
            # 4. Flag high inefficiency if ratio > 3.0
            data["high_inefficiency"] = ratio > 3.0
        else:
            data["inefficiency_ratio"] = None
            data["high_inefficiency"] = False
            
    return results


# ─────────────────────────────────────────────
# TASK 3 — PLOTS
# ─────────────────────────────────────────────

def make_plots(results: dict):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # Filter only cities that actually responded
    reachable = {}
    for city, data in results.items():
        if data.get("median_ms") is not None:
            reachable[city] = data
            
    # Sort cities by how far they are from the source
    sorted_names = sorted(reachable.keys(), key=lambda c: reachable[c]["distance_km"])

    # Figure 1: Bar Chart
    plt.figure(figsize=(11, 6))
    x_indices = np.arange(len(sorted_names))
    
    real_rtt = [reachable[name]["median_ms"] for name in sorted_names]
    ideal_rtt = [reachable[name]["theoretical_min_ms"] for name in sorted_names]
    
    plt.bar(x_indices - 0.2, real_rtt, 0.4, label='Measured Median RTT', color='navy')
    plt.bar(x_indices + 0.2, ideal_rtt, 0.4, label='Theoretical (Fiber Speed)', color='silver')
    
    plt.xticks(x_indices, sorted_names, rotation=30)
    plt.xlabel('Target City')
    plt.ylabel('Time (ms)')
    plt.title('Comparison: Actual Latency vs. Theoretical Physics Limit')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig1_rtt_comparison.png", dpi=120)

    # Figure 2: Scatter Plot
    plt.figure(figsize=(10, 7))
    for name in sorted_names:
        info = reachable[name]
        dot_color = CONTINENT_COLORS.get(info["continent"], "black")
        
        plt.scatter(info["distance_km"], info["median_ms"], c=dot_color, s=100)
        plt.text(info["distance_km"] + 150, info["median_ms"], name, fontsize=9)

    # Draw the dashed theoretical limit line
    farthest = max([reachable[n]["distance_km"] for n in sorted_names])
    x_line = np.linspace(0, farthest, 100)
    y_line = (x_line / FIBER_SPEED_KM_S) * 2 * 1000
    plt.plot(x_line, y_line, color='gray', linestyle='--', label='Theoretical Minimum')

    plt.xlabel('Great-Circle Distance (km)')
    plt.ylabel('Median RTT (ms)')
    plt.title('Network Inefficiency Map')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig2_distance_scatter.png", dpi=120)
    
    print(f"Figures saved to {FIGURES_DIR}/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    src_lat, src_lon, src_city = get_my_location()
    print(f"Your location: {src_city} ({src_lat:.4f}, {src_lon:.4f})\n")

    results = {}
    for city, info in TARGETS.items():
        print(f"Probing {city} ({info['url']}) ...", end=" ", flush=True)
        stats = measure_rtt(info["url"])
        results[city] = {**stats, "coords": info["coords"], "continent": info["continent"]}
        med = stats.get("median_ms")
        print(f"median={med:.1f} ms  loss={stats['loss_pct']:.0f}%" if med else "unreachable")

    results = compute_inefficiency(results, src_lat, src_lon)

    print(f"\n{'City':<14} {'Dist km':>8} {'Median ms':>10} {'Theor. ms':>10} {'Ratio':>7}")
    print("─" * 55)
    for city, d in sorted(results.items(), key=lambda x: x[1].get("distance_km", 0)):
        dist  = d.get("distance_km", 0)
        med   = d.get("median_ms")
        theor = d.get("theoretical_min_ms")
        ratio = d.get("inefficiency_ratio")
        flag  = " ⚠️" if d.get("high_inefficiency") else ""
        print(f"{city:<14} {dist:>8.0f} "
              f"{(f'{med:.1f}' if med else 'N/A'):>10} "
              f"{(f'{theor:.1f}' if theor else 'N/A'):>10} "
              f"{(f'{ratio:.2f}' if ratio else 'N/A'):>7}{flag}")

    make_plots(results)

if __name__ == "__main__":
    main()
