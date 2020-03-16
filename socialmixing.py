#!/usr/bin/env python3

"""
Groups social mixing data into age ranges
"""
__author__ = "Luke Massa"
__license__ = "MIT"
__email__ = "lukefrederickmassa@gmail.com"

import csv

POP_ESTIMATE_COLUMN = "CENSUS2010POP" # Which column to use from the census data

class AgeMixing():
    """
    Container for social mixing data, functions to manipulate it
    """

    def __init__(self):
        self.social_mixing_matrix = self.load_social_mixing_matrix()
        self.age_proportions = self.load_age_proportions()

        self.scaled_matrix = self.get_scaled_matrix(self.social_mixing_matrix)

    @staticmethod
    def _age_group_to_tuple(age_group):
        """
        Given an age group like "0-5" return (0, 5)
        """
        lower, upper = age_group.split('-')
        return (int(lower), int(upper))

    def _is_group_in_group(self, group1, group2):
        """
        Is group1 (i.e. "5-10") in group2 (i.e. "0-15")
        """
        total_min, total_max = self._age_group_to_tuple(group2)
        my_min, my_max = self._age_group_to_tuple(group1)
        return my_min >= total_min and my_max <= total_max

    def _proportion_in_group(self, group):
        """
        What proportion of the population is in this group (i.e. "0-5")
        """
        ret = 0

        lower, upper = self._age_group_to_tuple(group)
        for i in range(lower, upper+1):
            ret+=self.age_proportions[i]
        return ret

    def load_social_mixing_matrix(self):
        """
        Load the social mixing matrix into a dict of dicts
        """
        ret = {}
        table = []
        with open('Age-Mixing.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table.append(row)
                group_i = row["Age group"]
                for group_j, value in row.items():
                    if group_j == "Age group":
                        continue
                    if group_i not in ret:
                        ret[group_i] = {}
                    # group_i comes from the first column of this row, 
                    # group_j is the column for each cell
                    ret[group_i][group_j] = float(value)
        return ret

    def load_age_proportions(self):
        """
        Load age proportion data into a map from age to what proportion of the pop is that age
        """
        ret = {}

        with open("US-Age-Sex-Distribution.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["SEX"] == "0": # 0 == both sexes
                    age = int(row["AGE"])
                    # There's a row with age 999 that has the sum of all the data
                    if age == 999:
                        total = float(row[POP_ESTIMATE_COLUMN])
                    else:
                        ret[age] = float(row[POP_ESTIMATE_COLUMN])
        
        # Scale by the total
        for k, v in ret.items():
            ret[k] = v / total
        return ret

    def get_scaled_matrix(self, social_mixing_matrix):
        """
        Get the matrix, but scaled by proportions of population in both group a and b
        This amounts to multiplying each cell by the proportion of its row * its column * itself
        So if mixing from 0-5 to 10-15, had value of 2, and pop is 5% 0-5 and 8% 10-15, then new value is 2*.05*.08
        """

        ret = {}
        for group_i, row in social_mixing_matrix.items():
            for group_j, value in row.items():
                if group_i not in ret:
                    ret[group_i] = {}
                ret[group_i][group_j] = self._proportion_in_group(group_i) * self._proportion_in_group(group_j) * value
        return ret


    def get_cell_for_new_matrix(self, new_group_i, new_group_j):
        """
        Find value of a cell in the new matrix
        Sums up all the cells covered by the new groupings
        """


        # This is inefficient, just go through all the cells and see if they fit

        ret = 0
        for group_i in self.scaled_matrix:
            for group_j in self.scaled_matrix:
                if self._is_group_in_group(group_i, new_group_i) and self._is_group_in_group(group_j, new_group_j):
                    ret+= self.scaled_matrix[group_i][group_j]
        return ret



    def get_new_matrix(self, new_groups):
        """
        Take the new groups, and the scaled matrix, and return the new matrix
        """
        ret = {}

        for group_i in new_groups:
            for group_j in new_groups:
                if group_i not in ret:
                    ret[group_i] = {}
                ret[group_i][group_j] = self.get_cell_for_new_matrix(group_i, group_j)
        return ret

    def format_matrix(self, matrix):
        """
        Given a matrix, format it as a string (essentially reverse of load_social_mixing_matrix)
        """

        ret = []
        toprow = []
        groups = sorted(matrix.keys(), key=lambda x: self._age_group_to_tuple(x)[0])
        toprow.append("Age group")
        for group in groups:
            toprow.append(group)
        ret.append(",".join(toprow))
        for group_i in groups:
            row = []
            row.append(group_i)
            for group_j in groups:
                row.append(str(matrix[group_i][group_j]))
            ret.append(",".join(row))
        return '\n'.join(ret)

def main():

    a = AgeMixing()
    matrix = a.get_new_matrix(("0-20", "21-64", "65-100"))
    print(a.format_matrix(matrix))

if __name__ == "__main__":
    main()
