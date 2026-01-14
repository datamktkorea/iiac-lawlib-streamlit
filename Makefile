.PHONY: help eval-phoenix eval-langfuse eval-harness

LLM_TYPE ?= OpenAI
MODEL_VERSION ?= gpt-4o-mini

DATASET ?= eval/datasets/template.json
MAX_SAMPLES ?=
TAGS ?=

PHOENIX_TEST_TYPE ?= llm
PHOENIX_QUESTION ?= What is Incheon International Airport Corporation?
PHOENIX_PORT ?= 6006
PHOENIX_PROJECT ?= iiac-lawlib
PHOENIX_NO_UI ?=

HARNESS_TASK ?= iiac_mcq
HARNESS_LIMIT ?=
HARNESS_OUTPUT ?= eval/results/lm_eval_results.json

help:
	@echo "Targets:"
	@echo "  eval-phoenix   Run arize-phoenix LLM/RAG test"
	@echo "  eval-langfuse  Run Langfuse evaluation"
	@echo "  eval-harness   Run lm-evaluation-harness evaluation"
	@echo ""
	@echo "Variables (examples):"
	@echo "  make eval-phoenix PHOENIX_TEST_TYPE=rag PHOENIX_NO_UI=1"
	@echo "  make eval-langfuse DATASET=eval/datasets/template.json MAX_SAMPLES=5"
	@echo "  make eval-harness HARNESS_TASK=hellaswag HARNESS_LIMIT=10"

eval-phoenix:
	uv run python eval/run_phoenix_eval.py \
		--test-type $(PHOENIX_TEST_TYPE) \
		--question "$(PHOENIX_QUESTION)" \
		--llm-type $(LLM_TYPE) \
		--model-version $(MODEL_VERSION) \
		--port $(PHOENIX_PORT) \
		--project-name $(PHOENIX_PROJECT) \
		$(if $(PHOENIX_NO_UI),--no-ui,)

eval-langfuse:
	uv run python eval/run_langfuse_eval.py \
		--dataset $(DATASET) \
		--llm-type $(LLM_TYPE) \
		--model-version $(MODEL_VERSION) \
		$(if $(MAX_SAMPLES),--max-samples $(MAX_SAMPLES),) \
		$(if $(TAGS),--tags $(TAGS),)

eval-harness:
	uv run python eval/run_lm_eval_harness.py \
		--task $(HARNESS_TASK) \
		--llm-type $(LLM_TYPE) \
		--model-version $(MODEL_VERSION) \
		--output $(HARNESS_OUTPUT) \
		$(if $(HARNESS_LIMIT),--limit $(HARNESS_LIMIT),)
