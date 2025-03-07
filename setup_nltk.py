import nltk
import sys

def download_nltk_resources():
    """Download required NLTK resources."""
    resources = [
        'punkt',
        'stopwords',
        'wordnet'
    ]
    
    print("Downloading NLTK resources...")
    for resource in resources:
        try:
            print(f"Downloading {resource}...")
            nltk.download(resource)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {e}", file=sys.stderr)
            return False
    
    print("All NLTK resources downloaded successfully!")
    return True

if __name__ == "__main__":
    success = download_nltk_resources()
    if not success:
        print("Failed to download some NLTK resources. Please check the errors above.")
        sys.exit(1)
