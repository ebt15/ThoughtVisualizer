import re
import logging
import uuid

def extract_reasoning_and_answer(assistant_response):
    # Regular expression to extract content within <reasoning> tags
    reasoning_pattern = r"<reasoning>(.*?)</reasoning>"
    reasoning_match = re.search(reasoning_pattern, assistant_response, re.DOTALL)

    if reasoning_match:
        reasoning_content = reasoning_match.group(1).strip()
        # Remove the reasoning content and tags from the response
        iteration_output = re.sub(reasoning_pattern, '', assistant_response, flags=re.DOTALL).strip()
    else:
        reasoning_content = ''
        iteration_output = assistant_response.strip()

    return reasoning_content, iteration_output

def check_reasoning_completion(user_input, reasoning_content):
    from api_provider import api_provider
    from prompts import evaluator_system_prompt

    # Log the input to the reasoning completion checker
    logging.info("Reasoning Completion Checker Input:\n%s", reasoning_content)

    # Prepare the messages for the evaluator
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (f"User Query:\n{user_input}\n\n"
                            f"Reasoning Steps:\n{reasoning_content}\n\n"
                             "Analyze the reasoning and provide the following:\n"
                             "1. Feedback (Weaknesses, suggestions for improvement, and improved approaches):\n"
                             "2. Final Decision: True/False\n"
                             "True means further iteration is required based on the feedback, False means the reasoning is complete and final output can be generated.")
                }
            ]
        }
    ]

    # Agent to check reasoning completion and provide detailed feedback
    # Use the API provider to send the message
    response = api_provider.send_message(
        max_tokens=1000,
        temperature=0,
        system_prompt=evaluator_system_prompt,
        messages=messages
    )

    feedback_response = response.content[0].text.strip()

    # Log the response from the reasoning completion checker
    logging.info("Reasoning Completion Checker Response:\n%s", feedback_response)

    # Define the regex pattern to find 'Final Decision: True/False'
    pattern = r"Final Decision:\s*(True|False)"

    # Perform the regex search
    final_decision_match = re.search(pattern, feedback_response, re.IGNORECASE)
    logging.debug(f"Regex search result: {final_decision_match}")

    if final_decision_match:
        # Extract and process the matched value
        matched_value = final_decision_match.group(1).strip()
        logging.info(f"Matched value extracted: '{matched_value}'")

        # Convert the matched string to a boolean
        final_decision = matched_value.lower() == "true"
        logging.info(f"Final decision parsed as: {final_decision}")
    else:
        # Default decision if no match is found
        final_decision = False
        logging.warning("Final decision not found in feedback_response. Defaulting to False.")

    logging.info(f"Final decision returned: {final_decision}")

    return feedback_response, final_decision

def generate_final_output(input_context, reasoning_content, filename):
    from api_provider import api_provider
    from prompts import system_prompt_final_turn

    # Prepare the messages without the assistant role, including input_context and reasoning_content
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": input_context + f"\n\n<reasoning>{reasoning_content}</reasoning>"
                }
            ]
        }
    ]

    # Log the input to the assistant for the final output
    logging.info("Final Output Assistant Input:\n%s", messages)

    # Write final generation input to readme
    write_to_readme("## Final Generation\n\n### Input:\n" + input_context, filename=filename)

    # Assistant generates the final output using the API provider
    final_response = api_provider.send_message(
        max_tokens=8000,
        temperature=0.2,
        system_prompt=system_prompt_final_turn,
        messages=messages
    )

    # Log the assistant's final response
    logging.info("Final Output Assistant Response:\n%s", final_response.content[0].text)

    # Extract the final answer, ensuring reasoning is not included
    _, final_output = extract_reasoning_and_answer(final_response.content[0].text)
    return final_output

def write_to_readme(content, iteration=None, filename=None):
    if filename is None:
        # Generate a unique filename
        filename = f'thought_process_{uuid.uuid4().hex}.md'
    with open(filename, 'a', encoding='utf-8') as f:
        if iteration:
            f.write(f"\n## Iteration {iteration}\n\n")
        f.write(f"{content}\n\n")
    return filename  # Return the filename for future reference

def get_thought_process_documentation(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Thought Process Documentation not available."
