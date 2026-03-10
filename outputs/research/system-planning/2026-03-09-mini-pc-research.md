# Mini PC Research for Self-Hosting & Home Lab (2025-2026)

**Date:** 2026-03-09
**Purpose:** Comprehensive research on mini PCs for self-hosting automation (n8n, Docker), home servers, and home labs.

---

## TL;DR Recommendation

For your use case (n8n automation, Docker containers, 24/7 low-power operation):

- **Best budget pick:** Beelink EQ14 (N150, 16GB, 500GB) ~$189-229
- **Best value pick:** Beelink SER5 (Ryzen 5 5500U, 16GB, 500GB) ~$200-250
- **Best mid-range:** Beelink SER5 MAX (Ryzen 7 7735HS, 24GB, 500GB) ~$300-390
- **Best if you want headroom:** MinisForum UM790 Pro (Ryzen 9 7940HS) ~$351-440
- **Best enterprise-grade (used):** Dell OptiPlex 7070/7080 Micro or HP EliteDesk 800 G5 Mini ~$100-200

An N100/N150 system is **more than enough** for n8n + a dozen Docker containers at 8-12W idle. If you want headroom for future services (Proxmox, VMs, media server), step up to the SER5 or SER5 MAX.

---

## 1. Budget Tier ($50-150)

### Used Enterprise Machines (Best Value in This Tier)

| Model | CPU | Typical Price | RAM | Notes |
|-------|-----|---------------|-----|-------|
| **Dell OptiPlex 7050 Micro** | i5-7500T / i7-7700T | $60-120 | Up to 32GB | Older but rock-solid; eBay/refurb |
| **Dell OptiPlex 7060 Micro** | i5-8500T / i7-8700T | $80-150 | Up to 64GB | Sweet spot for used market |
| **HP EliteDesk 800 G4 Mini** | i5-8500T / i7-8700T | $70-130 | Up to 64GB | Better thermals than Dell |
| **HP ProDesk 600 G3 Mini** | i5-7500T | $50-90 | Up to 32GB | Cheapest viable option |
| **Lenovo ThinkCentre M720q** | i5-8400T / i7-8700T | $80-140 | Up to 64GB | MIL-SPEC tested durability |

**Why used enterprise machines at this price point:**
- Built for 24/7 operation in corporate environments
- Excellent thermal design and reliability
- ECC memory support on some models (ThinkCentre)
- Full vPro/AMT remote management
- Massive supply on eBay/Amazon Renewed = low prices
- 10-20% cheaper than equivalent Dell models when buying HP

**Where to buy:** eBay, Amazon Renewed, Micro Center (refurbished), Newegg refurbished

### Raspberry Pi 5 (8GB)

| Spec | Detail |
|------|--------|
| **Board only** | $95 (8GB), $75 (4GB) |
| **Complete kit** | $120-180 (with case, PSU, cooling, SD card) |
| **With NVMe SSD** | $150-200 (CanaKit assembled desktop PC) |
| **CPU** | Broadcom BCM2712, Cortex-A76 quad-core @ 2.4GHz |
| **Power** | 5-12W |

**Pros:**
- Lowest power consumption (~5W idle)
- Huge community and ecosystem
- GPIO for hardware projects

**Cons:**
- RAM is NOT upgradeable (8GB max)
- ARM architecture limits some x86 Docker images
- Once you add case + PSU + SSD + HAT, total cost approaches a mini PC
- An N100 mini PC beats it in every CPU benchmark at similar total cost
- Limited to lightweight workloads; struggles with 10+ containers

**Verdict:** For pure automation (n8n only), a Pi 5 works. But for the same $140-180 total cost, an N100 mini PC gives you x86 compatibility, more RAM, and better performance.

### Intel N100 / N150 Budget Mini PCs

| Model | CPU | Price | RAM | Storage | Key Feature |
|-------|-----|-------|-----|---------|-------------|
| **Beelink Mini S12 Pro** | N100 | ~$150-190 | 16GB DDR4 | 500GB SATA SSD | Cheapest Beelink; single 1GbE |
| **Beelink EQ12** | N100 | ~$180-210 | 16GB DDR5 | 500GB SSD | **Dual 2.5GbE**, WiFi 6 |
| **GMKtec G3** | N100 | ~$140-170 | 8-16GB | 256-512GB | Budget; community reports 6-8W idle |

