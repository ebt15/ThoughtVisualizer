# ThoughtVisualizer

A failed experiment that tried to improve LLM reasoning. Wanted to enhance Claude-3.5-Sonnet's ability to tackle unseen problems without training it on reasoning tags. The results show minimal improvements but offer some insights into LLM reasoning limitations.

## What It Does

- Shows the model's thought process step by step
- Produces slightly (but not impressively) better reasoning
- Exports the entire thought process as markdown files

## What It Can't Do

- Handle more than 2 chat exchanges (no chunking implemented)
- Dramatically improve reasoning quality

## Key Findings

To improve LLM reasoning, the evidence suggests:
1. Models need direct training on reasoning examples
2. Training should include explicit `<reasoning>`...`</reasoning>` tags
3. Real human reasoning patterns are necessary, not just prompt engineering

## Installation

### Local Setup (5 minutes)

1. Clone and enter:
```bash
git clone https://github.com/ebt15/ThoughtVisualizer.git
cd ThoughtVisualizer
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API key:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

5. Run:
```bash
python app.py
```

### Docker Setup (2 minutes)

One command:
```bash
docker-compose up --build
```

Access at: http://localhost:7860

## How It Works

A straightforward prompt pipeline:
1. Sends problem to Claude 3.5
2. Gets response
3. Reviews if the reasoning makes sense
4. If not satisfied, tries again
5. Repeats until reaching a good answer or max attempts

The model reviews reasoning (not the output) and uses higher temperature (0.7-1.0) for exploration.

## Notes

The experiment shows:
- Prompt engineering alone can't solve reasoning limitations
- Better training data with explicit reasoning examples is needed
- Meta-cognitive prompting provides minimal improvements
