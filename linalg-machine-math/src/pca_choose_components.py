from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def build_sample_data(
    observation_count: int = 300,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Create a reproducible dataset with correlated features."""
    rng = np.random.default_rng(random_seed)

    authentication_activity = rng.normal(
        loc=0.0,
        scale=1.0,
        size=observation_count,
    )

    session_activity = rng.normal(
        loc=0.0,
        scale=1.0,
        size=observation_count,
    )

    device_novelty = rng.normal(
        loc=0.0,
        scale=1.0,
        size=observation_count,
    )

    return pd.DataFrame(
        {
            "failed_logins": (
                12
                + 4.0 * authentication_activity
                + rng.normal(
                    0.0,
                    0.8,
                    observation_count,
                )
            ),
            "account_lockouts": (
                2
                + 1.3 * authentication_activity
                + rng.normal(
                    0.0,
                    0.25,
                    observation_count,
                )
            ),
            "authentication_alerts": (
                5
                + 2.8 * authentication_activity
                + 0.6 * device_novelty
                + rng.normal(
                    0.0,
                    0.6,
                    observation_count,
                )
            ),
            "bytes_transferred_mb": (
                500
                + 140.0 * session_activity
                + rng.normal(
                    0.0,
                    25.0,
                    observation_count,
                )
            ),
            "session_duration_min": (
                30
                + 8.5 * session_activity
                + rng.normal(
                    0.0,
                    1.8,
                    observation_count,
                )
            ),
            "new_device_score": (
                50
                + 14.0 * device_novelty
                + rng.normal(
                    0.0,
                    2.5,
                    observation_count,
                )
            ),
        }
    )


def main() -> None:
    variance_threshold = 0.90

    data = build_sample_data()

    # PCA is sensitive to feature scale, so standardize first.
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(data)

    # Fit PCA with every possible component so cumulative
    # explained variance can be examined.
    full_pca = PCA()
    full_pca.fit(standardized_data)

    explained_variance_ratio = (
        full_pca.explained_variance_ratio_
    )

    cumulative_explained_variance = np.cumsum(
        explained_variance_ratio
    )

    # Find the first component count whose cumulative
    # explained variance reaches the target threshold.
    component_count = int(
        np.searchsorted(
            cumulative_explained_variance,
            variance_threshold,
        )
        + 1
    )

    component_names = [
        f"PC{index}"
        for index in range(
            1,
            len(explained_variance_ratio) + 1,
        )
    ]

    variance_table = pd.DataFrame(
        {
            "component": component_names,
            "explained_variance_ratio": (
                explained_variance_ratio
            ),
            "cumulative_explained_variance": (
                cumulative_explained_variance
            ),
        }
    )

    # Fit PCA again using only the selected number
    # of components.
    selected_pca = PCA(
        n_components=component_count,
    )

    reduced_data = selected_pca.fit_transform(
        standardized_data
    )

    print(
        "Math Day 83: Choosing the Number "
        "of PCA Components"
    )
    print("=" * 58)

    print(
        f"\nOriginal feature count: "
        f"{data.shape[1]}"
    )

    print(
        f"Observation count: "
        f"{data.shape[0]}"
    )

    print(
        "Target cumulative explained variance: "
        f"{variance_threshold:.0%}"
    )

    print("\nExplained variance by component:")

    for row in variance_table.itertuples(
        index=False
    ):
        print(
            f"{row.component}: "
            f"individual="
            f"{row.explained_variance_ratio:.2%}, "
            f"cumulative="
            f"{row.cumulative_explained_variance:.2%}"
        )

    print(
        "\nMinimum components required to meet "
        f"the {variance_threshold:.0%} threshold: "
        f"{component_count}"
    )

    print(
        "Variance retained by selected components: "
        f"{selected_pca.explained_variance_ratio_.sum():.2%}"
    )

    print(
        "Reduced data shape: "
        f"{reduced_data.shape}"
    )

    reduced_table = pd.DataFrame(
        reduced_data,
        columns=[
            f"PC{index}"
            for index in range(
                1,
                component_count + 1,
            )
        ],
    )

    print("\nFirst five transformed observations:")

    print(
        reduced_table.head().round(3)
    )


if __name__ == "__main__":
    main()