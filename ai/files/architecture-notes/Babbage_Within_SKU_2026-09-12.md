10 ms versus 50 ms mean response time: at 900 requests/s, an illustrative M/M/1 queue makes that jump when service capacity falls from 1,000 to 920 requests/s. Power management correctly enforces electrical limits; treating one CPU SKU as interchangeable service capacity is the stale policy.

SKU-based allocation made sense when specification bins, spare capacity, and shallow request graphs absorbed modest differences. That shortcut weakens near saturation. In June 2026, Crop and colleagues reported up to 40 mV voltage variation across ten same-SKU Xeons at matched frequency and temperature. That establishes electrical heterogeneity—not an 8% capacity deficit or a latency forecast. [Measurements](https://arxiv.org/html/2606.11163v1#S3)

For independent, stationary M/M/1 shard queues, an all-results-required request violates its miss-rate budget when

$$
1-\prod_{i=1}^{N}\left[1-e^{-(\mu_i-\lambda_i)D}\right]>\epsilon.
$$

Here $\lambda_i<\mu_i$ are arrival and service rates, $D$ is the remaining deadline after fixed network and aggregation overhead, and $\epsilon$ is the allowed request miss probability. With 100 shards, 900 requests/s each, and a 100 ms budget, uniform 1,000-request/s capacity yields a calculated 0.45% miss rate. One 920-request/s shard raises it to 13.9%. An 8% local deficit breaches a 1% global budget. Shared arrivals, rack throttling, and correlated interference invalidate independence; production requires the joint distribution. Regardless of dependence, that slow shard alone imposes a 13.5% lower bound.

Hedged requests, replica retries, and blanket headroom can defend the endpoint. They also consume the capacity whose scarcity amplifies the defect. Hedging remains useful for transient stragglers; repeatedly hedging a persistently weak host becomes an operating subsidy. Tail-tolerant execution already addresses variability, and PAL demonstrates workload-aware placement in GPU clusters; the architectural step is connecting qualification to allocation. [Tail at Scale](https://research.google/pubs/the-tail-at-scale/) · [PAL](https://arxiv.org/abs/2408.11919)

Move the decision into fleet admission and placement. Procurement acceptance should measure workload-specific service curves across supported power limits, then expose capability classes to schedulers. Allocate traffic and replica groups against measured capacity, network locality, and correlated failure domains. Avoid a universal “fast silicon” ranking: a host’s advantage must be measured for the work assigned. Reclassify after firmware or cooling changes.

The missing diagnostic is a per-host counterfactual: how would the same request stream perform at matched temperature, power limit, NUMA placement, and software state? Join queue wait and service time with APERF/MPERF effective-frequency counters, package energy, throttle reasons, memory traffic, and workload identity. Controlled replay and component swaps must separate persistent silicon effects from cooling, firmware, and interference. Without that attribution, operators blame software regressions or fabric congestion and purchase more nominal capacity.

Does your scheduler allocate measured service capacity, or merely count identical labels?
