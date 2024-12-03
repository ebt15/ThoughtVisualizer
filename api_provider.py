import anthropic
import logging
import sys
import time

# Create an abstract class or interface for the API provider
class APIProvider:
    def send_message(self, max_tokens, temperature, system_prompt, messages):
        raise NotImplementedError("This method should be implemented by subclasses.")

# Implement the provider-specific logic in a subclass
class AnthropicAPI(APIProvider):
    def __init__(self, model_name):
        self.client = anthropic.Anthropic()
        self.model_name = model_name

    def send_message(self, max_tokens, temperature, system_prompt, messages):
        retries = 0
        max_retries = 4  # Total of 4 tries

        while retries < max_retries:
            try:
                # Prepare the API call parameters
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                )
                return response
            except anthropic.APIError as e:
                # Log the error
                logging.error(f"APIError occurred: {e}")

                # Check the error type and status code
                error_status_code = e.response.status_code if e.response else None
                error_type = e.error.type if e.error else None
                error_message = e.error.message if e.error else str(e)

                if error_status_code == 529 or error_type == 'overloaded_error':
                    # Overloaded error, implement retry logic
                    retries += 1
                    if retries <= 2:
                        wait_time = 5
                    else:
                        wait_time = 10
                    logging.info(f"Received 529 Overloaded Error. Retrying after {wait_time} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue  # Retry the request
                else:
                    # For other errors, log and exit gracefully
                    logging.error(f"An error occurred: {error_message}")
                    sys.exit(1)
            except Exception as e:
                # Log any other exceptions and exit gracefully
                logging.error(f"An unexpected error occurred: {e}")
                sys.exit(1)

        # If maximum retries exceeded, log and exit
        logging.error("Maximum retries exceeded for 529 Overloaded Error.")
        sys.exit(1)

# Initialize the API provider
api_provider = AnthropicAPI(model_name='claude-3-5-sonnet-20241022')
