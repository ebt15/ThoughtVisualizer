import gradio as gr
import logging
from reasoning_engine import run_iterative_reasoning
from utils import get_thought_process_documentation

logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define the model options
MODEL_OPTIONS = ["claude-3-5-sonnet-20241022"]

def chat_bot(user_input, chat_history, model_name, max_iterations, thought_process_files):
    logging.info(f"Received user input: {user_input}")
    logging.info(f"Current chat history length: {len(chat_history)}")
    logging.info(f"Selected model: {model_name}")
    logging.info(f"Max iterations: {max_iterations}")
    
    # Construct the chat history as a string
    chat_history_text = ""
    for past_user_input, past_assistant_response in chat_history:
        chat_history_text += f"User: {past_user_input}\nAssistant:\n<assistant_response>{past_assistant_response}</assistant_response>\n\n"
    # Append the current user input
    full_user_input = chat_history_text + f"User: {user_input}"

    # Run the main logic and get the filename
    try:
        response, filename = run_iterative_reasoning(full_user_input, model_name, max_iterations)
        logging.info(f"Generated response: {response}")
        logging.info(f"Thought process documentation saved to: {filename}")
    except Exception as e:
        logging.error(f"Error in run_iterative_reasoning: {e}")
        response = "An error occurred while processing your request."
        filename = None

    # Append the filename to the list of thought process files
    if filename:
        thought_process_files.append(filename)
    else:
        logging.warning("No filename returned; thought process file not appended.")

    # Update the chat history in-place
    chat_history.append((user_input, response))

    # Retrieve the latest thought process documentation
    try:
        thought_process = get_thought_process_documentation(filename)
        logging.info("Successfully retrieved thought process documentation.")
    except Exception as e:
        logging.error(f"Error in get_thought_process_documentation: {e}")
        thought_process = "An error occurred while retrieving the thought process documentation."

    return chat_history, "", thought_process, thought_process_files

def download_documentation(thought_process_files):
    # Provide the latest thought process file for download
    if thought_process_files:
        latest_file = thought_process_files[-1]
        logging.info(f"Providing file for download: {latest_file}")
        return gr.update(visible=True, value=latest_file)
    else:
        logging.info("No thought process files available for download.")
        return gr.update(visible=False)

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# LLM ThoughtVisualizer")

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot()
                user_input = gr.Textbox(
                    placeholder="Type your message here...",
                    show_label=False
                )
                send_button = gr.Button("Send")

            with gr.Column(scale=1):
                model_name = gr.Dropdown(
                    choices=MODEL_OPTIONS,
                    value=MODEL_OPTIONS[0],
                    label="Select Model"
                )
                max_iterations = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Max Iterations"
                )
                with gr.Accordion("Thought Process Documentation", open=False):
                    thought_process_output = gr.Textbox(
                        placeholder="Thought Process Documentation will appear here.",
                        lines=20,
                        show_label=False
                    )
                    download_button = gr.Button("Download Documentation")
                    # Add the hidden file component here
                    download_file = gr.File(visible=False, label="Download File")

        # Initialize state variables
        thought_process_files = gr.State([])

        def on_send(user_message, chat_history, model_name, max_iterations, thought_process_files):
            logging.info("Send button clicked.")
            chat_history, _, thought_process, thought_process_files = chat_bot(
                user_message, chat_history, model_name, max_iterations, thought_process_files
            )
            return chat_history, "", thought_process, thought_process_files

        send_button.click(
            on_send,
            inputs=[user_input, chatbot, model_name, max_iterations, thought_process_files],
            outputs=[chatbot, user_input, thought_process_output, thought_process_files]
        )

        download_button.click(
            download_documentation,
            inputs=[thought_process_files],
            outputs=download_file
        )

    demo.launch()

if __name__ == "__main__":
    main()
