#!/bin/env pyhton
import copy
import yaml
import os
import svgutils.transform as svgtransform
import glob
import shutil

import pathlib

EXPORT_PATH = "generate"


def ensure_exist(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


HAS_SVGO = shutil.which("svgo") is not None


def svgo_optimize(inpath: str, outpath: str = ""):
    # can't do anything w/out svgo...
    if not HAS_SVGO:
        return

    import subprocess as sp
    import sys

    if os.path.isfile(inpath) and (
        outpath == "" or os.path.isdir(os.path.dirname(outpath))
    ):
        args = ["svgo", inpath]
        if outpath != "":
            args.append(["-o", outpath])
        sp.run(args)
    else:
        print("A non existing file path was passed to svgoTreat().", file=sys.stderr)
        exit(2)


if __name__ == "__main__":
    ensure_exist(EXPORT_PATH)

    manifest = yaml.load(open("icongen.yaml", "r"), Loader=yaml.SafeLoader)

    root = os.getcwd()

    if not HAS_SVGO:
        print("SVGO not detected! SVG optimisation disabled.")

    for mapping in manifest["export-mappings"]:
        outroot = os.path.join(root, EXPORT_PATH, mapping["outputpath"])
        ensure_exist(outroot)

        if mapping["type"] == "copy":
            inpath = os.path.join(root, mapping["glob"])
            inglob = glob.glob(inpath)

            for file in inglob:
                filename = os.path.basename(file)
                outpath = os.path.join(
                    root, EXPORT_PATH, mapping["outputpath"], filename
                )

                if not os.path.exists(outpath):
                    shutil.copyfile(file, outpath)
                    svgo_optimize(outpath)

        elif mapping["type"] == "overlays":
            base_path = mapping.get("basepath", "./")
            overlays_path = mapping["overlayspath"]
            for base_layer in mapping["baselayers"]:
                base_layer_name = base_layer["name"]
                base_layer_path = (
                    os.path.join(root, base_path, base_layer_name) + ".svg"
                )

                basesvg = svgtransform.fromfile(base_layer_path)

                for overlay in base_layer["overlays"]:
                    outname = overlay["outname"]
                    if overlay["outname-type"] == "append":
                        outname = base_layer_name + outname

                    outpath = (
                        os.path.join(root, EXPORT_PATH, mapping["outputpath"], outname)
                        + ".svg"
                    )

                    overlay_path = (
                        os.path.join(root, overlays_path, overlay["overlay"]) + ".svg"
                    )

                    overlaid = copy.deepcopy(basesvg)
                    overlaysvg = svgtransform.fromfile(overlay_path)
                    overlaid.append(overlaysvg)
                    overlaid.save(outpath)

                    svgo_optimize(outpath)
