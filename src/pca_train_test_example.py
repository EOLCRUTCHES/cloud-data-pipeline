import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


X = np.array(
    [
        [1, 200, 10, 0],
        [2, 250, 12, 0],
        [3, 400, 15, 0],
        [4, 900, 18, 0],
        [5, 2500, 25, 0],
        [6, 4200, 30, 1],
        [7, 6000, 35, 0],
        [8, 7500, 40, 1],
        [9, 9000, 45, 1],
        [10, 10000, 48, 1],
        [11, 12000, 52, 1],
        [12, 15000, 60, 1],
    ],
    dtype=float,
)

y = np.array(
    [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1]
)

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )
)

pca_pipeline = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        (
            "pca",
            PCA(
                n_components=0.95,
                svd_solver="full",
            ),
        ),
    ]
)

X_train_pca = pca_pipeline.fit_transform(
    X_train
)

X_test_pca = pca_pipeline.transform(
    X_test
)

scaler = pca_pipeline.named_steps["scaler"]
pca = pca_pipeline.named_steps["pca"]

print("Original training shape:")
print(X_train.shape)

print("\nOriginal test shape:")
print(X_test.shape)

print("\nPCA training shape:")
print(X_train_pca.shape)

print("\nPCA test shape:")
print(X_test_pca.shape)

print("\nTraining feature means learned by scaler:")
print(scaler.mean_)

print("\nComponents retained:")
print(pca.n_components_)

print("\nExplained variance ratio:")
print(pca.explained_variance_ratio_)

print("\nTotal retained variance:")
print(pca.explained_variance_ratio_.sum())