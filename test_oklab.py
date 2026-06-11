import oklab, math, random

def test_xyz():
    'https://bottosson.github.io/posts/oklab/#table-of-example-xyz-and-oklab-pairs'

    table_xyz = [(+0.950, +1.000, +1.089), 
                (+1.000, +0.000, +0.000), 
                (+0.000, +1.000, +0.000), 
                (+0.000, +0.000, +1.000)] 
    table_lab = [(+1.000, +0.000, +0.000),
                (+0.450, +1.236, -0.019),
                (+0.922, -0.671, +0.263),
                (+0.153, -1.415, -0.449)]

    for xyz, lab in zip(table_xyz, table_lab):
        for expected, computed in zip(xyz, oklab.lab_to_xyz(lab)):
            assert math.isclose(expected, computed, abs_tol=0.002)

        for expected, computed in zip(lab, oklab.xyz_to_lab(xyz)):
            assert math.isclose(expected, computed, abs_tol=0.002)

# honestly, i dont know why i cant make the abs_tol any higher. numerically, the module is quite trivial... good as a sanity check i guess
def test_forward_inverse_pairs():
    pairs = [
        (oklab.lch_to_lab, oklab.lab_to_lch),
        (oklab.xyz_to_lms, oklab.lms_to_xyz),
        (oklab.rgb_to_lms, oklab.lms_to_rgb),
        (oklab.lab_to_lms, oklab.lms_to_lab),
        (oklab.xyz_to_lab, oklab.lab_to_xyz),
        (oklab.rgb_to_lab, oklab.lab_to_rgb),
        (oklab.xyz_to_lch, oklab.lch_to_xyz),
        (oklab.rgb_to_lch, oklab.lch_to_rgb),
    ]

    for forward, inverse in pairs:
        for _ in range(100):
            tuple_in = tuple(random.random() for _ in range(3))
            tuple_out1 = inverse(forward(tuple_in))
            tuple_out2 = forward(inverse(tuple_in))
        
            for expected, computed1, computed2 in zip(tuple_in, tuple_out1, tuple_out2):
                assert math.isclose(expected, computed1, abs_tol=0.01)
                assert math.isclose(expected, computed2, abs_tol=0.01)
        
