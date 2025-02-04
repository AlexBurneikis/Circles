"""
This module allows for the conversion from strings / tokens of strings
to actual condition objects.
"""

import json
import re
from typing import Tuple

from algorithms.objects.categories import (
    Category,
    CompositeCategory,
    ClassCategory,
    CourseCategory,
    FacultyCategory,
    LevelCategory,
    LevelCourseCategory,
    SchoolCategory,
)
from algorithms.objects.conditions import (
    CompositeCondition,
    CoreqCoursesCondition,
    CourseCondition,
    CourseExclusionCondition,
    GradeCondition,
    ProgramCondition,
    ProgramExclusionCondition,
    ProgramTypeCondition,
    SpecialisationCondition,
    UOCCondition,
    WAMCondition,
)
from algorithms.objects.helper import (
    Logic,
    get_grade,
    get_uoc,
    get_wam,
    is_course,
    is_grade,
    is_program,
    is_program_type,
    is_specialisation,
    is_uoc,
    is_wam,
    get_level_category,
    get_course_category
)

# Load in cached exclusions
CACHED_EXCLUSIONS_PATH = "./algorithms/cache/exclusions.json"
with open(CACHED_EXCLUSIONS_PATH, "r", encoding="utf8") as f:
    CACHED_EXCLUSIONS = json.load(f)

def create_category(tokens) -> Tuple[Category | None, int]: # pylint: disable=too-many-return-statements
    """
    Given a list of tokens starting from after the connector keyword, create
    and return the category object matching the category, as well as the current index
    of the token list.

    Returns:
        Category - Category object matching the category list
        int: The current index of the the token list
    """

    # At most we will only parse 1 or 2 tokens so no need for an iterator
    # NOTE: There will always be at least 2 tokens due to a closing ")" bracket
    # so it is safe to check tokens[1]

    if tokens[0] == "(":
        # Composite category

        # NOTE: there will always be at least 3 tokens due to a closing ")" bracket
        # and empty brackets won't be generated by the tokenizer
        # so it is safe to check tokens[2]

        category = CompositeCategory()
        opposite_logic = None
        if tokens[2] == "||":
            opposite_logic = "&&"
            category.set_logic(Logic.OR)
        elif tokens[2] == "&&":
            opposite_logic = "||"
            category.set_logic(Logic.AND)

        token_iter = enumerate(tokens)
        # skip opening parenthesis to avoid infinite recursion
        next(token_iter)
        for index, token in token_iter:
            if token == opposite_logic:
                # (COND1 || COND2 && COND3) or similar combinations is undefined
                print("WARNING: Found an undefined logic combination. Skipping.")
                return None, index - 1
            if token == ")":
                # We've reached the end of the condition
                return category, index - 1

            sub_category, sub_index = create_category(tokens[index:])
            if sub_category is not None:
                # don't throw errors for None categories
                # most likely they are one of (||, &&)
                # TODO: should this be revisited?
                category.add_category(sub_category)
            # skip the tokens used in the sub-category
            # should only be more than one if the sub-category is a composite
            [next(token_iter) for _ in range(sub_index + 1)]

    if re.match(r"^[A-Z]{4}$", tokens[0], flags=re.IGNORECASE):
        # Course type
        return CourseCategory(tokens[0]), 0

    if re.match(r"^L[0-9]$", tokens[0], flags=re.IGNORECASE):
        # Level category. Get the level, then determine next token if there is one
        level = get_level_category(tokens[0])

        if re.match(r"^[A-Z]{4}$", tokens[1], flags=re.IGNORECASE):
            # Level Course Category. e.g. L2 MATH
            course_code = get_course_category(tokens[1])

            return LevelCourseCategory(level, course_code), 1

        # There are no tokens after this. Simple level category
        return LevelCategory(level), 0


    # TODO: Levels (e.g. SPECIALISATIONS, PROGRAM)
    # These don't have categories, do they need a category?
    return (
        (SchoolCategory(f"{tokens[0]} {tokens[1]}"), 1)
            if re.match(r"^S$", tokens[0], flags=re.IGNORECASE)
        else (FacultyCategory(f"{tokens[0]} {tokens[1]}"), 1)
            if re.match(r"^F$", tokens[0], flags=re.IGNORECASE)
        else (ClassCategory(tokens[0]), 0)
            if re.match(r"^[A-Z]{4}[0-9]{4}$", tokens[0], flags=re.IGNORECASE)
        else (None, 0)          # No match, 1 token consumed
    )


