# AMD AI Infrastructure Architecture, 2023–2026

**Research cutoff:** 27 September 2026; includes Advancing AI 2026 and product documentation available by this date.

**Example prompt:** “Research AMD’s AI infrastructure architecture from 2023 through September 2026 for an experienced datacenter architect. Trace each EPYC and Instinct generation, then connect the GPU fabric, Pensando NICs and DPUs, adaptive silicon, rack designs, and ROCm. Normalize throughput and bandwidth, distinguish shipping from announcements, and identify engineering trade-offs using conference and primary technical disclosures.”

**Scope:** L1 EPYC and L2 Instinct: deep. L3 Infinity Fabric and UALink/UALoE: full. L4 Pensando DPUs and AI NICs: full. L5 Xilinx/Alveo/Versal: proportional. L6 systems and L7 software: full at generation level. The period starts in 2023; Genoa’s 2022 launch is retained as a baseline. Client Radeon and embedded derivatives are excluded except when they explain shared IP. AMD has no separately marketed AI scale-up switch generation comparable to a merchant Ethernet switch in this period; its Helios UALoE switch is covered as part of the system.

## Executive synthesis

AMD moved from selling CPUs and accelerators into specifying the whole AI node and then the rack. The EPYC 9004/9005 SP5 socket preserved 12 DDR5 channels and PCIe 5.0 as core counts rose from 96 to 192. This squeezed *peak memory bandwidth per core*: 460.8/96 = 4.8 GB/s for DDR5-4800 Genoa, versus 576/192 = 3.0 GB/s at DDR5-6000 Turin. Dense cores therefore principally buy throughput on workloads with locality or modest bytes per instruction. Venice/EPYC 9006 changes platform balance with up to 256 cores, up to 16 DDR5 channels and PCIe 6, targeting both host-node orchestration and many concurrent agents. The advertised 1.6 TB/s is a family upper bound, not a promise that every 256-core SKU reaches it.

Instinct MI300X established a capacity-led eight-GPU node: 192 GB HBM3 and 5.3 TB/s per GPU. MI325X retained CDNA 3 compute while raising memory to 256 GB HBM3E and 6 TB/s. MI350/355 introduced CDNA 4, lower-precision formats and 288 GB/8 TB/s; the air-cooled MI350X fits the older UBB8 platform, whereas MI355X needs 1.4 kW liquid cooling. MI455X and Helios move the design boundary to 72 GPUs, 432 GB HBM4 each, 23.3 TB/s each, and an open UALoE scale-up network. The older 2025 Helios preview gave 19.6 TB/s per GPU; the 2026 product page gives 23.3 TB/s. These are different disclosure vintages.

The main engineering bet is a split fabric: tightly coupled GPUs inside the rack; programmable Ethernet for inter-rack collectives; a DPU on the front end for security, storage and isolation. Its risks are software and network maturity, high-density power/cooling, and delivering usable rather than peak fabric bandwidth. AMD's own ROCm and cluster reference guides make clear that topology, collective algorithms, partitioning, and acceptance tests matter as much as peak GPU FLOPs.

| Era / flagship | Host cores, peak DDR | Accelerator dense BF16 / FP8 | HBM per GPU | Scale-up domain |
|---|---|---|---|---|
| 2023 Genoa + MI300X | 96; 460.8 GB/s at DDR5-4800 | 1.3 / 2.61 PFLOP/s | 192 GB, 5.3 TB/s | 8 GPU UBB |
| 2024 Turin + MI325X | 192; 576 GB/s at DDR5-6000 | 1.3 / 2.61 PFLOP/s | 256 GB, 6 TB/s | 8 GPU UBB |
| 2025 Turin + MI355X | 192; 576 GB/s at DDR5-6000 | ~5 / ~10 PFLOP/s, format-dependent | 288 GB, 8 TB/s | 8 GPU UBB |
| 2026 Venice + MI455X | up to 256; up to 1.6 TB/s, SKU-dependent | FP16 matrix 5 / OCP FP8 20.1 PFLOP/s; BF16 figure n/d here | 432 GB, 23.3 TB/s | 72 GPU Helios |

