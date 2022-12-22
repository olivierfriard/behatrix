"""
Behatrix
Behavioral sequences analysis with permutations test

Copyright 2017-2022 Olivier Friard

This file is part of Behatrix.

  Behatrix is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  Behatrix is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

"""

import itertools
import random
import numpy as np
from typing import Tuple


def remove_comments(s: str) -> str:
    """
    remove comments:
    split text in lines with \n and remove lines beginning with #

    Args:
        s (string): text

    Returns:
        str: text without commented lines (starting with #) separated by \n
    """

    strings_list = []
    for x in s.split("\n"):
        if not x.strip().startswith("#"):
            strings_list.append(x)
    return "\n".join(strings_list)


def behavioral_sequence_analysis(
    string: str, behaviors_separator: str = "", chunk: int = 0, flag_remove_repetitions: bool = False, ngram: int = 1
) -> dict:
    """
    Extract some information from behavioral sequences

    Args:
        string (str): behavioral sequences
        separator (str): string to use to split sequences in behaviors
        chunk (int): limit analysis to the chunk first characters
        flag_remove_repetitions (bool): if true remove behaviors repetions
        ngram (int): number of behaviors to group

    Returns:
        dict: results

    """

    # remove lines starting with #
    string = remove_comments(string)

    # check if behaviors are unique char
    if behaviors_separator:
        seq_list = []
        for seq in string.split("\n"):
            # skip empty line
            if not seq:
                continue
            seq_list.append(seq.strip().split(behaviors_separator))

    else:
        seq_list = []
        for seq in string.replace(" ", "").split():
            # skip empty line
            if not seq:
                continue
            seq_list.append(list(seq.strip()))

    sequences = []
    transitions = {}
    nodes = {}
    starting_nodes = {}
    min_chunk_length = 1e6
    line_count = 0

    for seq in seq_list:

        r = seq
        # check if repetitions
        if flag_remove_repetitions:
            r = [k for k, _ in itertools.groupby(r)]

        if chunk:
            r = r[0:chunk]

        sequences.append(r)

        line_count += 1

        min_chunk_length = min(min_chunk_length, len(r))

        for node in r:
            if node in nodes:
                nodes[node] += 1
            else:
                nodes[node] = 1

        for i in range(len(r) - 1):

            # starting node
            if i == 0:
                if r[i] in starting_nodes:
                    starting_nodes[r[i]] += 1
                else:
                    starting_nodes[r[i]] = 1

            if (r[i], r[i + 1]) in transitions:
                transitions[(r[i], r[i + 1])] += 1
            else:
                transitions[(r[i], r[i + 1])] = 1

    # total number of transitions
    tot_trans = 0
    for transition in transitions:
        tot_trans += transitions[transition]

    # number of transitions after behavior
    tot_trans_after_node = {}

    for transition in transitions:

        if transition[0] in tot_trans_after_node:
            tot_trans_after_node[transition[0]] += transitions[transition]
        else:
            tot_trans_after_node[transition[0]] = transitions[transition]

    tot_nodes = 0
    for node in nodes:
        tot_nodes += nodes[node]

    behaviours = []

    # extract unique behaviors
    for seq in sequences:
        for c in seq:
            if c not in behaviours:
                behaviours.append(c)

    behaviours.sort()

    out_ngrams = ""

    if ngram > 1:
        tot_ngrams, uniq_ngrams = [], []
        for sequence in sequences:
            tot_ngrams.extend(
                [
                    tuple(sequence[i : i + ngram])
                    for i, _ in enumerate(sequence)
                    if len(sequence[i : i + ngram]) == ngram
                ]
            )

        uniq_ngrams = list(dict.fromkeys(tot_ngrams))

        for element in sorted(uniq_ngrams):

            ngram_count = sum(
                [
                    [
                        tuple(sequence[i : i + ngram])
                        for i, _ in enumerate(sequence)
                        if len(sequence[i : i + ngram]) == ngram
                    ].count(element)
                    for sequence in sequences
                ]
            )

            out_ngrams += (
                f"{behaviors_separator.join(element)}\t"
                f"{ngram_count / len(tot_ngrams):.3f}\t"
                f"{ngram_count} / {len(tot_ngrams)}\n"
            )

    return {
        "sequences": sequences,
        "transitions": transitions,
        "nodes": nodes,
        "starting_nodes": starting_nodes,
        "tot_nodes": tot_nodes,
        "tot_trans": tot_trans,
        "tot_trans_after_node": tot_trans_after_node,
        "behaviours": behaviours,
        "out_ngrams": out_ngrams,
    }


