# Linear Algebra and Machine Learning Math
## Math Day 1-5
### Key Lessons
- Mean = average
- Median = middle value
- Mode = most common value
- Range = spread
- Averages can hide important information
### Most Important Insight
The average is often the beginning of the analysis, not the end.

## Math Day 6-10
### Key Lessons
- Standard deviation measures consistency.
- Variance is the foundation of standard deviation.
- Outliers can distort averages.
- Many phenomena follow a bell curve.
- Z-scores measure how unusual something is.

### Most Important Insight
The average tells me what is typical.
The standard deviation tells me whether typical is stable.

## Math Day 11-15
### Key Lessons
- Correlation measures relationships.
- Correlation does not prove causation.
- Scatterplots reveal patterns.
- Trends can be positive or negative.
- Regression is prediction from data.

### Most Important Insight
Seeing a relationship is easy.
Proving a cause is hard.

## Math Day 16-20
### Key Lessons
- Regression is prediction from data.
- A population is the full group being studied.
- A sample is the smaller group measured to estimate the population.
- Sampling bias happens when the sample does not fairly represent the population.
- Representative samples make conclusions more trustworthy.
- Confidence intervals show a likely range for the true value.
- Margin of error shows how far an estimate may be from the true value.

### Most Important Insight
A prediction or estimate is only as trustworthy as the data behind it.

### Plain-English Summary
Regression helps estimate an unknown value from known data.
Sampling determines whether the estimate is credible.
Confidence intervals and margin of error explain how precise or uncertain the estimate is.

### Career Connection
In data science, security metrics, surveys, risk scoring, and AI model evaluation, the result is only useful if the sample is valid and the uncertainty is understood.

## Math Day 21-25
### Key Lessons
- Probability measures uncertainty.
- Independent events do not affect each other.
- Dependent events do affect each other.
- Conditional probability incorporates new information.
- Bayes explains how beliefs should change when evidence appears.

### Most Important Insight
Good analysts do not cling to conclusions.
They update conclusions as evidence changes.

## Math Day 26-31
### Key Lessons
- False positives create noise.
- False negatives create risk.
- Precision measures alert quality.
- Recall measures detection coverage.
- Precision and recall usually trade off.
- Features are inputs.
- Labels are outputs.
- Training data teaches.
- Test data evaluates.
- Ground truth is reality.

### Most Important Insight
Every detection system must balance:
1. Missing real threats.
2. Wasting time on false alarms.

## Math Day 32-42
### Key Lessons
- Variables are things that can change.
- Observations are individual rows/examples.
- Features are inputs.
- Labels are outputs.
- Training data teaches the model.
- Test data evaluates the model.
- Classification predicts categories.
- Regression predicts numbers.
- Clustering finds groups.
- Recommendation systems suggest likely matches.
- Feature engineering creates better inputs from raw data.

### Most Important Insight
Machine learning is not magic.
It is pattern detection using examples, inputs, outputs, and evaluation.

## Math Day 43 - Overfitting
### Key Lesson
Overfitting happens when a model performs well on training data but poorly on new data because it memorized examples instead of learning the general pattern.

### Plain-English Definition
The model studied the practice test instead of learning the subject.

### Why It Matters
A model that looks accurate during training may fail in real-world use if it overfits.

### Career Connection
In AI security and governance, strong validation is necessary because impressive demo performance does not prove real-world reliability.

## Math Day 44 - Underfitting
### Key Lesson
Underfitting happens when a model is too simple to capture the real pattern in the data.

### Plain-English Definition
The model did not learn enough.

### Comparison
- Overfitting: memorized the training examples.
- Underfitting: failed to learn the real pattern.

### Why It Matters
An underfit model performs poorly because it is too weak, too simple, or missing useful features.

### Career Connection
In AI security and governance, model failures may come from weak features, shallow rules, poor training, or oversimplified detection logic.

## Math Day 45 - Validation Data
### Key Lesson
Validation data is separate data used while building a model to check whether it is learning useful patterns.

### Plain-English Definition
Training data teaches the model. Validation data helps tune the model. Test data is the final exam.

### Three Data Buckets
- Training data: used to learn
- Validation data: used to tune
- Test data: used to evaluate final performance

### Why It Matters
Validation helps detect overfitting and underfitting before final testing.

### Career Connection
In AI security and governance, validation data helps prove that a model is not just memorizing examples or performing well only in a demo.

