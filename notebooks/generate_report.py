import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

RAW_DIR = Path("data/raw")
OUT_DIR = Path("reports")
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUT_DIR / "Fashion_EDA_Report_v3.pdf"

MAX_TX = 500_000


def skewness(x):
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    return x.skew()


def iqr_outliers(x):
    x = x.dropna()
    if len(x) == 0:
        return 0, 0.0
    q1 = x.quantile(0.25)
    q3 = x.quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    mask = (x < low) | (x > high)
    return int(mask.sum()), float(mask.mean() * 100)


def save_fig(path):
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    styles = getSampleStyleSheet()

    articles = pd.read_parquet(RAW_DIR / "articles.parquet")
    customers = pd.read_parquet(RAW_DIR / "customers.parquet")
    transactions = pd.read_parquet(RAW_DIR / "transactions.parquet")

    if len(transactions) > MAX_TX:
        transactions = transactions.sample(MAX_TX, random_state=42)

    transactions["t_dat"] = pd.to_datetime(transactions["t_dat"])
    transactions["year"] = transactions["t_dat"].dt.year
    transactions["week"] = transactions["t_dat"].dt.isocalendar().week.astype(int)

    weekly_demand = (
        transactions.groupby(["article_id", "year", "week"])
        .size()
        .reset_index(name="demand")
    )

    # ---------- TABLES ----------
    overview = [
        ["Total Articles", f"{len(articles):,}"],
        ["Total Customers", f"{len(customers):,}"],
        [f"Total Transactions (sample)", f"{len(transactions):,}"],
        ["Weekly Demand Records", f"{len(weekly_demand):,}"],
        ["Article columns", str(articles.shape[1])],
        ["Customer columns", str(customers.shape[1])],
        ["Transaction columns", str(transactions.shape[1])],
    ]

    miss_articles = articles.isnull().sum()
    miss_customers = customers.isnull().sum()
    miss_transactions = transactions.isnull().sum()

    missing_rows = []
    for col, cnt in miss_articles.items():
        if cnt > 0:
            missing_rows.append([f"articles.{col}", int(cnt), round(cnt / len(articles) * 100, 2)])
    for col, cnt in miss_customers.items():
        if cnt > 0:
            missing_rows.append([f"customers.{col}", int(cnt), round(cnt / len(customers) * 100, 2)])
    for col, cnt in miss_transactions.items():
        if cnt > 0:
            missing_rows.append([f"transactions.{col}", int(cnt), round(cnt / len(transactions) * 100, 2)])

    if not missing_rows:
        missing_rows = [["-", 0, 0.0]]

    # numeric stats
    num_rows = []
    numeric_series = {
        "transactions.price": transactions["price"],
        "weekly_demand.demand": weekly_demand["demand"],
    }
    if "age" in customers.columns:
        numeric_series["customers.age"] = customers["age"]

    for name, s in numeric_series.items():
        s2 = s.dropna()
        num_rows.append([
            name,
            round(s2.mean(), 5),
            round(s2.std(), 5),
            round(s2.min(), 5),
            round(s2.max(), 5),
            round(skewness(s2), 5),
        ])

    # outliers
    out_rows = []
    for name, s in numeric_series.items():
        cnt, pct = iqr_outliers(s)
        out_rows.append([name, cnt, round(pct, 2)])

    # ---------- CHARTS ----------
    plt.figure()
    transactions["price"].hist(bins=50)
    plt.title("Price Distribution")
    plt.xlabel("price")
    plt.ylabel("count")
    save_fig(FIG_DIR / "price_dist.png")

    plt.figure()
    np.log1p(transactions["price"]).hist(bins=50)
    plt.title("Log(1+Price) Distribution")
    plt.xlabel("log1p(price)")
    plt.ylabel("count")
    save_fig(FIG_DIR / "price_log.png")

    plt.figure()
    weekly_demand["demand"].hist(bins=50)
    plt.title("Weekly Demand Distribution")
    plt.xlabel("demand")
    plt.ylabel("count")
    save_fig(FIG_DIR / "demand_dist.png")

    plt.figure()
    np.log1p(weekly_demand["demand"]).hist(bins=50)
    plt.title("Log(1+Demand) Distribution")
    plt.xlabel("log1p(demand)")
    plt.ylabel("count")
    save_fig(FIG_DIR / "demand_log.png")

    plt.figure()
    customers.isnull().sum().sort_values(ascending=False).plot(kind="bar")
    plt.title("Missing Values - Customers")
    plt.xlabel("feature")
    plt.ylabel("missing count")
    save_fig(FIG_DIR / "missing_customers.png")

    plt.figure()
    transactions["sales_channel_id"].value_counts().sort_index().plot(kind="bar")
    plt.title("Sales Channel Distribution")
    plt.xlabel("sales_channel_id")
    plt.ylabel("count")
    save_fig(FIG_DIR / "sales_channel.png")

    if "index_name" in articles.columns:
        top_cat = articles["index_name"].value_counts().head(10)
        plt.figure()
        top_cat.plot(kind="bar")
        plt.title("Top 10 Product Categories (articles.index_name)")
        plt.xlabel("category")
        plt.ylabel("count")
        save_fig(FIG_DIR / "top_categories.png")

    if "age" in customers.columns:
        plt.figure()
        customers["age"].dropna().hist(bins=50)
        plt.title("Customer Age Distribution")
        plt.xlabel("age")
        plt.ylabel("count")
        save_fig(FIG_DIR / "age_dist.png")

    # Demand by sales channel
    ch_demand = transactions.groupby("sales_channel_id").size().reset_index(name="tx_count")
    plt.figure()
    plt.bar(ch_demand["sales_channel_id"].astype(str), ch_demand["tx_count"])
    plt.title("Transactions Count by Sales Channel")
    plt.xlabel("sales_channel_id")
    plt.ylabel("transactions")
    save_fig(FIG_DIR / "tx_by_channel.png")

    # ---------- PDF ----------
    doc = SimpleDocTemplate(str(OUTPUT_FILE))
    elements = []

    elements.append(Paragraph("Fashion Retail Dataset - Exploratory Data Analysis Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("1. Executive Summary", styles["Heading2"]))
    elements.append(Paragraph(
        "This report analyzes product, customer, and transaction data to evaluate data quality and understand patterns "
        "useful for demand prediction modeling. The analysis covers dataset overview, missing values, statistics, "
        "distributions, outliers, and demand-related insights.",
        styles["BodyText"]
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("2. Dataset Overview", styles["Heading2"]))
    t = Table(overview)
    t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("3. Missing Values Analysis", styles["Heading2"]))
    miss_table = Table([["Column", "Missing Count", "Missing %"]] + missing_rows)
    miss_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))
    elements.append(miss_table)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Image(str(FIG_DIR / "missing_customers.png"), width=6*inch, height=3*inch))

    elements.append(PageBreak())

    elements.append(Paragraph("4. Numeric Features Statistics", styles["Heading2"]))
    stats_table = Table([["Feature", "Mean", "Std", "Min", "Max", "Skewness"]] + num_rows)
    stats_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("5. Distributions", styles["Heading2"]))
    elements.append(Image(str(FIG_DIR / "price_dist.png"), width=6*inch, height=3*inch))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Image(str(FIG_DIR / "price_log.png"), width=6*inch, height=3*inch))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Image(str(FIG_DIR / "demand_dist.png"), width=6*inch, height=3*inch))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Image(str(FIG_DIR / "demand_log.png"), width=6*inch, height=3*inch))

    elements.append(PageBreak())

    elements.append(Paragraph("6. Outlier Detection (IQR Method)", styles["Heading2"]))
    out_table = Table([["Feature", "Outlier Count", "Outlier %"]] + out_rows)
    out_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))
    elements.append(out_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("7. Categorical Distributions", styles["Heading2"]))
    elements.append(Image(str(FIG_DIR / "sales_channel.png"), width=6*inch, height=3*inch))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Image(str(FIG_DIR / "tx_by_channel.png"), width=6*inch, height=3*inch))
    if (FIG_DIR / "top_categories.png").exists():
        elements.append(Spacer(1, 0.15 * inch))
        elements.append(Image(str(FIG_DIR / "top_categories.png"), width=6*inch, height=3*inch))
    if (FIG_DIR / "age_dist.png").exists():
        elements.append(Spacer(1, 0.15 * inch))
        elements.append(Image(str(FIG_DIR / "age_dist.png"), width=6*inch, height=3*inch))

    doc.build(elements)
    print("Report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
