import os
import logging
from pathlib import Path
from datetime import date
from decimal import Decimal
from dateparser import parse
from lib_invoice import Invoice
from lib_utilys import read_json
from babel.numbers import parse_decimal
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentField

logger = logging.getLogger(__name__)

def analyze_document(endpoint: str, key: str, modelmap_path: Path, pdf: bytes, metadata: dict) -> dict:
    """Analyzes the document using Azure Form Recognizer."""
    try:
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        model_map = read_json(modelmap_path)
        model_id = model_map.get(metadata.get('business'), {}).get('model_id')
        poller = client.begin_analyze_document(model_id, pdf)
        result = poller.result()
        result = result.to_dict()
        result['locale'] = model_map.get(metadata.get('business'), {}).get('locale')
        result['Creditor_number'] = model_map.get(metadata.get('business'), {}).get('Creditor_number')
        result['Creditor_international_location_number'] = model_map.get(metadata.get('business'), {}).get('Creditor_international_location_number')
        return result
    except Exception as e:
        logger.exception("Failed to analyze document... ")
        raise e

def parse_numbers(result: dict) -> dict:
    """Parse the numbers in the result of the analysis."""
    locale = result.get('locale')
    for idx, document in enumerate(result.get('documents')):
        fields = document.get('fields', {})
        for field_name, field_data in fields.items():
            value_type = field_data.get('value_type')
            if value_type == 'list':
                value = field_data.get('value')
                for idxx, item_line in enumerate(value):
                    for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                        value_type = nested_field_data.get('value_type')
                        if nested_field_data.get('content') is not None: 
                            value = nested_field_data.get('content').replace(' ', '').replace('%', '').replace('€', '').replace('EUR', '')
                            if value_type == 'float':
                                if value.find('-') != 0 and value.find('-') != -1:
                                    value = '-' + value.replace('-', '')
                                value = parse_decimal(value, locale=locale)
                                result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value']  = Decimal(value)
                            elif value_type == 'integer':
                                if value.find('-') != 0 and value.find('-') != -1:
                                    value = '-' + value.replace('-', '')
                                result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = int(value)
                continue
            if field_data.get('content') is not None: 
                value = field_data.get('content').replace(' ', '').replace('%', '').replace('€', '').replace('():', '').replace('hoogtarief,', '21').replace('EUR', '')
                if value_type == 'float':
                    if value.find('-') != 0 and value.find('-') != -1:
                        value = '-' + value.replace('-', '')
                    value = parse_decimal(value, locale=locale)
                    result['documents'][idx]['fields'][field_name]['value']  = Decimal(value)
                elif value_type == 'integer':
                    value = value.replace(',', '').replace('Prijs/','')
                    if value.find('-') != 0 and value.find('-') != -1:
                        value = '-' + value.replace('-', '')
                    result['documents'][idx]['fields'][field_name]['value'] = int(value)
    return result

def parse_dates(result: dict, parsefmt_path: Path) -> dict:
    """Processes the dates in the result of the analysis."""
    parse_formats = read_json(parsefmt_path).get('formats')
    for idx, document in enumerate(result.get('documents')):
        fields = document.get('fields', {})
        for field_name, field_data in fields.items():
            value_type = field_data.get('value_type')
            if value_type == 'list':
                value = field_data.get('value')
                for idxx, item_line in enumerate(value):
                    for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                        value_type = nested_field_data.get('value_type')
                        if nested_field_data.get('content') is not None:
                            value = nested_field_data.get('content')
                            if value_type == 'date':
                                value = value.replace(',', '').replace('leverdatum:', '')
                                parsed_value = parse(value, parse_formats, settings={'STRICT_PARSING': True})
                                if parsed_value:
                                    result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = parsed_value.strftime('%Y%m%d')
                                elif len(value.split('-')) == 2:
                                    parsed_value = date.fromisocalendar(int(value.split('-')[1]), int(value.split('-')[0]), 3)
                                    result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = parsed_value.strftime('%Y%m%d')
                                else:
                                    logger.warning("Failed to parse date: %s", value)
                                    result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = None
                continue
            value = field_data.get('content')
            if value_type == 'date' and value is not None:
                value = value.replace(',', '')
                parsed_value = parse(value, parse_formats, settings={'STRICT_PARSING': True})
                if parsed_value:
                    result['documents'][idx]['fields'][field_name]['value'] = parsed_value.strftime('%Y%m%d')
                elif len(value.split('-')) == 2:
                    parsed_value = date.fromisocalendar(int(value.split('-')[1]), int(value.split('-')[0]), 3)
                    result['documents'][idx]['fields'][field_name]['value'] = parsed_value.strftime('%Y%m%d')
                else:
                    logger.warning("Failed to parse date: %s", value)
                    result['documents'][idx]['fields'][field_name]['value'] = None
    return result

