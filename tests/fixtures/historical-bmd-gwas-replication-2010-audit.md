# reader-side paper audit

## 1. reader conclusion
- scope status: in scope
- paper type: observational genetics study with discovery and independent replication cohorts

The paper's strongest evidence is the two-stage association result for CATSPERB: variants associated with femoral-neck bone mineral density in 1524 premenopausal European-American women, with supporting evidence for rs1285635 in an independently sampled group of 669 premenopausal African-American women. That is materially stronger than repeated analyses of one cohort because the replication cohort has a separate sample and ancestry structure. The evidence does not justify treating every top discovery locus as independently replicated, because the replication support is concentrated in one locus and the top 50 SNPs were selectively carried forward. The paper is mainly useful as a genetics result and as a clear example of genuine independent convergence inside one paper.

## 2. core claims

### claim 1
- content: In the European-American discovery cohort, variants in CATSPERB show evidence of association with femoral-neck bone mineral density.
- claim type: observational
- conclusion strength: medium

### claim 2
- content: The rs1285635 CATSPERB association receives supporting evidence in an independently sampled African-American replication cohort.
- claim type: observational
- conclusion strength: medium

### claim 3
- content: Several of the novel loci detected in the discovery GWAS are broadly established as BMD loci across premenopausal populations.
- claim type: generality
- conclusion strength: strong

### claim 4
- content: Using a distinct replication cohort materially strengthens the CATSPERB association beyond repeated analysis of the discovery cohort alone.
- claim type: methodological
- conclusion strength: medium

## 3. evidence and support

### claim 1
- evidence type: statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1
- evidence dependence: single-source
- source location: abstract and discovery GWAS results for 1524 premenopausal European-American women
- support level: sufficient
- reason: The discovery cohort directly provides association evidence for CATSPERB variants, including rs1298989 at P = 2.7 × 10^-5 and rs1285635 at P = 3.0 × 10^-5. This is one discovery evidence unit and should not be mistaken for replication.
- external dependency: none

### claim 2
- evidence type: statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- evidence dependence: independent convergence
- source location: abstract and replication analysis of the top discovery SNPs in 669 premenopausal African-American women
- support level: sufficient
- reason: The rs1285635 association identified in the European-American discovery cohort also shows supporting evidence in a separately sampled African-American cohort at P = 0.003. The two cohorts have materially separate participants and sampling/error structures, so the repeated direction at the same locus qualifies as independent convergence rather than shared-source corroboration.
- external dependency: none

### claim 3
- evidence type: statistical analysis + author interpretation
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- evidence dependence: partially independent convergence
- source location: discovery and replication results plus the conclusion
- support level: partial
- reason: Independent replication strengthens one CATSPERB signal, but the paper does not independently replicate every novel discovery locus. The broader plural claim about several novel loci therefore reaches beyond the strongest replicated evidence.
- external dependency: none

### claim 4
- evidence type: statistical analysis
- evidence provenance: paper-local
- evidence nodes: E1 + E2
- evidence dependence: independent convergence
- source location: study design, discovery cohort description, and African-American replication cohort analysis
- support level: sufficient
- reason: The replication result comes from a separately sampled cohort rather than another model, endpoint, or resampling of the discovery participants. That materially separates major sampling errors and makes the convergence stronger than repeated within-cohort analyses.
- external dependency: none

## 4. what is usable

### usable results
The discovery association statistics and the independent African-American replication result for rs1285635 are directly usable as bounded evidence for the CATSPERB-BMD association.

### usable methods or design
The discovery-then-replication architecture, with 1524 European-American women followed by 669 independently sampled African-American women, is a clear example of separating discovery evidence from replication evidence.

### usable materials or documentation
The paper reports cohort sizes, ancestry groups, BMD phenotypes, genotyping platform, top-SNP carry-forward strategy, and the key discovery/replication statistics sufficiently to inspect the dependence structure.

## 5. what to downweight

### worth noticing but should be downweighted
Cross-ancestry replication is especially informative because it changes linkage-disequilibrium and population structure, but differences between ancestry groups can also change power and tag-SNP behavior; failure or success should therefore be interpreted locus by locus.

### should be treated cautiously or ignored
Do not convert one successfully supported locus into a statement that all top discovery loci were independently replicated. Selection of the top 50 SNPs for follow-up also means the replication stage is conditional on discovery screening.

## 6. value breakdown
- result value: high
- method value: high
- theory or insight value: medium
- research design value: high
- material or documentation value: high

## 7. uncertainty and follow-up
The strongest independent-convergence claim applies to CATSPERB rs1285635, not to every discovery locus. Cross-ancestry differences complicate direct effect-size comparison, and the discovery P values themselves do not reach modern genome-wide significance thresholds. No external citation is structurally necessary to identify the independent replication architecture because both cohorts and the replication statistic are reported in the current paper.
