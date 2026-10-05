21.5 ms becomes 344 ms when sixteen equal transfers share a 400 Gb/s bottleneck: the calculated wire-time floor for retrieving a 1 GiB KV prefix. Reusing compatible KV state is correct; assuming that a cache hit must beat recomputation is a stale scheduling policy.

The heuristic inherited its credibility from locality. Reusing tensors already in GPU memory avoids another prefill without buying a network transfer. Disaggregation preserves the reusable state while changing the price of reaching it.

For the same prefix becoming usable on the same worker, fetching loses when:

$$
\max(Q_g,Q_n+S/B_{\mathrm{eff}})+D>Q_g+C.
$$

Here $Q_g$ is GPU availability delay, $Q_n$ transfer queueing, $S$ transferred bytes, $B_{\mathrm{eff}}$ effective bandwidth, $D$ restoration time, and $C$ recomputation time. This model credits transfer overlap with GPU waiting; restoration follows complete transfer.

With zero queues and an illustrative 200 ms recomputation time, the sixteen-transfer case loses before restoration begins. Layer streaming requires comparing exposed critical paths. Neither advertised bandwidth nor a hit counter establishes the winner.

Compression, codec offload, prefetching, and cache affinity can improve individual paths. Their composition can also move contention into GPU execution, temporary memory, or popular workers. KVFetcher's evaluation reports decompression interference and fetching-induced blocking of unrelated requests. The architectural risk is asymmetric: the requesting stream captures saved computation while other streams absorb shared-resource delay. [KVFetcher](https://arxiv.org/html/2602.09725v1)

Make reuse a cluster admission decision. The coordinator needs cache locations, shared-link occupancy, worker queues, restoration costs, and latency budgets. It must compare:

- Fetching existing state, including delay imposed on competing transfers.
- Recomputing locally, including interference with active inference.
- Routing execution to resident state, including the destination's queue.

This direction already has foundations: CacheGen can fall back to recomputation, and Dynamo balances cache overlap against worker load. The next requirement is joint resource admission that prevents individually attractive transfers from collectively saturating a link. Independent controllers reacting to yesterday's available bandwidth can all approve tomorrow's overload. [CacheGen](https://arxiv.org/html/2310.07240v6), [Dynamo](https://docs.nvidia.com/dynamo/v1.0.0/components/router/router-guide)

The diagnostic blind spot is the counterfactual: how much faster would this request have completed through the rejected path? Record source tier, bytes, queueing, exposed transfer stalls, restoration time, and predicted recomputation latency; calibrate predictions with sampled replays. Hit-rate and transfer-time dashboards alone cannot establish benefit. Without that comparison, operators can celebrate rising reuse while diagnosing deteriorating first-token latency as insufficient network capacity.

Does your scheduler still fetch every valid prefix whose retrieval costs more than rebuilding it?

