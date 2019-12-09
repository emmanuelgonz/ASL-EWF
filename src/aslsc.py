
def extract_intensity_histograms(boxes, field):
    pixel_histograms = []
    for x1,y1,x2,y2 in boxes[1:]:
        pixel_histograms.append(np.histogram(field[x1:x2,y1:y2].flatten(),bins=[64,128,160,192,208,224,232,240,244,248,250,252,253,254])[0])

    return np.array(pixel_histograms)

def calculate_sizes(boxes, field, return_kmeans=False):
    pixel_hists = extract_intensity_histograms(boxes, field)
    if os.path.exists("../model/k_means_model.pickle"):
        k_means = pickle.load(open("../model/k_means_model.pickle",'rb'))
        print("Model Found")
    else:
        k_means = KMeans(n_clusters=3)
        k_means.fit(pixel_hists)
        pickle.dump(k_means,open("../model/k_means_model.pickle",'wb'))
        print("Saving Kmeans Model")
    indexes = label_meaning(k_means.cluster_centers_)

    labels = k_means.predict(pixel_hists)

    if return_kmeans:
        return labels, indexes, k_means
    else:
        return labels, indexes
    
    label_output = []
    for label in labels:
        label_output.append(size_labels[label])
    np.save(name+"/size_labels.npy",np.array(label_output))