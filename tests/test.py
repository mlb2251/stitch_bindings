from stitch_core import compress, rewrite, StitchException, from_dreamcoder, Abstraction, name_mapping_stitch, stitch_to_dreamcoder
import json
import math

# simple test
programs = ["(a a a)", "(b b b)"]
res = compress(programs, iterations=1)
assert res.rewritten == ['(fn_0 a)', '(fn_0 b)']
assert res.abstractions[0].body == '(#0 #0 #0)'

# rewriting test
programs_to_rewrite = ["(c c c)", "(d d d)"]
rw = rewrite(programs_to_rewrite, res.abstractions)
assert rw.rewritten == ['(fn_0 c)', '(fn_0 d)']
assert stitch_to_dreamcoder(rw.rewritten, name_mapping_stitch(res.json)) == ['(#(lambda ($0 $0 $0)) c)', '(#(lambda ($0 $0 $0)) d)']

# example from Overview section of the Stitch paper (https://arxiv.org/abs/2211.16605)
programs = [
    "(lam (+ 3 (* (+ 2 4) 2)))",
    "(lam (map (lam (+ 3 (* 4 (+ 3 $0)))) $0))",
    "(lam (* 2 (+ 3 (* $0 (+ 2 1)))))"
]
res = compress(programs, iterations=1, max_arity=2)
assert res.abstractions[0].body == '(+ 3 (* #1 #0))'
assert res.rewritten == [
    '(lam (fn_0 2 (+ 2 4)))',
    '(lam (map (lam (fn_0 (+ 3 $0) 4)) $0))',
    '(lam (* 2 (fn_0 (+ 2 1) $0)))'
    ]

# loading from a file
with open('../data/cogsci/nuts-bolts.json','r') as f:
    programs = json.load(f)
res = compress(programs, iterations=3, max_arity=3)
assert res.abstractions[0].body == '(T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0))'
assert res.abstractions[1].body == '(repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0))'
assert res.abstractions[2].body == '(T (T c (M 2 0 0 0)) (M #0 0 0 0))'

# dreamcoder format
with open('../data/dc/origami/iteration_0_3.json','r') as f:
    dreamcoder_json = json.load(f)
kwargs = from_dreamcoder(dreamcoder_json)
res = compress(**kwargs, iterations=3, max_arity=3)
assert res.abstractions[0].body == '(if (empty? (cdr #0)) #2 (#1 (cdr #0)))'


# StitchException: passing in an argument that doesn't actually exist
try:
    out_json = compress(programs, iterations=3, nonexistant_arg=213879)
    assert False, "Should have thrown an exception"
except StitchException as e:
    pass

# StitchException: malformed programs (or any other panic in the rust backend)
bad_programs = ["(a a a"]
try:
    out_json = compress(bad_programs, iterations=3)
    assert False, "Should have thrown an exception"
except StitchException as e:
    # print(e)
    pass

# TypeError: passing in an argument of the wrong type, so that conversion to strongly typed Rust fails
bad_programs = 4
try:
    out_json = compress(bad_programs, iterations=3, loud_panic=True)
    assert False, "Should have thrown an exception"
except TypeError as e:
    # print(e)
    pass

# 1x (default) weighting vs 2x weighting vs weighting the "g" programs more
programs = ["(f a a)", "(f b b)", "(f c c)", "(g d d)", "(g e e)"]
res = compress(programs, iterations=1)
res2x = compress(programs, iterations=1, weights=[2. for _ in programs])
res_uneven = compress(programs, iterations=1, weights=[1., 1., 1., 2., 2.])

assert res.json["original_cost"] *2 == res2x.json["original_cost"]
assert res.json["final_cost"] *2 == res2x.json["final_cost"]
assert res.abstractions[0].body == res2x.abstractions[0].body == "(f #0 #0)"
assert res_uneven.abstractions[0].body == "(g #0 #0)"

# make sure compression ratio is as expected
assert math.fabs(res_uneven.json["original_cost"]/res_uneven.json["final_cost"] - res_uneven.json["compression_ratio"]) < 0.00001

# assert res.rewritten == ['(fn_0 a)', '(fn_0 b)']
# assert res.abstractions[0].body == '(#0 #0 #0)'


print("Passed all tests")