def check_exclusion_list(exclusion_str: str, sequences: list, behaviors_separator: str = "") -> dict:
    """
    check the transition exclusion strings
    format must be like:
    a:bc
    or
    a:b|c

    Args:
        exclusion_str (str): exclusion strings (format must be a:bc or a:b|c
        sequences (list): list of sequences
        behaviors_separator (str): string to be used to split sequences in behaviors

    Returns:
        dict: keys: "error_code": 0 or 1
                    "exclusion_list": {"a": ["b", "c"]}
    """

    exclusion_list = {}

    if exclusion_str:
        rows = exclusion_str.split("\n")

        for row in rows:
            if row.strip() and ":" in row:
                s1, s2 = row.strip().split(":")
                if s1 and s2:
                    if s1 not in exclusion_list:
                        exclusion_list[s1] = []
                    if behaviors_separator and behaviors_separator in s2:
                        exclusion_list[s1] += s2.split(behaviors_separator)
                    else:
                        exclusion_list[s1] += list(s2)

        # test if behavioral sequences do not contain an excluded transition
        for seq in sequences:
            for i in range(len(seq) - 1):
                if seq[i] in exclusion_list and seq[i + 1] in exclusion_list[seq[i]]:
                    return {
                        "error_code": 1,
                        "message": f"The behavioral sequences contain an excluded transition: {seq[i]} -> {seq[i + 1]}",
                        "exclusion_list": {},
                    }

    return {"error_code": 0, "exclusion_list": exclusion_list}


