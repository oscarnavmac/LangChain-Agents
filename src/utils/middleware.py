from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from llm_guard import scan_prompt
from llm_guard.input_scanners import BanTopics, PromptInjection, TokenLimit, Toxicity


class SafetyInputGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate inputs safety."""

    def __init__(self):
        super().__init__()
        self.input_scanners = [
            Toxicity(),
            TokenLimit(),
            PromptInjection(),
            BanTopics(["violence"]),
        ]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        # Check the latest user message for safety
        if not state["messages"]:
            return None

        first_message = state["messages"][-1]
        if first_message.type != "human":
            return None

        human_input = first_message.content

        print(f"\n\n\n{human_input}\n\n\n")

        if not isinstance(human_input, str):
            human_input = human_input[-1]["text"]

        sanitized_prompt, results_valid, results_score = scan_prompt(
            self.input_scanners, human_input
        )

        print(
            f"\n\nSanitized Prompt: {sanitized_prompt}. Results: {results_valid}. Scores: {results_score}\n\n"
        )

        if any(not result for result in results_valid.values()):
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "I cannot process that request. Please rephrase your message.",
                    }
                ],
                "jump_to": "end",
            }

        return None


class SafetyOutputGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate response safety."""

    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("openai:gpt-4o-mini")

    @hook_config(can_jump_to=["end"])
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the final AI response
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Use a model to evaluate safety
        safety_prompt = f"""Evaluate if this AI-generated response is authorized or not, based on certain guidelines.
# Scope of accepted responses
You must accept **only** Yaskawa-related topics responses:
- Yaskawa products, models, robots, drives, controllers, or accessories.
- Technical details, manuals, error codes, specifications, or SKUs.
- Spare parts (including AR1440).
- Comparisons **only when a Yaskawa product is involved**.
- Sales follow-up or contact requests.
- Normal human-AI interaction such as greetings.
- Automatic responses such as "I cannot provide a response to that request." and "No Information Found" are acceptable.

# Out-of-Scope topics for responses
You must reject responses that answered to:
- Personal or sensitive topics: religion, race, gender, sexuality, health or mental health, politics, or personal advice.
- Coding, software development, or debugging.
- Legal, medical, or financial advice.
- Pricing, quotations, or cost estimates.
- Non-Yaskawa brands.
- Irrelevant or creative requests (e.g., content writing, jokes, biographies, or news).
- Any request involving confidential information, codebase or internal data of Yaskawa.

        Respond with only 'ACCEPT' or 'REJECT'.

        AI-generated Response: {last_message.content}"""

        print(f"\n\n\nAI Response: {last_message.content}\n\n\n")

        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        print(f"\n\n\nSafety Evaluation Result: {result}\n\n\n")

        if "REJECT" in result.content:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "I cannot provide a response to that request.",
                    }
                ],
                "jump_to": "end",
            }

        return None
