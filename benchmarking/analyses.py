import pandas as pd
import matplotlib.pyplot as plt

#'feed_id', 'input_type', 'interval', 'interval_start_s',
#       'interval_end_s', 'duration_s', 'nominal_fps', 'frames_processed',
#       'frames_expected', 'skipped_frames', 'skipped_frame_rate', 'actual_fps',
#       'latency_mean_ms', 'latency_p95_ms', 'ram_mean_mb', 'ram_peak_mb',
#       'cpu_mean_percent', 'cpu_peak_percent'

def perform_analyses():
    df_s = pd.read_parquet("benchmark_server_cassette.parquet")
    df_c = pd.read_parquet("benchmark_client_cassette.parquet")

    df_s = df_s[df_s["interval"] < 60]
    df_c = df_c[df_c["interval"] < 60]

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax2.hist(df_s["skipped_frame_rate"], 5, color="red" , label="Server only", density=True)
    ax2.hist(df_c["skipped_frame_rate"], 30, color="blue", label="Server and Client", density=True)
    ax2.set_xlabel("Proportion of frames skipped per minute")
    ax2.legend()
    ax2.set_title("Skipped frame rate")

    ax1.hist(df_c["latency_mean_ms"], 30, color="blue", label="Server and Client", density=True)
    ax1.hist(df_s["latency_mean_ms"], 30, color="red" , label="Server only", density=True)
    ax1.set_xlabel("End-to-end latency (ms)")
    ax1.set_title("Latency")

    fig.savefig("benchmarking-metrics.png")
    fig.savefig("benchmarking-metrics.pdf")

def summarise_benchmarks():
    import pandas as pd

    files = {
        "Server only": "benchmark_server_cassette.parquet",
        "Server and Client": "benchmark_client_cassette.parquet",
    }

    metrics = {
        "Mean latency (ms)": "latency_mean_ms",
        "P95 latency (ms)": "latency_p95_ms",
        "Frame rate (FPS)": "actual_fps",
        "Skipped-frame rate (%)": "skipped_frame_rate",
        "Mean RAM (MB)": "ram_mean_mb",
        "P95 RAM (MB)": "ram_mean_mb",
        "Peak RAM (MB)": "ram_peak_mb",
        "Mean CPU (%)": "cpu_mean_percent",
        "P95 CPU (%)": "cpu_mean_percent",
        "Peak CPU (%)": "cpu_peak_percent",
    }

    results = {}

    for name, filename in files.items():
        df = pd.read_parquet(filename)

        # Exclude incomplete intervals
        df = df.dropna(subset=["duration_s", "actual_fps"])

        summary = {}

        for label, column in metrics.items():
            values = df[column].dropna()

            if label.startswith("P95"):
                summary[label] = values.quantile(0.95)
            else:
                summary[label] = values.mean()

        # Skipped-frame rate expressed as a percentage
        summary["Skipped-frame rate (%)"] *= 100

        results[name] = summary

    table = pd.DataFrame(results)

    print(table.to_latex(
        float_format="%.2f",
        na_rep="--",
        caption="Comparison of server-side and client-side benchmarking performance.",
        label="tab:benchmark_comparison",
    ))

    return table
if __name__ == "__main__":
    perform_analyses()
    summarise_benchmarks()
