import pytest

from dynamicprompts.commands import IfCommand, LiteralCommand
from dynamicprompts.commands.if_command import Predicate
from dynamicprompts.enums import SamplingMethod
from dynamicprompts.parser.parse import parse
from dynamicprompts.samplers.random import RandomSampler
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards.wildcard_manager import WildcardManager


def _create_context():
    return SamplingContext(
        default_sampling_method=SamplingMethod.RANDOM,
        wildcard_manager=WildcardManager()
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
