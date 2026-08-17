import argparse
import json
import logging
import os
import statistics
import sys
import time

try:
    import psutil
except ImportError:
    psutil = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_memory_usage_mb():
    """Returns the current process memory usage in MB."""
    if psutil:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    else:
        return 0.0


def benchmark_model(model_path: str, num_runs: int, input_shape: list):
    """
    Benchmarks cold load time, warm latency, p50, p95, and artifact size.
    Supports ONNX and PyTorch formats. Falls back to mock execution for others.
    """
    results = {}

    # 1. Artifact Size
    try:
        size_bytes = os.path.getsize(model_path)
        results["artifact_size_mb"] = round(size_bytes / (1024 * 1024), 3)
    except FileNotFoundError:
        logging.error(f"Model file '{model_path}' not found.")
        return None

    ext = os.path.splitext(model_path)[1].lower()

    # 2. Cold Load Time and Peak Memory
    mem_before = get_memory_usage_mb()
    start_time = time.perf_counter()

    model = None
    if ext == ".onnx":
        try:
            import onnxruntime as ort
            # Attempt to set provider to CPU to standardize benchmark, or allow generic default
            model = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            logging.info("Successfully loaded ONNX model.")
        except ImportError:
            logging.error("onnxruntime is not installed. Cannot benchmark ONNX.")
            return None
        except Exception as e:
            logging.error(f"Failed to load ONNX model: {e}")
            return None
    elif ext in [".pt", ".pth"]:
        try:
            import torch
            # Prefer TorchScript load if possible, fallback to torch.load for weights
            # To actually run, we need a traced model.
            try:
                model = torch.jit.load(model_path)
                model.eval()
            except RuntimeError:
                # Might just be state_dict, which we can't run blindly without model definition
                model = torch.load(model_path)
                if isinstance(model, torch.nn.Module):
                    model.eval()
                else:
                    logging.error("Loaded PyTorch file is not a ScriptModule or complete Module. Cannot benchmark.")
                    return None
            logging.info("Successfully loaded PyTorch model.")
        except ImportError:
            logging.error("torch is not installed. Cannot benchmark PyTorch.")
            return None
        except Exception as e:
            logging.error(f"Failed to load PyTorch model: {e}")
            return None
    else:
        logging.warning(f"Unsupported model extension '{ext}'. Using mock load & execution.")
        time.sleep(0.1)  # Mock load time
        model = "mock"

    load_time = time.perf_counter() - start_time
    mem_after = get_memory_usage_mb()

    results["cold_load_time_ms"] = round(load_time * 1000, 2)
    if mem_after > 0:
        results["peak_memory_mb_approx"] = round(mem_after - mem_before, 2)

    # 3. Warmup
    logging.info("Running warmup iterations...")

    def run_inference():
        if ext == ".onnx" and model is not None:
            import numpy as np
            input_name = model.get_inputs()[0].name
            in_shape = model.get_inputs()[0].shape
            resolved_shape = [s if isinstance(s, int) and s > 0 else 1 for s in in_shape]
            if len(input_shape) > 0 and len(input_shape) == len(resolved_shape):
                resolved_shape = input_shape
            dummy_input = np.random.randn(*resolved_shape).astype(np.float32)
            model.run(None, {input_name: dummy_input})

        elif ext in [".pt", ".pth"] and model is not None:
            import torch
            if not input_shape:
                input_shape_ = (1, 3, 224, 224)  # fallback default
            else:
                input_shape_ = tuple(input_shape)
            dummy_input = torch.randn(*input_shape_)
            with torch.no_grad():
                model(dummy_input)
        else:
            time.sleep(0.01)  # Mock inference

    # Run warmup
    for _ in range(5):
        try:
            run_inference()
        except Exception as e:
            logging.error(f"Error during warmup inference: {e}")
            return None

    # 4. Latency Measurement
    logging.info(f"Running {num_runs} benchmark iterations...")
    latencies = []
    for i in range(num_runs):
        t0 = time.perf_counter()
        try:
            run_inference()
        except Exception as e:
            logging.error(f"Error during benchmark inference: {e}")
            break
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    if latencies:
        results["warm_latency_mean_ms"] = round(statistics.mean(latencies), 2)
        results["p50_latency_ms"] = round(statistics.median(latencies), 2)
        # Using quantiles requires python 3.8+
        if hasattr(statistics, "quantiles") and len(latencies) >= 2:
            results["p95_latency_ms"] = round(statistics.quantiles(latencies, n=100)[94], 2)
        else:
            latencies_sorted = sorted(latencies)
            idx = int(0.95 * len(latencies_sorted))
            results["p95_latency_ms"] = round(latencies_sorted[idx] if idx < len(latencies_sorted) else latencies_sorted[-1], 2)
        results["min_latency_ms"] = round(min(latencies), 2)
        results["max_latency_ms"] = round(max(latencies), 2)
        results["iterations"] = len(latencies)

    return results


def main():
    parser = argparse.ArgumentParser(description="Real Model Evaluation Benchmark Tool")
    parser.add_argument("--model", type=str, required=True, help="Path to the model file (.onnx, .pt)")
    parser.add_argument("--runs", type=int, default=100, help="Number of iterations to measure latency")
    parser.add_argument("--input-shape", type=int, nargs="+", default=[1, 3, 224, 224], 
                        help="Input shape for PyTorch models (e.g. 1 3 224 224)")
    parser.add_argument("--output", type=str, help="Path to save the JSON results")
    
    args = parser.parse_args()

    logging.info(f"Starting benchmark for {args.model}")
    results = benchmark_model(args.model, args.runs, args.input_shape)

    if not results:
        logging.error("Benchmark failed.")
        sys.exit(1)

    print("\n--- Benchmark Results ---")
    print(json.dumps(results, indent=2))
    print("-------------------------\n")

    if args.output:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
