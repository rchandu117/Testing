import openai
import re
import json
import os
from profile_summarization import generate_profile_summarization_prompt

OPEN_API_KEY = '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'


def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.2,
        max_tokens=512
    )
    return response.choices[0].text.strip()


def read_text_from_file(filename):
    with open(filename, 'r') as file:
        text = file.read()
    return text


def extract_information(text, pattern):
    matches = re.findall(pattern, text)
    return matches


class TableExtraction:
    """
    Please extract the table content from the following paragraph:

    [Insert the paragraph you want to extract the table from]

    The table should include columns for "ROLE NAME," "DESIGNATION," "DEPARTMENT," and "DATE& TIME."

    """


class InvoiceExtractor:
    def __init__(self, openai_api_key, receivedJson_data):
        self.api_key = openai_api_key
        self.text_files_directory = None
        self.image_files_directory = None
        self.configured_fields = None
        self.image_file_names = None
        self.table_headers = None
        # Set OpenAI API key
        openai.api_key = self.api_key
        self.summarization_prompt = None
        # self.load_field_config_file(field_config_path)
        self.read_json_data(config_data=receivedJson_data)

    def load_field_config_file(self, field_config_path):
        with open(field_config_path, 'r') as json_file:
            config_data = json.load(json_file)
        self.text_files_directory = config_data['text_files_directory']
        self.image_files_directory = config_data['image_files_directory']
        self.configured_fields = config_data['configured_fields']
        self.image_file_names = [entry['image_file_name'] for entry in config_data['files']]

    def read_json_data(self, config_data):
        self.text_files_directory = config_data['text_files_directory']
        self.image_files_directory = config_data['image_files_directory']
        self.configured_fields = config_data['configured_fields']
        self.image_file_names = [entry['image_file_name'] for entry in config_data['files']]
        self.table_headers = config_data['table_headers']
        self.summarization_prompt = config_data['profile_summarization']['doc_qa']

    def process_files(self):
        data = []
        for image_name in self.image_file_names:
            text_file_path = os.path.join(self.text_files_directory, f"{os.path.splitext(image_name)[0]}.txt")
            try:
                response_data = {"image_file_name": image_name}
                content = read_text_from_file(text_file_path)
                if len(self.configured_fields) > 0:
                    for pattern in self.configured_fields:
                        extracted_info = extract_information(content, pattern)
                        _prompt = f"Question: Please provide the {pattern}\n from the following content. Text : {content}\nInformation: {', '.join(extracted_info)}\n If the value is extracted, return NULL"
                        _response = generate_response(_prompt)
                        cleaned_text = _response.replace(f"{pattern}:", "").replace("Answer:", "")
                        response_data[pattern] = cleaned_text.strip()

                if len(self.table_headers) > 0:
                    header_items = ",".join(self.table_headers)
                    _prompt = f"Question : Please extract the table content from the following " \
                              f"paragraph:\n Text: {content}\n The table should include columns {header_items} and " \
                              f"return in JSON "

                    _response = generate_response(_prompt)
                    response_data['table_data'] = _response

                if self.summarization_prompt is not None:
                    _prompt = f"Question: {self.summarization_prompt}\n from the following content. Text : {content}\n" \
                              "If the value is extracted, return NULL"
                    _response = generate_response(_prompt)
                    cleaned_text = _response.replace("Answer:", "")

                    response_data['summary'] = cleaned_text.strip()

            except FileNotFoundError:
                print(f"File not found: {text_file_path}")

            data.append(response_data)
        return data


# if __name__ == "__main__":
#     config_path = 'config.json'
#     invoice_extractor = InvoiceExtractor(OPEN_API_KEY, config_path)
#     invoice_extractor.process_files()


def process_fields(json_data):
    invoice_extractor = InvoiceExtractor(OPEN_API_KEY, json_data)
    response = invoice_extractor.process_files()
    return response