def extract_kv_pairs(result: dict) -> dict:
    """Extract only key-value pairs from analyze_document() result"""
    kv_pairs = {}
    kv_pairs['Creditor_number'] = result.get('Creditor_number')
    kv_pairs['Creditor_international_location_number'] = result.get('Creditor_international_location_number')
    for document in result.get('documents'):
        fields = document.get('fields', {})
        for field_name, field_data in fields.items():
            value_type = field_data.get('value_type')
            value = field_data.get('value')
            kv_pairs[field_name] = value
            if value_type == 'list':
                kv_pairs[field_name] = []
                for idx, item_line in enumerate(value):
                    kv_pairs[field_name].append({})
                    for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                        nested_value = nested_field_data.get('value')
                        kv_pairs[field_name][idx][nested_field_name] = nested_value
    return kv_pairs

class FormRecognizer:
    def __init__(self, dateformat: str ='%Y%m%d'):
        self.endpoint = os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT')
        self.key = os.getenv('AZURE_FORM_RECOGNIZER_KEY')
        self.client = DocumentAnalysisClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        self.dateformat = dateformat
    
    def __del__(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def analyze_document(self, modelmap_path: str, pdf_metadata: dict) -> dict:
        """Analyzes the invoice using Azure Form Recognizer."""
        try:
            model_map = read_json(modelmap_path)
            model_id = model_map.get(pdf_metadata.get('business'), {}).get('model_id')
            poller = self.client.begin_analyze_document(model_id, pdf_metadata.get('pdf'))
            result = poller.result()
            result = result.to_dict()
            result['locale'] = model_map.get(pdf_metadata.get('business'), {}).get('locale')
            result['Creditor_number'] = model_map.get(pdf_metadata.get('business'), {}).get('Creditor_number')
            result['Creditor_international_location_number'] = model_map.get(pdf_metadata.get('business'), {}).get('Creditor_international_location_number')
            return result
        except Exception:
            logger.exception("Failed to analyze document with %s", model_id)

    def print_result(self, result: dict):
        """Print the result of analyze_document in readable format"""
        try:
            for document in result.get('documents'):
                fields = document.get('fields', {})
                for field_name, field_data in fields.items():
                    value_type = field_data.get('value_type')
                    value = field_data.get('value')
                    if value_type == 'list':
                        for item in value:
                            value_type = item.get('value_type')
                            value = item.get('value')
                            for field_name, field_data in value.items():
                                value_type = field_data.get('value_type')
                                value = field_data.get('value')
                                content = field_data.get('content')
                                bounding_regions = field_data.get('bounding_regions', [])
                                spans = field_data.get('spans', [])
                                confidence = field_data.get('confidence')
                                print(f"Field Name: {field_name}")
                                print(f"  Value Type: {value_type}")
                                print(f"  Value: {value}")
                                print(f"  Content: {content}")
                                print(f"  Bounding Regions: {bounding_regions}")
                                print(f"  Spans: {spans}")
                                print(f"  Confidence: {confidence}")
                    content = field_data.get('content')
                    bounding_regions = field_data.get('bounding_regions', [])
                    spans = field_data.get('spans', [])
                    confidence = field_data.get('confidence')
                    print(f"Field Name: {field_name}")
                    print(f"  Value Type: {value_type}")
                    print(f"  Value: {value}")
                    print(f"  Content: {content}")
                    print(f"  Bounding Regions: {bounding_regions}")
                    print(f"  Spans: {spans}")
                    print(f"  Confidence: {confidence}")
        except Exception:
            logger.exception("Failed to print result")
                    

    def parse_numbers(self, result: dict) -> dict:
        """Parse the numbers in the result of the analysis."""
        locale = result.get('locale')
        for idx, document in enumerate(result.get('documents')):
            fields = document.get('fields', {})
            for field_name, field_data in fields.items():
                value_type = field_data.get('value_type')
                if value_type == 'list':
                    value = field_data.get('value')
                    for idxx, item_line in enumerate(value):
                        for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                            value_type = nested_field_data.get('value_type')
                            if nested_field_data.get('content') is not None: 
                                value = nested_field_data.get('content').replace(' ', '').replace('%', '').replace('€', '').replace('EUR', '')
                                if value_type == 'float':
                                    if value.find('-') != 0 and value.find('-') != -1:
                                        value = '-' + value.replace('-', '')
                                    value = parse_decimal(value, locale=locale)
                                    result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value']  = Decimal(value)
                                elif value_type == 'integer':
                                    if value.find('-') != 0 and value.find('-') != -1:
                                        value = '-' + value.replace('-', '')
                                    result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = int(value)
                    continue
                if field_data.get('content') is not None: 
                    value = field_data.get('content').replace(' ', '').replace('%', '').replace('€', '').replace('():', '').replace('hoogtarief,', '21').replace('EUR', '')
                    if value_type == 'float':
                        if value.find('-') != 0 and value.find('-') != -1:
                            value = '-' + value.replace('-', '')
                        value = parse_decimal(value, locale=locale)
                        result['documents'][idx]['fields'][field_name]['value']  = Decimal(value)
                    elif value_type == 'integer':
                        value = value.replace(',', '').replace('Prijs/','').replace('No.', '').replace('NMo.', '')
                        if value.find('-') != 0 and value.find('-') != -1:
                            value = '-' + value.replace('-', '')
                        result['documents'][idx]['fields'][field_name]['value'] = int(value)
        return result

    def parse_dates(self, result: dict, parsefmt_path: Path) -> dict:
        """Processes the dates in the result of the analysis."""
        parse_formats = read_json(parsefmt_path).get('formats')
        for idx, document in enumerate(result.get('documents')):
            fields = document.get('fields', {})
            for field_name, field_data in fields.items():
                value_type = field_data.get('value_type')
                if value_type == 'list':
                    value = field_data.get('value')
                    for idxx, item_line in enumerate(value):
                        for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                            value_type = nested_field_data.get('value_type')
                            if nested_field_data.get('content') is not None:
                                value = nested_field_data.get('content')
                                if value_type == 'date':
                                    value = value.replace(',', '').replace('leverdatum:', '')
                                    parsed_value = parse(value, parse_formats, settings={'STRICT_PARSING': True})
                                    if parsed_value:
                                        result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = parsed_value.strftime(self.dateformat)
                                    elif len(value.split('-')) == 2:
                                        parsed_value = date.fromisocalendar(int(value.split('-')[1]), int(value.split('-')[0]), 3)
                                        result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = parsed_value.strftime(self.dateformat)
                                    else:
                                        logger.warning("Failed to parse date: %s", value)
                                        result['documents'][idx]['fields'][field_name]['value'][idxx]['value'][nested_field_name]['value'] = None
                    continue
                value = field_data.get('content')
                if value_type == 'date' and value is not None:
                    value = value.replace(',', '').replace('/OM', '').replace('-kn', '')
                    parsed_value = parse(value, parse_formats, settings={'STRICT_PARSING': True})
                    if parsed_value:
                        result['documents'][idx]['fields'][field_name]['value'] = parsed_value.strftime(self.dateformat)
                    elif len(value.split('-')) == 2:
                        parsed_value = date.fromisocalendar(int(value.split('-')[1]), int(value.split('-')[0]), 3)
                        result['documents'][idx]['fields'][field_name]['value'] = parsed_value.strftime(self.dateformat)
                    else:
                        logger.warning("Failed to parse date: %s", value)
                        result['documents'][idx]['fields'][field_name]['value'] = None
        return result
    
    def extract_kv_pairs(self, result: dict) -> dict:
        """Extract only key-value pairs from analyze_document() result"""
        kv_pairs = {}
        kv_pairs['Creditor_number'] = result.get('Creditor_number')
        kv_pairs['Creditor_international_location_number'] = result.get('Creditor_international_location_number')
        for document in result.get('documents'):
            fields = document.get('fields', {})
            for field_name, field_data in fields.items():
                value_type = field_data.get('value_type')
                value = field_data.get('value')
                kv_pairs[field_name] = value
                if value_type == 'list':
                    kv_pairs[field_name] = []
                    for idx, item_line in enumerate(value):
                        kv_pairs[field_name].append({})
                        for nested_field_name, nested_field_data in item_line.get('value', {}).items():
                            nested_value = nested_field_data.get('value')
                            kv_pairs[field_name][idx][nested_field_name] = nested_value
        return kv_pairs


