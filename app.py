import os
#from dotenv import load_dotenv
import streamlit as st
import openai

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class Recipe(BaseModel):
    """A class to represent a recipe."""
    title: str = Field(description="The name of the recipe.")
    description: str = Field(description="An extremely detailed, mouth-watering description of the recipe, crafted as if describing an exquisite image of the finished dish.")
    ingredients: list[str] = Field(description="A list of ingredients with precise measurements required for the recipe.")
    instructions: dict[int, str] = Field(description="Numbered step-by-step instructions to prepare the dish.")
    
#load_dotenv()

OPENAI_MODEL = "gpt-4"
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

PROMPT = """
I want you to act as a recipe database. I will provide you with a list of ingredients, and you will generate a recipe out of those ingredients. Be very certain not to leave out any step in the instructions, and keep the recipe limited to the food items provided.

ingredients can be found in these three backticks: ```{user_input}```

{format_instructions}
"""


def main():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
    parser = PydanticOutputParser(pydantic_object=Recipe)

    st.title("Recipe Bot")

    # --- USER INTERACTION ---
    user_input = st.text_input("Share what's in your fridge, pantry and freezer:")

    message = HumanMessagePromptTemplate.from_template(template=PROMPT)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message])

    if st.button("Generate") and user_input:
        with st.spinner("Generating..."):

            chat_prompt_with_values = chat_prompt.format_prompt(user_input=user_input, format_instructions=parser.get_format_instructions())

            response = llm(chat_prompt_with_values.to_messages())
            data = parser.parse(response.content)

            st.write(f"# {data.title}")
            st.write("### Ingredients")
            for i in data.ingredients:
                st.markdown(f"- {i}")

            st.write("\n\n")
            for k, v in data.instructions.items():
                #st.write(f"##### Step {k}")
                #st.markdown(f"**Step {k}**")
                st.markdown(f"**Step {k}**: {v}")


if __name__ == "__main__":
    main()