def draw_diagram(
    cutoff_all,
    cutoff_behavior,
    unique_transitions,
    nodes,
    tot_nodes,
    tot_trans,
    tot_trans_after_node,
    starting_nodes=[],
    edge_label="percent_node",  # fraction_node/percent_node/percent_total
    transparent_background=False,
    include_first=True,
    decimals_number=3,
    significativity=None,
    behaviors=[],
) -> tuple:

    """
    create code for GraphViz
    return string containing graphviz code
    """

    def f_edge_label(
        edge_label, node1, node2, n_transition, tot_trans_after_node_i0, tot_trans, decimals_number, pen_width=1
    ):

        if edge_label == "fraction_node":
            return (
                f'"{node1}" -> "{node2}" [label = "  {n_transition}/{tot_trans_after_node_i0}" penwidth={pen_width}];\n'
            )

        elif edge_label == "percent_node":
            percent = n_transition / tot_trans_after_node_i0 * 100
            return f'"{node1}" -> "{node2}" [label = "  {percent:.{decimals_number}f} %" penwidth={pen_width}];\n'

        elif edge_label == "percent_total":
            percent = n_transition / tot_trans * 100.0
            return f'"{node1}" -> "{node2}" [label = "  {percent:.{decimals_number}f} %" penwidth={pen_width}];\n'

    def width(p: float) -> int:
        """
        return pen width for graphviz script according the significativity

        Args:
           p (float): significativity

        Returns:
            int: pen width to be used in graphviz script
        """

        if p <= 0.001:
            return 6
        elif p <= 0.005:
            return 3
        else:
            return 1

    header_out = "digraph G {\n"

    nodes_out = "/* node properties */\n"
    nodes_out += "\nnode []\n"

    nodes_list = []

    '''
    for node in nodes:
        nodes_out += f'"{node}"\n'
    '''

    edges_out = "\n/* edges */\n"

    if cutoff_all:

        for i in unique_transitions:

            if unique_transitions[i] / tot_trans * 100.0 >= cutoff_all:

                if i[0] in starting_nodes:
                    node1 = f"{i[0]} ({starting_nodes[i[0]]})"
                else:
                    node1 = f"{i[0]}"

                if i[1] in starting_nodes:
                    node2 = f"{i[1]} ({starting_nodes[i[1]]})"

                else:
                    node2 = f"{i[1]}"

                nodes_list.append(node1)
                nodes_list.append(node2)

                pen_width = (
                    width(significativity[behaviors.index(i[0]), behaviors.index(i[1])])
                    if significativity is not None
                    else 1
                )

                edges_out += f_edge_label(
                    edge_label,
                    node1,
                    node2,
                    unique_transitions[i],
                    tot_trans_after_node[i[0]],
                    tot_trans,
                    decimals_number,
                    pen_width,
                )
       

    elif cutoff_behavior:

        for i in unique_transitions:

            if unique_transitions[i] / tot_trans_after_node[i[0]] * 100 >= cutoff_behavior:

                if i[0] in starting_nodes and include_first:
                    node1 = f"{i[0]} ({starting_nodes[i[0]]})"
                else:
                    node1 = f"{i[0]}"

                if i[1] in starting_nodes and include_first:
                    node2 = f"{i[1]} ({starting_nodes[i[1]]})"

                else:
                    node2 = f"{i[1]}"

                nodes_list.append(node1)
                nodes_list.append(node2)

                pen_width = (
                    width(significativity[behaviors.index(i[0]), behaviors.index(i[1])])
                    if significativity is not None
                    else 1
                )

                edges_out += f_edge_label(
                    edge_label,
                    node1,
                    node2,
                    unique_transitions[i],
                    tot_trans_after_node[i[0]],
                    tot_trans,
                    decimals_number,
                    pen_width,
                )

    else:

        for i in unique_transitions:

            if i[0] in starting_nodes:
                node1 = f"{i[0]} ({starting_nodes[i[0]]})"
            else:
                node1 = f"{i[0]}"

            if i[1] in starting_nodes:
                node2 = f"{i[1]} ({starting_nodes[i[1]]})"

            else:
                node2 = f"{i[1]}"

            nodes_list.append(node1)
            nodes_list.append(node2)


            pen_width = (
                width(significativity[behaviors.index(i[0]), behaviors.index(i[1])])
                if significativity is not None
                else 1
            )

            edges_out += f_edge_label(
                edge_label,
                node1,
                node2,
                unique_transitions[i],
                tot_trans_after_node[i[0]],
                tot_trans,
                decimals_number,
                pen_width,
            )

    for node in set(nodes_list):
        nodes_out += f'"{node}"\n'

    graph_out = "\n/* graph statement */\n"

    # make png transparent
    if transparent_background:
        graph_out += 'graph [bgcolor="#ffffff00"]\n'
    else:
        graph_out += "graph []\n"

    footer_out = "}\n"

    return (header_out, nodes_out, edges_out, graph_out, footer_out, sorted(set(nodes_list)))


def create_observed_transition_matrix(sequences: list, behaviours: list) -> np.ndarray:
    """
    create the matrix of observed transitions
    """
    observed_matrix = np.zeros((len(behaviours), len(behaviours)))

    for seq in sequences:
        for i in range(len(seq) - 1):
            if seq[i] in behaviours and seq[i + 1] in behaviours:
                observed_matrix[behaviours.index(seq[i]), behaviours.index(seq[i + 1])] += 1

    return observed_matrix


