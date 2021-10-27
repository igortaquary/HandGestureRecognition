import math

no_thumb_dict = {
    "1 1 1 1": "O",
    "0 1 1 0": "P",
    "1 0 0 1": "U",
    "0 0 0 1": "I",
    "1 0 0 0": "I",
    "1 1 0 0": "V",
    "0 0 1 1": "V",
    "1 1 1 0": "E",
    "0 1 1 1": "E",
}

left_thumb_dict = {
    "1 1 1 1": "O",
    "0 1 0 0": "R",
    "1 0 0 1": "G",
    "0 0 0 1": "P",
    "1 0 0 0": "R"
}

right_thumb_dict = {
    "1 1 1 1": "O",
    "0 0 0 1": "L",
    "0 0 1 0": "A",
    "1 0 0 1": "P",
    "1 0 0 0": "K",
}

def classify(orientation, x_cent, y_cent, max_peaks, thumb):
    filtered_peaks = filter_peaks(orientation, x_cent, y_cent, max_peaks, thumb)

    distances = []
    for peak in filtered_peaks:
        distances.append( euclid_dist(peak, x_cent, y_cent) )

    significant_peaks = []
    significant_percent = 0.75

    max_distance = max(distances)
    for distance in distances:
        if( distance/max_distance > significant_percent ):
            significant_peaks.append(1)
        else:
            significant_peaks.append(0)

    print("significant_peaks")
    print(significant_peaks)
    code = " ".join(map(str, significant_peaks))

    if thumb == "LEFT":
        print(left_thumb_dict[code])
        return str(left_thumb_dict[code])
    elif thumb == "RIGHT":
        print(right_thumb_dict[code])
        return str(right_thumb_dict[code])
    else:
        print(no_thumb_dict[code])
        return str(no_thumb_dict[code])

def filter_peaks(orientation, x_cent, y_cent, max_peaks, thumb):
    filtered_peaks = []
    if orientation == "VERT":
        #Peak has to be higher than y_cent
        for peak in max_peaks:
            if peak[1] < y_cent:
                filtered_peaks.append(peak)

        filtered_peaks.sort(key=sort_criteria_vert)

        if thumb == "LEFT":
            filtered_peaks.pop(0)
        elif thumb == "RIGHT":
            filtered_peaks.pop(len(filtered_peaks) - 1)

    #print(len(filtered_peaks))
    return filtered_peaks


def sort_criteria_vert(peak):
    return peak[0]

def sort_criteria_horz(peak):
    return peak[1]

def euclid_dist(peak, x_cent, y_cent):
    return math.sqrt( math.pow( (peak[0] - x_cent) , 2) + math.pow( (peak[1] - y_cent) , 2) )
    