from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class CodeSnippetAgent:
    def __init__(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained('microsoft/codebert-base')
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')

    def get_response(self, query):
        inputs = self.tokenizer.encode(query, return_tensors='pt')
        outputs = self.model.generate(inputs)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