def permutations_test(
    nrandom: int,
    sequences,
    behaviours,
    exclusion_list,
    block_first,
    block_last,
    observed_matrix: np.array,
    no_repetition: bool = False,
) -> Tuple[int, np.ndarray]:
    """
    permutations test

    Args:
        nrandom (int): number of random permutations
        sequences (list): list of sequences
        behaviours (list): list of unique observed behaviours
        block_first (bool): avoid that 1st behavior be permuted
        block_last (bool): avoid that last behavior be permuted
        observed_matrix (np.array): matrix of observed transitions number

    Returns:
        count_tot
        risu (numpy array)
    """

    def strings_permutation(
        space: list,
        sequences: list,
        exclusion_list: list,
        block_first: bool,
        block_last: bool,
        no_repetition: bool = False,
    ) -> list:
        """
        create permutations of sequences following exclusions list, block first/last behavior

        Args:
            space (list): list of all behaviors ocuurences
            sequences (list): list of behavioral sequences
            exclusion_list (dict): dict of excluded behaviors
            block_first (bool):

        Returns:

            list: permuted sequences
        """

        space = list(space)
        perm_sequences = []

        for seq in sequences:

            if block_first:
                newseq = [seq[0]]
                element = seq[0]
            else:
                newseq = []
                element = ""

            for c in seq[int(block_first) : len(seq) - int(block_last)]:

                if element in exclusion_list:
                    lspazio3 = list(space)
                    # remove element that are not permitted
                    for i in exclusion_list[element]:
                        # remove all excluded behaviors
                        lspazio3 = list([x for x in lspazio3 if x != i])

                    lspazio2 = list(lspazio3)
                else:
                    lspazio2 = list(space)

                if lspazio2:
                    new_element = random.choice(lspazio2)

                    # remove extracted behavior
                    space.remove(new_element)

                else:
                    return []

                # check penultimate element
                if block_last and len(newseq) == len(seq) - 2:  # DO NOT REPEAT LAST BEHAVIOUR

                    while (new_element in exclusion_list) and (seq[-1] in exclusion_list[new_element]):
                        if lspazio2:
                            new_element = random.choice(lspazio2)
                        else:
                            return []

                        # remove last behaviour choosen and last behaviour from original string
                        lspazio2 = list(space)

                        if element in lspazio2:
                            lspazio2 = list([x for x in lspazio2 if x != element])

                        if seq[-1] in lspazio2:
                            lspazio2 = list([x for x in lspazio2 if x != seq[-1]])

                newseq.append(new_element)
                element = new_element

            if block_last:
                newseq.append(seq[-1])

            perm_sequences.append(newseq)

        return perm_sequences

    space = []
    for sequence in sequences:
        space += sequence[int(block_first) : len(sequence) - int(block_last)]

    # modify exclusions list to avoid repetitions
    if no_repetition:
        for behavior in behaviours:
            if behavior not in exclusion_list:
                exclusion_list[behavior] = []
            if behavior not in exclusion_list[behavior]:
                exclusion_list[behavior].append(behavior)

    count, count_tot = 0, 0

    results = np.zeros((len(behaviours), len(behaviours)))

    while True:

        permuted_sequences = strings_permutation(space, sequences, exclusion_list, block_first, block_last)

        count_tot += 1

        if permuted_sequences:
            count += 1

            # analysis
            permuted_transitions_matrix = np.zeros((len(behaviours), len(behaviours)))

            for seq in permuted_sequences:
                for i in range(len(seq) - 1):
                    permuted_transitions_matrix[behaviours.index(seq[i]), behaviours.index(seq[i + 1])] += 1

            results = results + (permuted_transitions_matrix >= observed_matrix)

        if count == nrandom:
            break

    return count, results


def levenshtein_distance(seq1: list, seq2: list) -> int:
    """
    calculate the Levenshtein distance between the 2 sequences
    """
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x, y] = min(matrix[x - 1, y] + 1, matrix[x - 1, y - 1], matrix[x, y - 1] + 1)
            else:
                matrix[x, y] = min(matrix[x - 1, y] + 1, matrix[x - 1, y - 1] + 1, matrix[x, y - 1] + 1)
    return matrix[matrix.shape[0] - 1, matrix.shape[1] - 1]


