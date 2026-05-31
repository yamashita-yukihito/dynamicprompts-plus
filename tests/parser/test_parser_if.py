import pytest
from dynamicprompts.commands import IfCommand, LiteralCommand
from dynamicprompts.enums import SamplingMethod
from dynamicprompts.parser.parse import parse
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards.wildcard_manager import WildcardManager


def _create_context():
    return SamplingContext(
        default_sampling_method=SamplingMethod.RANDOM,
        wildcard_manager=WildcardManager(),
    )


def test_parse_if_eq_command():
    prompt = "%if{eq$$${hat}$$big hat$$blue hat$$red hat}"
    command = parse(prompt)
    assert isinstance(command, IfCommand)
    assert command.predicate.op == "eq"
    assert len(command.predicate.args) == 2
    assert command.then_command == LiteralCommand("blue hat")
    assert command.else_command == LiteralCommand("red hat")


def test_parse_if_defined_command():
    prompt = "%if{defined$$hat$$blue hat}"
    command = parse(prompt)
    assert isinstance(command, IfCommand)
    assert command.predicate.op == "defined"
    assert command.predicate.args[0] == "hat"
    assert command.then_command == LiteralCommand("blue hat")
    assert command.else_command is None


def test_evaluate_if_truthy():
    prompt = "%if{truthy$$false$$Yes$$No}"
    context = _create_context()
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "No"

    prompt = "%if{truthy$$true$$Yes$$No}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "Yes"


def test_evaluate_if_eq():
    # evaluate false
    prompt = "%if{eq$$A$$B$$Match$$NoMatch}"
    context = _create_context()
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "NoMatch"

    # evaluate true
    prompt = "%if{eq$$A$$A$$Match$$NoMatch}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "Match"


def test_if_with_variable_assignment():
    prompt = "${hat=!small hat}%if{eq$$${hat}$$big hat$$blue$$red}"
    context = _create_context()
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "red"

    prompt2 = "${hat=!big hat}%if{eq$$${hat}$$big hat$$blue$$red}"
    results2 = list(context.sample_prompts(prompt2, 1))
    assert results2[0].text == "blue"


def test_parse_if_neq_command():
    prompt = "%if{neq$$${hat}$$big hat$$blue hat$$red hat}"
    command = parse(prompt)
    assert isinstance(command, IfCommand)
    assert command.predicate.op == "neq"
    assert len(command.predicate.args) == 2
    assert command.then_command == LiteralCommand("blue hat")
    assert command.else_command == LiteralCommand("red hat")


def test_parse_if_eq_without_else():
    prompt = "%if{eq$$A$$A$$Match}"
    command = parse(prompt)
    assert isinstance(command, IfCommand)
    assert command.predicate.op == "eq"
    assert command.then_command == LiteralCommand("Match")
    assert command.else_command is None


def test_parse_if_defined_with_else():
    prompt = "%if{defined$$hat$$blue hat$$red hat}"
    command = parse(prompt)
    assert isinstance(command, IfCommand)
    assert command.predicate.op == "defined"
    assert command.predicate.args[0] == "hat"
    assert command.then_command == LiteralCommand("blue hat")
    assert command.else_command == LiteralCommand("red hat")


def test_evaluate_if_neq():
    context = _create_context()

    # neq is true when the values differ
    prompt = "%if{neq$$A$$B$$Different$$Same}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "Different"

    # neq is false when the values match
    prompt = "%if{neq$$A$$A$$Different$$Same}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "Same"


def test_evaluate_if_defined():
    context = _create_context()

    # variable assigned earlier in the sequence is considered defined
    prompt = "${hat=!small hat}%if{defined$$hat$$YES$$NO}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "YES"

    # an unassigned variable is not defined
    prompt = "%if{defined$$hat$$YES$$NO}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "NO"


def test_evaluate_if_without_else_yields_empty_string():
    context = _create_context()

    # a false predicate with no else branch evaluates to an empty string
    prompt = "%if{eq$$A$$B$$Match}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == ""

    prompt = "%if{defined$$hat$$wearing a hat}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == ""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", "Yes"),
        ("TRUE", "Yes"),
        ("anything", "Yes"),
        ("1", "Yes"),
        ("false", "No"),
        ("0", "No"),
        ("no", "No"),
        ("off", "No"),
    ],
)
def test_evaluate_if_truthy_values(value, expected):
    context = _create_context()
    prompt = f"%if{{truthy$${value}$$Yes$$No}}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == expected


def test_evaluate_nested_if():
    context = _create_context()

    # the then-branch of the outer if is itself an if command
    prompt = "%if{eq$$A$$A$$%if{eq$$B$$B$$inner-yes$$inner-no}$$outer-no}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "inner-yes"

    # the outer predicate is false, so the inner if is never reached
    prompt = "%if{eq$$A$$Z$$%if{eq$$B$$B$$inner-yes$$inner-no}$$outer-no}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "outer-no"


def test_evaluate_if_with_variant_in_branch():
    context = _create_context()

    # a variant inside a branch is sampled normally
    prompt = "%if{eq$$A$$A$${x|x}$$no}"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "x"


def test_if_command_in_sequence():
    context = _create_context()

    # an if command surrounded by literal text composes into a sequence
    prompt = "a ${color=!blue} %if{eq$$${color}$$blue$$sky$$ground}!"
    results = list(context.sample_prompts(prompt, 1))
    assert results[0].text == "a  sky!"
