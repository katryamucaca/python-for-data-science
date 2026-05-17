"""
МКР з Python for Data Science — кейс «Метеослужба»
"""

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# ====================================================================
# Прізвище, ім'я, по батькові: Шиліна Катерина Валеріївна
# Група:                       КІ-33
# Дата виконання:              17.05.2026
# ====================================================================

DB_USER = "student"
DB_PASSWORD = "student"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "meteo"

PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def load_observations(retries=12, delay=2.5):
    url = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(url)

    for attempt in range(1, retries + 1):
        try:
            df = pd.read_sql("SELECT * FROM observations", engine)
            print(f"Підключено з {attempt}-ї спроби")
            return df

        except OperationalError:
            if attempt == retries:
                raise

            print(f"MySQL ще запускається... {attempt}/{retries}")
            time.sleep(delay)


# =========================================================
# БЛОК 1
# =========================================================

def block_1_numpy(df_raw):
    section("БЛОК 1. NumPy")

    temperature = df_raw["temperature_c"].to_numpy(dtype=float)
    humidity = df_raw["humidity_pct"].to_numpy(dtype=float)
    wind = df_raw["wind_speed_ms"].to_numpy(dtype=float)

    # 1
    apparent = temperature - (100 - humidity) / 5

    print(
        f"1) T_app: len={len(apparent)}, "
        f"min={np.nanmin(apparent):.2f}, "
        f"max={np.nanmax(apparent):.2f}"
    )

    # 2
    temperature_clean = np.where(
        (temperature > 60) | (temperature < -60),
        np.nan,
        temperature
    )

    wind_clean = np.where(
        wind > 100,
        np.nan,
        wind
    )

    temp_outliers = np.sum(
        (temperature > 60) | (temperature < -60)
    )

    wind_outliers = np.sum(wind > 100)

    print(f"2) Викидів температури замінено: {temp_outliers}")
    print(f"   Викидів вітру замінено: {wind_outliers}")

    # 3
    valid_mask = ~np.isnan(temperature_clean)

    mean_t = np.nansum(temperature_clean) / np.sum(valid_mask)

    median_t = np.nanmedian(temperature_clean)

    variance = (
        np.nansum((temperature_clean - mean_t) ** 2)
        / np.sum(valid_mask)
    )

    std_t = np.sqrt(variance)

    print(
        f"3) mean={mean_t:.3f} "
        f"median={median_t:.3f} "
        f"std={std_t:.3f}"
    )

    # 4
    n_frost = np.sum(temperature_clean < 0)
    n_hot = np.sum(temperature_clean > 30)

    print(f"4) морозних: {n_frost}")
    print(f"   жарких: {n_hot}")

    # 5
    max_idx = np.nanargmax(temperature_clean)
    min_idx = np.nanargmin(temperature_clean)

    print("\n5) Максимальна температура:")
    print(
        f"obs_id={df_raw.iloc[max_idx]['obs_id']}, "
        f"datetime={df_raw.iloc[max_idx]['datetime']}, "
        f"T={temperature_clean[max_idx]:.2f}"
    )

    print("\n   Мінімальна температура:")
    print(
        f"obs_id={df_raw.iloc[min_idx]['obs_id']}, "
        f"datetime={df_raw.iloc[min_idx]['datetime']}, "
        f"T={temperature_clean[min_idx]:.2f}"
    )


# =========================================================
# БЛОК 2
# =========================================================

