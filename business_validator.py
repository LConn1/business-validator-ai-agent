#!/usr/bin/env python3
"""
Business Validator AI Agent
A multi-agent system that validates business ideas using pyautogen.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
import autogen
from duckduckgo_search import DDGS
import openai
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("autogen").setLevel(logging.DEBUG)

_real_create = openai.ChatCompletion.create


def logging_create(*args, **kwargs):
    model = kwargs.get("model", "unknown")
    messages = kwargs.get("messages", [])
    if messages:
        first_msg = (
            messages[0].get("content", "")
            if isinstance(messages[0], dict)
            else str(messages[0])
        )
    else:
        first_msg = ""
    print(f"[LOG] OpenAI API call: model={model}, first_message={first_msg[:100]!r}")
    return _real_create(*args, **kwargs)


openai.ChatCompletion.create = logging_create


class WebSearchAgent(autogen.AssistantAgent):
    """Custom agent that can perform web searches."""

    def __init__(
        self,
        name: str,
        system_message: str,
        config_list: List[Dict],
        business_idea: str,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config={"config_list": config_list},
            **kwargs,
        )
        self.config_list = config_list
        self.business_idea = business_idea

    def web_search(self, query: str) -> List[str]:
        """Perform web search using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return [result["body"] for result in results]
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def generate_reply(self, messages=None, sender=None, config=None):
        """Override to include web search in responses."""
        # Get the last message content
        if messages and len(messages) > 0:
            last_message = messages[-1].get("content", "")

            # Perform web search if the agent is supposed to do research
            search_results = []
            if self.name == "MarketResearcher":
                query = f"market trends and analysis for {self.business_idea}"
                print(f"[DEBUG] MarketResearcher performing web search: {query}")
                search_results = self.web_search(query)
            elif self.name == "CompetitorScout":
                query = f"top competitors and alternatives for {self.business_idea}"
                print(f"[DEBUG] CompetitorScout performing web search: {query}")
                search_results = self.web_search(query)

            # Add search results to the context if available
            if search_results:
                print(f"[DEBUG] Found {len(search_results)} web search results")
                search_context = "\n\nWEB SEARCH RESULTS:\n" + "\n".join(
                    search_results[:3]
                )
                # Modify the last message to include search results
                messages[-1]["content"] = last_message + search_context
            else:
                print(f"[DEBUG] No web search results found for {self.name}")

        # Call the parent method to generate the reply
        return super().generate_reply(messages=messages, sender=sender, config=config)


class BusinessValidatorAgent:
    def __init__(self):
        """Initialize the Business Validator Agent system."""
        self.config_list = self._get_config_list()
        self.business_idea = None
        self.agents = None
        self.user_proxy = None

    def _get_config_list(self) -> List[Dict[str, Any]]:
        """Get the configuration for the LLM."""
        # Try to get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            return [
                {
                    "model": "gpt-4",
                    "api_key": api_key,
                }
            ]
        else:
            # Fallback to local model or provide instructions
            print(
                "Warning: No OpenAI API key found. Please set OPENAI_API_KEY environment variable."
            )
            print("You can also use local models by modifying the config_list.")
            return []

    def _create_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Create all the specialized agents for business validation."""
        agents = {}

        # Clarifier Agent - Clarifies and refines the business idea
        agents["clarifier"] = autogen.AssistantAgent(
            name="Clarifier",
            system_message="""You are a business idea clarifier. Your role is to:
1. Take a raw business idea and clarify it into a well-defined concept
2. Identify the core value proposition
3. Define the target market and customer segments
4. Specify the key features and benefits
5. Provide a clear, concise description of the business idea

Always respond with a structured format:
- CLARIFIED IDEA: [Clear description]
- VALUE PROPOSITION: [What problem it solves]
- TARGET MARKET: [Who will buy it]
- KEY FEATURES: [Main features]
- BUSINESS MODEL: [How it makes money]""",
            llm_config={"config_list": self.config_list},
        )

        # Market Research Agent - Researches market trends and opportunities
        agents["market_researcher"] = WebSearchAgent(
            name="MarketResearcher",
            system_message="""You are a market research specialist. Your role is to:
1. Research market trends related to the business idea
2. Identify market size and growth potential
3. Analyze market dynamics and opportunities
4. Research regulatory environment and barriers
5. Identify market risks and challenges

IMPORTANT: You have access to web search results. You MUST explicitly cite, quote, or summarize the WEB SEARCH RESULTS provided in your analysis. Clearly indicate which facts or data points come from the web search, and include direct quotes or links if available. If no relevant web search results are found, state this explicitly.