## Math Day 46 - Cross-Validation
### Key Lesson
Cross-validation checks whether a model performs consistently across multiple splits of the data.

### Plain-English Definition
Cross-validation is like giving the model several practice quizzes instead of trusting one.

### Why It Matters
A single validation split may be lucky or unlucky. Cross-validation reduces the chance that model performance is being misread because of one unusual split.

### Basic Idea
In k-fold cross-validation, the data is split into k parts. The model trains and validates multiple times, rotating which part is used for validation.

### Career Connection
In AI security and governance, cross-validation helps determine whether a model is actually reliable or just performing well on one convenient slice of data.

## Math Day 47 - Confusion Matrix
### Key Lesson
A confusion matrix compares model predictions against actual outcomes.

### Four Buckets
- True Positive: model flagged the threat correctly.
- False Positive: model flagged something safe as a threat.
- True Negative: model correctly ignored something safe.
- False Negative: model missed a real threat.

### Why It Matters
A confusion matrix shows what kind of mistakes a classification model is making.

### Career Connection
In AI security and governance, confusion matrices help evaluate detection tools, fraud models, phishing classifiers, anomaly systems, and risk-scoring models.

They reveal whether a model is creating noise, missing real threats, or performing reliably.

## Math Day 48 - ROC Curve Intuition

### Key Lesson

An ROC curve shows how a classification model performs as the decision threshold changes.

### Plain-English Definition

An ROC curve shows the tradeoff between catching more real positives and creating more false alarms.

### Key Measures

- True Positive Rate: how many real positives were caught.
- False Positive Rate: how many safe items were wrongly flagged.

### Why It Matters

Changing a model threshold changes the balance between missed threats and false alarms.

### Career Connection

In AI security and governance, ROC curves help evaluate whether a detection model remains useful across different sensitivity settings.

## Math Day 49 - AUC

### Key Lesson

AUC summarizes how well a classification model separates positives from negatives across thresholds.

### Plain-English Definition

AUC measures how well the model ranks real positives above real negatives.

### ROC vs AUC

- ROC curve: shows the threshold tradeoff.
- AUC: summarizes the curve into one score.

### Useful Interpretation

- 1.0 = perfect separation
- 0.8-0.9 = strong
- 0.7 = fair
- 0.5 = random guessing

### Why It Matters

AUC helps evaluate whether a model has useful separation power, but it does not replace confusion matrices, threshold analysis, or business risk judgment.

### Career Connection

In AI security and governance, AUC is a common model-performance metric, but leaders must understand what it does and does not prove.

## Math Day 50 - Thresholds and Tradeoffs
### Key Lesson
A threshold is the cutoff score where a model turns a probability or risk score into a decision.

### Plain-English Definition
The model gives a score. The threshold decides what action to take.

### Threshold Tradeoff
- High threshold: fewer false positives, more missed threats.
- Low threshold: more threats caught, more false positives.

### Why It Matters
The best threshold depends on the cost of different mistakes.

### Career Connection
In AI security and governance, threshold selection is a risk decision, not just a technical setting. Leaders need to understand what kind of error the organization is choosing to tolerate.

## Math Day 51 - Decision Trees 
### Key Lesson 
A decision tree is a model that makes predictions by asking a sequence of branching questions. 
### Plain-English Definition 
A decision tree is a learned flowchart. 

### Why It Matters 
Decision trees are useful because their decisions can often be traced and explained. 

### Strength 
They are easier to understand than many machine learning models. 

### Risk 
They can overfit if the tree becomes too detailed and memorizes the training data. 

### Career Connection 
In AI security and governance, decision trees help explain how model decisions are made, but they still require validation, testing, and review for overfitting.

## Math Day 52 - Random Forests
### Key Lesson
A random forest combines many decision trees to make a more stable prediction.

### Plain-English Definition
A random forest is a committee of decision trees.

### Why It Matters
One decision tree can overfit. A random forest reduces that risk by combining predictions from many trees.

### Strengths
- Often performs better than a single decision tree.
- Reduces overfitting.
- Works well with tabular data.
- Can provide feature-importance insight.

### Risks
Random forests can still fail if the data, labels, features, or validation process are weak.

### Career Connection
In AI security and governance, random forests are useful because they connect model performance, explainability, feature importance, and validation concerns.

## Math Day 53 - Ensembles
### Key Lesson
An ensemble combines multiple machine learning models to produce one final answer.

