#!/usr/bin/env python3

'''
Behavioural Strings Analysis (BSA) command line utility.
Randomization test

Multi core use

Copyright Olivier Friard - 2017
'''

import os
import sys
import argparse
import numpy
import concurrent.futures
import random

__version__ = "0.1"


def behav_strings_stats(string, chunk=0):
    """
    calculate some stats on behavioral strings
    """

    # replace space by undescore (_)
    string = string.replace(" ", "_")

    # check if behaviors are unique char
    if "|" in string:
        rows = string.split("\n")   # split rows in list
        flagOne = False
    else:
        rows = string.replace(" ", "").split()
        flagOne = True

    sequences = []

    d = {}
    nodes = {}
    starting_nodes = {}

    min_chunk_length = 1e6

    not_alnum = []
    pos_not_alnum = 0
    line_count = 0

    for row in rows:

        if flagOne:
            r = list(row.strip())
        else:
            r = row.strip().split("|")

        if chunk:
            r = r[0:chunk]

        sequences.append(r)

        line_count += 1

        min_chunk_length = min(min_chunk_length, len(r))

        for node in r:
            if flagOne and not node.isalnum():
                not_alnum = [line_count, ord(node)]

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

            if r[i] + '|' + r[ i + 1 ] in d:

               d[r[i] + '|' +r[i + 1]] += 1

            else:
                d[r[i] + '|' +r[i + 1]] = 1

    # exclusion
    '''
    exclusion_list = {}

    if exclusion_str:
        rows = exclusion_str.split("\n")

        for row in rows:
            if row.strip() and ':' in row:
                s1, s2 = row.strip().split(':')
                if s1:
                    if s1 in exclusion_list:
                        if '|' in string:
                            exclusion_list[s1] += s2.split('|')
                        else:
                            exclusion_list[s1] += list(s2)
                    else:
                        if '|' in string:
                            exclusion_list[s1] = s2.split('|')
                        else:
                            exclusion_list[s1] = list(s2)

        # test if exclusion list OK
        for seq in sequences:

            for i in range(0, len(seq) - 1):

                if seq[i] in exclusion_list and seq[i + 1] in exclusion_list[ seq[i] ]:

                    return (1, '<b>Check your strings and exclusion list</b><br><b>%s</b> is not allowed after <b>%s</b>\n' % (seq[i + 1], seq[i])),'', '', '', '' , '' , '', '', '', ''
    '''
 
    # total number of transitions
    tot_trans = 0
    for i in d:
        tot_trans += d[i]

    # number of transitions after behavior
    tot_trans_after_node = {}

    for i in d:

        b1,b2 = i.split('|')

        if b1 in tot_trans_after_node:

            tot_trans_after_node[ b1 ] += d[i]

        else:

            tot_trans_after_node[ b1 ] = d[i]

    tot_nodes = 0
    for node in nodes:
        tot_nodes += nodes[node]

    behaviours = []

    # extract unique behaviors
    for seq in sequences:
        for c in seq:
            if not c in behaviours:
                behaviours.append( c )

    behaviours.sort()

    #return 0, sequences, exclusion_list, d, nodes, starting_nodes, tot_nodes, tot_trans, tot_trans_after_node, behaviours
    return 0, sequences, d, nodes, starting_nodes, tot_nodes, tot_trans, tot_trans_after_node, behaviours


def check_exclusion_list(exclusion_str, sequences):
    """
    check the transition exclusion strings
    format must be like:
    a:bc
    or
    a:b|c
    """

    exclusion_list = {}

    if exclusion_str:
        rows = exclusion_str.split("\n")

        for row in rows:
            if row.strip() and ":" in row:
                s1, s2 = row.strip().split(":")
                if s1 and s2:
                    if s1 in exclusion_list:
                        if "|" in s2:
                            exclusion_list[s1] += s2.split('|')
                        else:
                            exclusion_list[s1] += list(s2)
                    else:
                        if "|" in s2:
                            exclusion_list[s1] = s2.split('|')
                        else:
                            exclusion_list[s1] = list(s2)

        # test if behavioral strings do not contain an excluded transition
        for seq in sequences:
            for i in range(0, len(seq) - 1):
                if seq[i] in exclusion_list and seq[i + 1] in exclusion_list[seq[i]]:
                    return {"error_code": 1,
                            "message": "The behavioral strings contain an excluded transition: {} -> {}".format(seq[i], seq[i + 1]),
                            "exclusion_list": {}}

    return {"error_code": 0, "exclusion_list": exclusion_list}