def block_2_cleaning(df_raw):
    section("БЛОК 2. Pandas — очищення")

    rows_before = len(df_raw)

    df = df_raw.copy()

    print("\nINFO:")
    print(df.info())

    print("\nDESCRIBE:")
    print(df.describe())

    # datetime
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")

    # duplicates
    before_dups = len(df)

    df = df.drop_duplicates()

    n_dups = before_dups - len(df)

    print(f"\nВидалено дублів: {n_dups}")

    # humidity fill
    before_nan = df["humidity_pct"].isna().sum()

    df["month"] = df.index.month

    df["humidity_pct"] = (
        df.groupby(["city", "month"])["humidity_pct"]
        .transform(lambda s: s.fillna(s.median()))
    )

    after_nan = df["humidity_pct"].isna().sum()

    n_filled = before_nan - after_nan

    print(f"Заповнено humidity NaN: {n_filled}")

    # outliers
    before_outliers = len(df)

    temp_mask = (
        (df["temperature_c"] >= -60)
        & (df["temperature_c"] <= 60)
    )

    wind_mask = (
        df["wind_speed_ms"].isna()
        | (
            (df["wind_speed_ms"] >= 0)
            & (df["wind_speed_ms"] <= 60)
        )
    )

    df = df[temp_mask & wind_mask]

    n_outliers = before_outliers - len(df)

    print(f"Видалено викидів: {n_outliers}")

    print(f"\nЗвіт очищення:")
    print(f"{rows_before} -> {len(df)} рядків")

    return df


# =========================================================
# БЛОК 3
# =========================================================