### Plain-English Definition
An ensemble is a team of models.

### Why It Matters
Different models make different mistakes. Combining them can improve stability and performance.

### Common Ensemble Methods
- Voting
- Averaging
- Stacking

### Strengths
- Can improve accuracy.
- Can reduce overfitting.
- Can perform better on messy real-world data.
- Can combine different types of signals.

### Risks
- Added complexity.
- Reduced explainability.
- Harder auditability.
- Possible hidden bias.
- Harder governance.

### Career Connection
In AI security and governance, ensembles raise an important tradeoff: better performance may come at the cost of weaker explainability.

## Math Day 54 - Explainability

### Key Lesson

Explainability means being able to understand why a model produced a result.

### Plain-English Definition

An explainable model gives humans a usable reason trail for its output.

### Why It Matters

Explainability supports trust, debugging, auditability, fairness review, incident response, and governance.

### Example

A suspicious-login model should not only return a risk score. It should also identify the major factors behind the score, such as unusual location, new device, impossible travel, or abnormal access time.

### Risk

An explanation may be incomplete or misleading if it is only a plausible story rather than a faithful description of the model’s decision process.

### Career Connection

In AI security and governance, explainability helps determine whether a model’s output can be trusted, challenged, audited, and defended.

## Math Day 55 - Interpretability

### Key Lesson

Interpretability means a human can understand the model's internal logic.

### Explainability vs Interpretability

Explainability asks whether the system can explain a specific output.

Interpretability asks whether the model itself is understandable.

### Examples

More interpretable models include decision trees, linear regression, rule-based systems, and simple scoring models.

Less interpretable models include deep neural networks, large ensembles, recommender systems, and large language models.

### Why It Matters

Interpretability supports auditability, debugging, validation, trust, fairness review, and governance.

### Career Connection

In AI security and governance, interpretability helps determine whether a model can be inspected, defended, challenged, and trusted in high-risk workflows.

## Math Day 56 - Neural Network Intuition

### Key Lesson

A neural network is a layered machine learning model that learns patterns by adjusting internal weights.

### Plain-English Definition

A neural network takes inputs, passes them through layers, and produces an output based on learned patterns.

### Basic Structure

- Input layer
- Hidden layer or layers
- Output layer

### Why It Matters

Neural networks can learn complex relationships that simpler models may miss.

### Governance Risk

Neural networks can be harder to interpret because their decisions may depend on many internal weights and layered interactions.

### Career Connection

In AI security and governance, neural networks matter because they power many modern AI systems, including large language models, but require strong controls around data, validation, explainability, monitoring, and human oversight.

## Math Day 57 - Hidden Layers

### Key Lesson

Hidden layers are internal layers in a neural network that transform inputs into learned patterns before the model produces an output.

### Plain-English Definition

A hidden layer sits between the input layer and the output layer.

### Why It Matters

Hidden layers allow neural networks to learn complex combinations of signals instead of relying on simple one-step rules.

### Example

In a phishing model, hidden layers may learn combinations like urgent language plus unknown sender, suspicious link plus new domain, or attachment plus unusual send time.

### Governance Risk

Hidden layers make neural networks powerful but harder to interpret, because humans may not easily understand exactly what internal patterns the model learned.

### Career Connection

In AI security and governance, hidden layers matter because they help explain why neural networks can be effective, but also why they require strong testing, monitoring, evidence, and human oversight.

## Math Day 58 - Weights

### Key Lesson

Weights are learned values that control how strongly inputs influence a model's output.

### Plain-English Definition

A weight is an importance setting inside the model.

### Why It Matters

Training a neural network means adjusting weights so the model makes better predictions.

### Example

In a login-risk model, unusual country, new device, privileged access, and impossible travel may all receive different weights depending on how strongly they predict risk.

### Governance Risk

A model may rely heavily on signals that are biased, unstable, fragile, or easy for attackers to manipulate.

### Career Connection

In AI security and governance, weights matter because they shape model behavior, influence trust, and can create hidden failure modes.

## Math Day 59 - Biases

### Key Lesson

Biases are learned adjustment values that shift a model's baseline output.

### Plain-English Definition

A bias is a baseline adjustment inside the model.

### Weights vs Biases

Weights determine how strongly input signals influence the model.

Biases shift the model's starting point or decision tendency.

### Why It Matters

Biases help the model fit patterns that cannot be captured by input weights alone.

### Important Distinction

