# Prompt Guard 2 — license notice

Meta **Llama Prompt Guard 2** (86M / 22M) is released under the **Llama Community
License Agreement**, and the model repository is **gated** on Hugging Face.

Before building the image or publishing the episode:

1. Visit the model page (`meta-llama/Llama-Prompt-Guard-2-86M`) and accept the license.
2. Build with an HF token that has accepted access:
   `docker build --build-arg HF_TOKEN=hf_xxx ./firewalls/prompt-guard-2`
3. Do not redistribute the weights; the image is for the local, offline lab only.
4. Attribute Meta and link the license in the blog/video description.

The weights are baked into the image solely so the lab runs with `internal: true`
(no runtime network). Nothing about this lab circumvents the license or gating.
