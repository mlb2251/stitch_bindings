import json
import math
import os
import unittest

from stitch_core import (
    compress,
    rewrite,
    StitchException,
    from_dreamcoder,
    name_mapping_stitch,
    stitch_to_dreamcoder,
)

data_path = os.path.join(os.path.dirname(__file__), "../data/")


class BasicTest(unittest.TestCase):
    def test_simple(self):
        # simple test
        programs = ["(a a a)", "(b b b)"]
        res = compress(programs, iterations=1)
        self.assertEqual(res.rewritten, ["(fn_0 a)", "(fn_0 b)"])
        self.assertEqual(res.abstractions[0].body, "(#0 #0 #0)")
        programs_to_rewrite = ["(c c c)", "(d d d)"]
        rw = rewrite(programs_to_rewrite, res.abstractions)
        self.assertEqual(rw.rewritten, ["(fn_0 c)", "(fn_0 d)"])
        self.assertEqual(
            stitch_to_dreamcoder(rw.rewritten, name_mapping_stitch(res.json)),
            ["(#(lambda ($0 $0 $0)) c)", "(#(lambda ($0 $0 $0)) d)"],
        )

    def test_overview_example(self):

        # example from Overview section of the Stitch paper (https://arxiv.org/abs/2211.16605)
        programs = [
            "(lam (+ 3 (* (+ 2 4) 2)))",
            "(lam (map (lam (+ 3 (* 4 (+ 3 $0)))) $0))",
            "(lam (* 2 (+ 3 (* $0 (+ 2 1)))))",
        ]
        res = compress(programs, iterations=1, max_arity=2)
        self.assertEqual(res.abstractions[0].body, "(+ 3 (* #1 #0))")
        self.assertEqual(
            res.rewritten,
            [
                "(lam (fn_0 2 (+ 2 4)))",
                "(lam (map (lam (fn_0 (+ 3 $0) 4)) $0))",
                "(lam (* 2 (fn_0 (+ 2 1) $0)))",
            ],
        )

    def test_loading_from_file(self):
        # loading from a file
        with open(os.path.join(data_path, "cogsci/nuts-bolts.json"), "r") as f:
            programs = json.load(f)
        res = compress(programs, iterations=3, max_arity=3)
        self.assertEqual(len(res.abstractions), 3)
        self.assertEqual(
            res.abstractions[0].body,
            "(T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0))",
        )
        self.assertEqual(
            res.abstractions[1].body,
            "(repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0))",
        )
        self.assertEqual(res.abstractions[2].body, "(T (T c (M 2 0 0 0)) (M #0 0 0 0))")

    def test_dreamcoder_format(self):
        # dreamcoder format
        with open(os.path.join(data_path, "dc/origami/iteration_0_3.json"), "r") as f:
            dreamcoder_json = json.load(f)
        kwargs = from_dreamcoder(dreamcoder_json)
        res = compress(**kwargs, iterations=3, max_arity=3)
        self.assertEqual(
            res.abstractions[0].body, "(if (empty? (cdr #0)) #2 (#1 (cdr #0)))"
        )

    def test_invalid_argument(self):
        self.assertRaises(
            StitchException,
            compress,
            ["(a a a)", "(b b b)"],
            iterations=1,
            nonexistant_arg=12345,
        )

    def test_invalid_programs(self):

        # StitchException: malformed programs (or any other panic in the rust backend)
        bad_programs = ["(a a a"]
        self.assertRaises(
            StitchException,
            compress,
            bad_programs,
            iterations=3,
        )

    def test_invalid_type(self):
        # TypeError: passing in an argument of the wrong type, so that conversion to strongly typed Rust fails
        bad_programs = 4
        self.assertRaises(
            TypeError,
            compress,
            bad_programs,
            iterations=3,
            loud_panic=True,
        )

    def test_weighting(self):
        # 1x (default) weighting vs 2x weighting vs weighting the "g" programs more
        programs = ["(f a a)", "(f b b)", "(f c c)", "(g d d)", "(g e e)"]
        res = compress(programs, iterations=1)
        res2x = compress(programs, iterations=1, weights=[2.0 for _ in programs])
        res_uneven = compress(programs, iterations=1, weights=[1.0, 1.0, 1.0, 2.0, 2.0])
        self.assertEqual(res.json["original_cost"] * 2, res2x.json["original_cost"])
        self.assertEqual(res.json["final_cost"] * 2, res2x.json["final_cost"])
        self.assertEqual(res.abstractions[0].body, res2x.abstractions[0].body)
        self.assertEqual(res_uneven.abstractions[0].body, "(g #0 #0)")
        self.assertLess(
            math.fabs(
                res_uneven.json["original_cost"] / res_uneven.json["final_cost"]
                - res_uneven.json["compression_ratio"]
            ),
            0.00001,
        )