**Normalization:** all accelerator rates above are peak, per GPU and *without structured sparsity*. OCP FP8 and legacy FP8 are identified separately where needed. CPU bandwidth is theoretical peak per socket; no achievable benchmark is implied.

## L1 — EPYC host CPUs

**Genoa and its 2023 branches.** EPYC 9004 Genoa, launched in 2022, provides the relevant SP5 baseline: Zen 4 CCDs around a separate I/O die; up to 96 cores, twelve DDR5-4800 channels and 128 PCIe 5.0 lanes. Bergamo (2023) uses denser Zen 4c CCDs for 128 cores and less L3 per core, retaining the memory/I/O platform. Genoa-X stacks L3 for cache-sensitive workloads and Siena/EPYC 8004 trades maximum socket I/O and memory width for a smaller, power-oriented server socket. These branches establish that “more cores” and “more cache” were different SKU responses to different bottlenecks.

**Turin / EPYC 9005 (GA October 2024).** Zen 5 and Zen 5c variants reach 192 cores in SP5, retaining the 12-channel DDR5 platform; selected configurations advertise DDR5-6400 but AMD's 2024 deck says broad production SKUs support DDR5-6000. The 192-core 9965 is a 500 W part. Zen 5’s wider front end and execution resources improve per-core work, while Zen 5c emphasizes density. The platform continuity accelerates adoption but makes bandwidth per core a deployment variable: use socket-level bandwidth, NUMA locality and actual DIMM rate rather than core count alone to predict KV staging or data-preparation throughput.

**Venice / EPYC 9006 (launched July 2026).** AMD advertises Zen 6/6c, up to 256 cores/512 threads, up to 16 DDR5 channels, PCIe 6 and up to 1.6 TB/s per socket. Its product page distinguishes SP7 and SP8 models, and a host-focused LP option. Do not assign the 16-channel maximum or 1.6 TB/s to every SP8/LP configuration: the exact memory channels, lanes, clocks, cache and TDP must be taken from the selected SKU datasheet. The architectural direction is wider memory and I/O to rebalance CPU throughput with accelerator feeding. Effective STREAM bandwidth, per-hop CCD-to-memory latency, CXL topology, and per-SKU limits remain procurement questions.

| Generation | Codename | GA | Status | Core µarch | Max cores/threads | Process (per die) | Chiplets and packaging | L2 per core | L3 (total; per sharing domain) | Memory (type, channels, speed, peak GB/s) | Sockets and socket links | PCIe/CXL | Max TDP | Matrix/vector ISA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EPYC 9004 | Genoa | 2022 | Shipping | Zen 4 | 96/192 | CCD 5 nm; IOD 6 nm | up to 12 CCD + IOD, organic substrate | 1 MB | 384 MB; 32 MB/CCX | DDR5, 12, 4800, 460.8 | 1–2; IF socket links | PCIe 5, 128 lanes; CXL 1.1 | 400 W class | AVX-512, BF16 |
| EPYC 9004 dense | Bergamo | 2023 | Shipping | Zen 4c | 128/256 | CCD 5 nm; IOD 6 nm | 8 dense CCD + IOD | 1 MB | 256 MB; 16 MB/CCX | DDR5, 12, 4800, 460.8 | 1–2; IF socket links | PCIe 5 / CXL 1.1 | 360 W class | AVX-512, BF16 |
| EPYC 9004 cache | Genoa-X | 2023 | Shipping | Zen 4 | 96/192 | CCD 5 nm; IOD 6 nm | 3D V-Cache CCD + IOD | 1 MB | up to 1,152 MB; 96 MB/CCX | DDR5, 12, 4800, 460.8 | 1–2; IF socket links | PCIe 5 / CXL 1.1 | 400 W class | AVX-512, BF16 |
| EPYC 9005 | Turin | Oct 2024 | Shipping | Zen 5/5c | 192/384 | compute 4 nm / 3 nm variants; IOD n/d here | CCD + IOD, SP5 | 1 MB | SKU-dependent; n/d here | DDR5, 12, 6000 general, 576; 6400 selected, 614.4 | 1–2; IF links | PCIe 5 / CXL | 500 W | AVX-512, BF16 |
| EPYC 9006 | Venice | Jul 2026 launch | Launched; SKU availability varies | Zen 6/6c | up to 256/512 | n/d per die | SP7/SP8 family | n/d | n/d | up to 16 DDR5; up to 1,600 family peak | SKU-dependent | PCIe 6; CXL details n/d | n/d here | n/d |

