# Public data and synthetic assets

**English** | [中文](README_ZH.md)

`assets/` is the reuse entry for selected outputs accepted through human scientific review. Experiments and their results belong to the corresponding project. Internal asset organization will be defined later; existing public examples below remain unchanged.

| Input kind | Declaration | Use |
|---|---|---|
| Published data | [public-data-manifest.json](public-data-manifest.json) | Reviewed source, license, attribution, exact file sizes and hashes; read-only inputs |
| Synthetic examples | [toy-manifest.json](toy-manifest.json) | Explicitly synthetic fixtures and reference CSVs; read-only inputs |

[AQ-Bench v1](data/03_atmospheric_transport/AQ-Bench/v1/README.md) is the current authorized published snapshot. It retains its CC BY 4.0 license and source credit. The external working copy and repository copy share the same dataset/version layout and CSV hashes. This deliberate public mirror does not authorize copying other private data, source mappings, credentials or scientific results. No automatic synchronization is implemented; changes require an explicitly reviewed new version.

The runner accepts only selected manifest-listed CSVs with matching hashes. Unlisted/changed files and unsafe paths are rejected. These manifests are input allowlists, not acquisition tools, automatic data-catalog registrations or scientific acceptance. Public data are not synthetic examples.

Start with the [synthetic walkthrough](../harness/usage/toy-demo.md) or the [repository-input regression preview](../config/examples/run-tool/aq-bench-repository.json). The four-row synthetic example has dimensionless values and reference weighted mean 40/3; it remains distinct from observations.

Keep experimental results and review records with the [project](../projects/README.md). Current runners retain their implemented external destinations and do not fall back to writing unreviewed results here. Human review of asset inclusion and public release are separate decisions. This revision does not move existing files; see the [result and review contract](../harness/assets.md).