Always respond with:
- MARKET SIZE: [Estimated market size with sources if available]
- GROWTH TREND: [Market growth direction with recent data]
- KEY TRENDS: [Relevant market trends from web search]
- REGULATORY FACTORS: [Legal/regulatory considerations]
- MARKET RISKS: [Potential market challenges]
- WEB SEARCH SOURCES: [List or summarize the web search results you used]""",
            config_list=self.config_list,
            business_idea=self.business_idea,
        )

        # SWOT Analyst - Performs SWOT analysis
        agents["swot_analyst"] = autogen.AssistantAgent(
            name="SWOTAnalyst",
            system_message="""You are a SWOT analysis specialist. Your role is to:
1. Analyze the business idea's Strengths, Weaknesses, Opportunities, and Threats
2. Provide detailed insights for each SWOT category
3. Prioritize the most important factors
4. Suggest strategies to leverage strengths and opportunities
5. Recommend ways to address weaknesses and threats

Always respond with a structured SWOT analysis:
- STRENGTHS: [List key strengths]
- WEAKNESSES: [List key weaknesses]
- OPPORTUNITIES: [List key opportunities]
- THREATS: [List key threats]
- STRATEGIC RECOMMENDATIONS: [Action items]""",
            llm_config={"config_list": self.config_list},
        )

        # Competitor Scout - Identifies and analyzes competitors
        agents["competitor_scout"] = WebSearchAgent(
            name="CompetitorScout",
            system_message="""You are a competitive intelligence specialist. Your role is to:
1. Identify direct and indirect competitors
2. Analyze competitor strengths and weaknesses
3. Research competitor business models and pricing
4. Identify competitive advantages and differentiators
5. Suggest competitive positioning strategies

IMPORTANT: You have access to web search results. You MUST explicitly cite, quote, or summarize the WEB SEARCH RESULTS provided in your analysis. Clearly indicate which facts or data points come from the web search, and include direct quotes or links if available. If no relevant web search results are found, state this explicitly.

Always respond with:
- DIRECT COMPETITORS: [List with brief descriptions from web search]
- INDIRECT COMPETITORS: [List with brief descriptions]
- COMPETITIVE LANDSCAPE: [Market positioning analysis]
- COMPETITIVE ADVANTAGES: [How to differentiate]
- COMPETITIVE THREATS: [What to watch out for]
- WEB SEARCH SOURCES: [List or summarize the web search results you used]""",
            config_list=self.config_list,
            business_idea=self.business_idea,
        )

        # Feedback Agent - Provides improvement suggestions
        agents["feedback_agent"] = autogen.AssistantAgent(
            name="FeedbackAgent",
            system_message="""You are a business strategy consultant. Your role is to:
1. Review all previous analyses and provide strategic feedback
2. Suggest improvements and pivots for the business idea
3. Identify potential business model innovations
4. Recommend next steps for validation
5. Provide actionable advice for moving forward

Always respond with:
- STRATEGIC FEEDBACK: [Overall assessment]
- IMPROVEMENT SUGGESTIONS: [Specific recommendations]
- POTENTIAL PIVOTS: [Alternative directions]
- VALIDATION STEPS: [Next steps to test the idea]
- SUCCESS FACTORS: [Key things to focus on]

