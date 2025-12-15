import spacy
import re

# Load SpaCy model - remember to install it: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    # Fallback or exit? For now let's just create a dummy object or re-raise
    raise

def extract_claims(text):
    """
    Extract factual claims that likely need sources
    Uses dependency parsing to find declarative statements
    """
    # Helper to clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    doc = nlp(text)
    claims = []
    
    for sent in doc.sents:
        # Pattern 1: Statements with numerical data
        if re.search(r'\d+%|\d+ percent|\$\d+|[0-9,]+', sent.text):
            claims.append({
                'text': sent.text,
                'type': 'statistical',
                'confidence': 0.9
            })
        
        # Pattern 2: Attribution phrases
        attribution_patterns = [
            r'according to (.+?),',
            r'(.+?) said',
            r'(.+?) reported',
            r'(.+?) found that',
            r'research (?:by|from) (.+?) shows',
            r'(?:a|the) (?:study|report) (?:by|from) (.+?) '
        ]
        
        for pattern in attribution_patterns:
            match = re.search(pattern, sent.text, re.IGNORECASE)
            if match:
                claims.append({
                    'text': sent.text,
                    'type': 'attributed',
                    'source_mention': match.group(1),
                    'confidence': 0.95
                })
        
        # Pattern 3: Definitive statements (potential unsourced claims)
        # Check if sentence is a declarative statement (simple heuristic)
        if len(sent) > 3 and sent[0].dep_ == 'nsubj' and sent.root.pos_ == 'VERB':
            # "X is Y", "X does Y", "X has Y"
            if not any(p in sent.text.lower() for p in ['i think', 'may', 'might', 'could']):
                claims.append({
                    'text': sent.text,
                    'type': 'assertion',
                    'confidence': 0.6
                })
    
    return claims

def extract_entities(text):
    """
    Find organizations, people, publications mentioned
    These are potential sources to search for
    """
    doc = nlp(text)
    
    entities = {
        'orgs': [],      # CDC, WHO, Harvard, etc.
        'people': [],    # Dr. Smith, researchers
        'publications': [],  # journals, newspapers
        'dates': []      # when was this claim made?
    }
    
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            entities['orgs'].append(ent.text)
        elif ent.label_ == 'PERSON':
            entities['people'].append(ent.text)
        elif ent.label_ == 'DATE':
            entities['dates'].append(ent.text)
    
    # Pattern matching for academic journals
    journal_pattern = r'(?:published in|appeared in|from) (?:the )?(.*?(?:Journal|Review|Science|Nature|Proceedings))'
    for match in re.finditer(journal_pattern, text, re.IGNORECASE):
        entities['publications'].append(match.group(1))
    
    # Deduplicate
    for key in entities:
        entities[key] = list(set(entities[key]))
        
    return entities
