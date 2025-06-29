# Business Validator AI Agent

A sophisticated multi-agent AI system that validates business ideas using Python and the `pyautogen` library. The system provides comprehensive business validation including market research, competitive analysis, SWOT analysis, and strategic recommendations.

## Features

- **Multi-Agent Workflow**: Five specialized AI agents work together to validate business ideas
- **Web Research**: Uses DuckDuckGo search for real-time market and competitor information
- **Structured Output**: Generates comprehensive, formatted validation reports
- **Markdown Export**: Saves results to markdown files for easy sharing and documentation
- **No API Keys Required**: Uses DuckDuckGo for web search (no additional API keys needed)

## Agent Roles

1. **Clarifier**: Refines and clarifies the business idea
2. **MarketResearcher**: Analyzes market trends and opportunities
3. **CompetitorScout**: Identifies and analyzes competitors
4. **SWOTAnalyst**: Performs comprehensive SWOT analysis
5. **FeedbackAgent**: Provides strategic feedback and improvement suggestions

## Prerequisites

- Python 3.10 or higher
- pyenv and pyenv-virtualenv (for environment management)
- OpenAI API key (for LLM functionality)

## Installation

1. **Clone or create the project directory**:

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
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage

### Basic Usage

Run the business validator:

```bash
python business_validator.py
```

The script will prompt you to enter your business idea, then run the complete validation workflow.

### Example Input

```
Enter your business idea: an AI tool that helps coffee shops choose locations
```

### Example Output

The system will generate a comprehensive report including:

- **Clarified Business Idea**: Refined concept with clear value proposition
- **Market Research**: Market size, trends, and opportunities
- **Competitive Analysis**: Direct and indirect competitors
- **SWOT Analysis**: Strengths, weaknesses, opportunities, threats
- **Strategic Feedback**: Improvement suggestions and next steps

The report is automatically saved as a markdown file with timestamp.

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

The system requires an OpenAI API key for LLM functionality. Set it in your `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### Model Configuration

You can modify the model configuration in `business_validator.py`:

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

To add a new specialized agent, modify the `_create_agents()` method in the `BusinessValidatorAgent` class:

```python
agents['new_agent'] = autogen.AssistantAgent(
    name="NewAgent",
    system_message="Your agent's role and instructions here",
    llm_config={"config_list": self.config_list}
)
```

### Modifying Agent Roles

Each agent's behavior is controlled by its `system_message`. Modify these messages to change how agents analyze and respond to business ideas.

### Custom Report Format

The report generation is handled by the `_generate_final_report()` method. Modify this method to change the report structure and format.

## Troubleshooting

### Common Issues

1. **No OpenAI API Key**: Set the `OPENAI_API_KEY` environment variable
2. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **Web Search Issues**: The system uses DuckDuckGo search which may occasionally fail - the system will continue without web search results

### Error Messages

- `ModuleNotFoundError`: Install missing dependencies
- `OpenAI API Error`: Check your API key and billing status
- `Web search error`: DuckDuckGo search failed, but analysis continues

## Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

---

**Note**: This tool provides AI-generated analysis and should be used as a starting point for business validation. Always conduct thorough research and consult with business professionals before making investment decisions.