The fixed schema intentionally retains “n/d” where the evidence inspected for this example does not establish a specific number. The 2026 launch is not evidence that every SKU or OEM platform is generally available.

## L2 — Instinct accelerators

**MI300A and MI300X (2023).** MI300A combines 24 Zen 4 cores and CDNA 3 graphics compute dies with a unified HBM pool, removing a discrete CPU–GPU copy boundary for HPC codes that can exploit shared data structures. MI300X allocates the package to GPU throughput and HBM capacity, using eight HBM3 stacks, 192 GB, 5.3 TB/s and 256 MB last-level cache. Its eight-device UBB uses Infinity Fabric peer connections and PCIe 5 to the host. The architecture uses stacked base/I/O dies and compute dies: package yield, HBM capacity and inter-die traffic become product-level design issues.

**MI325X (October 2024).** The same CDNA 3 compute configuration (304 CUs, 1.3 PFLOP/s BF16 and 2.61 PFLOP/s FP8 dense) gets 256 GB HBM3E and 6 TB/s at 1 kW peak TBP. This is principally a memory step, not a new compute architecture. For decode and long contexts, the extra 64 GB per GPU can alter tensor-parallel partitioning and offload decisions even when nominal FLOPs are unchanged.

**MI350X and MI355X (June 2025).** CDNA 4 updates matrix formats and compute dies (3 nm compute, 6 nm supporting dies). Both offer 288 GB HBM3E and 8 TB/s. The MI350X uses a 1 kW air-cooled tray designed to fit MI325X systems; MI355X offers a 1.4 kW direct liquid cooled, denser tray. That platform fork is consequential: liquid cooling raises rack GPU count, so a near-similar chip can yield a much larger rack throughput difference. CDNA 4 also adds microscaling FP4/FP6. The exact FP8 standard matters when comparing nominal rates across vendors.

**MI455X / MI400 family (announced July 2026).** CDNA 5, 256 work-group processors, TSMC 2 nm and 3 nm die technologies, 12 HBM4 stacks and 432 GB/23.3 TB/s per GPU. AMD gives 20.1 PFLOP/s dense OCP FP8 and 40.3 PFLOP/s OCP MXFP4; a separate 5 PFLOP/s matrix FP16 number is available. These are peak rates, not measured model throughput. MI455X is designed for the 72-device Helios rack, so GPU evaluation must include software partitioning, switch and NIC behavior, cooling and end-to-end serving/training efficiency.

