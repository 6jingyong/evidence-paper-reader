# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- evidence viability: auditable
- viability flags: none
- paper type: software and computational-benchmark paper

The paper-local evidence strongly supports a bounded claim that LIBLINEAR reaches competitive test accuracy quickly on the two displayed large sparse text-classification datasets, news20 and rcv1. The short JMLR paper is much weaker as stand-alone evidence for the broader statement that the package is generally efficient across large sparse problems because it explicitly omits full comparison details and delegates broader experiments and theoretical properties to cited companion papers. That delegation should remain visible rather than being absorbed into the current paper's evidence. The paper is mainly useful as a software/method reference and a compact benchmark report.

## 2. core claims

### claim 1
- content: On the displayed news20 and rcv1 experiments, LIBLINEAR reaches competitive testing accuracy quickly relative to Pegasos and SVMperf.
- claim type: performance
- conclusion strength: medium

### claim 2
- content: LIBLINEAR is generally very efficient for large sparse classification problems.
- claim type: generality
- conclusion strength: strong

### claim 3
- content: LIBLINEAR's solvers have broader empirical performance and theoretical properties established beyond the two experiments shown in this short paper.
- claim type: generality
- conclusion strength: strong

## 3. evidence and support

### claim 1
- evidence type: computational benchmark
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- upstream claims: none
- evidence dependence: partially independent convergence
- source location: Section 4 and Figure 1, news20 and rcv1 testing-accuracy-versus-training-time comparisons
- support level: sufficient
- reason: The paper directly compares LIBLINEAR with Pegasos and SVMperf on two large sparse datasets after parameter selection and shows rapid approach to competitive testing accuracy. This supports the claim for those displayed tasks and settings.
- external dependency: none

### claim 2
- evidence type: computational benchmark + literature citation
- evidence provenance: mixed
- evidence nodes: E1 + E2 + E3
- upstream claims: C1
- evidence dependence: unclear
- source location: abstract, introductory efficiency example, Section 4, and Section 5
- support level: partial
- reason: The two displayed datasets and the rcv1 timing example support efficiency in important large sparse cases, but the paper explicitly says full comparison details are omitted and points readers to companion work. The broad class-level claim therefore relies materially on evidence outside this four-page paper.
- external dependency: A Dual Coordinate Descent Method for Large-scale Linear SVM, Hsieh et al. (2008), plus other companion studies cited in Section 5; DOI not available in the inspected material; these works carry broader solver comparisons that the current paper omits

### claim 3
- evidence type: literature citation
- evidence provenance: external citation
- evidence nodes: E3
- upstream claims: C2
- evidence dependence: unclear
- source location: Section 5 conclusion, which attributes broader experiments, analysis, and theoretical properties to Lin et al. (2008), Hsieh et al. (2008), and Keerthi et al. (2008)
- support level: unclear
- reason: The current paper reports that those cited works establish the broader performance and theoretical claims, but it does not reproduce enough of their analysis to independently judge them here.
- external dependency: A Dual Coordinate Descent Method for Large-scale Linear SVM, Hsieh et al. (2008), and the other companion works named in Section 5; their contents need inspection before treating those broader claims as verified

## 4. what is usable

### usable results
The news20 and rcv1 timing/accuracy comparison and the reported rcv1 large-scale training example are usable as bounded performance evidence.

### usable methods or design
The package interface, supported linear models, parameter-selection setup, and reproducible comparison framing are useful as a software-method reference.

### usable materials or documentation
The paper identifies the software, commands/documentation, benchmark datasets, and companion experiment code locations, making the provenance of the package and comparisons inspectable.

## 5. what to downweight

### worth noticing but should be downweighted
The broad phrase that LIBLINEAR is very efficient on large sparse datasets is directionally supported, but this short paper itself displays only two benchmark datasets and deliberately delegates fuller evidence elsewhere.

### should be treated cautiously or ignored
Do not treat theoretical properties or comprehensive cross-dataset superiority as paper-local findings merely because the conclusion cites companion papers that establish them.

## 6. value breakdown
- result value: medium
- method value: high
- theory or insight value: low
- research design value: medium
- material or documentation value: high

## 7. uncertainty and follow-up
The main uncertainty is external-dependency depth: the short JMLR article intentionally compresses experiments and theory into citations. A useful next step is to inspect Hsieh et al. (2008), especially the larger solver comparison, before using this paper as evidence for broad optimizer superiority or theoretical guarantees.
