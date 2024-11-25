import pstats

# Load the profiling data
stats = pstats.Stats("latest_tutorial.prof")

# Strip directories for better readability
stats.strip_dirs()

# Sort by cumulative time and print the top 10 results
stats.sort_stats("time").print_stats(100)