| Generation | Codename/arch | GA | Status | Process | Dies and packaging | Compute units | Dense BF16 | Dense FP8 | Dense FP6/FP4 | FP64 (vector/matrix) | HBM (gen, stacks, GB, TB/s) | Last-level cache | Scale-up (links, GB/s per direction, domain) | Host link | TBP and cooling | Form factor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MI300A | CDNA 3 | Dec 2023 launch | Shipping | 5/6 nm | CPU+GPU dies atop supporting dies | 228 GPU CUs + 24 Zen 4 cores | n/d here | n/d here | n/a | n/d here | HBM3, 8, 128, 5.3 | 256 MB class | IF; per-link direction n/d, integrated node | integrated | package power n/d here | APU module |
| MI300X | CDNA 3 | Dec 2023 launch | Shipping | 5/6 nm | 8 GPU compute dies, stacked base dies | 304 CUs | 1.3 PF/s | 2.61 PF/s | n/a | 163.4 TF/s matrix | HBM3, 8, 192, 5.3 | 256 MB | 8 links; AMD quotes 128 GB/s/link without direction clarified here; 8 GPU | PCIe 5 x16 | 750 W peak, passive | OAM/UBB8 |
| MI325X | CDNA 3 | Oct 2024 launch | Shipping | 5/6 nm | as MI300X | 304 CUs | 1.3 PF/s | 2.61 PF/s | n/a | 163.4 TF/s matrix | HBM3E, 8, 256, 6 | 256 MB | IF, 8 GPU; direction n/d | PCIe 5 x16 | 1,000 W peak, passive | OAM/UBB8 |
| MI350X | CDNA 4 | Jun 2025 launch | Shipping | 3/6 nm | GPU chiplets with supporting dies | 256 CUs | n/d here | n/d here | MXFP4 supported; rate n/d here | n/d here | HBM3E, 8, 288, 8 | n/d here | IF, 8 GPU; direction n/d | PCIe 5 | 1,000 W air | OAM/UBB8 |
| MI355X | CDNA 4 | Jun 2025 launch | Shipping | 3/6 nm | GPU chiplets with supporting dies | 256 CUs | n/d here | ~10 PF/s OCP FP8 | ~10.1 PF/s MXFP4/MXFP6 | n/d here | HBM3E, 8, 288, 8 | n/d here | IF, 8 GPU; direction n/d | PCIe 5 | 1,400 W direct liquid | OAM/UBB8 |
| MI455X | CDNA 5 | n/d | Announced July 2026 | 2/3 nm | 3.5D, 12 HBM4 stacks | 256 WGPs | n/d here | 20.1 PF/s OCP FP8 | 20.1 PF/s MXFP6; 40.3 PF/s MXFP4 | n/d here | HBM4, 12, 432, 23.3 | n/d | UALoE, 72 GPU; per-link n/d | system integrated | n/d here; rack liquid | Helios module |

**Derived memory balance.** MI300X: 5.3 TB/s ÷ 1.3 PF/s = 0.00408 byte per dense BF16 FLOP; ÷2.61 PF/s = 0.00203 byte per FP8 FLOP. MI325X: 0.00462 and 0.00230 respectively. For MI455X, 23.3 TB/s ÷20.1 PF/s OCP FP8 = 0.00116 byte/FLOP. This compares peak memory to peak compute; it is neither arithmetic intensity of a model nor an achieved roofline. The format definitions and hardware utilization change across generations.

## L3–L4 — scale-up and networking

The MI300–MI350 server node uses an eight-way Infinity Fabric GPU domain; the GPU connects to its CPU via PCIe 5. Helios extends tightly coupled scale-up to 72 MI455X GPUs through UALoE, with 18 independent stations per GPU and a claimed 260 TB/s *aggregate rack fabric* figure. That rack aggregate cannot be substituted for per-GPU unidirectional bandwidth. Its resilience and partitioning depend on AMD Fabric Manager and Fabric OS.

Pensando's earlier Elba/Giglio generations provide the acquired DPU foundation; Salina is the current front-end DPU, accelerating network security, virtual networking and NVMe/KV extension. Pollara 400 is an Ethernet AI NIC for existing scale-out deployments; Vulcano 800 is the Helios AI NIC. AMD quotes up to 2.4 Tb/s of scale-out bandwidth **per GPU** in a specific Helios configuration; that is 300 GB/s per GPU after dividing bits by eight, before protocol overhead, and is an endpoint configuration claim, not the speed of one 800G NIC. Solarflare low-latency adapters and Alveo SmartNICs remain relevant inherited lines but are not the main training backend.

| Product | GA | Status | Class | Ports × speed | SerDes | Host interface | Programmable engine | Embedded CPU | On-card memory | Transport/RDMA | Congestion control | Key offloads | Power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pensando Elba/Giglio | pre-2023 / n/d | Shipping legacy | DPU | n/d | n/d | PCIe | P4 lineage | n/d | n/d | Ethernet | n/d | virtual networking, security, storage | n/d |
| Pensando Salina | n/d | Announced/product brief | DPU/front end | 2×400G or 4×200G among options | NRZ/PAM4 | n/d here | programmable P4 | n/d | n/d | Ethernet | n/d | security, SDN, storage/NVMe | n/d |
| Pensando Pollara 400 | n/d | Product brief | AI NIC/backend | 400G class | n/d | n/d | programmable | n/d | n/d | Ethernet/RDMA | programmable; algorithm n/d | collective-aware network features | n/d |
| Pensando Vulcano 800 | n/d | Announced July 2026 | AI NIC/backend | 800G class | n/d | n/d | third-gen P4 family | n/d | n/d | Ethernet | n/d | Helios scale-out | n/d |

