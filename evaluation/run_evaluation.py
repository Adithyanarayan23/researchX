import argparse
import asyncio
import json
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.evaluator import ResearchXEvaluator


def main():
    parser = argparse.ArgumentParser(description="ResearchX Multi-Agent System Evaluation Benchmark CLI")
    parser.add_argument(
        "--dataset",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "datasets", "benchmark_20.json"),
        help="Path to evaluation benchmark JSON dataset"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of questions to evaluate (default 5, up to 20 for full benchmark)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_results.json",
        help="Path to save output JSON metrics"
    )

    args = parser.parse_args()

    print("=====================================================================")
    print("           ResearchX Multi-Agent Intelligence Evaluation CLI         ")
    print("=====================================================================")
    print(f"Dataset: {args.dataset}")
    print(f"Sample limit: {args.limit}")

    evaluator = ResearchXEvaluator(args.dataset)
    results = asyncio.run(evaluator.run_benchmark(limit=args.limit))

    print("\n------------------------- AGGREGATE METRICS -------------------------")
    for metric, score in results["aggregate_metrics"].items():
        bar_len = int(score * 30)
        bar = "#" * bar_len + "-" * (30 - bar_len)
        pct = round(score * 100, 1)
        metric_name = metric.replace("avg_", "").replace("_", " ").title()
        print(f"{metric_name:<28} | [{bar}] | {pct:>5.1f}%")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("---------------------------------------------------------------------")
    print(f"Evaluation complete. Full report exported to: {args.output}\n")


if __name__ == "__main__":
    main()
