from genticode.quality.flake import detect_flakes


def test_detect_flakes_rate():
    seq = [True, False, True, False]
    idx = {"i": 0}

    def runner():
        i = idx["i"]
        idx["i"] = (i + 1) % len(seq)
        return seq[i]

    rate, fails = detect_flakes(4, runner)
    assert fails == 2 and abs(rate - 0.5) < 1e-9

