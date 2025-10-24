import random
from collections import defaultdict, deque


class Variable:
    # Represents a single timetable session (course instance)

    def __init__(self, name, course_id, level_id, session_index):
        self.name = name  
        self.course_id = course_id
        self.level_id = level_id
        self.session_index = session_index

    def __repr__(self):
        return f"Var({self.name})"


class CSP:
    """Core CSP container holding variables, domains, and constraints."""

    def __init__(self, variables, domains, constraints):
        self.variables = variables            # list of Variable
        self.domains = domains                # dict[var.name] = list of possible (room, instructor, timeslot)
        self.constraints = constraints        # dict[var.name] = list of (other_var, constraint_fn)

    def neighbors(self, var):
        """Return list of neighboring variables connected by constraints."""
        return [v for v, _ in self.constraints.get(var.name, [])]


def apply_ac3(csp):
    """AC-3 algorithm for initial arc consistency."""
    queue = deque()
    for var in csp.variables:
        for (neighbor, _) in csp.constraints[var.name]:
            queue.append((var.name, neighbor.name))

    while queue:
        xi, xj = queue.popleft()
        if revise(csp, xi, xj):
            if not csp.domains[xi]:
                return False 
            for (xk, _) in csp.constraints[xi]:
                if xk.name != xj:
                    queue.append((xk.name, xi))
    return True


def revise(csp, xi, xj):
    """Revise domain of xi to maintain arc consistency with xj."""
    revised = False
    constraints = [fn for (nbr, fn) in csp.constraints[xi] if nbr.name == xj]
    new_domain = []
    for val in csp.domains[xi]:
        # keep val if there exists some value in xj's domain that satisfies constraint
        if any(all(fn(val, other) for fn in constraints) for other in csp.domains[xj]):
            new_domain.append(val)
        else:
            revised = True
    csp.domains[xi] = new_domain
    return revised


def select_unassigned_variable(assignment, csp):
    """MRV heuristic: pick variable with fewest remaining domain values."""
    unassigned = [v for v in csp.variables if v.name not in assignment]
    return min(unassigned, key=lambda var: len(csp.domains[var.name]))


def order_domain_values(var, assignment, csp):
    """LCV heuristic: prefer values that eliminate fewest options from neighbors."""
    def count_conflicts(value):
        count = 0
        for (neighbor, constraint_fn) in csp.constraints.get(var.name, []):
            if neighbor.name in assignment:
                continue
            for nval in csp.domains[neighbor.name]:
                if not constraint_fn(value, nval):
                    count += 1
        return count

    return sorted(csp.domains[var.name], key=count_conflicts)


def forward_checking(csp, var, value, assignment):
    """Remove inconsistent values from domains of unassigned neighbors."""
    for (neighbor, constraint_fn) in csp.constraints.get(var.name, []):
        if neighbor.name in assignment:
            continue
        new_domain = [val for val in csp.domains[neighbor.name] if constraint_fn(value, val)]
        if not new_domain:
            return False 
        csp.domains[neighbor.name] = new_domain
    return True


def backtrack(assignment, csp):
    """Recursive backtracking search with MRV, LCV, and forward checking."""
    if len(assignment) == len(csp.variables):
        return assignment

    var = select_unassigned_variable(assignment, csp)
    for value in order_domain_values(var, assignment, csp):
        assignment[var.name] = value
        if forward_checking(csp, var, value, assignment):
            result = backtrack(assignment, csp)
            if result is not None:
                return result
        del assignment[var.name]
    return None
