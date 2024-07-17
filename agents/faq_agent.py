from transformers import BertForQuestionAnswering, BertTokenizer
import torch

class FAQAgent:
    def __init__(self):
        self.model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    def get_response(self, query, context):
        inputs = self.tokenizer(query, context, return_tensors='pt')
        outputs = self.model(**inputs)
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        answer = self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end]))
        return answer
