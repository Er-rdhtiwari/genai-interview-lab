# Refrence:
- https://chatgpt.com/share/693452f4-5dd4-800f-94cb-8ca7be2f1bf5

---

## Day 1 – Statistics & Data Foundations

### 1. Types of Statistics

#### 1.1 Descriptive Statistics

**Idea:**
Descriptive statistics **summarize what the data looks like right now**. No predictions, no conclusions about the future or unseen users. Just describing.

* Tools:

  * Tables (counts, group-by),
  * Charts (histograms, boxplots, time series),
  * Summary metrics (mean, median, min, max, percentiles).

**In AI/ML & GenAI:**

* **EDA before modeling**

  * Label distribution (class imbalance),
  * Input length distributions (token length, text length),
  * Feature correlations.
* **Monitoring production LLM systems**

  * Latency distributions (p50, p90, p99),
  * Daily request counts,
  * Error rate over time (HTTP 5xx, timeouts).
* **Model evaluation summaries**

  * Average accuracy, F1-score by segment,
  * Distribution of prediction confidence.

**Real examples (2–3):**

1. **LLM latency dashboard**

   * You plot p50, p90, p99 latency for each model version.
   * Helps you see if a new model is slower or unstable.
2. **Label distribution for a churn model**

   * You check `% churned` vs `% non-churn`.
   * If 95% non-churn, 5% churn → class imbalance → adjust metrics/weights.
3. **Token usage for cost control**

   * You calculate average tokens per request + 95th percentile.
   * Helps decide truncation strategies and cost alerts.

**Best practices & pitfalls:**

* ✅ **Always segment**: by user region, device, experiment group, etc.
* ✅ Use **percentiles instead of only mean** for skewed data (latency, incomes).
* ❌ Don’t draw causal conclusions from descriptive stats alone (“users are leaving because…”).
* ❌ Don’t forget the **time dimension** – recent data often more relevant.

---

#### 1.2 Inferential Statistics

**Idea:**
Inferential statistics = **use a sample to say something about a larger population**.

* You rarely see *all* users or *all* events.
* You use:

  * Confidence intervals,
  * Hypothesis tests,
  * A/B tests.

**In AI/ML & GenAI:**

* **Model comparison**

  * Compare old vs new model using a test set or A/B test sample.
  * Decide if performance difference is real or noise.
* **Estimating metrics**

  * Estimate “true” conversion rate of an LLM-based recommendation widget from a random sample of users.
* **A/B experiments**

  * Decide whether to roll out a new prompt, ranking algorithm, or UI.

**Real examples:**

1. **A/B test for new LLM prompt**

   * Old prompt CTR: measured from a **sample** of 50k users.
   * New prompt CTR: sample of 50k users.
   * Use inferential stats to check if the uplift is statistically significant.
2. **Estimating true error rate**

   * You manually label 1k model outputs to estimate “true” hallucination rate of an LLM.
   * That 1k is a sample; inferential stats gives CI for hallucination rate.
3. **Evaluating model on a test set**

   * Test set is a sample from future user queries.
   * You treat accuracy/F1 as an estimate of future performance, not absolute truth.

**Best practices & pitfalls:**

* ✅ Ensure **random, representative samples** before trusting results.
* ✅ Always think about **variance** (wide vs narrow confidence intervals).
* ❌ Avoid p-hacking: repeatedly slicing data until you find “significant” differences.
* ❌ Don’t over-trust results from **tiny samples**.

---

### 2. Basic Statistical Terminology

#### Population vs Sample

* **Population**: All possible entities you care about.

  * Example: all users who might use your product in a year.
* **Sample**: Subset of the population you actually observe.

  * Example: users in an experiment during the last week.

**In ML:**

* Population ≈ “all future queries or users”.
* Sample ≈ “your train/test/validation sets”, or “traffic during experiment”.

---

#### Sample

* A **subset** of observations taken from the population.
* We compute statistics on the sample and infer about the population.

Example:

* You log 10M requests/day but only sample 100k for analysis and monitoring.

---

#### Variable

* A **property you measure** on each unit (user, session, request).

  * Example: `latency_ms`, `country`, `num_clicks`, `is_churned`.