**N100 specs:** 4 cores / 4 threads, up to 3.4GHz, 6W TDP, Intel UHD graphics
**N150 specs:** 4 cores / 4 threads, up to 3.6GHz, 6W TDP (6-10% faster than N100)

**Power consumption (measured):**
- Idle (headless): 6-8W
- Mixed workloads: 9-11W
- Peak load: 25-30W
- **Annual cost at 10W 24/7: ~$12/year** (at US electricity rates)

---

## 2. Mid Tier ($150-300)

| Model | CPU | Price | RAM | Storage | Key Features |
|-------|-----|-------|-----|---------|-------------|
| **Beelink EQ14** | N150 | $189-229 | 16GB DDR4 | 500GB SSD | Dual 2.5GbE, WiFi 6, WOL/PXE |
| **Beelink SER5** | Ryzen 5 5500U (6C/12T) | $200-250 | 16GB DDR4 | 500GB NVMe | Best bang-for-buck; triple display |
| **Beelink SER5** | Ryzen 5 5500U (6C/12T) | $260-300 | 32GB DDR4 | 500GB NVMe | 32GB variant |
| **Beelink EQi12** | i5-1235U (10C/12T) | ~$479 (official) | 16GB DDR4 | 500GB SSD | Intel Iris Xe; more cores |
| **Beelink EQR6** | Ryzen 5 6600U (6C/12T) | ~$439-499 | 24-32GB LPDDR5 | 500GB-1TB | Soldered RAM |
| **Used Dell OptiPlex 7070 Micro** | i5-9500T / i7-9700T | $120-200 | Up to 64GB | NVMe + 2.5" | Enterprise reliability |
| **Used HP EliteDesk 800 G5 Mini** | i5-9500T / i7-9700T | $110-180 | Up to 64GB | NVMe + 2.5" | Better sustained clocks |
| **Used Lenovo M920q Tiny** | i5-8500T / i7-8700T | $130-200 | Up to 64GB | NVMe | Micro Center refurb ~$190 |

**Best pick in this tier: Beelink SER5 (Ryzen 5 5500U, 16GB)**
- 6 cores / 12 threads is massive overkill for n8n but gives headroom
- ~$200-250 on Amazon
- 2.5GbE, WiFi 6, triple display
- Upgradeable RAM (up to 64GB on some variants)
- Community-proven for Proxmox, Docker, Home Assistant
- Power draw: ~15-20W idle, ~45W load

---

## 3. High-End Tier ($300-600+)

| Model | CPU | Price | RAM | Storage | Key Features |
|-------|-----|-------|-----|---------|-------------|
| **Beelink SER5 MAX** | Ryzen 7 7735HS (8C/16T) | $300-390 | 24GB LPDDR5 | 500GB-1TB | Sweet spot for power users |
| **Beelink SER5 MAX** | Ryzen 7 6800U (8C/16T) | $350-445 | 24-32GB LPDDR5 | 500GB-1TB | Newer variant |
| **MinisForum UM790 Pro** | Ryzen 9 7940HS (8C/16T) | $351-440 | Configurable | Configurable | Often on sale; barebone available |
| **Beelink SER7** | Ryzen 7 7840HS (8C/16T) | $400-500 | 32GB | 1TB | USB4 x2, 2.5GbE |
| **Beelink SER8** | Ryzen 7 8745HS (8C/16T) | $500-600 | 32GB | 1TB | Latest gen; USB4, 2.5GbE |
| **Geekom A7** | Ryzen 9 7940HS (8C/16T) | $400-550 | Up to 64GB | Up to 2TB | Geekom build quality |
| **Geekom Mini IT13** | i9-13900HK (14C/20T) | $600-850 | 32GB DDR4 | 1TB | Quad display; USB4 |
| **MinisForum MS-01** | i9-13900H (14C/20T) | $549-829 | Up to 64GB DDR5 | 3x NVMe | **Dual 10GbE SFP+**, PCIe x16 slot |

