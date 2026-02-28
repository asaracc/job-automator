"""
config.py
Configuration file for LinkedIn search parameters and application filters.
"""

# LinkedIn Filter Codes (Reference for 2026)
# f_WT: 1 (On-site), 2 (Remote), 3 (Hybrid)
# f_E: 1 (Intern), 2 (Entry), 3 (Associate), 4 (Mid-Senior), 5 (Director)
# f_TPR: r604800 (Last 7 days), r86400 (Last 24 hours)

SEARCH_MATRIX = [
    {
        "keywords": "Data Engineer",
        "geoId": 100025096,  # Toronto geoId for more accurate results
        # "f_WT": "2",       # Location
        # "f_E": "4",        # Level
        "f_TPR": "r86400"    # Last X days
    },
    {
        "keywords": "Data Platform",
        "geoId": 100025096,  # Toronto geoId for more accurate results
        # "f_WT": "2",       # Location
        # "f_E": "4",        # Level
        "f_TPR": "r86400"    # Last X days
    },
    {
        "keywords": "SQL Developer",
        "geoId": 100025096,  # Toronto geoId for more accurate results
        # "f_WT": "2",       # Location
        # "f_E": "4",        # Level
        "f_TPR": "r86400"    # Last X days
    },
    {
        "keywords": "Data Engineer",
        "geoId": 101174742,  # Canada geoId for more accurate results
        "f_WT": "2",       # Location
        # "f_E": "4",        # Level
        "f_TPR": "r86400"    # Last X days
    },
    {
        "keywords": "Data Platform",
        "geoId": 101174742,  # Canada geoId for more accurate results
        "f_WT": "2",        # Location
        # "f_E": "4",       # Level
        "f_TPR": "r86400"   # Last X days
    },
    {
        "keywords": "SQL Developer",
        "geoId": 101174742,  # Canada geoId for more accurate results
        "f_WT": "2",        # Location
        # "f_E": "4",       # Level
        "f_TPR": "r86400"   # Last X days
    },
]

# General Settings
MAX_PAGES_PER_SEARCH = 3  # ~75 jobs per combination
COOLDOWN_BETWEEN_SEARCHES = 10  # Seconds to wait between different filter sets