A mathematical bias term is a normal part of many models.

Unfair or distorted model behavior is a governance problem and is different from the technical bias term.

### Career Connection

In AI security and governance, biases matter because they affect a model's default posture: too trusting, too suspicious, or poorly aligned to the risk of the environment.

## Math Day 60 - Why Deep Learning Works

### Key Lesson

Deep learning works because multiple neural network layers can learn increasingly complex representations of data.

### Plain-English Definition

Deep learning is machine learning using neural networks with multiple hidden layers.

### Why It Works

Deep learning models improve by repeatedly comparing predictions to correct answers and adjusting weights and biases to reduce error.

### Why Layers Matter

Earlier layers may learn simple patterns. Later layers combine those into more complex patterns.

### Connection to Linear Algebra

Deep learning relies heavily on vectors, matrices, matrix operations, distance, similarity, embeddings, and optimization.

### Governance Risk

Deep learning models can be powerful but difficult to inspect, explain, monitor, and secure.

### Career Connection

In AI security and governance, deep learning matters because modern AI systems depend on it, but trustworthy deployment requires validation, monitoring, explainability, evidence, and human oversight.

## Math Day 61 - Scalars

### Key Lesson

A scalar is a single numerical value.

### Plain-English Definition

A scalar is just one number.

### Examples

- Risk score: 0.87
- Confidence score: 0.91
- Login count: 5
- Threshold: 0.80
- Learning rate: 0.001

### Why It Matters

Scalars are the simplest building blocks in linear algebra. Vectors are made from multiple scalar values, and matrices are made from rows and columns of scalar values.

### Career Connection

In AI security and governance, scalar values appear as risk scores, thresholds, probabilities, weights, biases, loss values, and confidence scores. A number is only useful if we understand what it means and how it should be used.

## Math Day 62 - Vectors

### Key Lesson

A vector is an ordered list of numbers.

### Plain-English Definition

A vector is a numerical profile made from multiple scalar values.

### Examples

Scalar:

- `0.87`

Vector:

- `[0.87, 1.00, 0.25, 0.66]`

### Why Order Matters

Each position in a vector has meaning. If the order changes, the meaning changes.

Example:

- Position 1 = new device
- Position 2 = unusual country
- Position 3 = failed attempts
- Position 4 = privileged resource

### Career Connection

Machine learning systems usually process vectors. Login events, documents, users, images, and security findings can all be represented numerically as vectors.

### Governance Question

What does each position in the vector mean, and who decided that representation?

## Math Day 63 - Matrices

### Key Lesson

A matrix is a rectangular table of numbers arranged in rows and columns.

### Plain-English Definition

A matrix is a dataset where each row is an observation and each column is a feature.

### Examples

- One health measurement is a scalar.
- One day of health measurements is a vector.
- Many days of health measurements form a matrix.

### Shape

Matrix shape is written as:

`rows × columns`

Example:

`3 × 5`

This means 3 observations and 5 features.

### Career Connection

Machine learning datasets are often matrices. Security events, cloud findings, user behavior, health logs, and model features can all be represented as rows and columns.

### Governance Question

What does each row and column mean, and who decided that this is the right representation?

## Math Day 64 - Matrix Shape and Indexing

### Key Lesson

Matrix  shape describes the number of rows and columns. Indexing describes where a specific value lives inside the matrix.

### Shape

Matrix shape is written as:

`rows × columns`

Example:

`3 × 5`

This means 3 observations and 5 features.

### Indexing

Humans usually count from 1.

Python counts from 0.

Human:

`row 2, column 3`

Python:

`matrix[1][2]`

### Practical Rule

For most basic machine learning datasets:

- rows = examples or observations
- columns = features or measurements

### Career Connection

Many data science and AI errors are shape errors. The model may expect observations as rows and features as columns, but the data may be structured incorrectly.

### Governance Question

What does each row represent, what does each column represent, and are we sure the model is reading the data the way we think it is?

## Math Day 65 - Matrix Transpose

### Key Lesson

A transpose flips a matrix so that rows become columns, and columns become rows.

### Notation

`Aᵀ`

This means “A transpose.”

### Shape Change

If:

`A = 3 × 5`

Then:

`Aᵀ = 5 × 3`

### Excel Connection

Transpose in Excel is the same basic idea as transpose in linear algebra.

### Shape Error Connection

A transpose is a valid operation, but an accidental transpose can create a shape or orientation error.

