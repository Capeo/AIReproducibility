from PIL import Image

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import math
import re
import os

def load_rows(path_to_csv):
    df = pd.read_csv(path_to_csv,
                     sep=',',
                     quotechar='"',
                     doublequote=True,
                     header=0,
                     encoding='utf-8')
    # start counting at 1
    df.index += 1
    return df

def split_list(category_papers_field):
    """Given a text-field of paper indices (e.g. "1, 5, 7"),
       split out the paper indices as a list of integers.
       Perform a minimal amount of error correction like accounting for
       multiple or no spaces between numbers.
    """
    if type(category_papers_field) == float and math.isnan(category_papers_field):
        return []
    s = category_papers_field.replace(",", " ").replace(";", " ")
    s = re.sub("\s+", " ", s).strip()
    ints = [int(x) for x in s.split()]
    return ints

def create_heatmap(papers, categories):
    # rows of paper IDs, class, and titles -- the first three columns
    paper_rows = papers.iloc[:,0:3] #[papers.keys()[0:3]]
    # rows of category IDs (e.g P10)
    category_identifiers = categories.iloc[:,0]

    # for each X category out of the n, parse out the papers in the string
    # (e.g "1, 5, 6, ..."), and set the heatmap field for that (paper, Xn) to 1
    category_rows = [[0 for i in category_identifiers] for j in range(paper_rows.shape[0])]
    for IDX,(cat_ID,desc,indice_string) in categories.iterrows():
        paper_indices = split_list(indice_string)
        for paper_index in paper_indices:
            category_rows[paper_index-1][IDX-1] = 1

    category_map = pd.DataFrame.from_records(category_rows, columns=category_identifiers)
    category_map.index += 1

    # concatenate the rows of paper ids+titles with the rows of the heatmap
    # ID paper R1/R2 XC1 XC2 XC3 ...
    # 1   ABC   R1    1   0   1  ...
    # ...
    full_map = pd.concat([paper_rows, category_map], axis=1)
    return full_map

def load(path_to_papers_csv, path_to_category_csv):
    """Return the heatmap for the papers in a category (e.g problems)"""
    papers = load_rows(path_to_papers_csv)
    categories = load_rows(path_to_category_csv)
    heatmap = create_heatmap(papers, categories)
    return heatmap

def split_into_R1_R2(heatmap):
    R1 = heatmap.loc[heatmap["R1/R2"] == "R1"]
    R2 = heatmap.loc[heatmap["R1/R2"] == "R2"]
    return R1,R2

def savefig(heatmap, path, **kwargs):
    fig = sns.heatmap(heatmap, **kwargs)
    fig.get_figure().savefig(path)
    # clear figure
    plt.clf()
    return fig

def save_heatmap_vertical(heatmap, path, **kwargs):
    fig = sns.heatmap(heatmap, **kwargs)
    fig.xaxis.tick_top()
    fig.set_ylabel("Paper")
    fig.get_figure().savefig(path)
    # clear figure
    plt.clf()
    return fig

def save_stacked_bar_chart(frame, path, xlabel, ylabel, **kwargs):
    frame = frame.T
    fig = frame.plot.bar(stacked=True, **kwargs)
    fig.set_xlabel(xlabel)
    fig.set_ylabel(ylabel)
    fig.get_figure().savefig(path)
    plt.clf()
    return fig

def save_horizontal_bar_chart(frame, path, **kwargs):
    fig = frame.plot.barh(**kwargs)
    fig.invert_yaxis()
    fig.xaxis.tick_top()
    fig.set_ylabel("Paper")
    fig.set_xlabel("Count")
    fig.xaxis.set_label_position('top')
    fig.get_figure().savefig(path)
    plt.clf()

def blend(path1, path2, output_path):
    img1 = np.asarray(Image.open(path1))
    img2 = np.asarray(Image.open(path2))

    blended = (img1*0.5 + img2*0.5).astype(np.uint8)
    img = Image.fromarray(blended)
    img.save(output_path)