**In ML:**

* Variables become **features** and **labels**.

---

#### Data (singular vs plural)

* **Datum**: one observation (rarely used in practice).
* **Data**: collection of observations.

  * “The data *are* noisy” (formal) vs “The data *is* noisy” (common usage).

You don’t need to obsess over grammar, but know the idea.

---

#### Random Variable

* A variable whose value is **uncertain** and driven by some random process.

  * Example: `X = latency of the next LLM call`.
  * Example: `Y = 1 if user churns next month, else 0`.

In ML:

* Labels, errors, predictions are often modeled as random variables to reason about uncertainty, variance, and expectations.

---

#### Experiment

* Controlled process to **generate data**.

  * Example: A/B test, where you randomly assign users to model A or B.
  * Example: Offline simulation where you sample queries and log model outputs.

In GenAI:

* Experiment = “deploy new prompt to 10% traffic and measure metrics”.

---

#### Parameter (population value)

* A **true but unknown value** describing the population.

  * Example: true average latency of all LLM calls.
  * Example: true conversion rate for all users seeing variant B.

We can never observe the parameter directly; we estimate it.

---

#### Statistic (sample value)

* A **function of the sample**: mean, median, standard deviation, accuracy, etc.
* Used to estimate the corresponding parameter.

Example:

* Sample mean latency from yesterday’s logs → estimator of true mean latency.

---

**How these appear in ML/GenAI:**

* Test set accuracy = **statistic** estimating population accuracy (future queries).
* True underlying accuracy on all future traffic = **parameter**.
* A/B test CTR difference (sample statistic) estimates true CTR uplift (parameter).

---

### 3. Types of Data (for ML Features)

#### 3.1 Categorical Data

**Nominal (no order)**

* Categories without natural order.

  * Examples: `country`, `browser`, `color`, `language`.
* In ML:

  * Use **one-hot encoding**, **embeddings**, or **target encoding**.
  * Good models: tree-based, deep models with embeddings.

**Ordinal (has order)**

* Categories with meaningful ranking.

  * Examples: `low`, `medium`, `high` risk; `beginner`, `intermediate`, `advanced`.
* In ML:

  * Could encode as integers (1, 2, 3) to preserve ordering.
  * Be careful: treat as numeric only if **distance between levels is meaningful**.

**Impact on feature engineering & model choice:**

* **Encoding**

  * Nominal: one-hot or embeddings.
  * Ordinal: integer codes or ordinal encoders.
* **Scaling**

  * Categorical features don’t get standard scaling like continuous variables.
* **Pitfalls**

  * Treating IDs (user_id) as numeric features → meaningless.
  * Ignoring ordinality (using one-hot on ordinal variables may lose order info).

---

#### 3.2 Numerical Data

**Discrete (countable)**

* Integer counts: `num_logins`, `num_clicks`, `num_tickets`.
* Often non-negative.
* ML:

  * Can be used as-is or transformed (log, bucketed).
  * Poisson/Negative Binomial models sometimes used.

**Continuous (measurable)**

* Real-valued measurements: `response_time`, `amount_spent`, `temperature`.
* ML:

  * Typically standardize or normalize.
  * Often used in regression models, neural nets.

**Effect on feature engineering & model choice:**

* **Scaling**

  * Continuous variables often need **standardization** (0 mean, unit variance) for linear models, neural networks.
* **Transformations**

  * Skewed data (like spend or latency) → log transform or winsorize.
* **Binning**

  * Sometimes you bin numeric data into categories for interpretability (e.g., age groups).

**Examples:**

1. **Churn model**

   * Discrete: number of support tickets last month.
   * Continuous: average session duration.
   * Categorical: subscription plan (basic, pro).
2. **Recommendation system**

   * Continuous: user embedding dimensions.
   * Discrete: number of items bought last week.
   * Nominal: device type (mobile, desktop).

---

### 4. Probability Basics in Data Context

#### With Replacement vs Without Replacement

**With replacement**

* After sampling an item, you **put it back**.
* Each draw is independent, probabilities stay the same.

Example (ML context):

* You sample requests from a huge stream, allowing duplicates.
* Drawing a random batch from a large dataset using independent sampling (effectively with replacement when population is huge).

