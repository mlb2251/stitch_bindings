import copy
import json
import os
import unittest

import stitch_core


data_path = os.path.join(os.path.dirname(__file__), "../data/")

symbol_reuse_abstraction = stitch_core.Abstraction(
    name="fn_0",
    body="(+ 1 #2 #2 #1 #0 2 3 4)",
    arity=3,
    tdfa_annotation=None,
    variable_types=["S", "S", "S"],
)


class VariableTypeTest(unittest.TestCase):
    def load_data(self):
        with open(os.path.join(data_path, "python/symbol-reuse.json"), "r") as f:
            return json.load(f)

    def test_default(self):
        result = stitch_core.compress(
            self.load_data(), iterations=1, max_arity=0, symvar_prefix="&"
        )
        self.assertEqual(len(result.abstractions), 1)
        [abstr] = result.abstractions
        self.assertEqual(abstr.__dict__, symbol_reuse_abstraction.__dict__)
        rewritten = stitch_core.rewrite(
            self.load_data(), result.abstractions, symvar_prefix="&"
        )
        self.assertEqual(
            rewritten.rewritten,
            ["(fn_0 &z &y &x)", "(fn_0 &z &x &y)", "(+ 1 &x &x &x &z 2 3 4)"],
        )

    def test_metavariables(self):
        abstr = copy.deepcopy(symbol_reuse_abstraction)
        abstr.variable_types = ["M", "M", "M"]
        rewritten = stitch_core.rewrite(self.load_data(), [abstr], symvar_prefix="&")
        self.assertEqual(
            rewritten.rewritten,
            ["(fn_0 &z &y &x)", "(fn_0 &z &x &y)", "(fn_0 &z &x &x)"],
        )
