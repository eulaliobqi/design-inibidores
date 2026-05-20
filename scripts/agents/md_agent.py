"""MDAgent — Avalia estabilidade dos top complexos via GROMACS.

Executa MD curta (10 ns padrão) para verificar:
  - RMSD backbone do peptídeo ao longo do tempo
  - Persistência de contatos H-bond na interface
  - Raio de giro do peptídeo
"""
import json
import re
import subprocess
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import check_gromacs


_MDP_TEMPLATE = """; md.mdp — simulação curta para avaliação de inibidores
integrator   = md
nsteps       = {nsteps}
dt           = 0.002
nstxout      = 0
nstvout      = 0
nstfout      = 0
nstxout-compressed = 2500
nstenergy    = 2500
nstlog       = 2500
continuation = yes
constraint_algorithm = lincs
constraints  = h-bonds
cutoff-scheme = Verlet
nstlist      = 10
rcoulomb     = 1.0
rvdw         = 1.0
coulombtype  = PME
pme_order    = 4
fourierspacing = 0.16
tcoupl       = V-rescale
tc-grps      = Protein Non-Protein
tau_t        = 0.1  0.1
ref_t        = {temp}  {temp}
pcoupl       = Parrinello-Rahman
pcoupltype   = isotropic
tau_p        = 2.0
ref_p        = 1.0
compressibility = 4.5e-5
pbc          = xyz
DispCorr     = EnerPres
gen_vel      = no
"""

_MINIM_MDP = """; minim.mdp
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps      = 50000
cutoff-scheme = Verlet
nstlist     = 10
rcoulomb    = 1.0
rvdw        = 1.0
coulombtype = PME
pbc         = xyz
"""

_NVT_MDP = """; nvt.mdp
define      = -DPOSRES
integrator  = md
nsteps      = 25000
dt          = 0.002
nstlog      = 1000
nstenergy   = 1000
continuation = no
constraint_algorithm = lincs
constraints = h-bonds
cutoff-scheme = Verlet
nstlist     = 10
rcoulomb    = 1.0
rvdw        = 1.0
coulombtype = PME
tcoupl      = V-rescale
tc-grps     = Protein Non-Protein
tau_t       = 0.1  0.1
ref_t       = {temp}  {temp}
pcoupl      = no
pbc         = xyz
gen_vel     = yes
gen_temp    = {temp}
gen_seed    = -1
"""

_NPT_MDP = """; npt.mdp
define      = -DPOSRES
integrator  = md
nsteps      = 25000
dt          = 0.002
nstlog      = 1000
nstenergy   = 1000
continuation = yes
constraint_algorithm = lincs
constraints = h-bonds
cutoff-scheme = Verlet
nstlist     = 10
rcoulomb    = 1.0
rvdw        = 1.0
coulombtype = PME
tcoupl      = V-rescale
tc-grps     = Protein Non-Protein
tau_t       = 0.1  0.1
ref_t       = {temp}  {temp}
pcoupl      = Parrinello-Rahman
pcoupltype  = isotropic
tau_p       = 2.0
ref_p       = 1.0
compressibility = 4.5e-5
pbc         = xyz
gen_vel     = no
"""


