import numpy as np
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


X = np.array(
    [
        [1, 200, 10],
        [2, 250, 12],
        [8, 9000, 45],
        [9, 10000, 48],
        [5, 5000, 28],
    ],
    dtype=float,
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

X_pca = pca_pipeline.fit_transform(X)

X_reconstructed = pca_pipeline.inverse_transform(
    X_pca
)

scaler = pca_pipeline.named_steps["scaler"]
pca = pca_pipeline.named_steps["pca"]

standardized_reconstruction = scaler.transform(
    X_reconstructed
)

standardized_original = scaler.transform(X)

standardized_mse = np.mean(
    (
        standardized_original
        - standardized_reconstruction
    )
    ** 2
)

print("Original shape:")
print(X.shape)

print("\nPCA shape:")
print(X_pca.shape)

print("\nComponents retained:")
print(pca.n_components_)

print("\nFeature means:")
print(scaler.mean_)

print("\nFeature standard deviations:")
print(scaler.scale_)

print("\nExplained variance ratio:")
print(pca.explained_variance_ratio_)

print("\nTotal explained variance:")
print(pca.explained_variance_ratio_.sum())

print("\nPCA component directions:")
print(pca.components_)

print("\nPCA scores:")
print(X_pca)

print("\nReconstructed data:")
print(X_reconstructed)

print("\nStandardized reconstruction MSE:")
print(standardized_mse)