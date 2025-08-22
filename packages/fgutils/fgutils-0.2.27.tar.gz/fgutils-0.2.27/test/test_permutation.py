import pytest
import copy

from fgutils.permutation import (
    generate_mapping_permutations,
    PermutationMapper,
    MappingMatrix,
)


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        ([], ["A"], []),
        (["A"], [], []),
    ],
)
def test_single_to_empty_mapping(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A"], ["A"], [[(0, 0)]]),
        (["A"], ["B"], []),
        (["B"], ["A"], []),
    ],
)
def test_single_to_single_mapping(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A", "B"], ["A"], []),
        (["B", "A"], ["A"], []),
        (["A", "B"], ["C"], []),
    ],
)
def test_double_to_single_mapping(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A"], ["A", "B"], [[(0, 0)]]),
        (["A"], ["B", "A"], [[(0, 1)]]),
        (["C"], ["A", "B"], []),
    ],
)
def test_single_to_double(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A", "B"], ["A", "B"], [[(0, 0), (1, 1)]]),
        (["A", "B"], ["B", "A"], [[(0, 1), (1, 0)]]),
        (["A", "B"], ["A", "C"], []),
        (["A", "A"], ["A", "A"], [[(0, 0), (1, 1)], [(0, 1), (1, 0)]]),
    ],
)
def test_double_to_double(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (
            ["A", "A"],
            ["A", "A", "A"],
            [
                [(0, 0), (1, 1)],
                [(0, 0), (1, 2)],
                [(0, 1), (1, 0)],
                [(0, 1), (1, 2)],
                [(0, 2), (1, 0)],
                [(0, 2), (1, 1)],
            ],
        ),
    ],
)
def test_map_to_multiple(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["R"], ["A"], [[(0, 0)]]),
        (["R"], ["B"], [[(0, 0)]]),
        (["R"], ["A", "B"], [[(0, 0)], [(0, 1)]]),
    ],
)
def test_single_wildcard(pattern, structure, exp_mapping):
    m = generate_mapping_permutations(pattern, structure, wildcard="R")
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A"], ["R"], []),
    ],
)
def test_pattern_does_not_map_to_wildcard_in_structure(pattern, structure, exp_mapping):
    # Test case for PermutationMapper class documentation
    m = generate_mapping_permutations(pattern, structure, wildcard="R")
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["a"], ["A"], [[(0, 0)]]),
        (["A"], ["a"], [[(0, 0)]]),
        (["r"], ["a", "B"], [[(0, 0)], [(0, 1)]]),
    ],
)
def test_case_insensitivity(pattern, structure, exp_mapping):
    mapper = PermutationMapper(wildcard="R", ignore_case=True)
    m = mapper.permute(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A"], [], [[(0, -1)]]),
        (["A"], ["B"], [[(0, -1)]]),
        (["A"], ["A"], [[(0, 0)]]),
        (["A"], ["A", "B"], [[(0, 0)]]),
        (["A"], ["B", "A"], [[(0, 1)]]),
    ],
)
def test_map_to_nothing(pattern, structure, exp_mapping):
    mapper = PermutationMapper(can_map_to_nothing="A")
    input_structure = copy.deepcopy(structure)
    m = mapper.permute(pattern, structure)
    assert input_structure == structure
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["A", "B"], [], [[(0, -1), (1, -1)]]),
        (["A", "B"], ["A"], [[(0, 0), (1, -1)]]),
        (["A", "B"], ["B"], [[(0, -1), (1, 0)]]),
        (["A", "B"], ["A", "B"], [[(0, 0), (1, 1)]]),
    ],
)
def test_multiple_map_to_nothing(pattern, structure, exp_mapping):
    mapper = PermutationMapper(can_map_to_nothing=["A", "B"])
    m = mapper.permute(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping",
    [
        (["R"], [], [[(0, -1)]]),
        (["R"], ["A"], [[(0, 0)]]),
        (["A", "R"], ["A"], [[(0, 0), (1, -1)]]),
        (["R", "R"], [], [[(0, -1), (1, -1)]]),
    ],
)
def test_wildcard_and_map_to_nothing(pattern, structure, exp_mapping):
    mapper = PermutationMapper(wildcard="R", can_map_to_nothing="R")
    m = mapper.permute(pattern, structure)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "pattern,structure,exp_mapping,cmtn",
    [
        (["H", "R"], ["A"], [[(0, -1), (1, 0)]], ["R", "H"]),
        (["R", "H"], ["A"], [[(0, 0), (1, -1)]], ["R", "H"]),
        (["H", "R"], ["A"], [[(0, -1), (1, 0)]], ["H", "R"]),
        (["R", "H"], ["A"], [[(0, 0), (1, -1)]], ["H", "R"]),
    ],
)
def test_wildcard_and_multi_map_to_nothing(pattern, structure, exp_mapping, cmtn):
    mapper = PermutationMapper(wildcard="R", can_map_to_nothing=cmtn)
    m = mapper.permute(pattern, structure)
    print(m)
    assert exp_mapping == m


