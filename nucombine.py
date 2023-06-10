#!/bin/env pyhton
import copy
import yaml
import os
import svgutils.transform as svgtransform
import glob

import pathlib

EXPORT_PATH = "generate"


def ensure_exist(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_exist(EXPORT_PATH)

    manifest = yaml.load(open("icongen.yaml", "r"), Loader=yaml.SafeLoader)

    root = os.getcwd()

    for mapping in manifest["export-mappings"]:
        outroot = os.path.join(root, EXPORT_PATH, mapping["outputpath"])
        ensure_exist(outroot)

        if mapping["type"] == "hardlink":
            inpath = os.path.join(root, mapping["glob"])
            inglob = glob.glob(inpath)

            for file in inglob:
                filename = os.path.basename(file)
                outpath = os.path.join(
                    root, EXPORT_PATH, mapping["outputpath"], filename
                )

                if not os.path.exists(outpath):
                    os.link(file, outpath)

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
