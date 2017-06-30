from __future__ import division
from sklearn.cluster import KMeans 
from numbers import Number
from pandas import DataFrame
import sys, codecs, numpy
from autovivify_list import autovivify_list
import helpers,config # our own classes


def build_word_vector_matrix(vector_file, n_words, remove_all_id_properties=True):
        '''Read a GloVe array from sys.argv[1] and return its vectors and labels as arrays'''
        numpy_arrays = []
        labels_array = []
        properties = helpers.get_properties_by_id(config.PROPS_FILE)
        with codecs.open(vector_file, 'r', 'utf-8') as f:
                num_skipped = 0
                for c, r in enumerate(f):
                        sr = r.split()  
                        prop_label = properties[sr[0]]["label"]
                        if str(sr[1])=='nan' or prop_label.find("ID") >=0 or prop_label.find(" id") >= 0:
                            print "skipping", properties[sr[0]]["label"].encode('utf-8')
                            num_skipped+=1
                        else:
                            labels_array.append(sr[0])
                            numpy_arrays.append( numpy.array([float(i) for i in sr[1:]]) )

                            if c == n_words:
                                return numpy.array( numpy_arrays ), labels_array

        print "Number skipped:", num_skipped
        return numpy.array( numpy_arrays ), labels_array


def find_word_clusters(labels_array, cluster_labels):
        '''Read the labels array and clusters label and return the set of words in each cluster'''
        properties = helpers.get_properties_by_id(config.PROPS_FILE)
        cluster_to_words = autovivify_list()
        for c, i in enumerate(cluster_labels):
                wd_label = properties[labels_array[c]]["label"]
                #cluster_to_words[ i ].append( labels_array[c] ) # orig version
                cluster_to_words[ i ].append( wd_label ) 
        return cluster_to_words


def main_caller():
        """
        this function calls and does the clustering
        """
        input_vector_file = sys.argv[1] # The word-embeddings file to analyze (e.g. glove.6B.300d.txt)
        n_words           = int(sys.argv[2]) # The number of lines to read from the input file
        reduction_factor  = float(sys.argv[3]) # The desired amount of dimension reduction 

        clusters_to_make  = int( n_words * reduction_factor ) # The number of clusters to make
        df, labels_array  = build_word_vector_matrix(input_vector_file, n_words)

        #### do the clustering .. so simple :-)
        kmeans_model      = KMeans(init='k-means++', n_clusters=clusters_to_make, n_init=10)
        kmeans_model.fit(df)
        cluster_labels    = kmeans_model.labels_
        cluster_inertia   = kmeans_model.inertia_
        cluster_to_words  = find_word_clusters(labels_array, cluster_labels)

        ### print the clusters
        for c in cluster_to_words:
                print cluster_to_words[c], 
                print "\n"

if __name__ == "__main__":
        main_caller()