| Name/version | Year | Lane rate | Lanes per link | GB/s per link per direction | Links per device | Topology | Max domain | Coherence/memory semantics |
|---|---|---|---|---|---|---|---|---|
| Infinity Fabric GPU peer, MI300–350 | 2023–25 | n/d | n/d | n/d; AMD's 128 GB/s link figure lacks direction here | 8 on MI300X | fully connected UBB8 | 8 GPUs | peer memory access; exact coherence semantics n/d |
| UALoE, Helios | 2026 | n/d | n/d | n/d | 18 stations/GPU | switched single-hop | 72 GPUs | UALink over Ethernet; detailed ordering/coherence contract n/d |

## L5–L7 — adaptive compute, systems and software

The 2022 Xilinx acquisition brought Versal adaptive SoCs and Alveo cards into AMD. In this era they support embedded inference, network processing and specialized acceleration, but they are not substitutes for the HBM-rich Instinct training node. The 2022 Pensando acquisition brought the programmable DPU and networking software lineage. AMD acquired ZT Systems in 2025 to accelerate rack-level design and integration, then sold the US manufacturing operation to Sanmina. This is a change in system-design capability, not the addition of a new AMD-owned foundry or OEM server line.

| Platform | Year | CPUs/accelerators | Scale-up domain | Scale-out per accelerator | Rack power | Cooling |
|---|---|---|---|---|---|---|
| MI300X/325X UBB8 | 2023–24 | EPYC host, 8 GPUs | eight-way IF | deployment-specific | n/d | air/passive OAM |
| MI350X / MI355X UBB8 | 2025 | EPYC host, 8 GPUs | eight-way IF | deployment-specific | AMD reference examples 120–200 kW by density | MI350X air; MI355X liquid |
| Helios | 2026 launch | 18 Venice CPUs, 72 MI455X GPUs | 72 via UALoE, 260 TB/s aggregate rack claim | up to 2.4 Tb/s per GPU configuration | n/d authoritative installed load | direct liquid |

**Era stacks.** 2023–24: EPYC SP5 → PCIe 5 → 8× MI300X/325X on IF UBB → external Ethernet NICs; Pensando DPU handles front-end infrastructure; ROCm/HIP/RCCL and cluster management span the node. 2025: Turin + MI350 UBB, with Pollara and Salina options; 1.4 kW liquid-cooled MI355X allows denser racks. 2026: Venice + 72× MI455X → UALoE switch fabric within Helios → Vulcano Ethernet between racks; Salina on front-end/storage paths; ROCm, Fabric Manager/OS and rack telemetry coordinate the stack.

| Era | On-die | Die-to-die | GPU HBM per device | CPU–GPU | Scale-up per GPU | Scale-out per GPU |
|---|---|---|---|---|---|---|
| 2023–24 MI300X/325X | n/d | n/d | 5.3 / 6 TB/s | PCIe 5 x16; theoretical 64 GB/s each direction before overhead | IF link 128 GB/s as quoted; direction unresolved | deployment-specific |
| 2025 MI355X | n/d | n/d | 8 TB/s | PCIe 5 x16 | IF, per-direction n/d | deployment-specific |
| 2026 Helios | n/d | n/d | 23.3 TB/s | integrated system, per-link n/d | 260 TB/s rack aggregate; per-GPU direction n/d | up to 2.4 Tb/s = 300 GB/s configuration peak |

| Release | Date | Hardware enabled | Key features |
|---|---|---|---|
| ROCm CDNA 3 generation | 2023–24 | MI300A/X, MI325X | HIP, matrix formats, RCCL and framework integration |
| ROCm CDNA 4 generation | 2025 | MI350/355 | lower-precision microscaling support, optimized inference/training libraries |
| ROCm + Fabric Manager/OS | 2026 | MI455X/Helios | 72-GPU provisioning, telemetry, recovery and virtual GPU pods |