**Standout: MinisForum MS-01** ($549 barebone / $829 configured)
- Dual 10GbE SFP+ + dual 2.5GbE (4 network ports total)
- PCIe x16 expansion slot (add a GPU, NIC, HBA)
- 3x NVMe slots (including U.2)
- The "homelab king" according to ServeTheHome
- Overkill for n8n, but ideal if you want a proper Proxmox cluster node

---

## 4. Premium / Enthusiast Tier ($600+)

| Model | CPU | Price | RAM | Key Features |
|-------|-----|-------|-----|-------------|
| **Beelink SER9 Pro** | Ryzen AI 9 365 (10C/20T) | $729-929 | 32GB LPDDR5X | 73 TOPS NPU; USB4 |
| **Beelink SER9 MAX** | AMD (high-end) | ~$969 | 64GB DDR5 | Top-tier Beelink |
| **Beelink SER10 MAX** | Latest AMD | $1,259-1,699 | 32-64GB DDR5 | Flagship |
| **MinisForum MS-A2** | Ryzen 9 9955HX (16C/32T) | ~$2,000+ | Up to 96GB | Dual 10G SFP+; PCIe x16 |
| **ASUS NUC 15 Pro** | Core Ultra 7 255H (16C/22T) | ~$1,500+ | Up to 96GB DDR5 | WiFi 7; Thunderbolt 4 |
| **Geekom Mini IT13** | i9-13900HK (14C/20T) | $600-850 | 32GB | Best Buy carries it |

---

## 5. Intel NUC Status (2025-2026)

**Intel exited the NUC business in July 2023.** ASUS took over:

- ASUS now manufactures and sells NUC systems under license
- NUC 12 Pro was discontinued by end of 2024
- Current ASUS NUC lineup uses Core Ultra Series 2 processors
- **ASUS ROG NUC** announced for CES 2026 with RTX 5090 mobile GPU (gaming/AI focus)
- NUC 15 Pro and NUC 15 Performance are the current models (~3-liter case)

**For homelab purposes:** NUCs are now overpriced relative to Beelink/MinisForum equivalents with the same CPUs. The NUC brand premium no longer reflects better hardware quality since ASUS took over.

---

## 6. Brand Comparison & Reliability

### Tier List (Community Consensus)

| Tier | Brands | Notes |
|------|--------|-------|
| **A - Enterprise** | Dell, HP, Lenovo (used/refurbished) | Built for 24/7; best long-term reliability; firmware updates |
| **B - Reliable Consumer** | Beelink, MinisForum, Geekom | Good quality; decent support; community-proven |
| **C - Budget/Caution** | GMKtec, Trigkey, ACEMAGIC | Lower prices but support issues; buy via Amazon for returns |
| **D - Avoid** | No-name brands, ACEMAGIC (malware incidents) | Security concerns; poor/no support |

### Brand-Specific Notes

**Beelink:**
- Most popular Chinese mini PC brand for homelabs
- OK-to-good customer support; generally honors warranty
- Some thermal issues on first-batch releases of new CPU models
- Clean Windows installs (no spyware found in independent testing)
- Best bought through Amazon for easy returns

**MinisForum:**
- Higher-end models are excellent (MS-01 is legendary)
- Support can be spotty; reports of rejected warranty claims
- Some customers asked to pay return shipping to China
- Hardware quality is generally good

**GMKtec:**
- Cheapest option but "dubious past for support and security vulnerabilities"
- Engineering described as "chaotic without joined-up thinking"
- Slow customer support response times
- Best for tech-savvy buyers who can self-troubleshoot
- Buy ONLY through Amazon for buyer protection

**Geekom:**
- Higher build quality than Beelink/MinisForum
- Intel NUC-like design philosophy
- More expensive but better fit-and-finish
- Good for people who want a "premium" feel

**ACEMAGIC:**
- **WARNING: Documented malware found pre-installed on units**
- Multiple independent reviewers found trojans in the Windows install
- Avoid entirely

---

## 7. What the Self-Hosted Community Recommends

### For Docker Containers (n8n, Home Assistant, etc.)

