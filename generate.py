import sys

from crossword import *
from operator import itemgetter


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        for variable in self.domains:
            for value in self.domains[variable].copy():
                if len(value) != variable.length:
                    self.domains[variable].remove(value)
        
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
      
        revised = False
        square_x,square_y = self.crossword.overlaps[x,y]
                  
        for value_x in self.domains[x].copy():
            y_arc_consistent_x = False
            for value_y in self.domains[y]:
                if value_x[square_x] == value_y[square_y]:
                    y_arc_consistent_x = True
                    break
            
            if y_arc_consistent_x == False:                
                self.domains[x].remove(value_x)
               # y_arc_consistent = False
                revised = True

        return revised
        
        
        #raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        if arcs is None:
            queue = [i for i in self.crossword.overlaps if self.crossword.overlaps[i] != None]
        else:
            queue = arcs
       
        while len(queue) != 0:
            x,y = queue.pop()
            
            if self.revise(x,y):
                if len(self.domains[x])==0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z,x))
               
        return True
           
                
        
        #raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        if len(self.crossword.variables) != len(assignment):
            return False
        else: 
            return True
        
        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #set for distinct values 
        set_of_values = set()
        
        for variable, value in assignment.items():
            
            #check correct value's length
            if variable.length != len(value):
                return False
            
            #add distinct values from assignment
            set_of_values.add(value)
            
            #get each neighbor for all variables
            for neighbor in self.crossword.neighbors(variable):
                #check neighbor is already in assignment
                if assignment.get(neighbor):
                    index_v,index_n = self.crossword.overlaps[variable,neighbor]
                    #check conflicts between neighboring variables
                    if value[index_v] != assignment.get(neighbor)[index_n]:
                        return False
                    
        #check distinct values in assignment            
        if len(set_of_values) != len(assignment):
            return False
        else: 
            return True
            
        
        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        list_of_values = dict()
        n = 0
       
        for value in self.domains[var]:
            for neighbor in self.crossword.neighbors(var):
                for value_neighbor in self.domains.get(neighbor):
                    index_var, index_neighbor= self.crossword.overlaps[var,neighbor]
                    if value[index_var] != value_neighbor[index_neighbor]:
                        n+=1
            list_of_values[value] = n
        
        return list(sorted(list_of_values.keys(), key = itemgetter(1)))
    
        
        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        remaining_values = []
        sorted_remaining_values = []
        
        for v in self.crossword.variables:
            if assignment.get(v, 0) == 0:
                
                remaining_values.append((len(self.domains.get(v)), len(self.crossword.neighbors(v)),v))  
                              
        
        sorted_remaining_values = sorted(remaining_values, key = itemgetter(1), reverse = True)
        sorted(sorted_remaining_values, key = itemgetter(0))
        
        
        return sorted_remaining_values[0][2]
        
        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                 
                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment.pop(var)
        return None
        
        
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
