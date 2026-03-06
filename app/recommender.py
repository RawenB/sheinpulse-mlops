from pathlib import Path
from collections import Counter
import pandas as pd


CUSTOMER_HISTORY_PATH = Path("models/customer_history.parquet")
ARTICLE_CUSTOMERS_PATH = Path("models/article_customers.parquet")
POPULARITY_PATH = Path("models/article_popularity.parquet")
ARTICLES_PATH = Path("data/raw/articles.parquet")


history_df = pd.read_parquet(CUSTOMER_HISTORY_PATH)
article_customers_df = pd.read_parquet(ARTICLE_CUSTOMERS_PATH)
popularity_df = pd.read_parquet(POPULARITY_PATH)
articles_df = pd.read_parquet(ARTICLES_PATH)

customer_history = dict(zip(history_df["customer_id"], history_df["article_id"]))
article_customers = dict(zip(article_customers_df["article_id"], article_customers_df["customer_id"]))
article_popularity = dict(zip(popularity_df["article_id"], popularity_df["purchase_count"]))

article_details = articles_df[
    ["article_id", "prod_name", "product_type_name", "product_group_name"]
].drop_duplicates(subset=["article_id"])

article_details = article_details.set_index("article_id").to_dict(orient="index")


def recommend_for_customer(customer_id: str, top_k: int = 5):
    bought_items = set(customer_history.get(customer_id, []))

    if not bought_items:
        return get_popular_recommendations(set(), top_k)

    similar_customers = set()
    for article_id in bought_items:
        customers = article_customers.get(article_id, [])
        similar_customers.update(customers)

    similar_customers.discard(customer_id)

    candidate_scores = Counter()

    for other_customer in similar_customers:
        other_items = customer_history.get(other_customer, [])
        for article_id in other_items:
            if article_id not in bought_items:
                candidate_scores[article_id] += 1

    if not candidate_scores:
        return get_popular_recommendations(bought_items, top_k)

    ranked_articles = sorted(
        candidate_scores.items(),
        key=lambda x: (x[1], article_popularity.get(x[0], 0)),
        reverse=True
    )

    recommendations = []
    for article_id, _ in ranked_articles:
        details = article_details.get(article_id, {})
        recommendations.append(
            {
                "article_id": int(article_id),
                "prod_name": details.get("prod_name"),
                "product_type_name": details.get("product_type_name"),
                "product_group_name": details.get("product_group_name"),
            }
        )
        if len(recommendations) == top_k:
            break

    if len(recommendations) < top_k:
        existing_ids = {item["article_id"] for item in recommendations}
        fallback = get_popular_recommendations(
            bought_items.union(existing_ids),
            top_k - len(recommendations)
        )
        recommendations.extend(fallback)

    return recommendations


def get_popular_recommendations(excluded_items: set, top_k: int = 5):
    recommendations = []

    for article_id in popularity_df["article_id"]:
        if article_id in excluded_items:
            continue

        details = article_details.get(article_id, {})
        recommendations.append(
            {
                "article_id": int(article_id),
                "prod_name": details.get("prod_name"),
                "product_type_name": details.get("product_type_name"),
                "product_group_name": details.get("product_group_name"),
            }
        )

        if len(recommendations) == top_k:
            break

    return recommendations