def draw_diagram(cutoff_all,
                 cutoff_behavior,
                 d,
                 nodes,
                 tot_nodes,
                 tot_trans,
                 tot_trans_after_node,
                 starting_nodes=[],
                 edge_label="percent_node",   # fraction_node/percent_node/percent_total
                 transparent_background=False,
                 include_first = True
                 ):

        """
        create code for GraphViz
        return string containing graphviz code
        """
        
        
        def f_edge_label(edge_label, node1, node2, di, tot_trans_after_node_i0, tot_trans):
            if edge_label == 'fraction_node':

                return '"{node1}" -> "{node2}" [label = "{di}/{tot_transition_after_node}"];\n'.format(node1=node1,
                                                                                                       node2=node2,
                                                                                                       di=di,
                                                                                                       tot_transition_after_node_i0=tot_transition_after_node_i0)

            elif edge_label == 'percent_node':
                return '"{node1}" -> "{node2}" [label = "{percent:.2f} %"];\n'.format(node1=node1,
                                                                                      node2=node2,
                                                                                      percent=d[i] / tot_trans_after_node[i0] *100)

            elif edge_label == 'percent_total':
                return '"{node1}" -> "{node2}" [label = "{percent:.2f} %"];\n'.format(node1=node1,
                                                                                      node2=node2,
                                                                                      percent=di / tot_trans * 100.0)


        out = 'digraph G {\n'

        # make png transparent
        if transparent_background:
            out += 'graph [bgcolor="#ffffff00"]\n'

        if cutoff_all:

            for i in d:

                if d[i] / tot_trans * 100.0 >= cutoff_all:

                    i0, i1 = i.split('|')

                    if i0 in starting_nodes:
                        node1 = '%s (%d)' % (i0, starting_nodes[i0])
                    else:
                        node1 = '%s' % (i0)

                    if i1 in starting_nodes:
                        node2 = '%s (%d)' % (i1, starting_nodes[i1])

                    else:
                        node2 = '%s' % (i1)

                    
                    out += f_edge_label(edge_label, node1, node2, d[i], tot_trans_after_node[i0], tot_trans)
                    
        elif cutoff_behavior:

            for i in d:

                #if d[i] / tot_trans * 100.0 >= cutoff_all:

                i0, i1 = i.split("|")

                if d[i] / tot_trans_after_node[i0] * 100 >= cutoff_behavior:

                    if i0 in starting_nodes and include_first:
                        node1 = '%s (%d)' % (i0, starting_nodes[i0])
                    else:
                        node1 = '%s' % (i0)

                    if i1 in starting_nodes and include_first:
                        node2 = '%s (%d)' % (i1, starting_nodes[i1])

                    else:
                        node2 = '%s' % (i1)

                    out += f_edge_label(edge_label, node1, node2, d[i], tot_trans_after_node[i0], tot_trans)
                    '''
                    if edge_label == 'fraction_node':

                        out += '"%s" -> "%s" [ label = "%s" ];\n' %  (node1, node2, str(d[i]) + '/' + str(tot_trans_after_node[i0]) )

                    elif edge_label == 'percent_node':

                        #out += '"%s" -> "%s" [label = "%.1f%%"];\n' %  (node1, node2,  d[i]/tot_trans_after_node[i0] *100)
                        out += '"{node1}" -> "{node2}" [label = "{percent:.2f}"];\n'.format(node1=node1, node2=node2, percent=d[i] / tot_trans_after_node[i0] * 100)

                    elif edge_label == 'percent_total':

                        out += '"%s" -> "%s" [label = "%.1f%%"];\n' % (node1, node2, 1.0 * d[i] / tot_trans * 100.0)
                    '''

        else:

            for i in d:

                    i0, i1 = i.split('|')

                    if i0 in starting_nodes:
                        node1 = '%s (%d)' % (i0, starting_nodes[i0])
                    else:
                        node1 = '%s' % (i0)

                    if i1 in starting_nodes:
                        node2 = '%s (%d)' % (i1, starting_nodes[i1])

                    else:
                        node2 = '%s' % (i1)

                    if edge_label == 'fraction_node':

                        out +=  '"%s" -> "%s" [ label = "%s" ];\n' %  (node1, node2, str(d[i]) + '/' + str(tot_trans_after_node[i0]) )

                    elif edge_label == 'percent_node':

                        out +=  '"%s" -> "%s" [ label = "%.1f%%" ];\n' %  (node1, node2,  d[i]/tot_trans_after_node[i0] *100)

                    elif edge_label == 'percent_total':

                        out +=  '"%s" -> "%s" [ label = "%.1f%%" ];\n' % (node1, node2, 1.0 * d[i] / tot_trans * 100.0)

        out += '}\n'

        return out


