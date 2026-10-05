# The Cheapest Accelerator Can Waste the Most Expensive Megawatt

One hundred 10 kW inference nodes or 125 equally productive 8 kW nodes fit inside a 1 MW facility envelope. In this illustrative comparison, the 8 kW node costs 40% more. The hardware meets its specification; maximizing throughput per purchase dollar becomes a stale deployment policy once power binds.

The purchasing heuristic works while capital limits deployment: buy more compute and treat electricity as operating expense. A fixed electrical envelope introduces a second constraint. For independently scaling replicas, achievable SLO-qualified goodput is

$$
G_i=g_i\min\left(\frac{K}{c_i},\frac{P}{w_i}\right).
$$

Here $K$ is equipment budget, $c_i$ deployed node cost, $P$ allocatable facility power, and $w_i$ each node’s facility allocation, including networking, cooling, conversion loss, and reserve. $g_i$ is sustained throughput at identical model, quality, context, first-token latency, and inter-token latency requirements. Ignore integer rounding. MLPerf likewise qualifies LLM throughput against explicit TTFT and TPOT limits. [MLCommons](https://mlcommons.org/2025/09/small-llm-inference-5-1/)

When both choices are power-limited, the ranking collapses to $g_i/w_i$. The 8 kW fleet supplies 25% more goodput, but costs 75% more to fill the megawatt: $125\times1.4/(100\times1.0)=1.75$. That premium is rational when electrical capacity, not cash, blocks incremental revenue.

The local repair is to buy the bargain, then layer power caps, oversubscription, and admission exceptions around it. These controls can work: Google reported 25% or higher oversubscription from a production co-design spanning a medium-voltage power plane and priority-aware capping. [Google Research](https://research.google/pubs/data-center-power-oversubscription-with-a-medium-voltage-power-plane-and-priority-aware-capping/) The mistake is treating reclaimed watts as free capacity while preserving uncapped throughput assumptions. Correlated demand can throttle replicas together; queueing then converts a modest service-rate reduction into latency failures. Procurement books the discount while operations inherits the performance debt.

Move the decision into joint procurement and capacity planning, with runtime enforcement:

- Benchmark hardware at feasible power caps against the actual workload mix.
- Allocate electrical headroom by measured marginal SLO-qualified goodput per watt.
- Price shared network, cooling, rack limits, and usable deployment dates before ordering.

The coordinator must distinguish unavailable site power from available power stranded by rack topology or placement. Fleet-average PUE cannot resolve a constrained power domain.

The missing diagnostic is the power-response curve: how many additional requests meet their latency budget when this workload receives another kilowatt? Join time-aligned facility power, cap residency, queue depth, throttling state, and completed-request telemetry; calibrate the curve with controlled allocation changes. Utilization and average watts cannot answer the counterfactual. Without it, operators misdiagnose procurement-induced capacity loss as scheduler inefficiency and request machines the site cannot energize.

Does your procurement scorecard still reward the cheapest node for occupying the megawatt that limits your business?