**Without replacement**

* Once selected, item is **not returned** to the pool.
* Probabilities change as you draw more items.

Example:

* You have 10k labeled test queries and you select a subset of 1k **distinct** queries for manual evaluation.
* When you do cross-validation: fold splits are created without replacement.

**Why it matters:**

* **Variance estimates**

  * Without replacement → slightly lower variance (no duplicates).
* **Finite populations**

  * When population is small (e.g., 100 customers in a B2B product), sampling without replacement is more realistic.
* **Simulation**

  * When modeling how many unique users see an experiment, use without replacement concept.

**Best practices:**

* For huge datasets: treating sampling as “with replacement” is often fine.
* For small/limited data: be explicit about without-replacement to avoid bias.
* Keep in mind independence assumptions: many statistical formulas assume independent samples (closer to with replacement behavior).

---

### Day 1 – Interview Q&A

1. **Q:** Why do we need inferential statistics if we already have descriptive summaries?
   **A:** Descriptive stats tell you what happened in your **sample**, inferential stats tell you whether those patterns are likely to hold in the **population** (e.g., whether a CTR increase in your experiment is real or just noise).

2. **Q:** In an ML context, what is the “population” and what is the “sample”?
   **A:** Population = all future or possible user requests; Sample = the data you actually see (train/test sets, experiment traffic). Metrics from the sample estimate performance on the population.

3. **Q:** Why is it dangerous to treat user IDs as numeric features?
   **A:** The numeric value of an ID has no meaning or ordering; models may learn spurious patterns. Use IDs only for grouping, joins, or embeddings with care.

4. **Q:** When would you prefer median over mean as a summary metric?
   **A:** For skewed data like latency, incomes, or spend. Median is robust to extreme outliers, while mean can be heavily influenced by a few large values.

5. **Q:** Give an example of a random variable in an LLM service.
   **A:** “Latency of the next request” or “whether the next response is accepted by the user” – their values vary randomly across requests.

6. **Q:** How does “with vs without replacement” appear in ML workflows?
   **A:** Sampling mini-batches from huge datasets (effectively with replacement) vs selecting distinct evaluation samples for manual labeling (without replacement).

---

## Day 2 – Descriptive Statistics, Sampling & Hypothesis Testing

### 1. Steps in Descriptive Statistics / EDA

1. **Collecting the data**

   * Identify sources: logs, DB tables, APIs.
   * Ensure correct joins, time ranges, filters.
   * Handle missing values and data quality issues.

2. **Presenting the data**

   * Tables: pivot tables, group-by summaries.
   * Plots: histograms, boxplots, time series, bar charts.
   * Dashboards: Grafana, Kibana, custom monitoring UI.

3. **Summarizing the data**

   * Central tendency: mean, median, mode.
   * Spread: range, variance, std dev, IQR.
   * Distributions: normal, heavy-tailed, multimodal.

**Connection to ML pipeline:**

* Before feature engineering and model selection:

  * Check missingness patterns, distributions, correlations.
* During monitoring:

  * Track feature drift (distributions changing over time),
  * Track output metrics (CTR, NDCG, latency, error rate).

---

### 2. Measures of Central Tendency

#### Mean

* Average: sum of values / count.
* Sensitive to outliers.

LLM example:

* Mean latency may look OK (e.g., 400ms), but if a few calls take 20s, mean is pulled up; doesn’t show tail behavior.

#### Median

* Middle value when sorted.
* Robust to outliers; better for skewed distributions.

LLM example:

* Median latency is more stable and robust; often used along with p90/p99.

#### Mode

* Most frequent value.
* Useful for categorical data (most common error type, most used language).

**When to use what:**

* **Mean**: roughly symmetric distributions, no extreme outliers (e.g., height, small-noise metrics).
* **Median**: skewed data like latency, spend, API errors.
* **Mode**: categorical; e.g., which prompt template is most used.

---

### 3. Measures of Spread / Variability

#### Range

* `max - min`.
* Very sensitive to outliers.

Pitfall:

* Two models with same range can have very different overall variability; range alone is insufficient.

#### Interquartile Range (IQR)

