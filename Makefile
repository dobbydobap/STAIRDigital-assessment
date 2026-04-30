.PHONY: install run api ui test eval docker-build docker-run clean

install:
	pip install -e ".[dev]"
	python -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)"

api:
	uvicorn pdfagent.api.app:app --host 0.0.0.0 --port 8000 --reload

ui:
	streamlit run pdfagent/ui/streamlit_app.py --server.port 8501

run:
	@echo "Start API and UI in separate terminals: 'make api' and 'make ui'"

test:
	pytest tests/ -v

eval:
	python eval/run_eval.py

docker-build:
	docker build -t pdfagent:latest .

docker-run:
	docker run --rm -p 8000:8000 -p 8501:8501 \
		-e ANTHROPIC_API_KEY=$$ANTHROPIC_API_KEY \
		-v $$(pwd)/data:/app/data pdfagent:latest

clean:
	rm -rf data/chroma data/traces *.egg-info build dist
	find . -type d -name __pycache__ -exec rm -rf {} +