**Consensus: Intel N100/N150 or Ryzen 5 5500U**

- n8n needs: 2 CPU cores + 2GB RAM minimum; 4 cores + 8GB recommended for production
- A 16GB N100 system comfortably runs 10-15 containers
- A 16GB Ryzen 5 system comfortably runs 20-40 containers
- Most homelab users **never max out an N100**

### For 24/7 Low-Power Operation

| System | Idle Power | Load Power | Annual Cost (24/7) |
|--------|-----------|-----------|-------------------|
| Raspberry Pi 5 | 3-5W | 10-12W | $5-8 |
| N100 mini PC | 6-8W | 25-30W | $8-12 |
| N150 mini PC | 7-9W | 25-30W | $9-13 |
| Ryzen 5 5500U | 12-18W | 40-55W | $15-22 |
| Ryzen 7 7735HS | 15-25W | 50-65W | $20-30 |
| Used Dell/HP i5-8500T | 10-15W | 35-50W | $12-18 |

*Based on ~$0.14/kWh US average*

### For Quiet/Silent Operation

- **N100/N150 systems:** Often fanless or near-silent (fan rarely spins up)
- **Beelink EQ series:** Named for "Energy saving & Quiet" philosophy
- **Used Dell/HP/Lenovo:** Small fans but very quiet; designed for office environments
- **Ryzen systems:** Fan audible under load but quiet at idle
- **Worst:** High-end Ryzen 7/9 under sustained load

### Community "Just Buy This" Recommendations (Reddit/YouTube)

1. **Cheapest possible:** Used Dell OptiPlex 7060 Micro from eBay ($80-120)
2. **Best new budget:** Beelink EQ14 or Mini S12 Pro (~$189)
3. **Best all-around:** Beelink SER5 with Ryzen 5 5500U (~$200-250)
4. **Best if you want VMs:** Beelink SER5 MAX or MinisForum UM790 Pro (~$300-400)
5. **Best for serious homelab:** MinisForum MS-01 (~$549-829)

---

## 8. Key Specs People Care About

| Spec | Why It Matters | What to Look For |
|------|---------------|-----------------|
| **TDP/Power** | 24/7 electricity cost | N100 (6W) vs Ryzen 5 (15W) vs Ryzen 7 (35-45W) |
| **RAM expandability** | Future-proofing | SODIMM slots (upgradeable) vs soldered (fixed) |
| **NVMe slots** | Storage expansion | 1 slot minimum; 2 slots ideal; MS-01 has 3 |
| **Ethernet speed** | Network performance | 2.5GbE preferred; dual NICs for VLANs; 10GbE for NAS |
| **USB ports** | External devices | USB 3.2 minimum; USB4 for future devices |
| **WiFi** | Backup connectivity | WiFi 6 minimum; most homelabs use wired ethernet |
| **Noise** | 24/7 in living space | Fanless N100 > small fan Ryzen > active cooling i9 |
| **VESA mount** | Attach behind monitor | Most mini PCs include VESA bracket |

---

## 9. Common Warnings & Pitfalls

### General
- **Always do a fresh OS install** on Chinese mini PCs (even reputable brands)
- **Buy through Amazon** for easy returns and buyer protection
- **Check RAM type before buying:** LPDDR5 = soldered (not upgradeable), DDR4/DDR5 SODIMM = upgradeable
- **Beelink official store prices are often HIGHER than Amazon** — always compare
- **First-batch thermal issues:** Wait 1-2 months after a new model launches for thermal fixes

### N100-Specific
- Some N100 mini PCs use SATA SSDs (slower) instead of NVMe — check specs
- N100 has only 4 threads; fine for Docker but struggles with many concurrent VMs
- If considering N100 vs N150 in 2026: get N150 — only ~6-10% faster but same price tier

### Ryzen-Specific
- Ryzen LPDDR5 models have soldered RAM — cannot upgrade later
- Ryzen 5 5500U/5560U are Zen 3 (older); 6600U/6800U are Zen 3+ (RDNA2 iGPU); 7735HS is Zen 3+ refreshed
- For pure server use, the iGPU doesn't matter — don't pay extra for better graphics

