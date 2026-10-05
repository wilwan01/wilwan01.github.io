# Babbage Research

## One CPU SKU Is Not One Latency Distribution

A 1% per-shard deadline-miss rate becomes 63.4% across 100 independent shards when every result is required. A CPU SKU remains a valid specification boundary; treating it as a unit of interchangeable service capacity is the stale policy.

The approximation worked when modest fan-out and spare capacity absorbed small differences. Equal core counts and nominal frequencies simplified qualification, procurement, and placement. At fleet scale, those labels can conceal persistent differences in the operating points that individual processors sustain.

A 2026 characterization of ten same-SKU Xeons reported up to 40 mV of voltage variation and nearly twofold leakage differences at 2 GHz and 50°C. These are electrical measurements, not evidence of an equivalent latency spread. The operational question is whether variation changes service capacity under the production power envelope. [Per-CPU characterization](https://arxiv.org/html/2606.11163v1)

For independent shard completion times, the placement policy violates a request miss budget $\epsilon$ when:

$$
1-\prod_{i=1}^{N}(1-p_i)>\epsilon.
$$

Here $p_i$ is shard $i$’s probability of missing its allocated deadline. For 100 identical distributions and a 1% request budget, each shard needs approximately 99.99% deadline compliance. Correlation requires measuring the joint distribution. Fan-out amplifies variability; it does not identify its cause.

Hedged requests, work stealing, and blanket headroom can absorb transient delays. Applied to persistent capacity differences, however, they can repeatedly purchase the same correction: duplicate execution, displaced warm state, and spare servers. A lagging worker creates work elsewhere precisely when queues are already stressed. Tail-tolerance techniques remain useful, but their resource costs belong in the capacity model. [The Tail at Scale](https://research.google/pubs/the-tail-at-scale/)

Make measured capability a contract between qualification, procurement, and scheduling. Characterize each host across workload classes and supported power limits, then assign work against its measured service envelope. A processor that trails on sustained vector work may remain suitable for a memory-bound service.

Qualification should establish repeatability and uncertainty; procurement should value the delivered distribution; placement should allocate latency-critical shards using the relevant capability class. Recharacterize after firmware, cooling, or configuration changes. A permanent “slow” label is another stale heuristic.

The missing diagnostic is a persistent, workload-conditioned service curve joined to effective frequency, package energy, throttling reasons, temperature, and queueing. Existing counters provide ingredients; they do not establish causality. Controlled replays must separate silicon effects from firmware, placement, and interference. Without that join, operators can misdiagnose stable capacity differences as noisy neighbors and keep adding replicas.

Does your scheduler buy capacity from the processor’s measured behavior, or from the name printed on its box?

---

## Known-Good Die Does Not Mean Known-Good Product

At 90% final yield, an illustrative \$800 screened die set plus \$200 of assembly and test becomes \$1,111 per shipped package, versus a \$1,000 delivered alternative. Assume equal qualifying performance and no salvage. Known-good-die screening is sound; equating cheaper good dies with cheaper products is the stale policy.

Smaller dies reduce the silicon discarded around a defect. Reusing those dies can spread design expense across products. But packaging, test, and die-to-die interfaces move cost beyond the wafer, while demand determines whether reuse actually amortizes anything. Chiplet Actuary explicitly models these competing effects. [Chiplet Actuary](https://arxiv.org/html/2203.12268v4)

For a sequence of assembly and test gates, the partition loses when:

$$
\sum_{s=1}^{m}\frac{c_s}{\prod_{k=s}^{m}y_k}
+\frac{F+I}{V}>C_{\mathrm{reference}}.
$$

Here $c_s$ is cost added per unit entering stage $s$, including screened components, interfaces, packaging, and test; $y_k$ is conditional yield at gate $k$; $F$ is allocated development expense; $I$ is excess-inventory write-offs; and $V$ is shipped volume. Compare equal performance, quality, and cost scope. This no-salvage model charges early costs for subsequent failures, without charging later operations to already rejected units. Upstream die yield is embedded in screened-component cost.

Longer screening and broader package reuse are useful local responses. Applied independently, they can defend the wrong objective. More test patterns consume tester time; an undetected defect can destroy the value of healthy companions after irreversible assembly. CATCH models precisely this coverage-versus-scrap tradeoff. [CATCH](https://arxiv.org/html/2503.15753v1)

Common packaging can make the smallest product pay recurring area cost to subsidize portfolio reuse. Chiplet Actuary’s modeled example raises that product’s total cost by more than 20%. [Chiplet Actuary](https://arxiv.org/html/2203.12268v4)

Move the decision to a product-family cost model with visibility across architecture, test, assembly, and demand:

- Choose partitions and interfaces against required bandwidth, power, and delivered performance.
- Place tests before irreversible value accumulation where avoided scrap justifies their cost.
- Select shared components and packages against realistic product volumes and bin demand.

The diagnostic gap is dollars stranded at each failure gate, linked to die genealogy, test coverage, salvage outcome, and the SKU that could actually have shipped. Add tester and assembly minutes per saleable bin. Separate yield dashboards cannot show whether better wafer economics merely relocated losses downstream. Without that linkage, teams celebrate die yield while blaming margin erosion on packaging prices or disappointing demand.

Does your chiplet roadmap minimize the cost of a good die, or the cost of a product someone will buy?

---

## The Cheapest Accelerator Can Waste the Most Expensive Megawatt

100 versus 125 equally productive inference nodes fit into 1 MW when their facility power allocations are 10 versus 8 kW. In this illustrative comparison, the second node costs 40% more. The hardware meets its specifications; maximizing throughput per purchase dollar becomes a stale deployment policy once power binds.

The purchasing heuristic works while capital limits deployment: buy more compute and budget electricity as an operating expense. A fixed electrical envelope introduces another constraint. For independently scaling replicas, achievable goodput is:

$$
G_i=g_i\min\left(\frac{K}{c_i},\frac{P}{w_i}\right).
$$

Here $K$ is equipment budget, $c_i$ deployed node cost, $P$ allocatable facility power, and $w_i$ each node’s power allocation, including networking, cooling, and reserve. $g_i$ is sustained throughput meeting identical model, quality, context, and latency requirements. Ignore integer rounding. MLPerf likewise distinguishes throughput under different first-token and inter-token latency limits. [MLCommons](https://mlcommons.org/2025/09/small-llm-inference-5-1/)

When both configurations are power-limited, the ranking becomes $g_i/w_i$. The premium fleet delivers 25% more goodput, but filling it requires 75% more capital. That trade becomes relevant when electrical capacity blocks additional business.

The local repair is to buy the bargain, then stack power caps, oversubscription, and admission exceptions around it. These controls can work: Google’s coordinated production design enabled at least 25% power oversubscription. [Google Research](https://research.google/pubs/data-center-power-oversubscription-with-a-medium-voltage-power-plane-and-priority-aware-capping/) The failure is treating reclaimed watts as free capacity while preserving the original throughput assumption. Correlated demand can trigger throttling across replicas simultaneously; queueing then converts a modest service-rate reduction into latency failures. Procurement books the discount while operations inherits the performance debt.

Move the decision into joint procurement and capacity planning, with runtime enforcement:

- Evaluate hardware at feasible power caps against the actual workload mix.
- Allocate electrical headroom using measured additional goodput per watt.
- Include shared network, cooling, rack limits, and deployment dates before buying.

This coordinator must also distinguish unavailable electrical capacity from available capacity that the current placement cannot use. Average facility efficiency cannot resolve a constrained rack.

The missing measurement is the response curve: how many additional requests meet their latency budget when this workload receives another kilowatt? Join time-aligned power, cap residency, queueing, and completed-request telemetry, then calibrate controlled changes in allocation. Accelerator utilization and average watts cannot answer that question. Without it, operators diagnose a procurement-induced capacity loss as scheduler inefficiency and request more machines that the site cannot power.

Does your procurement scorecard still reward the cheapest node for occupying the megawatt that limits your business?

