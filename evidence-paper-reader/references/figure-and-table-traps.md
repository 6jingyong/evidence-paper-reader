# Figure and table traps

Use this reference when figures or tables materially support a core claim.

The goal is not to treat unusual visualization choices as misconduct. The goal is to reconstruct what the visual actually encodes before accepting the visual impression.

## First-pass reconstruction

Before interpreting a figure, identify:
- x and y variables
- units
- linear, logarithmic, categorical, cumulative, normalized, indexed, or transformed scale
- axis limits and whether zero is meaningful
- denominator or normalization reference
- sample size and what counts as an independent observation
- uncertainty representation, if any
- filtering, smoothing, binning, interpolation, or aggregation
- whether the figure shows raw observations, summaries, fitted values, predictions, or a selected example

For a table, identify:
- denominator for every percentage or rate
- units and transformations
- missing-data handling
- adjusted versus unadjusted estimates
- whether rows use the same population or denominator
- whether values are absolute, relative, normalized, indexed, or cumulative

## Axis and scale traps

### Truncated baseline
A bar or area chart with a non-zero baseline can visually magnify small absolute differences.

Do not require a zero baseline for every plot. For variables where zero is not meaningful, a truncated axis can be appropriate. The audit should compare the numerical effect size with the visual impression.

### Log scale
Equal visual distance on a log axis represents multiplicative rather than additive change.

Check:
- whether the axis is log transformed
- whether zeros or negative values were excluded or transformed
- whether a straight line on log or log-log axes is being interpreted correctly

### Reversed or irregular axes
A reversed axis or uneven numeric spacing can change perceived direction or slope.

Categorical spacing should not be interpreted as numeric distance.

### Dual y-axes
Two independently scaled y-axes can create or suppress apparent co-movement.

Do not infer correlation from visual alignment alone. Check the underlying values and whether the axis ranges were chosen independently.

### Aspect ratio
Changing panel height or width can make the same slope appear steep or flat. Use numerical slopes/effect sizes when slope magnitude matters.

## Denominator and normalization traps

### Denominator drift
Percentages can look comparable while using different denominators across groups, time points, or panels.

### Relative versus absolute change
A large relative change can correspond to a small absolute change, and vice versa.

Keep:
- absolute risk versus relative risk
- percentage change versus percentage-point change
- fold change versus absolute concentration
separate.

### Indexed or rebased series
A series rebased to 100 or normalized to a control shows relative trajectories, not absolute levels.

### Row-wise or column-wise normalization
Heatmaps often z-score each row or normalize each sample independently. Color then represents relative position within that row/sample, not cross-row absolute abundance.

### Compositional closure
Shares constrained to sum to 100 percent can move mechanically when another component changes. Do not interpret each share as independently varying.

## Aggregation traps

### Mean hides distribution
Means can hide skew, multimodality, outliers, ceiling/floor effects, or heterogeneous subgroups.

### Simpson's paradox
An aggregate trend can reverse within relevant subgroups. Check stratification when group composition differs materially.

### Binning
Histogram/bin choices can create or hide apparent modes and thresholds.

### Cumulative curves
Cumulative totals, cumulative returns, cumulative incidence, or running sums can look smooth even when underlying period-by-period behavior is volatile.

### Smoothing
Moving averages, LOESS, spline fits, and other smoothers can suppress noise and create apparent turning points. Distinguish fitted trend from observed data.

## Uncertainty and sample-size traps

### Error-bar identity
Do not assume error bars are SD, SEM, CI, or credible intervals. Determine which one is reported.

SEM describes uncertainty of an estimated mean and is typically narrower than the underlying observation spread; it should not be read as population variability.

### Error-bar overlap
Overlap or non-overlap of error bars is not a universal significance test.

### Technical versus biological replication
Many technical repeats do not create the same inferential breadth as independent biological specimens, participants, sites, or cohorts.

### Hidden n
If n differs across groups or time points, the same-looking error bar can have a different meaning.

## Selection and presentation traps

### Representative image
A microscopy, imaging, waveform, qualitative field, or case image can illustrate a phenomenon but does not establish frequency or typicality without a sampling/quantification basis.

### Selected range or time window
Cropping the displayed range may hide reversals, baseline instability, startup transients, or later degradation.

### Best-run or best-configuration figure
A displayed best result is not an estimate of typical performance unless the selection rule and distribution across runs/configurations are also shown.

### Missing negative panels
A figure set can emphasize successful conditions while adverse or null configurations remain only in tables, supplements, or text.

## Image-specific traps

### Contrast and saturation
Brightness, contrast, gamma, color mapping, and clipping can change visual salience. Treat images as qualitative evidence unless intensity quantification and acquisition/processing are described.

### Pseudocolor
Color differences do not imply absolute differences unless the color scale is shared and quantitatively defined.

### Scale bars and magnification
Visual size comparisons require a valid scale bar or known common magnification.

### Composite or stitched images
Panel assembly, stitching, different exposures, or different acquisition settings can invalidate direct visual comparison unless clearly documented.

Do not infer manipulation or misconduct merely from appearance; state only what comparison is or is not justified.

## Scatter and line-plot traps

### Overplotting
Dense points can hide multiplicity and distribution. Transparency, jitter, or density views may be needed to infer concentration.

### Connected categories
Lines connecting unordered categories can imply continuity or trajectory that does not exist.

### Fitted line versus data
A regression line can look strong even with broad scatter. Check effect size, uncertainty, residual pattern, and sample distribution.

### Extrapolation
A fitted trend beyond the observed x-range is not directly supported by the plotted observations.

## Table-specific traps

### Adjusted versus unadjusted estimates
Do not compare estimates across rows/models without checking covariate sets and target estimands.

### Odds, risk, rate, hazard, and prevalence
These are not interchangeable. Similar-looking ratios can have different interpretations.

### Missing-data denominator
Complete-case analyses may silently change the population across rows or models.

### Multiple-testing display
A table with many comparisons can contain nominally significant findings expected by chance. Check multiplicity control when the paper makes selection claims from many tests.

## Visual-text consistency

Compare:
- caption
- axes and legend
- values shown
- nearby prose
- abstract/conclusion restatement

If the prose says "continuous increase" but the plotted points dip, or the caption calls a difference large while the axis exaggerates it, preserve the direct visual/numerical evidence and report the mismatch.

## Usage rule

Apply only traps relevant to a decision-critical figure or table. Do not produce a checklist dump in the final audit. State the concrete visual issue and how it changes the support judgment.