### Used Enterprise
- Check generation carefully: 8th gen i5 (Coffee Lake) is the minimum worthwhile
- Some used units come without drive caddies or power adapters — verify listing includes them
- Dell Micro and HP Mini use different power bricks — non-interchangeable

### Security
- No confirmed hardware-level backdoors in Beelink/MinisForum/GMKtec
- Pre-installed Windows may contain bloatware but not malware (except ACEMAGIC)
- **ACEMAGIC had confirmed pre-installed trojans** — avoid entirely
- For maximum security: install Linux (Proxmox, Ubuntu Server, Debian) fresh

---

## 10. Specific Model Quick Reference

| Model | CPU | Cores/Threads | RAM | Storage | Price Range | Best For |
|-------|-----|--------------|-----|---------|------------|---------|
| Raspberry Pi 5 (8GB) | BCM2712 Cortex-A76 | 4C/4T | 8GB (fixed) | External | $95-180 (kit) | Minimal; learning |
| Beelink Mini S12 Pro | Intel N100 | 4C/4T | 16GB DDR4 | 500GB SATA | $150-190 | Budget Docker host |
| Beelink EQ12 | Intel N100 | 4C/4T | 16GB DDR5 | 500GB SSD | $180-210 | Budget + dual 2.5GbE |
| Beelink EQ14 | Intel N150 | 4C/4T | 16GB DDR4 | 500GB SSD | $189-229 | Best new budget pick |
| GMKtec NucBox G3/G5 | Intel N100/N150 | 4C/4T | 8-16GB | 256-512GB | $140-200 | Cheapest new option |
| Dell OptiPlex 7060 Micro (used) | i5-8500T | 6C/6T | 8-32GB | Varies | $80-150 | Best used value |
| HP EliteDesk 800 G5 (used) | i5-9500T | 6C/6T | 8-64GB | Varies | $110-180 | Reliable 24/7 |
| Lenovo M920q Tiny (used) | i5-8500T | 6C/6T | 8-64GB | NVMe | $130-200 | Enterprise quality |
| Beelink SER5 | Ryzen 5 5500U | 6C/12T | 16-32GB DDR4 | 500GB NVMe | $200-300 | Best all-around value |
| Beelink SER5 MAX | Ryzen 7 7735HS | 8C/16T | 24GB LPDDR5 | 500GB-1TB | $300-390 | Power user sweet spot |
| MinisForum UM790 Pro | Ryzen 9 7940HS | 8C/16T | Configurable | Configurable | $351-440 | High-end AMD |
| Beelink SER7 | Ryzen 7 7840HS | 8C/16T | 32GB | 1TB | $400-500 | USB4 + 2.5GbE |
| Beelink SER8 | Ryzen 7 8745HS | 8C/16T | 32GB | 1TB | $500-600 | Latest gen Ryzen |
| Geekom A7 | Ryzen 9 7940HS | 8C/16T | Up to 64GB | Up to 2TB | $400-550 | Premium build |
| Geekom Mini IT13 | i9-13900HK | 14C/20T | 32GB DDR4 | 1TB | $600-850 | Maximum Intel perf |
| MinisForum MS-01 | i9-13900H | 14C/20T | Up to 64GB DDR5 | 3x NVMe | $549-829 | Homelab king; 10GbE |
| Beelink SER9 Pro | Ryzen AI 9 365 | 10C/20T | 32GB LPDDR5X | 1TB | $729-929 | AI/NPU workloads |

---

## Sources