def create_observed_transition_matrix(sequences, behaviours):
    """
    create the matrix of observed transitions
    """
    observed_matrix = numpy.zeros((len(behaviours), len(behaviours)))

    for seq in sequences:
        for i in range(len(seq) - 1):
            if seq[i] in behaviours and seq[i + 1] in behaviours:
                observed_matrix[behaviours.index(seq[i]), behaviours.index(seq[i + 1])] += 1

    return observed_matrix


def strings2matrix_cl(nrandom, sequences, behaviours, exclusion_list, block_first, block_last, conta_obs):
    """
    randomization test
    """

    def strings_permutation(spazio, sequences, exclusion_list, block_first, block_last):

        spazio = list(spazio)
        perm_sequences = []
        flagEmpty = False

        for seq in sequences:

            if block_first:
                newseq = [seq[0]]
                element = seq[0]
            else:
                newseq = []
                element = ''

            for c in seq[int(block_first):len(seq) - int(block_last) ]:

                if element in exclusion_list:

                    lspazio3 = list(spazio)

                    # remove element that are not permitted

                    for i in exclusion_list[element]:
                        # remove all excluded behaviors
                        lspazio3 = list([x for x in lspazio3 if x != i])

                    lspazio2 = list(lspazio3)
                else:

                    lspazio2 = list(spazio)

                if lspazio2:
                    new_element = random.choice(lspazio2)

                    # remove extracted behavior
                    spazio.remove( new_element )

                else:
                    return True, []

                # check penultimate element
                if block_last and len(newseq) == len(seq) - 2:   # DO NOT REPEAT LAST BEHAVIOUR

                    while (new_element in exclusion_list) and (seq[-1] in exclusion_list[new_element]):
                        if lspazio2:
                            new_element = random.choice(lspazio2)
                        else:
                            return True, []

                        # remove last behaviour choosen and last behaviour from original string
                        lspazio2 = list(spazio)

                        if element in lspazio2:
                            lspazio2 = list(  [x for x in lspazio2 if x != element] )

                        if seq[-1] in lspazio2:
                            lspazio2 = list(  [x for x in lspazio2 if x != seq[-1]] )

                newseq.append( new_element )
                element = new_element

            if block_last:
                newseq += seq[-1]

            perm_sequences.append(newseq)

        return flagEmpty, perm_sequences


    spazio = []
    for seq in sequences:
        spazio +=  seq[int(block_first):len(seq) - int(block_last) ]

    count = 0
    count_tot = 0

    risu = numpy.zeros((len(behaviours), len(behaviours)))

    while True:

        flagEmpty, permuted_sequences = strings_permutation(spazio, sequences, exclusion_list, block_first, block_last)

        count_tot += 1

        if flagEmpty == False:
            count += 1

            # analysis
            conta = numpy.zeros((len(behaviours), len(behaviours)))

            for seq in permuted_sequences:
                for i in range(len(seq) - 1):
                    if seq[i] in behaviours and seq[i + 1] in behaviours:
                        conta[ behaviours.index(seq[i]), behaviours.index(seq[i + 1]) ] += 1

            risu = risu + (conta >= conta_obs)

        if count == nrandom:
            break

    return count_tot, risu


