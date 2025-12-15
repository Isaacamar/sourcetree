import anthropic
import os
import json

# Initialize the client. 
# Defaults to ANTHROPIC_API_KEY environment variable
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("DEBUG: ANTHROPIC_API_KEY not found in environment variables.")
else:
    print(f"DEBUG: ANTHROPIC_API_KEY found (starts with {api_key[:10]}...)")

try:
    client = anthropic.Anthropic(api_key=api_key)
except Exception as e:
    print(f"Warning: Anthropic client failed to initialize (check API key): {e}")
    client = None

def llm_extract_implicit_sources(page_text, page_url):
    """
    Use Claude to identify claims that SHOULD have sources
    but don't explicitly link to them
    """
    if not client:
        return []

    prompt = f"""You are analyzing a webpage for epistemological research.

URL: {page_url}

TEXT:
{page_text[:4000]}  # Truncate to fit context

Your task:
1. Identify 5-10 FACTUAL CLAIMS in this text that would require external verification
2. For each claim, identify:
   - The specific claim text
   - What type of source would verify it (research study, government data, expert testimony, etc.)
   - Any people/organizations mentioned who might be the original source
   - Whether the claim seems to have an explicit source in the text or not

Return ONLY a JSON array like:
[
  {{
    "claim": "70% of Americans support X",
    "needs_source_type": "poll/survey data",
    "mentioned_source": "Pew Research Center",
    "has_explicit_link": false,
    "search_query": "Pew Research Americans support X 2024"
  }},
  ...
]
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514", # Updated to user-specified model
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        response_text = message.content[0].text
        # Cleanup if markdown code blocks are present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
             response_text = response_text.split("```")[1].split("```")[0].strip()

        claims = json.loads(response_text)
        return claims
    except Exception as e:
        print(f"LLM Analysis failed: {e}")
        return []

import re

def verify_link_significance(context_text, link_url, link_anchor):
    """
    Asks LLM to determine if loop is a CAUSAL SOURCE or just related reading.
    Returns: { 'score': 0-100, 'reason': '...', 'is_source': True/False }
    """
    if not client:
        return {'score': 50, 'reason': 'No LLM available', 'type': 'Error'}

    prompt = f"""
    Analyze the following citation link in its context.
    
    Context Text: "{context_text}"
    Link Anchor Text: "{link_anchor}"
    Link URL: "{link_url}"
    
    Task: Determine if this link is provided as EVIDENTIAL PROOF for a specific claim in the context, or if it is just "Related Reading" / "Navigation".
    
    Return a JSON object with:
    1. "score": integer 0-100. (0=Navigation/Ad, 20=Related Topic, 50=Background Context, 80=Direct Source of Data/Quote, 100=The Primary Subject)
    2. "type": One of ["Source", "Related", "Navigation", "Ad"]
    3. "reason": Brief explanation (15 words max)
    """
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                'score': data.get('score', 0),
                'type': data.get('type', 'Related'),
                'reason': data.get('reason', '')
            }
        else:
             return {'score': 0, 'type': 'Error', 'reason': 'Failed to parse JSON'}
             
    except Exception as e:
        print(f"LLM Error in verification: {e}")
        return {'score': 50, 'type': 'Error', 'reason': str(e)}
