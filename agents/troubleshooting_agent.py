from transformers import T5ForConditionalGeneration, T5Tokenizer

class TroubleshootingAgent:
    def __init__(self):
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')

    def get_response(self, query):
        inputs = self.tokenizer.encode(f"troubleshoot: {query}", return_tensors='pt', max_length=512, truncation=True)
        outputs = self.model.generate(inputs, max_length=150, num_beams=4, early_stopping=True)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