def main():
    
    parser = argparse.ArgumentParser(description="Behavioural Strings Analysis (BSA) command line utility")
    parser.add_argument("-v", action="store_true", dest='version', help='BSA version')
    parser.add_argument("--strings", action="store", dest='strings', help='Path of file containing behavioral strings')
    
    parser.add_argument("--output", action="store", dest='output', help='Path of output files')
    parser.add_argument("--exclusions", action="store", dest='exclusions', help='Path of file containing exclusions')
    parser.add_argument("--n_random", action="store", dest='nrandom', help='Number of randomizations', type=int, default=0)
    parser.add_argument("--n_cpu", action="store", dest='n_cpu', help='Number of CPU to use for randomizations test', type=int, default=0)    
    parser.add_argument("--block_first", action="store_true", dest='block_first', help='block first behavior during randomization test')
    parser.add_argument("--block_last", action="store_true", dest='block_last', help='block last behavior during randomization test')
    
    parser.add_argument("--verbose", action="store_true", dest='verbose', default=False, help='Print results on terminal')
    
    args = parser.parse_args()

    if args.version:
        print("version {}".format(__version__))
        sys.exit()

    if not args.strings:
        print("The 'strings' argument is required")
        parser.print_usage()
        print()
        sys.exit()
    else:
        if not os.path.isfile(args.strings):
            print("{} is not a file\n".format(args.strings))
            sys.exit()

    with open(args.strings) as f_in:
        behav_str = f_in.read()

    (return_code, sequences, 
     d, nodes , starting_nodes , tot_nodes,
     tot_trans, tot_trans_after_node, behaviours) = behav_strings_stats(behav_str, chunk=0)
    
        
    if args.nrandom:
        nrandom = args.nrandom
    else:
        nrandom = 0
    
    if nrandom:

        if args.exclusions:
            if not os.path.isfile(args.exclusions):
                print("{} is not a file\n".format(args.exclusions))
                sys.exit()
            else:
                with open(args.exclusions) as f_in:
                    exclusion_str = f_in.read()
        else:
            exclusion_str = ""

        result = check_exclusion_list(exclusion_str, sequences)
        if not result["error_code"]:
            exclusion_list = result["exclusion_list"]
        else:
            print(result["message"])
            return

        block_first = 1 if args.block_first else 0
        block_last = 1 if args.block_last else 0
    
    
    if args.verbose:

        print("\nBehaviours list:\n================\n{}\n".format("\n".join(behaviours)))

        print("Statistics\n==========")
        print('Number of different behaviours: {}'.format(len(behaviours)))
        print('Total number of behaviours: {}'.format(tot_nodes))
        print('Number of different transitions: {}'.format(len(d)))
        print('Total number of transitions: {}'.format(tot_trans))

        print('\nBehaviours frequencies:\n=======================')

        for behaviour in sorted(behaviours):
            countBehaviour = 0
            for seq in sequences:
                countBehaviour += seq.count(behaviour)

            print('%(behaviour)s\t%(freq).3f\t%(countBehaviour)d / %(tot_nodes)d' % {'behaviour': behaviour, 'freq': countBehaviour / tot_nodes, 'countBehaviour': countBehaviour, 'tot_nodes':tot_nodes})

    observed_matrix = create_observed_transition_matrix(sequences, behaviours)
    
    if args.verbose:
        print("\nObserved transition matrix:\n===========================\n{}".format(observed_matrix))
    
    if args.output:
        file_name = '{fileName}.observed_transitions.tsv'.format(fileName=args.output)
    else:
        file_name = '{fileName}.observed_transitions.tsv'.format(fileName=args.strings)
    
    numpy.savetxt(file_name, observed_matrix, fmt='%d', delimiter='\t')
    
    
    with open(file_name, mode="r", encoding="utf-8") as f_in:
        rows = f_in.readlines()
    
    with open(file_name, mode="w", encoding="utf-8") as f_out:
        f_out.write('\t' + '\t'.join(behaviours) + '\n')
        c = 0
        for row in rows:
            f_out.write((behaviours)[c] + '\t' + row)
            c += 1

    
    '''
    f = open(file_name, mode = 'w', encoding = 'utf-8')
    f.write('\t' + '\t'.join( list( behaviours) ) + '\n' )
    c = 0
    for row in rows:
        f.write( (behaviours)[c] + '\t' + row)
        c += 1
    
    f.close()
    '''
   
    if nrandom:
        
        if args.n_cpu:
            num_proc = args.n_cpu
        else:
            num_available_proc = int(os.sysconf("SC_NPROCESSORS_ONLN"))
            if num_available_proc <= 2:
                num_proc = 1
            else:
                num_proc = num_available_proc - 1
    
        results = numpy.zeros((len(behaviours), len(behaviours)))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            lst = []
            n_required_randomizations = 0
            for i in range(num_proc):
                
                if i < num_proc - 1:
                    n_random_by_proc = nrandom // num_proc
                else:
                    n_random_by_proc = nrandom - n_required_randomizations
                
                lst.append(executor.submit(strings2matrix_cl, n_random_by_proc, sequences, behaviours, exclusion_list, block_first, block_last, observed_matrix))
                n_required_randomizations += n_random_by_proc
                
            print("\nnumber of required randomizations: ", n_required_randomizations)
        
            nb_randomization_done = 0
        
            for l in lst:
                nb_randomization_done += l.result()[0]
                results += l.result()[1]
        
        
        print("Number of done randomizations: {}".format(nb_randomization_done))
        
        if args.output:
            file_name = '{fileName}.randomized_transitions.{nrandom}.tsv'.format(fileName=args.output, nrandom=nrandom)
        else:
            file_name = '{fileName}.randomized_transitions.{nrandom}.tsv'.format(fileName=args.strings, nrandom=nrandom)

        
        numpy.savetxt(file_name, results / nrandom, fmt='%f', delimiter='\t')
        
        with open(file_name, mode='r', encoding='utf-8') as f:
            rows = f.readlines()
        
        with open(file_name, mode='w', encoding='utf-8') as f:
            f.write( '\t' + '\t'.join( list( behaviours) ) + '\n' )
            c = 0
            for row in rows:
                f.write( (behaviours)[c] + '\t' + row)
                c += 1
    


if __name__ == '__main__':
    main()


