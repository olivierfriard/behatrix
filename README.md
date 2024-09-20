Behatrix
=======================


# Behavioral sequences analysis with permutations test

![Behatrix logo](images/logo_behatrix.png)


Researchers who observe and study behavior often collect data in the
form of sequences of behavioral displays that they need to analyze and
visualize to test hypotheses. **Behatrix** is free and open-source
software available for GNU/Linux, Windows and Mac OS X.

By using a flexible and efficient approach, **Behatrix** allows
analyzing large sets of behavioral sequences and can organize data into
contingency tables. The program can also perform permutations test and
autonomously generate the code for a flow diagram representing the
transitions between behaviors.

**Behatrix** can read data exported from [**BORIS**](http://www.boris.unito.it)
(see [Events as behavioral sequences](http://www.boris.unito.it/user_guide/export_events/#export-events-as-behavioral-sequences))
and can also be used as a standalone program.

## Features

-   Behavioral sequences statistics (with n-gram size option)
-   Observed transitions matrix (with n-gram size option)
-   Generation of the [Graphviz](https://graphviz.org/) script from observed transitions
-   Flow diagram generation  (with n-gram size option)
-   Random permutations test (with multiprocessing module) with generation of the transitions significativity matrix
-   Flow diagram generation with transitions significativity
-   Behavioral sequences distances: **Levenshtein distances** and **Needleman-Wunsch identities**

The flow diagram generation requires the the [Graphviz](https://graphviz.org/) open source graph visualization software.


# User guide

[Usage of Behatrix](https://github.com/olivierfriard/behatrix/blob/master/user_guide.md)


# Download Behatrix


[Latest release on GitHub repository](https://github.com/olivierfriard/behatrix/releases/latest)

[Issues and feature request](https://github.com/olivierfriard/behatrix/issues) on GitHub


# Change Log

Please consult the [change log page](https://github.com/olivierfriard/behatrix/wiki/revision-history).