* Q1 = 25th percentile, Q3 = 75th percentile.
* IQR = Q3 − Q1.
* Captures the middle 50% of the data; robust to outliers.

#### Outlier Detection Using IQR

* **Lower bound**: Q1 − 1.5 × IQR
* **Upper bound**: Q3 + 1.5 × IQR

Values outside these bounds are considered potential outliers.

**In practice (ML/LLM):**

* **Training data cleaning**

  * Remove or cap extremely large feature values (e.g., insane `num_clicks` due to bot activity).
* **Latency monitoring**

  * Compute Q1, Q3, IQR of latency per hour.
  * Flag requests beyond upper bound; trigger alerts or investigate.
* **Code/Tool implementation**

  * In Pandas:

    * `q1 = series.quantile(0.25)`
    * `q3 = series.quantile(0.75)`
    * `iqr = q3 - q1`
    * `lower = q1 - 1.5 * iqr`
    * `upper = q3 + 1.5 * iqr`
    * Then filter for outliers.

**Best practices:**

* ✅ Use robust measures (median, IQR) when outliers are likely.
* ✅ Decide whether to **remove, cap, or keep** outliers based on business context (e.g., fraud).
* ❌ Don’t blindly drop all outliers; they may represent important edge cases (e.g., DDoS, abuse, VIP users).

---

### 4. Data Collection & Sampling Design

**Data collection steps:**

1. **Define the objective**

   * e.g., “Estimate hallucination rate of the LLM on customer queries.”
2. **Define variables & population**

   * Population: all customer queries over the next month.
   * Variables: query text, model output, human label (correct/incorrect).
3. **Define data collection & measurement scheme**

   * Randomly sample queries from production logs.
   * Send to human annotators with clear labeling guidelines.
4. **Define analysis techniques**

   * Descriptive: compute overall hallucination rate, by segment.
   * Inferential: CI for hallucination rate; hypothesis test for new model.

**Methods to collect data:**

* **Experiment**

  * Controlled changes; random assignment (A/B tests).
* **Survey**

  * Ask users for feedback or labels (e.g., satisfaction scores).
* **Census**

  * Collect data from entire population (rare, expensive).
* **Judgment samples**

  * Experts select “representative” items manually (risk of bias).
* **Probability samples**

  * Sampling methods where each unit has known probability of selection (see next section).

---

### 5. Types of Sampling

#### Probability Sampling

1. **Simple random sampling**

   * Every unit has equal chance.
   * Example: randomly sample 10k user sessions for evaluation.

2. **Stratified sampling**

   * Divide population into **strata** (segments) and sample within each.
   * Example: stratify by country, device, or class label to ensure representation.
   * ML use: balanced dataset for classification; ensure enough minority class.

3. **Systematic sampling**

   * Pick every k-th item after a random start.
   * Example: sampling every 100th log line.
   * Be cautious if there is periodicity in data.

4. **Cluster random sampling**

   * Randomly select **groups (clusters)**, then sample all or some units within.
   * Example: sample a few data centers, then all users in those centers.

5. **Multistage random sampling**

   * Combination of cluster + simple random at multiple stages.
   * Example: pick random regions, then random cities, then random users.

#### Non-probability Sampling

* Selection is not based on known probabilities.

  * Convenience sampling, expert sampling, self-selection.
* Appears in:

  * Log-based datasets (only active users),
  * Feedback data (only users who choose to rate).

**ML/AI examples:**

* **Stratified**

  * Ensure equal number of spam and non-spam emails in training.
* **Cluster**

  * Sample whole customer accounts instead of individual users.
* **Non-probability**

  * Using only “power users” (who give feedback) to evaluate models → bias.

**Best practices:**

* Prefer **probability sampling** for evaluation/experiments.
* When stuck with non-probability samples:

  * Explicitly acknowledge bias,
  * Try re-weighting or matching techniques.

---

### 6. Sampling Error

* **Sampling error** = difference between sample statistic and population parameter **due to random sampling**.
* It decreases with:

  * Larger sample sizes,
  * Better sampling strategies (less bias).

**Why it matters:**

* Model evaluation:

  * Accuracy on a small test set (n=1k) has more sampling error than on a large test set (n=100k).