def create_condition(tokens, course=None) -> CompositeCondition | None:
    """
    The main wrapper for make_condition so we don't get 2 returns.
    Given the parsed logical tokens list (assuming starting and ending bracket),
    and optionally a course for which this condition applies to,
    returns the condition
    """
    return make_condition(tokens, True, course)[0]


def make_condition(tokens, first=False, course=None) -> Tuple[CompositeCondition | None, int]:
    """
    To be called by create_condition
    Given the parsed logical tokens list, (assuming starting and ending bracket),
    return the condition object and the index of that (sub) token list
    """
    # Everything is wrapped in a CompositeCondition
    result = CompositeCondition()
    # Add exclusions
    if first and CACHED_EXCLUSIONS.get(course):
        # NOTE: we dont check for broken exclusions
        for exclusion in CACHED_EXCLUSIONS[course].keys():
            if is_course(exclusion):
                result.add_condition(CourseExclusionCondition(exclusion))
            elif is_program(exclusion):
                result.add_condition(ProgramExclusionCondition(exclusion))

    # Define index before loop to prevent undefined return
    index = 0
    item = enumerate(tokens)
    for index, token in item:
        if token == "(":
            # Parse content in bracket 1 layer deeper
            sub_result, sub_index = make_condition(tokens[index + 1 :])
            if sub_result is None:
                # Error. Return None
                return None, index + sub_index

            # Adjust the current position to scan the next token after this sub result
            result.add_condition(sub_result)
            [next(item) for _ in range(sub_index + 1)]
        elif token == ")":
            # End parsing and go up one layer
            return result, index
        elif token == "&&":
            # AND type logic
            result.set_logic(Logic.AND)
        elif token == "||":
            # OR type logic
            result.set_logic(Logic.OR)
        elif token == "[":
            # Beginning of co-requisite. Parse courses and logical
            # operators until closing "]"
            coreq_cond = CoreqCoursesCondition()
            i = 1  # Helps track our index offset to parse this co-requisite
            while tokens[index + i] != "]":
                if is_course(tokens[index + i]):
                    coreq_cond.add_course(tokens[index + i])
                elif tokens[index + i] == "&&":
                    coreq_cond.set_logic(Logic.AND)
                elif tokens[index + i] == "||":
                    coreq_cond.set_logic(Logic.OR)
                else:
                    # Error, bad token processed. Return None
                    return None, index + i
                i += 1
                next(item)

            result.add_condition(coreq_cond)

            # Skip the closing "]" so the iterator will continue with the next token
            next(item)
        elif is_course(token):
            # Condition for a single course
            result.add_condition(CourseCondition(token))
        elif is_program(token):
            result.add_condition(ProgramCondition(token))
        elif is_specialisation(token):
            result.add_condition(SpecialisationCondition(token))
        elif is_program_type(token):
            result.add_condition(ProgramTypeCondition(token))
        else:
            cond: UOCCondition | WAMCondition | GradeCondition
            if is_uoc(token):
                # Condition for UOC requirement
                cond = UOCCondition(get_uoc(token))
            elif is_wam(token):
                # Condition for WAM requirement
                cond = WAMCondition(get_wam(token))
            elif is_grade(token):
                # Condition for GRADE requirement (mark in a single course)
                cond = GradeCondition(get_grade(token))
            else:
                # Unmatched token. Error
                return None, index + 1

            if index + 1 < len(tokens) and tokens[index + 1] == "in":
                # Create category according to the token after 'in'
                next(item)  # Skip "in" keyword

                # Get the category of the condition
                category, sub_index = create_category(tokens[index + 2 :])

                if category is None:
                    # Error. Return None.
                    return None, index

                # Add the category to the condition and adjust the current index position
                cond.set_category(category)
                [next(item) for _ in range(sub_index + 1)]

            result.add_condition(cond)

    return result, index