The software row is intentionally at generation level: exact minimum ROCm, driver, firmware, framework and RCCL versions must be matched to a chosen platform release before qualification.

## Trends and trade-offs

1. **Packaging and memory.** Stacked MI300 dies enabled large HBM capacity and shared MI300A CPU/GPU memory, but add thermal and die-to-die complexity. The MI455X 12-stack HBM4 design amplifies supply and packaging exposure.
2. **Bytes per FLOP.** HBM bandwidth rose from 5.3 to 23.3 TB/s, while dense OCP FP8 peak rose more sharply from 2.61 to 20.1 PFLOP/s. The falling peak bytes/FLOP increases pressure for reuse, low precision and topology-aware placement.
3. **Power as topology.** MI350X's air-cooled compatibility reduces upgrade friction; MI355X's liquid cooling raises rack density. A procurement comparison at the single-device level misses this system effect.
4. **Fabric boundary.** Eight-way direct IF gives way to a 72-way switched UALoE domain. Open protocol promises supplier flexibility, while switch silicon, fault recovery and software collectively determine the usable domain.
5. **CPU role.** EPYC is simultaneously an accelerator host, a memory and storage orchestrator, and an agent execution engine. Venice's extra channels and PCIe bandwidth reflect host-side pressure, but SKU-specific bandwidth and latency matter more than the family maximum.

## Conference-to-product index

This is an **index of research targets and verified disclosure channels**, not a claim that every product was presented at every venue. Venue-specific talk titles and presenter names are left n/d unless located in the public material inspected.

| Venue | Year | Paper or talk | Presenters | Product/generation | Disclosure type | Link |
|---|---|---|---|---|---|---|
| Advancing AI | 2024 | Distribution deck | n/d | Turin / MI325X | launch/specifications | https://www.amd.com/content/dam/amd/en/documents/corporate/events/advancing-ai-2024-distribution-deck.pdf |
| Advancing AI | 2025 | Distribution deck | n/d | MI350 / Helios preview | product/system roadmap | https://www.amd.com/content/dam/amd/en/documents/corporate/events/advancing-ai-2025-distribution-deck.pdf |
| Advancing AI | 2026 | AMD launch and product sessions | n/d | Venice, MI455X, Helios, Vulcano, Salina | product/system | https://www.amd.com/en/corporate/events/advancing-ai.html |
| Hot Chips / IEEE Micro | 2023–26 | generation-specific papers: title verification pending | n/d | MI300, EPYC and networking | architecture | https://www.hotchips.org/ |
| ISSCC / JSSC | 2023–26 | generation-specific papers: title verification pending | n/d | Zen, packaging, MI300 | circuit/implementation | https://www.isscc.org/ |

**Conference coverage gap:** This demonstration located vendor technical whitepapers and event decks, but did not verify the exact Hot Chips/ISSCC paper inventory, slide versions, or presenter lists. Thus it does not assert circuit dimensions, die-to-die energy or circuit-level values merely because the skill calls for those venues. A publication-grade conference index requires that targeted retrieval pass.

## Codename crosswalk

| Codename / architecture | Market name | Relevant identity |
|---|---|---|
| Genoa / Zen 4 | EPYC 9004 | standard SP5, up to 96 cores |
| Genoa-X / Zen 4 | EPYC 9004 X variants | 3D V-Cache |
| Bergamo / Zen 4c | EPYC 9004 97x4 | density branch |
| Siena / Zen 4c | EPYC 8004 | smaller server platform |
| Turin / Zen 5, Zen 5c | EPYC 9005 | SP5, up to 192 cores |
| Venice / Zen 6, Zen 6c | EPYC 9006 | SP7/SP8 family, up to 256 cores |
| CDNA 3 | MI300A, MI300X, MI325X | APU branch and GPU capacity refresh |
| CDNA 4 | MI350X, MI355X | microscaling formats; cooling split |
| CDNA 5 | MI455X / MI400 series | Helios HBM4 accelerator |
| Pollara / Vulcano | Pensando 400 / 800 AI NIC | scale-out Ethernet |
| Salina | Pensando DPU | front-end/storage offload |

