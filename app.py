import gradio as gr
from reasoning_engine import run_iterative_reasoning, get_thought_process_documentation

# Define the model options
MODEL_OPTIONS = ["claude-3-5-sonnet-20241022"]

def chat_bot(user_input, chat_history, model_name, max_iterations, thought_process_files):
    # Construct the chat history as a string
    chat_history_text = ""
    for past_user_input, past_assistant_response in chat_history:
        chat_history_text += f"User: {past_user_input}\nAssistant:\n<assistant_response>{past_assistant_response}</assistant_response>\n\n"
    # Append the current user input
    full_user_input = chat_history_text + f"User: {user_input}"

    # Run the main logic and get the filename
    response, filename = run_iterative_reasoning(full_user_input, model_name, max_iterations)
    # Append the filename to the list of thought process files
    thought_process_files.append(filename)
    # Update the chat history in-place
    chat_history.append((user_input, response))
    # Retrieve the latest thought process documentation
    thought_process = get_thought_process_documentation(filename)
    return chat_history, "", thought_process, thought_process_files

def download_documentation(thought_process_files):
    # Provide the latest thought process file for download
    if thought_process_files:
        latest_file = thought_process_files[-1]
        return gr.update(visible=True, value=latest_file)
    else:
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
