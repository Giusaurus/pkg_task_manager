import argparse
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import py_trees


from georg_task_manager.bt.missions.Test_Mapping_BT import TestMapping as TestMapping
from georg_task_manager.bt.missions.Comparison_BT import ComparisonBT as ComparisonBT

MISSIONS = {
    
    "1": ("Test_Mapping", TestMapping),
    "2": ("Comparison", ComparisonBT),

}

V = py_trees.common.VisibilityLevel
LEVELS = {
    "all": V.ALL,
    "detail": V.DETAIL,
    "component": V.COMPONENT,
    "big": V.BIG_PICTURE,
}


def main():
    parser = argparse.ArgumentParser(description="Mission als Dot-Graph ausgeben")
    parser.add_argument("mission", choices=list(MISSIONS), help="Mission-ID wie im Selector")
    parser.add_argument("-o", "--out", default=".", help="Zielordner")
    parser.add_argument("-l", "--level", choices=list(LEVELS), default="detail",
                        help="Detailgrad des Graphen")
    parser.add_argument("-c", "--collapse", action="store_true",
                        help="Decorators (Retry, Discard, ...) zusammenklappen")
    args = parser.parse_args()

    name, builder = MISSIONS[args.mission]


    root = builder(MagicMock(), SimpleNamespace())

    out = os.path.expanduser(args.out)
    os.makedirs(out, exist_ok=True)

    py_trees.display.render_dot_tree(
        root,
        visibility_level=LEVELS[args.level],
        collapse_decorators=args.collapse,
        name=f"{name}_BT",
        target_directory=out,
    )

    print(py_trees.display.unicode_tree(root))
    print(f"\nGraph geschrieben nach: {out}/{name}_BT.(dot|png|svg)")


if __name__ == "__main__":
    main()