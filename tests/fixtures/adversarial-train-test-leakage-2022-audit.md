# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- paper type: computational benchmark contamination experiment

The paper directly demonstrates that semantically overlapping training queries can inflate retrieval effectiveness and can even alter system rankings under deliberately constructed leakage conditions. It also reports that these effects become smaller as leakage forms a smaller and more realistic share of the training data, with many nDCG@10 differences not statistically significant. This is a useful stress case because the correct reading is neither "leakage invalidates every zero-shot result" nor "small average metric changes mean leakage is harmless." The strongest conclusion is conditional: leakage is a real benchmark-design threat whose practical magnitude depends on contamination amount and evaluation setup. The paper is mainly useful as a method/design reference for benchmark integrity.

## 2. core claims

### claim 1
- content: Robust04 test topics have substantial semantic near-duplicate overlap with MS MARCO/ORCAS training queries.
- claim type: observational
- conclusion strength: medium

### claim 2
- content: Increasing deliberately selected train-test query overlap can improve neural retrieval effectiveness and can change model rankings.
- claim type: performance
- conclusion strength: medium

### claim 3
- content: The practical effect of leakage becomes smaller as leaked examples make up a smaller and more realistic fraction of training data.
- claim type: performance
- conclusion strength: medium

### claim 4
- content: Existing zero-shot neural-retrieval evaluations using these datasets are broadly invalid because of train-test leakage.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: computational benchmark + text coding or content analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: shared-source convergence
- source location: Abstract and leakage-candidate analysis; 69%-76% of topics reported to have near-duplicate training queries after semantic search and manual review
- support level: sufficient
- reason: The paper directly searches training-query corpora against test topics and manually reviews high-similarity candidates. This establishes substantial semantic overlap under the paper's operational near-duplicate definition.
- external dependency: none

### claim 2
- evidence type: computational benchmark + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E3 + E4 + E5
- upstream claims: C1
- evidence dependence: partially independent convergence
- source location: controlled leakage experiments across Duet, KNRM, monoBERT, monoT5, and PACRR; effectiveness and ranking comparisons
- support level: sufficient
- reason: Deliberately varying leakage while evaluating multiple retrieval systems directly supports a causal benchmark-design statement within the constructed experiment: contaminated training can improve metrics and alter ranking.
- external dependency: none

### claim 3
- evidence type: computational benchmark + statistical analysis
- evidence provenance: paper-local
- evidence nodes: E6 + E7
- upstream claims: C2
- evidence dependence: partially independent convergence
- source location: Results and Conclusion comparing high-leakage with larger, more realistic training mixtures
- support level: sufficient
- reason: The paper reports diminishing average leakage effects as the contaminated fraction becomes smaller and notes that most nDCG@10 differences are not significant in realistic regimes. This bounds rather than negates the leakage concern.
- external dependency: none

### claim 4
- evidence type: computational benchmark + author interpretation
- evidence provenance: paper-local
- evidence nodes: E1 + E3 + E6
- upstream claims: C1 + C2 + C3
- evidence dependence: partially independent convergence
- source location: Introduction and Conclusion
- support level: insufficient
- reason: The experiments show that leakage can matter, but they do not establish that every published zero-shot result using these corpora is materially biased or invalid. Effect magnitude varies with contamination fraction and metric, and the paper itself reports reassuringly small effects in many realistic conditions.
- external dependency: none

## 4. what is usable

### usable results
The semantic-overlap prevalence, controlled contamination experiments, metric changes, ranking swaps, and rank-offset memorization results are reusable benchmark-design evidence.

### usable methods or design
Constructing training sets with controlled amounts of semantically test-like queries is a strong way to test leakage causally rather than merely speculate about contamination.

### usable materials or documentation
The paper identifies datasets, models, leakage-search procedure, and experimental contamination regimes sufficiently to audit the design logic.

## 5. what to downweight

### worth noticing but should be downweighted
The headline 69%-76% near-duplicate prevalence is an overlap measure, not by itself a measure of performance inflation.

### should be treated cautiously or ignored
Do not convert "leakage can change rankings" into "all zero-shot benchmark rankings are invalid." The experiment explicitly shows effect size depends on leakage prevalence and configuration.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: medium
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The leakage detector itself depends on semantic-similarity and manual-review definitions, and constructed contamination regimes are not identical to every historical training pipeline. The paper nevertheless directly establishes the benchmark-design hazard. Future audits of a specific model should inspect that model's actual training data and benchmark exposure rather than infer contamination from dataset family names alone.