IMPORTANT: After providing your analysis, end your response with "TERMINATE" on a new line to signal that the business validation process is complete.""",
            llm_config={"config_list": self.config_list},
        )

        return agents

    def _create_user_proxy(self) -> autogen.UserProxyAgent:
        """Create the user proxy agent."""
        return autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "")
            .rstrip()
            .endswith("TERMINATE"),
            code_execution_config={"work_dir": "workspace", "use_docker": False},
            llm_config={"config_list": self.config_list},
        )

    def _web_search(self, query: str) -> List[str]:
        """Perform web search using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return [result["body"] for result in results]
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def validate_business_idea(self, business_idea: str) -> str:
        """Main method to validate a business idea using the multi-agent system."""
        print(f"Starting business validation for: {business_idea}")
        print("=" * 60)
        self.business_idea = business_idea
        self.agents = self._create_agents()
        self.user_proxy = self._create_user_proxy()

        # Initialize the workflow
        groupchat = autogen.GroupChat(
            agents=[self.user_proxy] + list(self.agents.values()),
            messages=[],
            max_round=50,
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat, llm_config={"config_list": self.config_list}
        )

        # Start the validation process
        initial_message = f"""
Please validate this business idea: "{business_idea}"

Here's the workflow:
1. Clarifier: First, clarify and refine the business idea
2. MarketResearcher: Research market trends and opportunities (will use web search for current data)
3. CompetitorScout: Identify and analyze competitors (will use web search for current competitors)
4. SWOTAnalyst: Perform a comprehensive SWOT analysis
5. FeedbackAgent: Provide strategic feedback and improvement suggestions

Each agent should build upon the previous agent's work. The MarketResearcher and CompetitorScout agents will perform real web searches to get current information.
"""

        # Start the conversation
        self.user_proxy.initiate_chat(manager, message=initial_message)

        # Extract the final report
        final_report = self._generate_final_report(business_idea, groupchat.messages)
        return final_report

    def _generate_final_report(
        self, business_idea: str, messages: List[Dict], debug: bool = False
    ) -> str:
        """Generate a structured final report from the conversation. Optionally print the full conversation for debugging."""
        if debug:
            print("\n--- FULL CONVERSATION LOG ---\n")
            for m in messages:
                print(f"[{m.get('role')}] {m.get('content','')[:500]}\n---")
            print("\n--- END OF CONVERSATION LOG ---\n")

        report = f"""
# Business Validation Report
**Business Idea:** {business_idea}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report provides a comprehensive validation analysis of the business idea using a multi-agent AI system with real-time web research.

## Analysis Results
"""

        # Extract agent responses by looking for content patterns since the name field may not be set correctly
        def find_agent_response(pattern_start, pattern_end=None):
            for m in reversed(messages):
                if m.get("role") == "assistant":
                    content = m.get("content", "")
                    if pattern_start in content:
                        if pattern_end:
                            start_idx = content.find(pattern_start)
                            end_idx = content.find(pattern_end, start_idx)
                            if end_idx != -1:
                                return content[start_idx : end_idx + len(pattern_end)]
                        return content
            return None

        # Market Research - look for "MARKET RESEARCHER" or "MARKET SIZE:"
        market_research = find_agent_response(
            "### MARKET RESEARCHER"
        ) or find_agent_response("MARKET SIZE:")
        if market_research:
            report += f"\n### Market Research\n{market_research}\n"
        else:
            report += "\n### Market Research\n(No MarketResearcher output found.)\n"

        # Competitor Analysis - look for "COMPETITOR SCOUT" or "DIRECT COMPETITORS:"
        competitor_analysis = find_agent_response(
            "### COMPETITOR SCOUT"
        ) or find_agent_response("DIRECT COMPETITORS:")
        if competitor_analysis:
            report += f"\n### Competitive Analysis\n{competitor_analysis}\n"
        else:
            report += "\n### Competitive Analysis\n(No CompetitorScout output found.)\n"

        # Clarified Idea - look for "CLARIFIED IDEA:"
        clarified = find_agent_response("CLARIFIED IDEA:", "BUSINESS MODEL:")
        if clarified:
            report += f"\n### Clarified Business Idea\n{clarified}\n"

        # SWOT Analysis - look for "SWOT ANALYSIS" or "STRENGTHS:"
        swot = find_agent_response("### SWOT ANALYSIS") or find_agent_response(
            "STRENGTHS:"
        )
        if swot:
            report += f"\n### SWOT Analysis\n{swot}\n"

        # Feedback - look for "STRATEGIC FEEDBACK:"
        feedback = find_agent_response("STRATEGIC FEEDBACK:", "TERMINATE")
        if feedback:
            report += f"\n### Strategic Feedback\n{feedback}\n"

        report += """
## Recommendations
Based on the analysis above, consider the following next steps:
1. Validate assumptions with potential customers
2. Create a minimum viable product (MVP)
3. Test the business model with early adopters
4. Refine the value proposition based on feedback
5. Develop a go-to-market strategy

---
*Report generated by Business Validator AI Agent with real-time web research*
"""
        return report

    def save_report(self, report: str, filename: str = None) -> str:
        """Save the report to a markdown file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_validation_report_{timestamp}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Report saved to: {filename}")
        return filename


def main():
    """Main function to run the business validator."""
    print("🚀 Business Validator AI Agent")
    print("=" * 40)

    # Get business idea from user
    business_idea = input("Enter your business idea: ")

    if not business_idea.strip():
        print("Please provide a business idea to validate.")
        return

    # Create validator and run analysis
    validator = BusinessValidatorAgent()

    try:
        report = validator.validate_business_idea(business_idea)

        # Save the report
        filename = validator.save_report(report)

        print("\n" + "=" * 60)
        print("✅ Business validation completed!")
        print(f"📄 Report saved to: {filename}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        print("Please check your OpenAI API key and try again.")


if __name__ == "__main__":
    main()
