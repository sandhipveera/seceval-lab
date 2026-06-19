# Security Lab — task runner (Docker-first). Run `make help`.
SHELL := /bin/bash
.DEFAULT_GOAL := help
EP ?=

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n",$$1,$$2}'
	@echo ""
	@echo "  Most targets take EP=<episode-folder>, e.g.  make lab-up EP=01-mcp-agent-security"

# ---- episode labs (Docker) ----
lab-up: ## Bring up an episode's lab:  make lab-up EP=<folder>
	@cd episodes/$(EP)/lab && docker compose up -d --build && docker compose ps

lab-gateway: ## Bring up the lab incl. runtime gateway:  make lab-gateway EP=<folder>
	@cd episodes/$(EP)/lab && docker compose --profile gateway up -d --build

lab-down: ## Tear down an episode's lab:  make lab-down EP=<folder>
	@cd episodes/$(EP)/lab && docker compose --profile gateway down -v

lab-logs: ## Tail lab logs:  make lab-logs EP=<folder>
	@cd episodes/$(EP)/lab && docker compose logs -f

# ---- video pipeline ----
voiceover: ## ElevenLabs narration + captions for an episode:  make voiceover EP=<folder>
	@cd video && python3 voiceover/generate_voiceover.py --script ../episodes/$(EP)/script.yaml --out ./build/$(EP)
	@cd video && python3 assemble/make_captions.py ./build/$(EP)

record: ## Record browser scenes:  make record EP=<folder>
	@cd video && node record/record_scenes.js --manifest ./build/$(EP)/manifest.json --out ./build/$(EP)/video

video: ## Assemble final mp4:  make video EP=<folder>
	@cd video && assemble/build_video.sh ./build/$(EP)

# ---- authoring ----
new-episode: ## Scaffold an episode folder:  make new-episode SLUG=<NN-slug>
	@mkdir -p episodes/$(SLUG)/lab && cp episodes/_TEMPLATE/* episodes/$(SLUG)/ 2>/dev/null || true
	@echo "created episodes/$(SLUG) (copy structure from 01-mcp-agent-security if no _TEMPLATE)"

status: ## Show every episode's pickup status
	@for f in episodes/*/STATUS.yaml; do printf "%-32s " "$$(dirname $$f | xargs basename)"; grep '^status:' $$f; done

.PHONY: help lab-up lab-gateway lab-down lab-logs voiceover record video new-episode status
