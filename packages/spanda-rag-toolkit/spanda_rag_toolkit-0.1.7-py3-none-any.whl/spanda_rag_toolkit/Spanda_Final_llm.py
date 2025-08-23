from openai import OpenAI
from google.genai import errors

class Spanda_Final_Query():

    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(base_url=self.base_url)
        #self.q = result_item["question"]
        #self.rankedchunks = result_item["search_results"]
        
    def caller_function(self, user_question, final_ranked_list):
        # Collect all decomposed questions and their summaries
        all_qa_context = []

        for i,result_item in enumerate(final_ranked_list,1):
            decomposed_question = result_item["question"]
            summaries = result_item["search_results"]

            formated_summaries = "\n".join([f"   - {summary}" for summary in summaries])

            qa_selection = f"""
            Sub-question {i}: {decomposed_question}
            Relevant summaries: {formated_summaries}
            """
            all_qa_context.append(qa_selection)
            print(f"\nDebug-Sub-question {i}: {decomposed_question}")
            print(f"Debug-Sub-question {i} context: {formated_summaries}")    

            # Combine all Q&A sections
            combined_context = "\n\n".join(all_qa_context)

            prompt_template = """
You are an assistant who synthesizes information to answer complex questions.

Original User Question: {user_question}

Below are decomposed sub-questions with their relevant context summaries:

{qa_context}

Task:
1. Create a well-structured, comprehensive answer using ALL available information
2. Organize the response with clear headings and subheadings
3. If some aspects are incomplete, provide what you can and note gaps briefly at the end
4. Focus on synthesis rather than just stating "information not found"

Provide a complete educational response that addresses the user's question as thoroughly as possible with the available information.
IMPORTANT - Base your answer strictly on the provided summaries. If the complete answer cannot be found in the summaries, say "Partial answer available - some information not found in provided context".
"""
            prompt_filled = prompt_template.format(
                user_question=user_question,
                qa_context=combined_context 
            )
            print("\n ---------------- \n", combined_context,"\n ------------------ \n" )
            
            # API call
            try:
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role": "system", "content": prompt_filled},
                        {"role": "user", "content": f"Please provide a comprehensive answer to: {user_question}"},
                    ]
                )
                final_response = response.choices[0].message.content
            except Exception as e:  
                print(f"API Error: {e}")
                return f"Error generating response: {e}"
        return final_response