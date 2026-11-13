"""Mede recuperação por documento e latência; não julga factualidade automaticamente."""
import argparse
import json
import os
import statistics
import time
from pathlib import Path
import httpx


def evaluate(client, dataset):
    results = []
    for case in dataset:
        relevant = set(case['relevant_documents'])
        started = time.perf_counter()
        response = client.post('/chat/ask', json={'question': case['question'], 'top_k': 4})
        response.raise_for_status()
        answer = response.json()
        retrieved = {s['name'] for s in answer['sources']}
        hits = len(retrieved & relevant)
        results.append({'question': case['question'], 'answer_id': answer['id'],
                        'precision': hits / len(retrieved) if retrieved else 0,
                        'recall': hits / len(relevant) if relevant else None,
                        'latency_ms': round((time.perf_counter() - started) * 1000),
                        'status': answer['status'], 'retrieved': sorted(retrieved)})
    recalls = [r['recall'] for r in results if r['recall'] is not None]
    return {'cases': results, 'mean_precision': statistics.mean(r['precision'] for r in results),
            'mean_recall': statistics.mean(recalls) if recalls else None,
            'mean_latency_ms': statistics.mean(r['latency_ms'] for r in results)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:8080/doc-rag/api/v1')
    parser.add_argument('--dataset', type=Path, default=Path('examples/evaluation.json'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    dataset = json.loads(args.dataset.read_text())
    if not dataset:
        parser.error('Dataset vazio')
    headers = {'Authorization': 'Bearer ' + os.environ['API_TOKEN']} if os.environ.get('API_TOKEN') else {}
    with httpx.Client(base_url=args.url, headers=headers, timeout=600) as client:
        result = json.dumps(evaluate(client, dataset), ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding='utf-8')
    print(result)
