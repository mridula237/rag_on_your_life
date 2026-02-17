import time
from statistics import mean

from app.query.rag import retrieve_documents


# ---------------------------------
# Test Queries (replace with real ones later)
# ---------------------------------
TEST_QUERIES = [
    "What is the main topic of the document?",
    "What are the key findings?",
    "Summarize the introduction section.",
    "What conclusions were drawn?",
]


def evaluate():
    print("🔎 Running Retrieval Evaluation...\n")

    total_latency = []
    all_confidences = []
    empty_results = 0

    for query in TEST_QUERIES:
        start = time.time()

        docs_with_scores = retrieve_documents(
            query=query,
            source=None,
            cross_document=True,
        )

        latency = time.time() - start
        total_latency.append(latency)

        if not docs_with_scores:
            empty_results += 1
            print(f"❌ No results for: {query}")
            continue

        scores = [score for (_, score) in docs_with_scores]

        avg_distance = sum(scores) / len(scores)
        confidence = 1 / (1 + avg_distance)
        all_confidences.append(confidence)

        print(f"Query: {query}")
        print(f"  Retrieved: {len(docs_with_scores)} docs")
        print(f"  Avg Distance: {round(avg_distance, 4)}")
        print(f"  Confidence: {round(confidence, 4)}")
        print(f"  Latency: {round(latency, 3)} sec\n")

    print("------ SUMMARY ------")
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print(f"Empty Results: {empty_results}")
    print(f"Avg Retrieval Latency: {round(mean(total_latency), 4)} sec")

    if all_confidences:
        print(f"Avg Confidence: {round(mean(all_confidences), 4)}")


if __name__ == "__main__":
    evaluate()
