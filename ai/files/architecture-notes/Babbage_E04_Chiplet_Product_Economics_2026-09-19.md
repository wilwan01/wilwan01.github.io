# Known-Good Die Does Not Mean Known-Good Product

At 90% final yield, an illustrative $800 screened-die set plus $200 of assembly and test costs $1,111 per shipped package—more than a $1,000 delivered alternative. Assume equal qualifying performance, quality, volume, and no salvage. Known-good-die screening is sound; treating cheaper good dies as cheaper products is the stale policy.

The heuristic came from wafer economics: smaller dies discard less silicon around each defect, and reusable dies can amortize design expense across products. It still holds upstream. But chiplets add die-to-die area and power, package and test cost, assembly loss, and demand-dependent inventory. The crossover is not die yield; for sequential assembly and test gates, partitioning loses when

$$
\sum_{s=1}^{m}\frac{c_s}{\prod_{k=s}^{m}y_k}
+\frac{F+I}{V}>C_{\mathrm{reference}}.
$$

Here $c_s$ is cost added to a unit entering stage $s$; $y_k$ is conditional yield at gate $k$; $F$ is allocated development expense; $I$ is excess-inventory write-off; and $V$ is shipped volume. $C_{\mathrm{reference}}$ must describe an equally usable product, not a bare die. This no-salvage model correctly charges early value for every downstream failure.

The local patches are more screening, common packages, and broader chiplet reuse. Each can help; none is free. More patterns consume tester time, while weak intermediate coverage lets one latent bad die destroy healthy companions after assembly. In a modeled 16-chiplet case, CATCH found 95% fault coverage cheapest: 50% created excessive scrap, while still higher coverage raised test cost. [CATCH](https://arxiv.org/html/2503.15753v1) Reuse can invert similarly. Chiplet Actuary’s modeled package reuse reduced package NRE by two-thirds for its largest system but increased total cost by more than 20% for the smallest; the result depends on its stated architecture and 500,000-unit assumptions, not on a universal chiplet tax. [Chiplet Actuary](https://arxiv.org/html/2203.12268v4)

Move partitioning policy into a product-family optimizer spanning architecture, packaging, test, and demand. It must jointly choose boundaries and links against bandwidth, power, and delivered performance; place tests before irreversible value accumulation where avoided scrap exceeds tester cost; and select shared dies and packages against forecast bin mix, lead times, and salvage paths. A design team minimizing die cost cannot own that decision alone.

The missing diagnostic is value stranded at each failure gate, joined to die genealogy, fault coverage, assembly route, salvage outcome, and the saleable SKU displaced. Add tester and assembly minutes per shipped bin plus inventory aging by component compatibility. Without that ledger, teams celebrate wafer yield while misdiagnosing margin erosion as packaging inflation or weak demand.

Does your chiplet roadmap minimize the cost of a known-good die, or the cost of a qualifying product the market will absorb?