### Practical Rule

For most basic machine learning datasets:

- rows = observations
- columns = features

If that orientation gets flipped unintentionally, the model may interpret the data incorrectly.

### Governance Question

Was the matrix intentionally transposed, and is the model reading rows and columns the way we think it is?

## Math Day 66 - Matrix Addition

### Key Lesson

Matrix addition combines two matrices by adding values in matching positions.

### Shape Rule

Two matrices can be added only when they have the same shape.

Example:

`3 × 5 + 3 × 5 = valid`

`3 × 5 + 5 × 3 = not valid`

### Practical Meaning

Matrix addition works when both matrices represent the same structure.

Examples:

- baseline + adjustment
- actuals + correction
- risk score + risk modifier
- forecast + scenario impact

### Governance Question

Do both matrices have the same shape, same row meaning, same column meaning, and compatible units?

### Warning

Same shape does not always mean same meaning.

## Math Day 67 - Scalar Multiplication

### Key Lesson

Scalar multiplication means multiplying every value in a vector or matrix by one number.

### Shape Rule

Scalar multiplication does not change matrix shape.

If:

`A = 3 × 5`

Then:

`2A = 3 × 5`

### Practical Meaning

Scalar multiplication is used for:

- scaling values
- weighting features
- adjusting risk scores
- normalizing data
- changing units
- amplifying or reducing signals

### Career Connection

In AI security and analytics, scalar multiplication often appears as feature weighting or risk adjustment. The math is simple, but the judgment behind the multiplier matters.

### Governance Question

Who chose the multiplier, and what evidence supports scaling the values that way?

## Math Day 68 - Dot Product

### Key Lesson

A dot product multiplies matching positions in two vectors, then adds the results.

### Shape Rule

The two vectors must have the same length.

### Result

A dot product returns one scalar.

### Machine Learning Connection

A basic model score can be represented as:

`features · weights = score`

This means each feature is multiplied by a weight, and the results are added together.

### Career Connection

Dot products appear in model scoring, similarity search, embeddings, recommendations, and risk scoring.

### Governance Question

Who chose the weights, and does the resulting score actually represent what we claim it represents?

## Math Day 69 - Matrix-Vector Multiplication

### Key Lesson

Matrix-vector multiplication runs one dot product per row of the matrix.

### Shape Rule

If:

`A = m × n`

and:

`x = n × 1`

then:

`Ax = m × 1`

### Plain-English Meaning

A feature matrix multiplied by a weight vector produces one score per row.

### Machine Learning Connection

A common model pattern is:

`feature matrix × weight vector = prediction scores`

or:

`Xw = ŷ`

### Career Connection

Matrix-vector multiplication appears in risk scoring, prediction, linear models, embeddings, neural networks, and security analytics.

### Governance Question

Who chose the weights, and does the score actually represent the risk or outcome we claim it represents?

## Math Day 70 - Matrix-Matrix Multiplication

### Key Lesson

Matrix-matrix multiplication runs row-column dot products across two matrices.

### Shape Rule

If:

`A = m × n`

and:

`B = n × p`

then:

`AB = m × p`

The inner dimensions must match. The outer dimensions become the result.

### Plain-English Meaning

A matrix of observations multiplied by a matrix of weights can produce multiple outputs for every observation.

### Machine Learning Connection

A common pattern is:

`XW = Y`

where:

- `X` = input feature matrix
- `W` = weight matrix
- `Y` = output matrix

### Python

`A @ B` performs matrix multiplication in NumPy.

`A * B` performs element-by-element multiplication.

They are not the same thing.

### Governance Question

What assumptions are hidden inside the weight matrix?

## Math Day 71 - The Identity Matrix

### Key Lesson

The identity matrix is the matrix version of the number 1. Multiplying a matrix by a correctly sized identity matrix leaves the original matrix unchanged.

### Structure

An identity matrix has:

- 1s on the main diagonal
- 0s everywhere else

Example:

`[[1, 0], [0, 1]]`

### Shape Rule

Identity matrices are square: `n × n`.

The size must match the multiplication side where it is used.

### Python

`np.eye(n)` creates an `n × n` identity matrix.

### Career Connection

The identity matrix is the baseline for understanding matrix transformations. It represents “no change,” which makes it useful when comparing transformations, inverses, projections, and model behavior.

### Governance Question

Is the operation preserving the original feature meaning, or transforming it in a way that needs explanation?