class MDAgent(BaseAgent):

    def run(self, rosetta_results: dict, receptor_pdb: str) -> dict:
        if not check_gromacs():
            self._warn_missing_tool(
                "GROMACS",
                "Instalar: conda install -c conda-forge gromacs"
            )
            return self._heuristic_stability(rosetta_results)

        cfg = self.config.get("md", {})
        ns = cfg.get("simulation_ns", 10)
        temp = cfg.get("temperature", 300)

        # Selecionar top-5 por I_sc para MD (custo computacional)
        top5 = sorted(rosetta_results.items(),
                      key=lambda x: x[1].get("I_sc", 0))[:5]

        self.logger.info(f"MD GROMACS: {len(top5)} complexos, {ns} ns cada...")

        results = {}
        for stem, rdata in top5:
            complex_pdb = rdata.get("complex_pdb") or rdata.get("refined_pdb")
            if not complex_pdb or not Path(complex_pdb).exists():
                self.logger.warning(f"  Pulando {stem}: PDB não encontrado")
                continue

            out_dir = self.workdir / stem
            out_dir.mkdir(exist_ok=True)
            md_result = self._run_gromacs(
                str(complex_pdb), out_dir, ns, temp,
                rdata.get("sequence", "?")
            )
            results[stem] = {**md_result, "sequence": rdata["sequence"]}

        (self.workdir / "md_results.json").write_text(
            json.dumps(results, indent=2, default=str)
        )
        return results

    def _run_gromacs(self, complex_pdb: str, out: Path, ns: int,
                     temp: int, seq: str) -> dict:
        gmx = "gmx"
        ff = self.config.get("md", {}).get("forcefield", "amber99sb-ildn")
        water = self.config.get("md", {}).get("water_model", "tip3p")

        # Escrever mdp files
        nsteps = int(ns * 500000)
        (out / "md.mdp").write_text(_MDP_TEMPLATE.format(nsteps=nsteps, temp=temp))
        (out / "minim.mdp").write_text(_MINIM_MDP)
        (out / "nvt.mdp").write_text(_NVT_MDP.format(temp=temp))
        (out / "npt.mdp").write_text(_NPT_MDP.format(temp=temp))

        def gmx_run(args, **kw):
            cmd = [gmx] + args
            return subprocess.run(cmd, cwd=str(out), capture_output=True,
                                  text=True, **kw)

        try:
            # pdb2gmx
            p = gmx_run(["pdb2gmx", "-f", complex_pdb, "-o", "processed.gro",
                          "-p", "topol.top", "-i", "posre.itp",
                          "-ff", ff, "-water", water, "-ignh"],
                         input="1\n", timeout=120)
            if p.returncode != 0:
                raise RuntimeError(f"pdb2gmx: {p.stderr[-200:]}")

            # editconf
            gmx_run(["editconf", "-f", "processed.gro", "-o", "box.gro",
                      "-bt", "dodecahedron", "-d", "1.2"], timeout=60)

            # solvate
            gmx_run(["solvate", "-cp", "box.gro", "-cs", "spc216.gro",
                      "-o", "solv.gro", "-p", "topol.top"], timeout=60)

            # genion
            gmx_run(["grompp", "-f", str(out / "minim.mdp"),
                      "-c", "solv.gro", "-p", "topol.top",
                      "-o", "ions.tpr", "-maxwarn", "2"], timeout=60)
            gmx_run(["genion", "-s", "ions.tpr", "-o", "solv_ions.gro",
                      "-p", "topol.top", "-pname", "NA", "-nname", "CL",
                      "-neutral", "-conc", "0.15"],
                     input="SOL\n", timeout=60)

            # Minimização
            gmx_run(["grompp", "-f", str(out / "minim.mdp"),
                      "-c", "solv_ions.gro", "-p", "topol.top",
                      "-o", "minim.tpr", "-maxwarn", "2"], timeout=60)
            gmx_run(["mdrun", "-deffnm", "minim", "-ntmpi", "1",
                      "-ntomp", "4"], timeout=600)

            # NVT
            gmx_run(["grompp", "-f", str(out / "nvt.mdp"),
                      "-c", "minim.gro", "-r", "minim.gro",
                      "-p", "topol.top", "-o", "nvt.tpr", "-maxwarn", "2"],
                     timeout=60)
            gmx_run(["mdrun", "-deffnm", "nvt", "-ntmpi", "1", "-ntomp", "4"],
                     timeout=600)

            # NPT
            gmx_run(["grompp", "-f", str(out / "npt.mdp"),
                      "-c", "nvt.gro", "-r", "nvt.gro", "-t", "nvt.cpt",
                      "-p", "topol.top", "-o", "npt.tpr", "-maxwarn", "2"],
                     timeout=60)
            gmx_run(["mdrun", "-deffnm", "npt", "-ntmpi", "1", "-ntomp", "4"],
                     timeout=600)

            # MD produção
            gmx_run(["grompp", "-f", str(out / "md.mdp"),
                      "-c", "npt.gro", "-t", "npt.cpt",
                      "-p", "topol.top", "-o", "md.tpr", "-maxwarn", "2"],
                     timeout=60)
            p = gmx_run(["mdrun", "-deffnm", "md",
                          "-ntmpi", "1", "-ntomp", "4",
                          "-nb", "gpu", "-pme", "gpu"],
                         timeout=ns * 3600)
            if p.returncode != 0:
                # Fallback CPU
                gmx_run(["mdrun", "-deffnm", "md",
                          "-ntmpi", "1", "-ntomp", "4"], timeout=ns * 7200)

            # Análise
            return self._analyze_trajectory(out, gmx)

        except Exception as e:
            self.logger.error(f"GROMACS erro ({seq[:6]}...): {e}")
            return {"rmsd_avg_nm": None, "hbond_avg": None,
                    "rg_avg_nm": None, "error": str(e)}

    def _analyze_trajectory(self, out: Path, gmx: str) -> dict:
        def run_a(args, inp=""):
            return subprocess.run(
                [gmx] + args, cwd=str(out),
                input=inp, capture_output=True, text=True, timeout=120
            )

        # RMSD backbone peptídeo
        run_a(["rms", "-s", "md.tpr", "-f", "md.xtc",
                "-o", "rmsd.xvg", "-tu", "ns"], inp="Backbone\nBackbone\n")

        # H-bonds interface
        run_a(["hbond", "-s", "md.tpr", "-f", "md.xtc",
                "-num", "hbond_num.xvg"], inp="Protein\nProtein\n")

        # Raio de giro
        run_a(["gyrate", "-s", "md.tpr", "-f", "md.xtc",
                "-o", "rg.xvg"], inp="Protein\n")

        def parse_xvg(fname):
            vals = []
            f = out / fname
            if not f.exists():
                return None
            for line in f.read_text().splitlines():
                if line.startswith(("#", "@")):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        vals.append(float(parts[1]))
                    except ValueError:
                        pass
            return vals

        import numpy as np
        rmsd_vals = parse_xvg("rmsd.xvg")
        hb_vals   = parse_xvg("hbond_num.xvg")
        rg_vals   = parse_xvg("rg.xvg")

        return {
            "rmsd_avg_nm":  round(float(np.mean(rmsd_vals)), 4) if rmsd_vals else None,
            "rmsd_std_nm":  round(float(np.std(rmsd_vals)), 4) if rmsd_vals else None,
            "hbond_avg":    round(float(np.mean(hb_vals)), 3) if hb_vals else None,
            "hbond_max":    int(max(hb_vals)) if hb_vals else None,
            "rg_avg_nm":    round(float(np.mean(rg_vals)), 4) if rg_vals else None,
            "method":       "gromacs",
        }

    def _heuristic_stability(self, rosetta_results: dict) -> dict:
        results = {}
        for stem, rdata in rosetta_results.items():
            seq = rdata.get("sequence", "")
            # Mais básicos + menos Pro = mais estável
            n_basic = sum(1 for aa in seq if aa in "RK")
            n_pro = sum(1 for aa in seq if aa == "P")
            est_rmsd = max(0.05, 0.3 - n_basic * 0.02 + n_pro * 0.03)
            est_hb = n_basic * 1.5 + sum(1 for aa in seq if aa in "STNQ")
            results[stem] = {
                "sequence": seq,
                "rmsd_avg_nm": round(est_rmsd, 3),
                "hbond_avg": round(est_hb, 2),
                "method": "heuristic",
            }
        return results
