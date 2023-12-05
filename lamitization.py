import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def lemmatize_and_clean(text):
    # Tokenize the text into words
    words = nltk.word_tokenize(text)

    # Remove punctuation and convert to lowercase
    words = [word.lower() for word in words if word.isalpha()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join the words back into a cleaned text
    cleaned_text = ' '.join(words)

    return cleaned_text

# Example usage
input_text = "kushir cover. kushir cover benson and hezes nih unique capsule of our janum benson and hesses breeze aprajanara kushiha benjay a capsule roche egg thorne refreshing taste and smell arapnajudiya trial kotachan tahal ajinita parnakti trial kit donnabat."
cleaned_text = lemmatize_and_clean(input_text)

print("Original Text:")
print(input_text)
print("\nCleaned Text:")
print(cleaned_text)