def block_3_analytics(df):
    section("БЛОК 3. Аналітика")

    # 1
    by_city_temp = (
        df.groupby("city")["temperature_c"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\n1) Середня температура:")
    print(by_city_temp.round(2))

    print(f"\nНайтепліше місто: {by_city_temp.idxmax()}")
    print(f"Найхолодніше місто: {by_city_temp.idxmin()}")

    # 2
    by_city_precip = (
        df.groupby("city")["precipitation_mm"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\n2) Сумарні опади:")
    print(by_city_precip.round(1))

    print(f"\nНайвологіше місто: {by_city_precip.idxmax()}")

    # 3
    monthly_mean = (
        df["temperature_c"]
        .resample("ME")
        .mean()
    )

    print("\n3) Місячна середня температура:")
    print(monthly_mean.round(2))

    # 4
    pivot = pd.pivot_table(
        df,
        values="temperature_c",
        index="city",
        columns="month",
        aggfunc="mean"
    )

    print("\n4) Pivot table:")
    print(pivot.round(1))

    # 5
    daily_precip = (
        df.groupby(
            [
                "city",
                pd.Grouper(freq="D")
            ]
        )["precipitation_mm"]
        .sum()
    )

    rainy_days = (
        daily_precip[daily_precip > 5]
        .groupby("city")
        .count()
    )

    print("\n5) Днів з опадами >5 мм:")
    print(rainy_days)

    # 6 anomaly
    monthly_city = (
        df["temperature_c"]
        .resample("ME")
        .mean()
    )

    anomaly_df = pd.DataFrame({
        "temp": monthly_city
    })

    anomaly_df["year"] = anomaly_df.index.year
    anomaly_df["month"] = anomaly_df.index.month

    month_norm = (
        anomaly_df.groupby("month")["temp"]
        .mean()
    )

    anomaly_df["norm"] = (
        anomaly_df["month"]
        .map(month_norm)
    )

    anomaly_df["deviation"] = (
        anomaly_df["temp"]
        - anomaly_df["norm"]
    )

    max_dev_idx = anomaly_df["deviation"].abs().idxmax()

    anomaly_month = max_dev_idx.strftime("%Y-%m")

    anomaly_dev = anomaly_df.loc[
        max_dev_idx,
        "deviation"
    ]

    print(
        f"\n6) Аномальний місяць: "
        f"{anomaly_month}"
    )

    print(
        f"Відхилення: {anomaly_dev:+.2f}°C"
    )

    if anomaly_dev > 0:
        print("Це хвиля спеки")
    else:
        print("Це хвиля холоду")

    return {
        "by_city_temp": by_city_temp,
        "by_city_precip": by_city_precip,
        "monthly_mean": monthly_mean,
        "pivot": pivot,
    }


# =========================================================
# БЛОК 4
# =========================================================

def block_4_plots(df, analytics):
    section("БЛОК 4. Графіки")

    # 1 LINE
    fig, ax = plt.subplots(figsize=(12, 5))

    cities = df["city"].unique()[:3]

    for city in cities:
        city_monthly = (
            df[df["city"] == city]["temperature_c"]
            .resample("ME")
            .mean()
        )

        ax.plot(
            city_monthly.index,
            city_monthly.values,
            label=city
        )

    ax.set_title("Місячна динаміка температур")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Температура °C")
    ax.legend()

    fig.savefig(
        PLOTS_DIR / "01_monthly_temperature_lines.png",
        dpi=120,
        bbox_inches="tight"
    )

    plt.close(fig)

    # 2 BAR
    fig, ax = plt.subplots(figsize=(8, 5))

    analytics["by_city_precip"].plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Сумарні опади по містах")
    ax.set_xlabel("Місто")
    ax.set_ylabel("Опади (мм)")

    fig.savefig(
        PLOTS_DIR / "02_precipitation_by_city.png",
        dpi=120,
        bbox_inches="tight"
    )

    plt.close(fig)

    # 3 HIST
    fig, ax = plt.subplots(figsize=(9, 5))

    temperatures = df["temperature_c"].dropna()

    mean_t = temperatures.mean()
    median_t = temperatures.median()

    ax.hist(
        temperatures,
        bins=30
    )

    ax.axvline(
        mean_t,
        linestyle="--",
        label=f"Mean {mean_t:.2f}"
    )

    ax.axvline(
        median_t,
        linestyle="-.",
        label=f"Median {median_t:.2f}"
    )

    ax.set_title("Розподіл температур")
    ax.set_xlabel("Температура °C")
    ax.set_ylabel("Частота")
    ax.legend()

    fig.savefig(
        PLOTS_DIR / "03_temperature_histogram.png",
        dpi=120,
        bbox_inches="tight"
    )

    plt.close(fig)

    # 4 HEATMAP
    fig, ax = plt.subplots(figsize=(11, 5))

    pivot = analytics["pivot"]

    im = ax.imshow(
        pivot,
        aspect="auto"
    )

    ax.set_title("Heatmap середніх температур")

    ax.set_xlabel("Місяць")
    ax.set_ylabel("Місто")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    fig.colorbar(im)

    fig.savefig(
        PLOTS_DIR / "04_city_month_heatmap.png",
        dpi=120,
        bbox_inches="tight"
    )

    plt.close(fig)

    print("4 графіки збережено у папку plots/")


# =========================================================

def main():
    df_raw = load_observations()

    print(f"Завантажено дані: {df_raw.shape}")

    block_1_numpy(df_raw)

    df_clean = block_2_cleaning(df_raw)

    analytics = block_3_analytics(df_clean)

    block_4_plots(df_clean, analytics)


if __name__ == "__main__":
    main()


"""
ВИСНОВКИ

У результаті аналізу метеорологічних даних було досліджено
кліматичні особливості п’яти міст України. Найвищу середню
температуру показав Київ (12.69°C), а найнижчу — Харків
(8.11°C). Це може пояснюватися особливостями регіонального
клімату та різницею у географічному положенні міст.

Аналіз температур підтвердив чітко виражену сезонність:
найвищі температури спостерігались у літні місяці,
а найнижчі — взимку. Найбільш вологим містом виявився Львів,
де зафіксовано найбільшу суму опадів (733.6 мм) та найбільшу
кількість дощових днів.

Під час очищення даних було видалено дублікати,
оброблено пропущені значення та прибрано фізично
неможливі викиди температури і швидкості вітру.
Це дозволило отримати коректні результати аналізу.

Аномальним місяцем став березень 2024 року,
де відхилення температури від норми склало +4.44°C.
Це свідчить про аномальну хвилю потепління.
Отримані результати можуть бути корисними для
планування енергоспоживання, транспорту та оцінки
кліматичних ризиків у різних регіонах України.
"""