* A/B tests:

  * Small experiments → noisy metrics.
  * Large experiments → more stable estimates.

**Key idea for a Senior AI Engineer:**

* Always ask: “What is the **confidence interval** of this metric?”
  Not just: “What is the accuracy?”

---

### 7. Hypothesis Testing – Core Terminology

* **Hypothesis:** Claim about a population parameter.

* **Null Hypothesis (H0):** Status quo; no effect, no difference.

* **Alternate Hypothesis (H1):** What you want to prove; effect exists.

* **Simple hypothesis:** Fully specifies the parameter.

  * H0: “Conversion rate = 5%”.

* **Composite hypothesis:** Parameter lies in a range.

  * H1: “Conversion rate > 5%”.

**Simple A/B example:**

* Goal: Check if new LLM-based recommender increases conversion.

* **H0:** Conversion rate (new model) = Conversion rate (old model).

* **H1:** Conversion rate (new model) > Conversion rate (old model).

You collect sample data, compute test statistics, p-values, confidence intervals to decide whether to reject H0.

---

### Day 2 – Interview Q&A

1. **Q:** Why is median often used instead of mean for latency?
   **A:** Latency is skewed with long tails; median is robust to a few very slow requests, while mean gets distorted by them.

2. **Q:** How would you detect outliers using IQR in model training data?
   **A:** Compute Q1, Q3, IQR; treat values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR as outliers, then decide whether to remove or cap based on domain context.

3. **Q:** What is the difference between range and IQR?
   **A:** Range uses only min and max (very sensitive to outliers). IQR uses Q1 and Q3, capturing the middle 50% and is more robust.

4. **Q:** Why is stratified sampling useful for training classification models?
   **A:** It ensures each class (especially rare ones) is adequately represented, reducing variance and improving model performance on minority classes.

5. **Q:** What is sampling error and how can you reduce it?
   **A:** Sampling error is the difference between sample metrics and population metrics due to random sampling; you reduce it by increasing sample size and using better, less biased sampling.

6. **Q:** Give an example of a non-probability sample in an ML context.
   **A:** Using only users who clicked “Provide feedback” in your app; they’re self-selected and not representative of all users.

7. **Q:** In an A/B test, what are H0 and H1 typically?
   **A:** H0: no difference in the metric between A and B; H1: B has a higher (or different) metric than A.

---

## Day 3 – Analytics Types, Data Roles, Domain Analysis & Python Foundations

### 1. Types of Data Analytics

#### Descriptive Analytics (What happened?)

* Summarize past data:

  * Counts, totals, averages, trends over time.
* Examples:

  * Daily active users, total revenue,
  * Average LLM latency last week.

#### Diagnostic Analytics (Why did it happen?)

* Drill down into causes:

  * Segment by country, device, user cohort,
  * Root-cause analysis of anomalies.

Examples:

* Investigate why engagement dropped after a UI change.
* Analyze why hallucination rate increased after a new prompt rollout.

#### Predictive Analytics (What can happen in the future?)

* Use models to **predict future outcomes**:

  * Churn models, demand forecasting, time-series forecasting.
  * LLM-based models for lead scoring, next-best action.

Examples:

* Predict probability of churn for each user.
* Forecast traffic to plan LLM capacity and cost.

#### Prescriptive Analytics (What should we do?)

* Recommend actions given predictions and constraints:

  * Pricing optimization,
  * Budget allocation,
  * Auto-scaling policies.

Examples:

* Given predicted traffic and latency, decide how many GPU replicas to run.
* Given predicted churn, decide which users to target with retention campaigns.

**In one product (LLM assistant):**

* Descriptive: current CSAT, number of sessions.
* Diagnostic: why CSAT dropped (prompt change, latency, domain issues).
* Predictive: which tickets are likely to escalate.
* Prescriptive: which tickets to route to humans vs bots.

---

### 2. Data Roles: DS vs DE vs DA (Churn Example)

#### Data Engineer (DE)

* Build and maintain data infrastructure.
* Responsibilities:

  * Ingest raw events into data lake/warehouse.
  * Create cleaned, joined tables (user profile, events, churn labels).
  * Ensure pipelines are reliable, scalable, and secure.