- [PC Build Advisor - Best Mini PC for Home Server](https://www.pcbuildadvisor.com/best-mini-pc-for-home-server-the-ultimate-guide-with-comparisons/)
- [PC Build Advisor - Best Mini PC for Self-Hosting 2026](https://www.pcbuildadvisor.com/best-mini-pc-for-self-hosting-in-2026-the-ultimate-guide/)
- [PC Build Advisor - Do Chinese Mini PCs Have Spyware?](https://www.pcbuildadvisor.com/do-chinese-mini-pcs-have-spyware/)
- [PC Build Advisor - Best Mini PC Manufacturers](https://www.pcbuildadvisor.com/what-are-the-best-mini-pc-manufacturers-minisforum-beelink-geekom-gmktec-aoostar-acemagic-trigkey-reviewed/)
- [Bitdoze - Best Mini PC for Home Server 2026](https://www.bitdoze.com/best-mini-pc-home-server/)
- [TerminalBytes - Best Mini PCs for Home Lab 2025](https://terminalbytes.com/best-mini-pcs-for-home-lab-2025/)
- [Virtualization HowTo - Ultimate Home Lab Starter Stack 2026](https://www.virtualizationhowto.com/2025/12/ultimate-home-lab-starter-stack-for-2026-key-recommendations/)
- [Virtualization HowTo - Best Mini PCs for Home Labs 2025](https://www.virtualizationhowto.com/2025/11/the-best-mini-pcs-for-home-labs-in-2025-ranked-by-real-performance/)
- [ServeTheHome - MinisForum MS-01 Review](https://www.servethehome.com/minisforum-ms-01-review-the-10gbe-with-pcie-slot-mini-pc-intel/)
- [ServeTheHome - Beelink SER7 Review](https://www.servethehome.com/beelink-ser7-review-a-smaller-and-cheaper-amd-ryzen-7-7840hs-mini-pc/)
- [ServeTheHome - Project TinyMiniMicro](https://www.servethehome.com/introducing-project-tinyminimicro-home-lab-revolution/)
- [XDA - Docker Containers on $100 Mini PC](https://www.xda-developers.com/docker-containers-that-run-247-on-my-100-mini-pc/)
- [XDA - Stop Buying Raspberry Pi 5s](https://www.xda-developers.com/mini-pc-outperforms-raspberry-pi-5-at-similar-price/)
- [Jeff Geerling - N100 vs Raspberry Pi Value](https://www.jeffgeerling.com/blog/2025/intel-n100-better-value-raspberry-pi)
- [DIY Tech Guru - N100 vs N305](https://www.diytechguru.com/intel-n100-vs-n305-mini-pcs/)
- [Marc Ismal - N150 vs N100](https://marcismal.com/223/n150-better-in-2025-vs-n100-mini-pcs/)
- [Hobbyist's Hideaway - N100 Power Consumption Guide](https://bishalkshah.com.np/blog/low-power-homelab-n100-mini-pc)
- [2ndboot - Mini PC Buying Guide 2026](https://2ndboot.com/mini-pc-buying-guide-2026/)
- [2ndboot - OptiPlex vs EliteDesk](https://2ndboot.com/dell-optiplex-vs-hp-elitedesk/)
- [Hardware Corner - OptiPlex vs EliteDesk vs ThinkCentre](https://www.hardware-corner.net/guides/optiplex-vs-elitedesk-prodesk-vs-thinkcentre/)
- [Beelink Official Store](https://www.bee-link.com/collections/product)
- [MinisForum Official Store](https://store.minisforum.com/)
- [Geekom Official Store](https://www.geekompc.com/)
- [ASUS NUC Transition FAQ](https://www.asus.com/us/support/faq/1053028/)
- [Neowin - Beelink EQ14 Review](https://www.neowin.net/reviews/beelink-eq14-review-office-class-mini-pc-powered-by-the-new-intel-twin-lake-n150/)
- [Neowin - AceMagic/Beelink/Geekom Malware Testing](https://www.neowin.net/news/we-tested-acemagic-beelink-and-geekom-mini-pcs-with-several-anti-malware-programs/)
- [TechRadar - Best Mini PCs 2026](https://www.techradar.com/best/mini-pcs)
- [Liliputing - Geekom A7 Review](https://liliputing.com/geekom-a7-review-this-amd-ryzen-7000u-mini-pc-hits-the-sweet-spot/)
- [Latenode - n8n System Requirements 2025](https://latenode.com/blog/low-code-no-code-platforms/n8n-setup-workflows-self-hosting-templates/n8n-system-requirements-2025-complete-hardware-specs-real-world-resource-analysis)
- [Edywerder - MinisForum MS-01 Review](https://edywerder.ch/minisforum-ms-01-review/)
