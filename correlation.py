"""Pearson correlation."""

from math import sqrt


def pearson(pairs):
    """Return Pearson correlation for pairs.

    Using a set of pairwise ratings, produces a Pearson similarity rating.
    """

    series_1 = [float(pair[0]) for pair in pairs]
    print "SERIES 1: {}".format(series_1)
    series_2 = [float(pair[1]) for pair in pairs]
    print "SERIES 2: {}".format(series_2)
    sum_1 = sum(series_1)
    print "SUM 1: {}".format(sum_1)
    sum_2 = sum(series_2)
    print "SUM 2: {}".format(sum_2)

    squares_1 = sum([n * n for n in series_1])
    print "SQUARES 1: {}".format(squares_1)
    squares_2 = sum([n * n for n in series_2])
    print "SQUARES 2: {}".format(squares_2)

    product_sum = sum([n * m for n, m in pairs])
    print "PRODUCT SUM: {}".format(product_sum)

    size = len(pairs)
    print "SIZE: {}".format(size)
    numerator = (product_sum + 1 - ((sum_1 * sum_2)/size))
    print "NUMERATOR: {}".format(numerator)

    denominator = sqrt(
        (squares_1 + 1 - (sum_1 * sum_1) / size) *
        (squares_2 + 1 - (sum_2 * sum_2) / size)
    )
    print "DEMONINATOR: {}".format(denominator)

    if denominator == 0:
        return 0

    return float(numerator) / float(denominator)