@pytest.mark.parametrize(
    "structure,exp_mapping",
    [
        (["O"], [[(0, 0), (1, -1), (2, -1)]]),
        (["O", "C"], [[(0, 0), (1, -1), (2, 1)]]),
        (["O", "H"], [[(0, 0), (1, 1), (2, -1)]]),
        (["C", "O", "H"], [[(0, 1), (1, 2), (2, 0)]]),
    ],
)
def test_chem_map_hydrogen_and_wildcard(structure, exp_mapping):
    mapper = PermutationMapper(wildcard="R", can_map_to_nothing=["R", "H"])
    m = mapper.permute(["O", "H", "R"], structure)
    assert exp_mapping == m


def test_map_specific_to_general():
    mapper = PermutationMapper(wildcard="R", can_map_to_nothing=["R"])
    m = mapper.permute(["C"], ["R"])
    assert [] == m


def assert_matrix_mappings(matrix, pattern_symbols, structure_symbols, exp_mappings):
    for ps in pattern_symbols:
        for ss in structure_symbols:
            if (ps, ss) in exp_mappings:
                assert matrix.is_mapping(
                    ps, ss
                ), "Expected {} to be a mapping but it is not.".format((ps, ss))
            else:
                assert not matrix.is_mapping(
                    ps, ss
                ), "Expected {} to NOT be a mapping but it is.".format((ps, ss))


@pytest.mark.parametrize(
    "pattern_symbols,structure_symbols,exp_mappings,wildcard",
    [
        (["A", "B"], ["A", "B"], [("A", "A"), ("B", "B")], None),
        (["A", "B"], ["A", "B"], [("A", "A"), ("B", "B"), ("A", "B")], "A"),
        (["A"], ["A", "C"], [("A", "A")], None),
        (["A", "C"], ["A"], [("A", "A")], None),
        (["A", "R"], ["A", "C"], [("A", "A"), ("R", "A"), ("R", "C")], "R"),
    ],
)
def test_matching_matrix(pattern_symbols, structure_symbols, exp_mappings, wildcard):
    mapper = PermutationMapper(wildcard=wildcard)
    matrix = MappingMatrix(pattern_symbols, structure_symbols, mapper)
    assert_matrix_mappings(matrix, pattern_symbols, structure_symbols, exp_mappings)


@pytest.mark.parametrize(
    "pattern_symbols,structure_symbols,exp_symbol",
    [
        (["A", "A", "B"], ["A", "A", "A", "B", "B"], ("B", "B")),
        (["A", "A", "B"], ["A", "A", "B", "C"], ("B", "B")),
        (["C"], ["A", "B"], None),
    ],
)
def test_matrix_min_mapping_symbol(pattern_symbols, structure_symbols, exp_symbol):
    mapper = PermutationMapper()
    matrix = MappingMatrix(pattern_symbols, structure_symbols, mapper)
    sym = matrix.min_mapping_symbol(pattern_symbols, structure_symbols)
    assert sym == exp_symbol


def test_matrix_min_mapping_raises_value_error_when_pattern_longer_structure():
    with pytest.raises(ValueError):
        pattern_symbols = ["A", "B"]
        structure_symbols = ["A"]
        mapper = PermutationMapper()
        matrix = MappingMatrix(pattern_symbols, structure_symbols, mapper)
        matrix.min_mapping_symbol(pattern_symbols, structure_symbols)