def levenshtein_distance_seq_list(seq_list: list) -> np.ndarray:
    """
    calculate Levenshtein distances for all combinations of 2 sequences in list

    Args:
        seq_list (list): list of sequences

    Returns:
        numpy array: Levenshtein distances
    """

    results = np.zeros((len(seq_list), len(seq_list)))
    for p in itertools.combinations(enumerate(seq_list), 2):
        results[p[0][0], p[1][0]] = levenshtein_distance(p[0][1], p[1][1])
        results[p[1][0], p[0][0]] = results[p[0][0], p[1][0]]
    return results


def needleman_wunsch_identity(seq1: list, seq2: list) -> dict:
    """
    calculate the Needleman-Wunsch identity between the 2 sequences
    """

    match_award = 1
    mismatch_penalty = -1
    gap_penalty = -1  # both for opening and extanding

    def match_score(alpha, beta):
        if alpha == beta:
            return match_award
        elif alpha == "-" or beta == "-":
            return gap_penalty
        else:
            return mismatch_penalty

    def finalize(align1, align2):
        align1 = align1[::-1]  # reverse sequence 1
        align2 = align2[::-1]  # reverse sequence 2

        i, j = 0, 0

        # calculate identity, score and aligned sequences
        symbol = []
        found = 0
        score = 0
        identity = 0
        for i in range(0, len(align1)):
            if align1[i] == align2[i]:
                symbol.append(align1[i])
                identity = identity + 1
                score += match_score(align1[i], align2[i])

            elif align1[i] != align2[i] and align1[i] != "-" and align2[i] != "-":
                score += match_score(align1[i], align2[i])
                symbol.append(" ")
                found = 0

            elif align1[i] == "-" or align2[i] == "-":
                symbol.append(" ")
                score += gap_penalty

        identity = float(identity) / len(align1) * 100

        return {"identity": identity, "score": score, "align1": align1, "align2": align2, "symbol": symbol}

    m, n = len(seq1), len(seq2)  # length of two sequences

    # Generate DP table and traceback path pointer matrix
    score = np.zeros((m + 1, n + 1))

    # Calculate DP table
    for i in range(0, m + 1):
        score[i][0] = gap_penalty * i
    for j in range(0, n + 1):
        score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[i - 1], seq2[j - 1])
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)

    align1, align2 = [], []
    i, j = m, n
    while i > 0 and j > 0:
        score_current = score[i][j]
        score_diagonal = score[i - 1][j - 1]
        score_up = score[i][j - 1]
        score_left = score[i - 1][j]

        if score_current == score_diagonal + match_score(seq1[i - 1], seq2[j - 1]):
            align1.append(seq1[i - 1])
            align2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif score_current == score_left + gap_penalty:
            align1.append(seq1[i - 1])
            align2.append("-")
            i -= 1
        elif score_current == score_up + gap_penalty:
            align1.append("-")
            align2.append(seq2[j - 1])
            j -= 1

    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(seq1[i - 1])
        align2.append("-")
        i -= 1
    while j > 0:
        align1.append("-")
        align2.append(seq2[j - 1])
        j -= 1

    return finalize(align1, align2)


def needleman_wunsch_identity_seq_list(seq_list: list) -> np.ndarray:
    """
    calculate the Needleman-Wunsch identities for all combinations of 2 sequences in list

    Args:
        seq_list (list): list of sequences

    Returns:
        numpy array: Needleman-Wunsch identities
    """

    results = np.zeros((len(seq_list), len(seq_list)))
    for p in itertools.combinations(enumerate(seq_list), 2):
        results[p[0][0], p[1][0]] = needleman_wunsch_identity(p[0][1], p[1][1])["identity"]
        results[p[1][0], p[0][0]] = results[p[0][0], p[1][0]]
    return results
