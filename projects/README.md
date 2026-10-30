# Scientific research projects

**English** | [中文](README_ZH.md)

Each project organizes experiments around a specific scientific question: hypotheses, study scope, data references, comparisons, interpretation and human review. [Workflows](../workflows/README.md) provide reusable combinations of data and skills; projects reference those combinations and define what evidence the study needs. [Methods](../methods/README.md) supply scientific reasoning, and [skills](../skills/README.md) supply operational instructions.

## Numbering and identity

- Name directories `0001_<topic>`, `0002_<topic>` and so on, using a four-digit sequential number and a meaningful lowercase topic. Start at `0001`, allocate the next unused number, and retain existing numbers rather than renumbering or reusing them.
- The number is for display and navigation. It is separate from the four research stages and does not impose an execution order.
- Keep a stable `project_id` without the numeric prefix, matching the runner's lowercase identifier convention. Store both the display number and stable identifier in `project.json`; it connects the project directory with runner receipts and compatibility output locations.
- A project can reference several workflows and research stages. A workflow can serve several projects. Reference shared input versions rather than copying datasets or workflow code into each project.

## Project index

| Number | Scientific question | Stable project ID | Status |
|---|---|---|---|
| 0001 | [Environmental features and long-term ozone: predictive association and stability](0001_ozone_environmental_drivers/README.md) | `ozone_environmental_drivers` | First prediction and original-model comparison complete; provenance gaps and human review pending |

## Minimal contents

| File | Responsibility |
|---|---|
| `README.md` and `README_ZH.md` | Research question, scope, input/workflow references and current status |
| `project.json` | Display number, stable ID, fixed input versions, workflow/tool references and planned experiments |
| `study-plan.md` and `study-plan_ZH.md` | Hypotheses, comparison design, development/test separation and acceptance criteria |
| `review.md` and `review_ZH.md` | Pending review template and instructions for recording a human decision |
| `experiments/<experiment_id>/` (optional) | Shareable experiment protocols, prompts and reviewed study code; does not register tools or claim general orchestration support |
| `results/` (local/private) | Experimental code and settings, outputs, evaluation and review evidence; not shared automatically |

## Use and storage

1. Read the scientific question and study plan; define the permitted input scope, experiment design and compute budget.
2. Verify the named workflow and real tool ID. Create task-specific non-secret settings under `${AIRMOSAIC_CONFIG_DIR}/projects/<project_id>/`, using the referenced configuration example as a starting point.
3. Preview the registered tool, then run the authorized experiment with the stable project ID. Record its experiment label, configuration hash and run ID in private results.
4. Compare artifacts using the predefined scientific criteria. Keep human review and approved reuse distinct from process completion.

Experiments and their results belong to `projects/<number_topic>/`. Use its `results/` for generated code, configuration, metrics, predictions, figures and review evidence, choosing a layout suited to the study. This is an ownership convention, not a fixed output-file template. Private results stay in an external project directory; personal mappings stay outside Git. Repository project `results/` directories are Git-ignored, which does not itself authorize a runner to write there.

Human scientific review decides whether to revise an experiment, retain a result only in the project, release a report or include selected outputs in `assets/`. Keep the original experiment and its review record. Successful execution and file creation are not approval. Asset internals will be defined later; see the [result and review contract](../harness/assets.md).

Current adapters still use their existing external result locations. They do not yet write to the new project-directory layout, and Git-ignore rules do not bypass path checks. Existing project-specific examples describe their actual compatibility locations; retain historical outputs there until a separate migration is implemented and authorized. Public project files may include reviewed designs, protocols, code and references; private settings, research details, machine-specific paths, credentials and row-level results remain outside Git.

`project.json` is currently a human/agent reference manifest, not a CLI parameter file or automatically loaded project. Project discovery, multi-experiment orchestration, approval and data promotion are not implemented. Project files do not register tools or grant execution permission.

Choose folders and filenames for the study; no universal run/stage/tool hierarchy is imposed. Retain configurations, provenance and an artifact inventory. Current adapters retain their implemented output contracts until project-directory support is added.
