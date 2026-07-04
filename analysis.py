import pandas as pd


def books_to_dataframe(books):
    return pd.DataFrame(
        [
            {
                "title": book.title,
                "link": book.link,
                "img_link": book.img_link,
                "price": book.price,
                "stock": book.stock,
                "rating": book.rating,
                "description": book.description,
                "category": book.category,
                "in_stock": book.stock > 0,
            }
            for book in books
        ]
    )


def category_summary(df):
    summary = (
        df.groupby("category")
        .agg(book_count=("title", "count"), avg_price=("price", "mean"), avg_rating=("rating", "mean"))
        .reset_index()
        .sort_values("book_count", ascending=False)
        .reset_index(drop=True)
    )
    return summary


def top_n_categories(summary_df, metric, n=15):
    return summary_df.sort_values(metric, ascending=False).head(n).reset_index(drop=True)


def rating_distribution(df):
    grouped = df.groupby("rating").agg(book_count=("title", "count"), avg_price=("price", "mean"))
    reindexed = grouped.reindex(range(1, 6), fill_value=0)
    reindexed["avg_price"] = reindexed["avg_price"].fillna(0)
    return reindexed.reset_index()


def price_stats(df):
    prices = df["price"]
    return {
        "min": prices.min(),
        "max": prices.max(),
        "mean": prices.mean(),
        "median": prices.median(),
        "std": prices.std(),
        "count": prices.count(),
    }


def price_histogram_bins(df, bins=12):
    counts, bin_edges = pd.cut(df["price"], bins=bins, retbins=True)
    ordered_counts = counts.value_counts(sort=False)
    return list(ordered_counts.values), list(bin_edges)


def stock_summary(df):
    grouped = (
        df["in_stock"]
        .map({True: "In stock", False: "Out of stock"})
        .value_counts()
        .reindex(["In stock", "Out of stock"], fill_value=0)
        .reset_index()
    )
    grouped.columns = ["status", "book_count"]
    return grouped


def export_to_csv(df, path):
    df.to_csv(path, index=False)


def export_to_excel(sheets, path):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
