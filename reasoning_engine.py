import uuid
import logging
import re
from api_provider import api_provider
from prompts import (
    system_prompt_first_turn,
    system_prompt_intermediate_turn
)
from utils import (
    extract_reasoning_and_answer,
    check_reasoning_completion,
    generate_final_output,
    write_to_readme
)

def iterative_reasoning(user_input, max_iterations, filename=None):
    iteration = 0
    reasoning_complete = False
    input_context = user_input  # Initialize with the user's input
    iteration_outputs = []  # List to store iteration outputs

    if filename is None:
        filename = f'thought_process_{uuid.uuid4().hex}.md'

    # Create new readme file and write initial input
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Thought Process Documentation\n\n")
        f.write("## Initial Input\n\n")
        f.write(f"{user_input}\n\n")

    while not reasoning_complete and iteration < max_iterations:
        iteration += 1

        # Select the appropriate system prompt
        if iteration == 1:
            system_prompt = system_prompt_first_turn
        else:
            system_prompt = system_prompt_intermediate_turn

        # Prepare the messages for the assistant
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input_context
                    }
                ]
            }
        ]

        # Log the input to the assistant
        logging.info("Assistant Input (Iteration %d):\n%s", iteration, messages)

        # Assistant performs reasoning and provides an answer using the API provider
        reasoning_response = api_provider.send_message(
            max_tokens=2000,
            temperature=0.7,
            system_prompt=system_prompt,
            messages=messages
        )
        assistant_response = reasoning_response.content[0].text

        # Write assistant response to readme
        write_to_readme(f"### Assistant Response:\n{assistant_response}", iteration, filename)

        # Log the assistant's response
        logging.info("Assistant Response (Iteration %d):\n%s", iteration, assistant_response)

        # Extract reasoning and iteration output
        reasoning_content, iteration_output = extract_reasoning_and_answer(assistant_response)

        # Check if reasoning_content is empty and log a warning if necessary
        if not reasoning_content.strip():
            logging.warning("Reasoning content is empty at iteration %d.", iteration)

        # Accumulate iteration outputs
        iteration_outputs.append(iteration_output)

        # Check if reasoning is complete and get feedback
        feedback_response, further_reasoning_required = check_reasoning_completion(user_input, reasoning_content)

        # Write reasoning checker response to readme
        write_to_readme(f"### Reasoning Checker Response:\n{feedback_response}", iteration, filename)

        # Remove '2. Final Decision: True/False' from feedback_response
        feedback_response_cleaned = re.sub(r"2\\.\\s*Final Decision:.*", "", feedback_response, flags=re.DOTALL).strip()

        if further_reasoning_required:
            # For the next iteration, update input_context with user_input, accumulated iteration outputs, and latest feedback
            iteration_outputs_text = "\n\n".join(iteration_outputs)
            input_context = f"{user_input}\n\nPrevious Responses:\n{iteration_outputs_text}\n\nFeedback:\n{feedback_response_cleaned}"
        else:
            # Proceed to generate the final output
            iteration_outputs_text = "\n\n".join(iteration_outputs)
            input_context = f"{user_input}\n\nPrevious Responses:\n{iteration_outputs_text}"
            final_output = generate_final_output(input_context, reasoning_content, filename)
            # Write final output to readme
            write_to_readme("## Final Output\n\n" + final_output, iteration, filename)
            return final_output, filename

    # If maximum iterations reached without completion, generate final output
    iteration_outputs_text = "\n\n".join(iteration_outputs)
    input_context = f"{user_input}\n\nPrevious Responses:\n{iteration_outputs_text}"
    final_output = generate_final_output(input_context, reasoning_content, filename)
    # Write final output to readme
    write_to_readme("## Final Output\n\n" + final_output, iteration, filename)
    return final_output, filename

def run_iterative_reasoning(user_input, model_name, max_iterations):
    filename = f'thought_process_{uuid.uuid4().hex}.md'
    api_provider.model_name = model_name  # Update the model name in the API provider
    final_answer, filename = iterative_reasoning(user_input, max_iterations, filename)
    return final_answer, filename