Churn example:

* DE builds ETL to produce a daily `user_churn_features` table with last-30-day activity.

#### Data Scientist (DS)

* Build & evaluate models.
* Responsibilities:

  * Understand churn drivers with EDA.
  * Feature engineering (recency, frequency, monetary value, engagement).
  * Train models, tune hyperparameters, design experiments.

Churn example:

* DS trains a model predicting `P(churn | features)`, evaluates AUC, calibrates probabilities.

#### Data Analyst (DA)

* Analyze and communicate insights; focus on **business questions**.
* Responsibilities:

  * Build churn dashboards.
  * Track KPIs, segments, cohorts.
  * Work with stakeholders to interpret results and propose actions.

Churn example:

* DA reports monthly churn rate by region/plan, monitors the impact of retention campaigns.

**As a Senior AI Engineer, you often sit between DS & DE:**

* Understand model details (DS side).
* Understand pipelines and deployment (DE side).
* Communicate results (DA side).

---

### 3. Domain Analysis

#### What is domain analysis?

* Systematic understanding of:

  * Business problem & stakeholders,
  * KPIs & constraints,
  * Processes & data sources.

Without domain analysis, you risk building technically “cool” but useless solutions.

#### Steps:

1. **Identify stakeholders and problem**

   * Who cares? Product, operations, finance, compliance?
   * Problem: high churn, low CSAT, fraud, latency issues.

2. **Define KPIs and success criteria**

   * Churn rate, average handling time, NPS, CSAT, conversion rate, latency SLO.

3. **Map processes and data sources**

   * Where is data generated? Apps, CRM, logs, support systems.
   * How data flows between systems.

4. **Note constraints**

   * Budget, latency, SLAs, privacy, regulations (GDPR, HIPAA),
   * Cultural/operational realities.

#### 1-minute domain walkthrough – Healthcare AI assistant

* Stakeholders:

  * Doctors, hospital admin, compliance, IT.
* Problem:

  * Reduce time doctors spend on note-taking and improve documentation quality.
* KPIs:

  * Average documentation time per patient,
  * Doctor satisfaction,
  * Error rate in clinical notes.
* Data sources:

  * EHR system, voice transcripts, historical notes.
* Constraints:

  * Strong privacy rules (HIPAA),
  * Must be explainable, low hallucination tolerance,
  * Latency constraints in clinic.

Senior AI Engineer thinking:

* Prefer on-prem or VPC.
* Strict logging and redaction of PHI.
* Evaluate hallucination rate and factual consistency carefully.
* Balance model size vs latency vs cost.

---

### 4. Data Types – Quick Recap (Practical)

* **Categorical**

  * Nominal: `disease_type`, `country`.
  * Ordinal: `severity_level` (mild, moderate, severe).
  * Feature engineering:

    * One-hot, embeddings, ordinal encoders.

* **Numerical**

  * Discrete: `num_visits`, `num_medications`.
  * Continuous: `blood_pressure`, `amount_spent`.
  * Feature engineering:

    * Scaling, log transform, binning.

**Impact on ML:**

* Choice of **loss function**

  * Regression (continuous target) vs classification (categorical target).
* Choice of **metrics**

  * MSE/RMSE vs accuracy/F1 vs AUC.
* Encoding affects model quality & interpretability.

---

### 5. Python Foundations for Data & Analytics Work

#### 5.1 Type Casting / Data Type Conversion

**Implicit (auto) casting**

* Python automatically converts to a common type in some operations:

```python
x = 3      # int
y = 2.5    # float
z = x + y  # float 5.5 (int -> float)
```

**Explicit casting**

* You manually convert:

```python
user_id_str = "123"
user_id = int(user_id_str)  # explicit cast to int

prob_str = "0.87"
prob = float(prob_str)      # cast to float for ML scoring
```

**Why it matters in ML/analytics:**

* Reading from CSV/DB → everything is often string; you must cast to `int`, `float`, `datetime` to do math.
* Feature preparation:

  * Convert booleans (`"True"`/`"False"`) to `0/1`.
  * Ensure labels are numeric for ML libraries.

Pitfalls:

* Failing conversion → `ValueError` (e.g., `"abc"` to int).
* Silent type issues (e.g., `'10' + '20'` = `'1020'`, not 30).

---

#### 5.2 Python Operators (with ML/Data Examples)

##### Arithmetic operators

`+`, `-`, `*`, `/`, `%`, `**`, `//`

```python
# total_tokens for a conversation
prompt_tokens = 150
completion_tokens = 300
total_tokens = prompt_tokens + completion_tokens  # 450

# average tokens per message
num_messages = 9
avg_tokens = total_tokens / num_messages  # division

# square for feature engineering (sometimes)
x = 3
x_sq = x ** 2  # 9
```

##### Assignment operators

`=`, `+=`, `-=`, `*=`, `/=`, etc.

```python
num_requests = 0
for _ in range(10):
    num_requests += 1  # increment counter in logs

latency_sum = 0.0
for latency in latencies:
    latency_sum += latency
```

##### Comparison operators

`==`, `!=`, `>`, `<`, `>=`, `<=`

```python
if latency_ms > 1000:
    print("Slow request")

if predicted_label == true_label:
    correct_predictions += 1
```

Used heavily in evaluation loops and filters.

##### Logical operators

`and`, `or`, `not`

```python
if (latency_ms > 1000) and (status_code != 200):
    alert("Slow and failing requests")

if (country == "IN") or (country == "US"):
    allowed_region = True
```

##### Membership operators

`in`, `not in`

```python
blocked_users = {"user123", "user456"}

if user_id in blocked_users:
    deny_request()

if feature_name not in feature_columns:
    raise ValueError("Missing feature")
```

Useful for checking feature availability, config flags, etc.

##### Identity operators

`is`, `is not` (object identity, not equality)

```python
result = None

if result is None:
    # no prediction yet
    result = model.predict(x)
```

Use `is None` instead of `== None` for clarity and correctness.

##### Bitwise operators

`&`, `|`, `^`, `<<`, `>>`, `~`

* Often used for:

  * Efficient flag/permission handling,
  * Mask operations on arrays.

Example (Pandas-style boolean masks):

```python
import pandas as pd

df = pd.DataFrame({"latency": [100, 500, 1500], "status": [200, 500, 200]})

# note: '&' is bitwise AND used for boolean masks
slow_and_error = df[(df["latency"] > 1000) & (df["status"] != 200)]
```

---

### Day 3 – Interview Q&A

1. **Q:** How do descriptive, diagnostic, predictive, and prescriptive analytics relate in an LLM-based customer support system?
   **A:** Descriptive: number of tickets, CSAT trends; Diagnostic: why CSAT dropped (topics, latency); Predictive: which tickets will escalate; Prescriptive: which tickets to route to senior agents vs bot vs junior staff.

2. **Q:** In a churn reduction project, how do DE, DS, and DA collaborate?
   **A:** DE builds churn datasets and pipelines; DS models churn and designs experiments; DA builds dashboards, monitors churn KPIs, and communicates insights to business teams.

3. **Q:** Why is domain analysis critical before building an ML model?
   **A:** It ensures you solve the right problem with the right KPIs, use the correct data, and respect constraints (budget, SLAs, regulations). Without it, you risk building accurate models that don’t help the business.

4. **Q:** Give a Python example where explicit type casting is necessary in data processing.
   **A:** When reading CSV logs, numeric fields come as strings; you must cast `"123"` to `int` for aggregations or `"0.56"` to `float` for thresholding (e.g., `if prob > 0.8`).

5. **Q:** When would you use membership operators (`in`, `not in`) in ML code?
   **A:** Checking if required features are present in a dataset, if a user ID is in a blacklist, or if a config key exists in a dictionary.

6. **Q:** Why is `is None` preferred over `== None` in Python?
   **A:** `is` checks identity, which is the correct way to test for the singleton `None`; `==` may be overloaded and give unexpected results.

7. **Q:** How does understanding data types help you choose model and metric?
   **A:** Categorical vs numeric determines encoding and choice of algorithms; type of target (binary, multiclass, continuous) determines whether to use classification vs regression and which metrics (accuracy/F1 vs MSE/RMSE/AUC).

---

