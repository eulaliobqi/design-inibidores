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

        # Selecionar top-5 por Vina kcal/mol (energia física real)
        # Fallback para I_sc heurístico se docking_results.json não existir
        top5 = self._select_top5_vina(rosetta_results)

        self.logger.info(f"MD GROMACS: {len(top5)} complexos, {ns} ns cada...")

        results = {}
        for stem, rdata in top5:
            seq = rdata.get("sequence", "?")
            complex_pdb = rdata.get("complex_pdb") or rdata.get("refined_pdb")
            # Construir complex PDB quando o Rosetta não gerou um para este candidato
            if not complex_pdb or not Path(complex_pdb).exists():
                self.logger.info(f"  Construindo complex PDB para {seq[:12]}...")
                built = self._build_complex_for_md(seq, receptor_pdb)
                complex_pdb = str(built) if built else None

            if not complex_pdb or not Path(str(complex_pdb)).exists():
                self.logger.warning(f"  Pulando {stem}: impossível construir PDB")
                continue

            out_dir = self.workdir / stem
            out_dir.mkdir(exist_ok=True)
            md_result = self._run_gromacs(
                str(complex_pdb), out_dir, ns, temp, seq
            )
            results[stem] = {**md_result, "sequence": seq,
                             "vina_kcal": rdata.get("vina_kcal")}

        (self.workdir / "md_results.json").write_text(
            json.dumps(results, indent=2, default=str)
        )
        return results

    def _select_top5_vina(self, rosetta_results: dict) -> list:
        """Seleciona top-5 por Vina kcal/mol do docking_results.json.
        Cria entradas mínimas para sequências que não passaram pelo Rosetta.
        Fallback para I_sc heurístico se docking_results.json não existir."""
        docking_json = self.workdir.parent / "docking" / "docking_results.json"
        if docking_json.exists():
            try:
                dock = json.loads(docking_json.read_text())
                # Mapeia sequência → dados rosetta (se existir)
                seq_ros = {v.get("sequence"): (k, v)
                           for k, v in rosetta_results.items() if v.get("sequence")}
                # Ordenar por Vina (mais negativo = melhor)
                valid = [(k, v) for k, v in dock.items()
                         if v.get("best_affinity_kcal") is not None]
                valid.sort(key=lambda x: x[1]["best_affinity_kcal"])
                result = []
                for dk, dv in valid[:5]:
                    seq = dv["sequence"]
                    vina = dv["best_affinity_kcal"]
                    if seq in seq_ros:
                        rk, rv = seq_ros[seq]
                        rv["vina_kcal"] = vina
                        result.append((rk, rv))
                    else:
                        # Entrada mínima — complex PDB será construído em run()
                        result.append((f"vina_{dk}", {
                            "sequence": seq,
                            "length": dv.get("length", len(seq)),
                            "vina_kcal": vina,
                        }))
                if result:
                    self.logger.info(
                        "Top-5 por Vina: " +
                        ", ".join(f"{v['sequence'][:8]}({v.get('vina_kcal',0):.2f})"
                                  for _, v in result)
                    )
                    return result
            except Exception as e:
                self.logger.warning(f"Leitura docking_results.json falhou: {e}")
        # Fallback: I_sc heurístico
        self.logger.warning("Selecionando por I_sc heurístico (docking_results.json indisponível)")
        return sorted(rosetta_results.items(),
                      key=lambda x: x[1].get("I_sc", 0))[:5]

    def _get_binding_center(self) -> list:
        """Lê centro de ligação do checkpoint; fallback para consenso padrão."""
        try:
            ckpt_file = Path(self.workdir).parent / "checkpoint.json"
            if ckpt_file.exists():
                ckpt = json.loads(ckpt_file.read_text())
                c = ckpt.get("structure", {}).get("consensus_center_xyz")
                if c and len(c) == 3:
                    return [float(x) for x in c]
        except Exception:
            pass
        return [2.607, 4.572, -1.885]  # consenso calculado na etapa structure

    def _build_complex_for_md(self, sequence: str, receptor_pdb: str) -> Path | None:
        """Constrói complex PDB (receptor + peptídeo all-atom) via PeptideBuilder."""
        try:
            import numpy as np
            from PeptideBuilder import Geometry, PeptideBuilder as PB
            import Bio.PDB

            center = self._get_binding_center()

            # Construir peptídeo all-atom
            geo = Geometry.geometry(sequence[0])
            structure = PB.initialize_res(geo)
            for aa in sequence[1:]:
                try:
                    PB.add_residue(structure, aa)
                except Exception:
                    PB.add_residue(structure, "A")

            # COM centering
            atoms = list(structure.get_atoms())
            com = np.mean([a.coord for a in atoms], axis=0)
            offset = np.array(center) - com
            for a in atoms:
                a.coord += offset

            # Escrever receptor
            safe_name = sequence[:10].replace("/", "_")
            out_pdb = self.workdir / f"complex_md_{safe_name}.pdb"
            parser = Bio.PDB.PDBParser(QUIET=True)
            rec = parser.get_structure("REC", receptor_pdb)
            io = Bio.PDB.PDBIO()
            io.set_structure(rec)
            io.save(str(out_pdb))

            # Append peptídeo como cadeia P
            AA3 = {
                "A":"ALA","R":"ARG","N":"ASN","D":"ASP","C":"CYS","Q":"GLN",
                "E":"GLU","G":"GLY","H":"HIS","I":"ILE","L":"LEU","K":"LYS",
                "M":"MET","F":"PHE","P":"PRO","S":"SER","T":"THR","W":"TRP",
                "Y":"TYR","V":"VAL",
            }
            with open(out_pdb, "a") as f:
                f.write("TER\n")
                n = 1
                for res in structure.get_residues():
                    idx = res.id[1] - 1
                    aa1 = sequence[idx] if idx < len(sequence) else "A"
                    res3 = AA3.get(aa1, "ALA")
                    for atom in res.get_atoms():
                        x, y, z = atom.coord
                        elem = (atom.element or atom.name[0]).strip()
                        f.write(
                            f"ATOM  {n:5d}  {atom.name:<4s}{res3:3s} P"
                            f"{res.id[1]:4d}    {x:8.3f}{y:8.3f}{z:8.3f}"
                            f"  1.00  0.00          {elem:>2s}\n"
                        )
                        n += 1
                f.write("END\n")

            return out_pdb
        except Exception as e:
            self.logger.error(f"_build_complex_for_md ({sequence[:8]}): {e}")
            return None

    def _find_gmx(self) -> str:
        """Retorna o path completo para gmx_mpi ou gmx.
        Estratégias em cascata: PATH do processo → bash --login → glob específico → fallback."""
        import shutil, glob

        # 1. PATH do processo atual (funciona quando o usuário ativa o env manualmente)
        for cmd in ("gmx_mpi", "gmx"):
            p = shutil.which(cmd)
            if p:
                return p

        # 2. Shell de login (carrega ~/.bashrc e conda init — PATH completo)
        for shell_cmd in (
            "bash --login -c 'which gmx_mpi 2>/dev/null'",
            "bash --login -c 'which gmx 2>/dev/null'",
        ):
            try:
                r = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=8)
                p = r.stdout.strip()
                if p and Path(p).exists():
                    self.logger.info(f"gmx encontrado via bash --login: {p}")
                    return p
            except Exception:
                pass

        # 3. Paths padrão HPC e conda
        candidates = [
            "/usr/local/gromacs/bin/gmx_mpi",
            "/usr/local/gromacs/bin/gmx",
            "/opt/gromacs/bin/gmx_mpi",
            "/opt/gromacs/bin/gmx",
            str(Path.home() / "gromacs/bin/gmx_mpi"),
            str(Path.home() / "gromacs/bin/gmx"),
        ]
        for c in candidates:
            if Path(c).exists():
                return c

        # 4. Glob não-recursivo — padrões específicos do servidor (rápido, sem **):
        #    - Nextflow work conda: ~/gromacs/MD-gromacs/work/conda/env-*/bin/gmx_mpi
        #    - miniforge pkgs:      ~/miniforge3/pkgs/gromacs*/bin/gmx_mpi
        patterns = [
            str(Path.home() / "gromacs/MD-gromacs/work/conda/env-*/bin/gmx_mpi"),
            str(Path.home() / "miniforge3/pkgs/gromacs*/bin/gmx_mpi"),
            str(Path.home() / "mambaforge/pkgs/gromacs*/bin/gmx_mpi"),
            str(Path.home() / "miniforge3/envs/*/bin/gmx_mpi"),
        ]
        for pat in patterns:
            matches = sorted(glob.glob(pat, recursive=False))
            if matches:
                self.logger.info(f"gmx encontrado via glob: {matches[0]}")
                return matches[0]

        return "gmx_mpi"  # fallback — vai falhar com mensagem clara

    def _run_gromacs(self, complex_pdb: str, out: Path, ns: int,
                     temp: int, seq: str) -> dict:
        gmx = self._find_gmx()
        self.logger.info(f"  gmx executável: {gmx}")
        ff = self.config.get("md", {}).get("forcefield", "amber99sb-ildn")
        water = self.config.get("md", {}).get("water_model", "tip3p")

        # Escrever mdp files
        nsteps = int(ns * 500000)
        (out / "md.mdp").write_text(_MDP_TEMPLATE.format(nsteps=nsteps, temp=temp))
        (out / "minim.mdp").write_text(_MINIM_MDP)
        (out / "nvt.mdp").write_text(_NVT_MDP.format(temp=temp))
        (out / "npt.mdp").write_text(_NPT_MDP.format(temp=temp))

        use_mpirun = "mpi" in Path(gmx).name

        def gmx_run(args, **kw):
            if args[0] == "mdrun" and use_mpirun:
                cmd = ["mpirun", "-np", "1", gmx] + args
            else:
                cmd = [gmx] + args
            return subprocess.run(cmd, cwd=str(out), capture_output=True,
                                  text=True, **kw)

        try:
            # Pré-processar PDB: remover HETATM (HOH, ions, ligandos) que pdb2gmx rejeita
            clean_pdb = out / "complex_clean.pdb"
            src = Path(complex_pdb).read_text(errors="replace")
            lines_clean = [l for l in src.splitlines(keepends=True)
                           if l.startswith(("ATOM", "TER", "END", "REMARK", "SSBOND", "CONECT"))]
            clean_pdb.write_text("".join(lines_clean) + "\nEND\n")
            self.logger.info(f"  PDB limpo: {len(lines_clean)} linhas ATOM/TER")

            # pdb2gmx
            p = gmx_run(["pdb2gmx", "-f", str(clean_pdb), "-o", "processed.gro",
                          "-p", "topol.top", "-i", "posre.itp",
                          "-ff", ff, "-water", water, "-ignh"],
                         input="1\n", timeout=120)
            if p.returncode != 0:
                # Salvar log completo para diagnóstico
                (out / "pdb2gmx_stderr.log").write_text(p.stderr)
                raise RuntimeError(f"pdb2gmx: {p.stderr[-1000:]}")

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
            gmx_run(["mdrun", "-deffnm", "minim",
                      "-ntomp", "4"], timeout=600)

            # NVT
            gmx_run(["grompp", "-f", str(out / "nvt.mdp"),
                      "-c", "minim.gro", "-r", "minim.gro",
                      "-p", "topol.top", "-o", "nvt.tpr", "-maxwarn", "2"],
                     timeout=60)
            gmx_run(["mdrun", "-deffnm", "nvt", "-ntomp", "4"],
                     timeout=600)

            # NPT
            gmx_run(["grompp", "-f", str(out / "npt.mdp"),
                      "-c", "nvt.gro", "-r", "nvt.gro", "-t", "nvt.cpt",
                      "-p", "topol.top", "-o", "npt.tpr", "-maxwarn", "2"],
                     timeout=60)
            gmx_run(["mdrun", "-deffnm", "npt", "-ntomp", "4"],
                     timeout=600)

            # MD produção
            gmx_run(["grompp", "-f", str(out / "md.mdp"),
                      "-c", "npt.gro", "-t", "npt.cpt",
                      "-p", "topol.top", "-o", "md.tpr", "-maxwarn", "2"],
                     timeout=60)
            p = gmx_run(["mdrun", "-deffnm", "md",
                          "-ntomp", "4",
                          "-nb", "gpu", "-pme", "gpu"],
                         timeout=ns * 3600)
            if p.returncode != 0:
                # Fallback CPU
                gmx_run(["mdrun", "-deffnm", "md",
                          "-ntomp", "4"], timeout=ns * 7200)

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