## Math Day 72 - Inverse Matrices

### Key Lesson

An inverse matrix reverses the effect of another matrix when that reversal is possible.

### Core Idea

If:

`A × A⁻¹ = I`

then:

- `A` is the original matrix
- `A⁻¹` is the inverse matrix
- `I` is the identity matrix

### Plain-English Meaning

A matrix inverse is the matrix version of undoing multiplication.

### Important Rule

Not every matrix has an inverse.

A matrix must be square and must not collapse or duplicate information.

### Python

`np.linalg.inv(A)` computes the inverse of matrix `A`.

If the matrix cannot be inverted, NumPy raises:

`LinAlgError: Singular matrix`

### Governance Question

Did the transformation preserve enough information to be meaningfully reversed, or did it collapse the signal?

## Math Day 73 - Determinants

### Key Lesson

The determinant is a single number that helps tell whether a square matrix can be inverted.

### 2x2 Formula

For:

`A = [[a, b], [c, d]]`

the determinant is:

`det(A) = ad - bc`

### Invertibility Rule

- If `det(A) = 0`, the matrix does not have an inverse.
- If `det(A) ≠ 0`, the matrix has an inverse.

### Plain-English Meaning

A zero determinant means the matrix collapsed information. Once information is collapsed, the transformation cannot be perfectly undone.

### Python

`np.linalg.det(A)` computes the determinant.

Use `np.isclose(det, 0)` when checking whether a floating-point determinant is effectively zero.

### Governance Question

Are our features independent signals, or are we duplicating/collapsing information and pretending the model has more evidence than it really does?

## Math Day 74 - Linear Independence and Rank

### Key Lesson

Rank tells us how much independent information a matrix really contains.

### Plain-English Meaning

A matrix can have many rows or columns but fewer independent signals.

### Core Rule

For a square matrix:

- Full rank means the matrix has enough independent information.
- Rank deficient means some information is duplicated, dependent, or collapsed.

### Connection to Determinants

For a square matrix:

- Full rank means determinant is not zero.
- Rank deficient means determinant is zero.
- A rank-deficient square matrix does not have an inverse.

### Python

`np.linalg.matrix_rank(A)` returns the rank of matrix `A`.

### Governance Question

Are our features independent signals, or are we double-counting the same evidence under different names?

## Math Day 75 - Span and Basis

### Key Lesson

Span is the space that a set of vectors can reach. A basis is a clean independent set of vectors that spans that space.

### Plain-English Definitions

- Span = everything you can build from a set of vectors.
- Basis = independent vectors that cover the space without redundancy.
- Rank = how many independent directions the matrix contains.

### Example

`[1, 0]` and `[0, 1]` span 2D space.

`[1, 0]` and `[2, 0]` only span one line because the second vector is just a scaled version of the first.

### Python

`np.linalg.matrix_rank(A)` helps identify how many independent directions a matrix contains.

### Governance Question

Do our features span the risk space we claim to model, or are we missing directions and double-counting others?

## Math Day 76 - Linear Transformations

### Key Lesson

A matrix can act as a transformation that takes an input vector and produces an output vector.

### Plain-English Meaning

A matrix can move, stretch, flip, rotate, compress, project, or otherwise transform vectors.

### Core Pattern

`matrix × vector = transformed vector`

### Important Distinction

Some transformations preserve information and can be undone.

Other transformations collapse or discard information and cannot be perfectly reversed.

### Python

Use the `@` operator for matrix-vector multiplication:

`A @ v`

### Governance Question

What did the transformation preserve, emphasize, distort, or discard?

## Math Day 77 - Eigenvectors and Eigenvalues

### Key Lesson

An eigenvector is a direction that a matrix transformation does not turn. The eigenvalue tells how much that direction is stretched, shrunk, flipped, or preserved.

### Core Pattern

`A v = λ v`

### Plain-English Meaning

A matrix transforms a vector, but an eigenvector stays on the same line after the transformation.

### Why It Matters

Eigenvectors and eigenvalues help identify dominant directions in transformations and datasets. They are foundational for PCA, dimensionality reduction, ranking systems, and signal analysis.

### Python

`np.linalg.eig(A)` returns eigenvalues and eigenvectors for matrix `A`.

### Governance Question

Do the dominant mathematical directions actually correspond to meaningful risk signals?

## Math Day 78 - Principal Components

### Key Lesson

Principal components are the strongest independent directions of variation in a dataset.

