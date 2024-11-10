# import spacy
# from sklearn.metrics.pairwise import cosine_distances
# import numpy as np
# from spacy.cli import download
# from k_means_constrained import KMeansConstrained

# class NLPLayer:
#     def __init__(self):
#         # Load the pre-trained spaCy model (en_core_web_md provides word vectors)
#         try:
#             self.nlp = spacy.load('en_core_web_md')
#         except OSError:
#             download('en_core_web_md')
#             self.nlp = spacy.load('en_core_web_md')

#     def get_word_embeddings(self, words):
#         """
#         Convert words into their embeddings using spaCy's word vectors.
#         """
#         embeddings = []
        
#         for i in range(len(words)):
#             doc = self.nlp(words[i])  # Process the word
#             embeddings.append(doc.vector)  # Get the word's vector (embedding)
#         return np.array(embeddings)

#     def get_initial_groups(self, words):
#         """
#         Generate initial candidate groups of 4 words by clustering word embeddings
#         using cosine similarity.
#         """
#         # Clean the list of words: filter out any unwanted characters (if needed)
#         if len(words) < 4:
#             return []  # Return empty if not enough words to form clusters
        
#         embeddings = self.get_word_embeddings(words)

#         # Compute the cosine distance matrix (1 - cosine similarity) 
#         cosine_dist = cosine_distances(embeddings)

#         # Perform Agglomerative (Hierarchical) Clustering with cosine distances
#         clustering = KMeansConstrained(n_clusters=4, size_min=4, size_max=4, random_state=0)
#         cluster_labels = clustering.fit_predict(cosine_dist)

#         # Group words based on their cluster labels
#         clusters = [[] for _ in range(4)]
#         for word, label in zip(words, cluster_labels):
#             clusters[label].append(word)
#         print("Clusters:", clusters)
#         # Ensure each cluster has exactly 4 words (if not, adjust clusters or retry)
#         candidate_groups = [group for group in clusters if len(group) == 4]
#         # print("Candidate groups:", candidate_groups)
#         # Return the candidate groups only if valid
#         return candidate_groups if len(candidate_groups) == 4 else []  # Return valid groups only


import spacy
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
from spacy.cli import download
from k_means_constrained import KMeansConstrained

class NLPLayer:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_md')
        except OSError:
            download('en_core_web_md')
            self.nlp = spacy.load('en_core_web_md')

    def get_word_embeddings(self, words):
        embeddings = [self.nlp(word).vector for word in words]
        return np.array(embeddings)

    def refine_groups(self, initial_groups):
        """
        Validate initial groups by clustering word embeddings using cosine similarity.
        """
        refined_groups = []
        for group in initial_groups:
            embeddings = self.get_word_embeddings(group)
            # print("size of embeddings: ", embeddings.shape)
            clustering = KMeansConstrained(n_clusters=1, size_min=4, size_max=4, random_state=0)
            cluster_labels = clustering.fit_predict(embeddings)
            if len(set(cluster_labels)) == 1:
                refined_groups.append(group)
        return refined_groups