## Claims ledger (selected audit rows)

| Claim | Value | Basis | Source | Disclosure date | Status |
|---|---|---|---|---|---|
| MI300X memory | 192 GB, 5.3 TB/s | per accelerator, HBM3 peak | AMD MI300X product page | Dec 2023 | shipping |
| MI300X compute | BF16 1.3; FP8 2.61 PF/s | per accelerator, dense peak | AMD MI300X product page | Dec 2023 | shipping |
| MI325X memory | 256 GB, 6 TB/s | per accelerator, HBM3E peak | AMD MI325X product page | Oct 2024 | shipping |
| MI355X cooling | 1,400 W direct liquid | TBP, reference tray | AMD CDNA 4 whitepaper | Jun 2025 | shipping |
| MI455X memory | 432 GB, 23.3 TB/s | per accelerator HBM4, peak; newer than 2025 preview | AMD MI455X product page | Jul 2026 | announced |
| MI455X OCP FP8 | 20.1 PF/s | dense peak per accelerator | AMD MI455X product page | Jul 2026 | announced |
| Helios scale-up | 72 GPUs; 260 TB/s | aggregate rack claim, direction unspecified | AMD networking overview | Jul 2026 | announced |
| Helios scale-out | up to 2.4 Tb/s/GPU | configuration aggregate, divide by eight to GB/s | AMD networking overview | Jul 2026 | announced |
| Venice maximum | 256 cores, 16 channels, up to 1.6 TB/s | family maxima, not same SKU guaranteed | AMD EPYC 9006 pages | Jul 2026 | launched; SKU GA varies |

## Bibliography and source keys

**Vendor technical documentation:** [EPYC 9004 architecture overview](https://www.amd.com/content/dam/amd/en/documents/epyc-technical-docs/tuning-guides/58015-epyc-9004-tg-architecture-overview.pdf); [EPYC 9005 architecture whitepaper](https://www.amd.com/content/dam/amd/en/documents/epyc-business-docs/white-papers/5th-gen-amd-epyc-processor-architecture-white-paper.pdf); [EPYC 9006 family](https://www.amd.com/en/products/processors/server/epyc/9006-series.html); [MI300X](https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html); [MI325X](https://www.amd.com/en/products/accelerators/instinct/mi300/mi325x.html); [CDNA 4 architecture whitepaper](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf); [MI355X](https://www.amd.com/en/products/accelerators/instinct/mi350/mi355x.html); [MI455X](https://www.amd.com/en/products/accelerators/instinct/mi400/mi455x.html); [MI3XX cluster reference](https://instinct.docs.amd.com/projects/MI3XX-reference/latest/index.html); [Salina brief](https://www.amd.com/content/dam/amd/en/documents/pensando-technical-docs/product-briefs/pensando-salina-product-brief.pdf); [Pollara brief](https://www.amd.com/content/dam/amd/en/documents/pensando-technical-docs/product-briefs/pensando-pollara-400-product-brief.pdf).

**Company events and systems:** [2024 Advancing AI deck](https://www.amd.com/content/dam/amd/en/documents/corporate/events/advancing-ai-2024-distribution-deck.pdf); [2025 Advancing AI deck](https://www.amd.com/content/dam/amd/en/documents/corporate/events/advancing-ai-2025-distribution-deck.pdf); [2026 Advancing AI announcement](https://ir.amd.com/news-events/press-releases/detail/1294/aai-2026-amd-delivers-full-stack-compute-for-the-agentic-ai-era); [AMD Helios](https://www.amd.com/en/products/rackscale-solutions/helios.html); [AMD AI networking](https://www.amd.com/en/blogs/2026/ai-networking-built-for-scale.html); [CDNA 5 and Helios software overview](https://rocm.blogs.amd.com/ecosystems-and-partners/cdna5-helios/README.html).

**Conference materials:** The specific Hot Chips and ISSCC archival entries remain to be located and verified. No unpublished or paywalled circuit details are attributed to them in this report.
