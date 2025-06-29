# Business Validator AI Agent

A multi-agent AI system that validates business ideas using Python and `pyautogen`. The system performs market research, competitive analysis, SWOT analysis, and provides strategic recommendations.

## Features

- **Multi-Agent Workflow**: Five specialized AI agents coordinate to validate business ideas
- **Web Research**: Uses DuckDuckGo search for market and competitor data
- **Structured Output**: Generates formatted validation reports
- **Markdown Export**: Saves results to markdown files
- **No Additional API Keys**: Uses DuckDuckGo for web search

## Agent Roles

1. **Clarifier**: Refines and clarifies the business idea
2. **MarketResearcher**: Analyzes market trends and opportunities
3. **CompetitorScout**: Identifies and analyzes competitors
4. **SWOTAnalyst**: Performs SWOT analysis
5. **FeedbackAgent**: Provides strategic feedback and suggestions

## Prerequisites

- Python 3.10 or higher
- pyenv and pyenv-virtualenv
- OpenAI API key

## Installation

1. **Create project directory**:

   ```bash
   mkdir business_validator_agent
   cd business_validator_agent
   ```

2. **Set up Python environment**:

   ```bash
   pyenv virtualenv 3.10.12 business-validator-env
   pyenv local business-validator-env
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage

### Basic Usage

Run the business validator:

```bash
python business_validator.py
```

Enter your business idea when prompted.

### Example Input

```
Enter your business idea: an AI tool that helps coffee shops choose locations
```

### Example Output

The system generates a report containing:

- **Clarified Business Idea**: Refined concept with value proposition
- **Market Research**: Market size, trends, and opportunities
- **Competitive Analysis**: Direct and indirect competitors
- **SWOT Analysis**: Strengths, weaknesses, opportunities, threats
- **Strategic Feedback**: Improvement suggestions and next steps

Results are saved as a timestamped markdown file.

## Project Structure

```
business_validator_agent/
├── business_validator.py    # Main application script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                    # Environment variables (create this)
└── .python-version         # Python version file (auto-generated)
```

## Configuration

### OpenAI API Key

Set your OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### Model Configuration

Modify the model in `business_validator.py`:

```python
config_list = [
    {
        "model": "gpt-4",  # Change to your preferred model
        "api_key": api_key,
    }
]
```

## Customization

### Adding New Agents

Add a new agent in the `_create_agents()` method:

```python
agents['new_agent'] = autogen.AssistantAgent(
    name="NewAgent",
    system_message="Your agent's role and instructions here",
    llm_config={"config_list": self.config_list}
)
```

### Modifying Agent Roles

Change agent behavior by modifying the `system_message` for each agent.

### Custom Report Format

Modify the `_generate_final_report()` method to change report structure.

## Troubleshooting

### Common Issues

1. **No OpenAI API Key**: Set the `OPENAI_API_KEY` environment variable
2. **Import Errors**: Install dependencies with `pip install -r requirements.txt`
3. **Web Search Issues**: DuckDuckGo search may fail - analysis continues without web results

### Error Messages

- `ModuleNotFoundError`: Install missing dependencies
- `OpenAI API Error`: Check API key and billing status
- `Web search error`: DuckDuckGo search failed, analysis continues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License

## Support

For issues:

1. Check the troubleshooting section
2. Review code comments
3. Create an issue in the repository

---

**Note**: This tool provides AI-generated analysis for initial business validation. Conduct thorough research and consult business professionals before making investment decisions.
