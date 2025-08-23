from IPython.display import Video, Image

# import dill
import PIL.Image

# import skrf as rf
from pprint import pprint
import os
import subprocess
import json
import numpy as np
import requests
from .pic.sparams import *
from .utils import *
from .layers import *
from .constants import *
from PIL import Image as PILImage

from subprocess import Popen, PIPE

URL = "http://127.0.0.1:8975"


def start_fdtd_server(url=URL):
    try:
        r = requests.get(url)
    except:
        print("starting julia fdtd server on localhost...")
        cmd = ["julia", "-e", "using Luminescent; start_fdtd_server()"]
        proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with proc:
            for line in proc.stdout:
                print(str(line.decode().strip()), flush=True)
            err_message = proc.stderr.read().decode()
            print(err_message)


def solve(path, nthreads=None, **kwargs):
    if nthreads is None:
        nthreads = os.cpu_count()
    path = os.path.abspath(path)
    prob = load_prob(path)
    prob = {**prob, **kwargs}
    with open(os.path.join(path, "problem.json"), "w") as f:
        json.dump(prob, f)

    # prob["action"] = "solve"
    # r = requests.post(f"{url}/local", json=prob)
    1
    # print(f"""
    #       using simulation folder {path}
    #       starting julia process...
    #       """)
    # start_time = time.time()

    def run(cmd):
        print("=" * 40)
        print()
        proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # proc.wait()
        with proc:
            for line in proc.stdout:
                print(str(line.decode().strip()), flush=True)
            err_message = proc.stderr.read().decode()
            print(err_message)
        return proc.returncode

    # if dev:
    #     env = r'using Pkg;Pkg.activate(raw"c:\Users\pxshe\OneDrive\Desktop\beans\Luminescent.jl\luminescent");'
    # else:
    #     env = '0;'
    # cmd = ["lumi", path]
    # try:
    c = run(["Luminescent", path, f" --julia-args -t{nthreads}"])
    if c != 0:
        print("failed")
        exit(1)

    # except:
    # run(["julia", "-e", f'println(Base.active_project())'])
    # print("no binaries found - starting julia session to compile - will alternate between execution and JIT compilation - will take 3 mins before simulation starts.\nYou can take a break and come back :) ...")

    # prob = json.loads(open(os.path.join(path, "problem.json"), "rb").read())
    # a = ['julia', '-e', ]
    # gpu_backend = prob["gpu_backend"]
    # _class = prob["class"]
    # if gpu_backend == "CUDA":
    #     array = "cu"
    #     pkgs = ",CUDA"
    # else:
    #     array = "Array"
    #     pkgs = ""

    # run([f'using Luminescent;picrun(raw"{path}")'])
    # b = [f'using Luminescent{pkgs};{_class}run(raw"{path}",{array})']
    # run(a+b)

    # with Popen(cmd,  stdout=PIPE, stderr=PIPE) as p:
    #     if p.stderr is not None:
    #         for line in p.stderr:
    #             print(line, flush=True)
    # exit_code = p.poll()
    # subprocess.run()
    # print(f"julia simulation took {time.time()-start_time} seconds")
    # print(f"images and results saved in {path}")
    # sol = load(path=path)
    # return sol


def load_sparams(sparams):
    if "re" in list(sparams.values())[0]:
        return {k: v["re"] + 1j * v["im"] for k, v in sparams.items()}
    return {
        wavelength: {k: (v["re"] + 1j * v["im"]) for k, v in d.items()}
        for wavelength, d in sparams.items()
    }


def load_sol(path, show=True):
    path = os.path.abspath(path)
    print(f"loading solution from {path}")
    prob = json.loads(open(os.path.join(path, "problem.json"), "rb").read())
    p = os.path.join(path, "solution.json")
    # if os.path.exists(p):
    #     sol = json.loads(open(p).read())
    sol = json.loads(open(p).read())

    if prob["class"] == "gen":
        S = np.load(os.path.join(path, "S.npy"))
        frequencies = rf.Frequency.from_f(sol["fs"], unit="GHz")
        ntwk = rf.Network(frequency=frequencies, s=S)
        ntwk.write_touchstone(os.path.join(path, "S.s2p"))
        sol.update({"S": S, "network": ntwk})
    elif prob["class"] == "pic":
        # sol = json.loads(p, "rb").read())["sol"]
        # sol["S"] = load_sparams(sol["S"])
        # sol["component"] = gf.import_gds(os.path.join(path, "component.gds"))
        if prob["study"] == "sparams":
            pass
        elif prob["study"] == "inverse_design":
            # l = [np.array(d) for d in sol["optimized_designes"]]
            # sol["optimized_designes"] = l
            # print(
            #     f"loading optimized design regions at resolution {sol['dl']}")
            # for i, a in enumerate(l):
            #     path = f"optimized_design_{i+1}.png"
            #     Image.fromarray(np.flip(np.uint8((1-a)) * 255, 0),
            #                     'L').save(os.path.join(path, name))
            # pic2gds(os.path.join(
            #     path, name), sol["dx"])
            # c = apply_design(sol["component"],  sol)
            # sol["optimized_component"] = copy.deepcopy(c)
            # sol["optimized_component"] = c
            # c.write_gds(os.path.join(path, "optimized_component.gds"))
            0

        if show:
            # p = os.path.join(path, f"sim.png")
            # if os.path.exists(p):
            #     img = Image.open(p)
            #     img.show()
            #     try:
            #         display(img)
            #     except:
            #         pass

            _sol = {
                k: sol[k]
                for k in [
                    "T",
                    "dB",
                    "S",
                    "phasors",
                ]
            }
            # "total_power_T", "total_power_dB"]}
            # _sol["optimized_designes"] = "[[...]]"
            # pprint(_sol)

    if show:
        # for fn in os.listdir(path):
        #     fn = os.path.join(path, fn)
        #     if fn.endswith(".png") or fn.endswith(".jpg"):
        #         img = Image.open(fn)
        #         img.show()
        #         try:
        #             display(img)
        #         except:
        #             pass
        #     if fn.endswith(".mp4"):
        #         Video(fn)
        0

    make_design_gds(path)

    return sol


def design_from_gds(path, i=1):
    # make_design_gds(path)
    c = gf.import_gds(os.path.join(path, f"design{i}.gds"))
    d = json.load(open(os.path.join(path, "info.json")))
    for p in d[f"designs"][i - 1]["ports"]:
        c.add_port(**p, layer=WG)
    c.info = d
    return c
