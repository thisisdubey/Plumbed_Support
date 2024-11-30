import os
import warnings
import gc
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool
from utils import get_openai_api_key,get_openai_model_name

# Suppress warnings
warnings.filterwarnings('ignore')

# Set up API key and model environment


openai_api_key = get_openai_api_key()
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    st.error("OpenAI API key not found. Please set up your API key correctly.")

openai_model_name = get_openai_model_name()
if openai_model_name:
    os.environ["OPENAI_MODEL_NAME"] = openai_model_name
else:
    st.error("OpenAI API model name found. Please set up your model name correctly.")

# Streamlit UI setup
st.title("Customer Support - Plumbed")
st.subheader("Plumbed system for support responses and quality assurance.")

# Initializing session state variables
if "result" not in st.session_state:
    st.session_state["result"] = {}

if "query" not in st.session_state:
    st.session_state["query"] = ""


# Function to clear inputs and results in session state
def clear_inputs():
    # Clear session state and reset widgets
    st.session_state["query"] = ""
    st.session_state["result"] = {}
    st.empty()  # This will clear any rendered widgets like text inputs
    st.session_state.clear()
    gc.collect()

# Inputs
query_input = st.text_input("Enter your query:", key="query")

# Define Agents with clear roles and goals
support_agent = Agent(
    role="Senior Support Representative",
    goal="Provide top-tier customer support with complete and accurate responses.",
    backstory=(
        "As a Senior Support Representative at Plumbed (https://www.plumbed.io) support team, you are assisting a technical customer, "
        "an important client. Your mission is to ensure a helpful, complete answer "
        "with no assumptions and the best support possible."
        "Do not put your signature at the end of response, and do not put customer name in response."
    ),
    allow_delegation=False,
    verbose=True
)


support_quality_assurance_agent = Agent(
    role="Support Quality Assurance Specialist",
    goal="Get recognition for delivering best-in-class quality assurance for customer support responses.",
    backstory=(
        "You are part of the Plumbed (https://www.plumbed.io) support team and are reviewing responses to ensure "
        "the highest quality and accuracy. "
        "on a request from an important customer ensuring that "
        "the support representative is "
		"providing the best support possible.\n"
		"You need to make sure that the support representative "
        "is providing full"
		"complete answers, and make no assumptions,"
        "also ensure the support tone is friendly and helpful."
        "Do not put your signature at the end of response."
    ),
    verbose=True
)

# Define the Tool and Tasks
docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://www.plumbed.io"
)


query_resolution = Task(
    description=(
        "customer just reached out with a super important ask:\n"
	    f"{query_input}\n\n"
		"Make sure to use everything you know "
        "to provide the best support possible."
		"You must strive to provide a complete "
        "and accurate response to the customer's query."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's query that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered, and maintain a helpful and friendly "
		"tone throughout."
    ),
	tools=[docs_scrape_tool],
    agent=support_agent,
    verbose=True
)


quality_assurance_review = Task(
    description=(
        "Review the response drafted by the Senior Support Representative for the customer's query. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
		"high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's query "
        "have been addressed "
		"thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
		"ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's query, incorporating all "
		"relevant feedback and improvements.\n"
		"Don't be too formal, we are a chill and cool company "
	    "but maintain a professional and friendly tone throughout."
    ),
    agent=support_quality_assurance_agent,
)

# Crew setup
crew = Crew(
    agents=[support_agent, support_quality_assurance_agent],
    tasks=[query_resolution, quality_assurance_review],
    verbose=2,
    memory=True
)

# Button to execute the Crew workflow
if st.button("Generate Response"):
    if query_input:
        inputs = {
            "query": query_input
        }

        try:
            # Run the Crew task and store result in session state
            result = crew.kickoff(inputs=inputs)
            st.session_state["result"] = {"query_resolution": result}  # Store as dict
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display results with fallback if 'result' is incorrectly set
if st.session_state["result"]  != {}:
    result_display = st.session_state["result"].get("query_resolution", "No response generated.")
    st.write(result_display)

# Clear button that calls clear_inputs on click
st.button("Clear", on_click=clear_inputs)
