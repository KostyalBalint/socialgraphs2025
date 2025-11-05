import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from wordcloud import WordCloud
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

from extract_wikipedia_text_to_string import get_wiki_text
from sentiment_analysis import calculate_sentiment
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS



def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'


class TFIDF_Communities:
    def __init__(self, _type, communities_sorted, custom_stopwords=False):

        #this is the type of community we are working on, genre-based or formed by louvain-algorithm for example
        self.type = _type

        #these are the concatanated texts of the artists who are in the same community
        self.documents = self.calculate_documents(communities_sorted)
        #Here we perform lemmatization with POS tagging, so that we can work on words in their base form and achieve a better TF-IDF representation
        lemmatizer = WordNetLemmatizer()

        lemmatized_docs = []
        for doc in self.documents:
            # Tokenize the document
            tokens = word_tokenize(doc.lower())
            # Get POS tags
            pos_tags = pos_tag(tokens)
            # Lemmatize with POS information
            lemmatized = [lemmatizer.lemmatize(word, pos=get_wordnet_pos(tag))
                          for word, tag in pos_tags]
            # Join back into a string
            lemmatized_docs.append(' '.join(lemmatized))

        self.documents = lemmatized_docs

        # Calculate TF-IDF
        if custom_stopwords:
            custom_stop_words = list(ENGLISH_STOP_WORDS.union([
                'album', 'band', 'song', 'release', 'tour', 'record', 'music'
            ]))
            self.tfidf = TfidfVectorizer(stop_words=custom_stop_words)
        else:
            self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.documents)
        self.tfidf_array = self.tfidf_matrix.toarray()
        self.feature_names = self.tfidf.get_feature_names_out()
        self.tfidf_df = pd.DataFrame(self.tfidf_array, columns=self.feature_names)

        # Sentiment scores for each document
        self.sentiment_scores_of_documents = {}

    # Given the communities, we create documents by concatenating the Wikipedia texts of all artists in each community
    def calculate_documents(self, communities_sorted):
        documents = []
        for community in communities_sorted[:15]:
            all_text = ""
            for artist in community:
                artist_file_name = "wikipedia_pages/" + artist.replace("(", "").replace(")", "").replace(".",
                                                                                                         "").replace(
                    "–", "").replace("'", "").replace("/", "").replace("&", ""
                                                                       ).replace("!", "").replace(",", "") + ".json"
                text = get_wiki_text(artist_file_name)
                all_text = all_text + " " + text
            documents.append(all_text)
        return documents

    # Calculate sentiment scores for each document based on the provided word scores
    def calculate_sentiment_scores(self, word_scores, community_names):
        for text in self.documents:
            sentiment = calculate_sentiment(text, word_scores)['mean']
            self.sentiment_scores_of_documents[community_names[self.documents.index(text)]] = sentiment


    # Plot PCA of the TF-IDF matrix
    def plot_pca(self, enumerator):
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(self.tfidf_array)
        tsne_genre = TSNE(n_components=2, perplexity=2, random_state=0)
        tsne_result_genre = tsne_genre.fit_transform(self.tfidf_array)
        plt.figure(figsize=(10, 7))
        plt.scatter(pca_result[:, 0], pca_result[:, 1], c='blue', edgecolor='k', s=50)
        for i, txt in enumerate(enumerator):
            plt.annotate(txt, (pca_result[i, 0], pca_result[i, 1]))
        plt.title('PCA of TF-IDF Matrix')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.show()

    # Plot Word Cloud based on mean TF-IDF scores
    def plot_wordcloud(self):
        mean_tfidf = np.asarray(self.tfidf_matrix.mean(axis=0)).flatten()
        word_freq = {self.feature_names[i]: mean_tfidf[i] for i in range(len(self.feature_names))}
        wordcloud_genre = WordCloud(width=1600, height=800,
                                    background_color='white',
                                    colormap='viridis',
                                    relative_scaling=0.5,
                                    min_font_size=10).generate_from_frequencies(word_freq)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_genre, interpolation='bilinear')
        plt.axis('off')
        plt.title('TF-IDF Word Cloud - All Documents of' + self.type + ' communities', fontsize=20, fontweight='bold', pad=20)
        plt.tight_layout(pad=0)