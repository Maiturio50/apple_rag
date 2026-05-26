import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

def ask_ai_with_context(user_query, word_to_find):
    # Let's read your Apple text file
    with open("toyotaw_practice.txt", "r", encoding="utf-8") as file:
        raw_document = file.read()
    
    # Simple keyword extraction: find the keyword and grab a chunk around it
    index = raw_document.lower().find(word_to_find.lower())
    if index == -1:
        extracted_context = "Keyword not found."
    else:
        extracted_context = raw_document[index:index + 4000]
    
    # Call the OpenAI API safely with matching variables
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": f"Answer using ONLY this text:\n\n{extracted_context}"
            },
            {
                "role": "user", 
                "content": str(user_query) # Forced as a string to guarantee no 'null' errors!
            }
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Test text questions
    query_text = "What car parts does warranty cover?"
    keyword = "warranty"
    
    print("Searching engine memory...")
    answer = ask_ai_with_context(query_text, keyword)
    print("\n🤖 Engine Answer:\n", answer)