def main(output_directory):
    plt.style.use('seaborn-white')
    #{ ass:[full_map, R1_map, R2_map],
    #  prob:[...],
    #  ...}
    maps = {"assumption" : [load("papers.csv", "acat.csv")],
            "problem" : [load("papers.csv", "pcat.csv")],
            "error" : [load("papers.csv", "ecat.csv")]
           }
    # add the maps where R1 and R2 are separate
    for key in maps:
        heatmap = maps[key][0]
        maps[key].extend(split_into_R1_R2(heatmap))

    # [assumption, problem, error]
    for overall_category in maps:
        # 2D version, i.e only 0 or 1 and each paper has its own row
        # [both, R1, R2]
        for division,divtag in zip(maps[overall_category], ["both", "R1", "R2"]):
            # skip the first three columns with paper title etc
            heatmap = division.iloc[:,3:]
            filename = "{}_{}_{}".format(
                                         "2D",
                                         overall_category,
                                         divtag)
            path = os.path.join(output_directory, filename)
            savefig(heatmap, path, annot=True)

        # 1D version, i.e only one row where each column is the number of
        # occurences for that X category across the papers
        # [both, R1, R2]
        for division,divtag in zip(maps[overall_category], ["both", "R1", "R2"]):
            # skip the first three columns with paper title etc
            heatmap = pd.DataFrame(division.iloc[:,3:].sum(axis=0)).T
            # all rows are collapsed into one, so give it an appropriate label
            heatmap.index=["Collated count"]
            filename = "{}_{}_{}".format(
                                         "1D",
                                         overall_category,
                                         divtag)
            path = os.path.join(output_directory, filename)
            savefig(heatmap , path, square=True, annot=True)

        # generate bar charts
        r1_map = pd.DataFrame(maps[overall_category][1].iloc[:,3:].sum(axis=0)).T
        r1_map.index = ["R1"]
        r2_map = pd.DataFrame(maps[overall_category][2].iloc[:,3:].sum(axis=0)).T
        r2_map.index = ["R2"]
        combined_map = pd.concat([r1_map, r2_map])
        for division, divtag in zip([combined_map, r1_map, r2_map], ["both", "R1", "R2"]):
            filename = "{}_{}_bar".format(
                overall_category,
                divtag)
            path = os.path.join(output_directory, filename)
            save_stacked_bar_chart(division, path, overall_category.capitalize(), "Count")


        # 1D version, R1 and R2 normalized to number of papers
        # [R1, R2]
        R1 = pd.DataFrame(maps[overall_category][1].iloc[:,3:])
        R2 = pd.DataFrame(maps[overall_category][2].iloc[:,3:])
        weighted_R1 = pd.DataFrame(R1.sum(axis=0)/R1.shape[0]).T
        weighted_R2 = pd.DataFrame(R2.sum(axis=0)/R2.shape[0]).T

        # set the center value of the heatmap based on the category with the
        # highest count
        max1,max2 = weighted_R1.values.max(), weighted_R2.values.max()
        center = max(max1, max2)*0.5

        # temporary file, blended with PIL (Pillow) later
        path1 = os.path.join(output_directory, "tmp_R1.png")
        fig1 = savefig(weighted_R1, path1, square=True, annot=False, cmap="Blues", center=center)

        # temporary file, blended with PIL (Pillow) later
        path2 = os.path.join(output_directory, "tmp_R2.png")
        fig2 = savefig(weighted_R2, path2, square=True, annot=False, cmap="Reds",  center=center)

        # perform a very cheap blend by creating a new image using half of each
        filename = "{}_{}.png".format("blended", overall_category)
        output_path = os.path.join(output_directory, filename)
        blend(path1, path2, output_path)

    # plot problems, assumptions, and errors per paper
    category_maps = []
    for overall_category in maps:
        frame = pd.DataFrame(maps[overall_category][0].iloc[:,3:].sum(axis=1))
        # rename column
        frame.columns = [overall_category.capitalize()]
        category_maps.append(frame)
    frames = pd.concat(category_maps, axis=1)
    filename = "papers_bar.png"
    output_path = os.path.join(output_directory, filename)
    save_horizontal_bar_chart(frames, output_path, cmap='tab20b', width=0.5, figsize=(6,12))
    filename = "papers_heatmap.png"
    output_path = os.path.join(output_directory, filename)
    save_heatmap_vertical(frames, output_path, annot=True)

if __name__ == '__main__':
    main(output_directory="output_figures")