### Plain-English Meaning

PCA looks for the directions where the data varies the most.

### Connection to Eigenvectors

In PCA:

- eigenvectors identify the principal directions
- eigenvalues show how much variation those directions explain

### Why It Matters

PCA can reduce dimensionality, compress features, reduce noise, and reveal major patterns.

### Governance Question

Did dimensionality reduction preserve the signal we care about, or did it make the system harder to explain?

## Math Day 79 - Covariance Matrix

### Key Lesson

A covariance matrix shows how features move together across observations.

### Plain-English Meaning

Covariance asks whether two features tend to rise and fall together.

### Matrix Shape

If the data matrix has 1,000 observations and 100 features, the covariance matrix is 100 × 100.

### Important Detail

- Diagonal cells = variance of each feature
- Off-diagonal cells = covariance between feature pairs

### PCA Connection

PCA uses the covariance matrix to find the strongest directions of variation.

### Python

`np.cov(X_centered, rowvar=False)`

### Governance Question

Are the feature relationships real signals, or artifacts of collection, logging, or duplicate design?

## Math Day 80 - Eigenvectors and Eigenvalues in PCA

### Key Lesson

Eigenvectors identify the principal directions in the data. Eigenvalues measure how much variation exists along each direction.

### Formula

`Σv = λv`

- `Σ` = covariance matrix
- `v` = eigenvector or direction
- `λ` = eigenvalue or variation along that direction

### PCA Sequence

Covariance matrix → eigenvectors and eigenvalues → ranked principal components

### Important Detail

PCA sorts components by eigenvalue from largest to smallest.

### Python

- `np.linalg.eigh(covariance)`
- `np.argsort(eigenvalues)[::-1]`
- `eigenvalues / eigenvalues.sum()`

### Governance Question

Does the dominant component represent meaningful behavior, or merely dominant bias or duplication in the data?

## Math Day 81 - Project Data onto Principal Components

### Key Lesson

PCA compresses data by projecting centered observations onto selected eigenvectors.

### Formula

`Z = X_centered W`

- `X_centered` = centered original data
- `W` = selected eigenvectors
- `Z` = projected data

### Shape Example

- Original data: 1,000 × 100
- Selected eigenvectors: 100 × 10
- Projected data: 1,000 × 10

The observations remain; the number of descriptive dimensions decreases.

### Python

`X_pca = X_centered @ W`

The `@` operator performs matrix multiplication.

### Dot Product Connection

Each principal-component coordinate is the dot product between one centered observation and one eigenvector.

### Governance Question

Could a discarded low-variance feature still be operationally, legally, or security-relevant?

## Math Day 82 - Standardize Before PCA

### Key Lesson

PCA ranks directions according to variance, so features with larger numerical scales can dominate the result even when they are not more important.

### Standardization Formula

`z = (x - μ) / σ`

- `x` = original value
- `μ` = feature mean
- `σ` = feature standard deviation
- `z` = standardized value

### Centering Versus Standardization

- Centering produces mean 0.
- Standardization produces mean 0 and standard deviation 1.

### PCA Connection

Standardization places features on comparable scales before calculating covariance, eigenvectors, and principal components.

### Important Limitation

Standardization prevents measurement units from dominating PCA. It does not establish operational or security importance.

### Python

- `X.mean(axis=0)`
- `X.std(axis=0)`
- `(X - feature_means) / feature_std_devs`

### Governance Question

Should absolute magnitude matter, or should PCA compare each feature according to its variation relative to its own scale?

## Math Day 83 - Choose Principal Components

### Key Lesson

Eigenvalues measure the variance captured by principal components. Explained variance ratios and cumulative explained variance help determine how many components to retain.

### Formulas

`explained variance ratio = eigenvalue / total eigenvalues`

`cumulative explained variance = running sum of explained variance ratios`

### Selection Rule

Choose the smallest `k` that preserves enough variance for the analytical purpose.

### Common Methods

- Variance threshold
- Scree-plot elbow
- Downstream model performance
- Domain-risk judgment

### Important Limitation

A low-variance component may still contain operationally important information. PCA measures variance, not consequence or importance.

### Python

- `eigenvalues / eigenvalues.sum()`
- `np.cumsum(explained_variance_ratio)`
- `W = eigenvectors[:, :k]`
- `X_pca = X_standardized @ W`

### Carry-Forward Question

How much information loss is acceptable for the intended use?

##