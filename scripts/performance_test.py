"""Run a 20-request latency check. Health is the no-cost default; chat is opt-in."""
import argparse
import asyncio
import os
import statistics
import time
import httpx


async def run(base_url: str, target: str, count: int, token: str):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    latencies = []
    statuses = []
    rate_limit_events = 0
    payload = {"question": "Give one practical tip for contacting a campus support office.", "history": []}
    async with httpx.AsyncClient(timeout=60.0) as client:
        for index in range(count):
            start = time.perf_counter()
            if target == "chat":
                response = await client.post(f"{base_url}/chat", headers=headers, json=payload)
            else:
                response = await client.get(f"{base_url}/health")
            latencies.append((time.perf_counter() - start) * 1000)
            statuses.append(response.status_code)
            if response.status_code == 429:
                rate_limit_events += 1
            print(f"Request {index + 1:02d}: HTTP {response.status_code} | {latencies[-1]:.2f} ms")

    successful = sum(200 <= status < 400 for status in statuses)
    failed = count - successful
    print("\nPERFORMANCE SUMMARY (measured on this run)")
    print(f"Total requests:          {count}")
    print(f"Successful requests:     {successful}")
    print(f"Failed requests:         {failed}")
    print(f"Success rate:            {successful / count * 100:.2f}%")
    print(f"Error rate:              {failed / count * 100:.2f}%")
    print(f"Average latency:         {statistics.mean(latencies):.2f} ms")
    print(f"Maximum latency:         {max(latencies):.2f} ms")
    print(f"Rate-limit events:       {rate_limit_events}")
    print("\nNote: --target chat sends real LLM requests and may incur cost. The health default does not call the LLM.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("CAMPUSASSIST_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--target", choices=["health", "chat"], default="health")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--token", default=os.getenv("CAMPUSASSIST_API_KEY", ""))
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be at least 1")
    asyncio.run(run(args.base_url.rstrip("/"), args.target, args.count, args.token))


if __name__ == "__main__":
    main()
