# -*- coding: utf-8 -*-

"""Non-graphical part of the Thermomechanical step in a SEAMM flowchart"""

from datetime import datetime
import json
import logging
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import sys
import textwrap
import traceback

import numpy as np
from tabulate import tabulate

import thermomechanical_step
import molsystem
import seamm
from seamm_util import getParser, Q_, units_class  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: "job" and "printer". "job" send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# "printer" sends output to the file "step.out" in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Thermomechanical")

# Add this module's properties to the standard properties
path = Path(pkg_resources.resource_filename(__name__, "data/"))
csv_file = path / "properties.csv"
if path.exists():
    molsystem.add_properties_from_file(csv_file)


class Thermomechanical(seamm.Node):
    """
    The non-graphical part of a Thermomechanical step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : ThermomechanicalParameters
        The control parameters for Thermomechanical.

    See Also
    --------
    TkThermomechanical,
    Thermomechanical, ThermomechanicalParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="Thermomechanical",
        namespace="org.molssi.seamm",
        extension=None,
        logger=logger,
    ):
        """A step for Thermomechanical in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        namespace : str
            The namespace for the plug-ins of the subflowchart
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug(f"Creating Thermomechanical {self}")
        self.subflowchart = seamm.Flowchart(
            parent=self, name="Thermomechanical", namespace=namespace
        )  # yapf: disable

        super().__init__(
            flowchart=flowchart,
            title="Thermomechanical",
            extension=extension,
            module=__name__,
            logger=logger,
        )  # yapf: disable

        self._metadata = thermomechanical_step.metadata
        self.parameters = thermomechanical_step.ThermomechanicalParameters()
        self._data = {}

    @property
    def version(self):
        """The semantic version of this module."""
        return thermomechanical_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return thermomechanical_step.__git_revision__

    def analyze(self, indent="", **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        # Loop over the subnodes, asking them to do their analysis
        while node is not None:
            for value in node.description:
                printer.important(value)
                printer.important(" ")

            node.analyze()

            node = node.next()

    def _calculate_elastic_constants(self, _P):
        """The driver for calculating elastic constants.

        Parameters
        ----------
        _P : dict(str, any)
            The control parameters for this step

        Returns
        -------
        None
        """
        data = {}  # Results to be stored if chosen by user
        _, configuration = self.get_system_configuration()

        # Save the cell and coordinates so that we can recreate the structure
        cell0 = configuration.cell.parameters
        fractionals0 = configuration.coordinates

        # First run the unstrained system
        results = {}
        results[0] = self._run_subflowchart(name="unstrained")
        configuration.cell.parameters = cell0
        configuration.coordinates = fractionals0

        # Find the units of the stress
        if "Sxx,units" in results[0]:
            units = results[0]["Sxx,units"]
            factor = Q_(1.0, units).m_as("GPa")
        else:
            units = "GPa"
            factor = 1

        # Save the stress
        data["stress"] = [
            results[0][key] * factor
            for key in ("Sxx", "Syy", "Szz", "Syz", "Sxz", "Sxy")
        ]

        # And the strains, + & -
        step = _P["step size"]
        for indx, strain in enumerate(("xx", "yy", "zz", "yz", "xz", "xy")):
            strn = [0.0] * 6
            if indx > 2:
                # Voigt off-diagonals have factor of 2
                strn[indx] = -2 * step
            else:
                strn[indx] = -step
            configuration.strain(strn)
            results[(indx, "-")] = self._run_subflowchart(name=f"e{strain} -{step}")
            configuration.cell.parameters = cell0
            configuration.coordinates = fractionals0

            if indx > 2:
                # Voigt off-diagonals have factor of 2
                strn[indx] = 2 * step
            else:
                strn[indx] = step
            configuration.strain(strn)
            results[(indx, "+")] = self._run_subflowchart(name=f"e{strain} +{step}")
            configuration.cell.parameters = cell0
            configuration.coordinates = fractionals0

        # Create the elastic constant matrix, converting to GPa on the way
        C = []
        for i in range(6):
            plus = results[(i, "+")]
            minus = results[(i, "-")]
            row = []
            for j, strain in enumerate(("Sxx", "Syy", "Szz", "Syz", "Sxz", "Sxy")):
                Cij = factor * (plus[strain] - minus[strain]) / (2 * step)
                row.append(Cij)
            C.append(row)

        # Print the unsymmetrized matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(C, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [*row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".2f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Unsymmetrized elastic constant matrix (GPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Symmetrize the matrix
        for i in range(6):
            for j in range(i):
                Cij = C[i][j]
                Cji = C[j][i]
                C[j][i] = (Cij + Cji) / 2
                C[i][j] = Cij - Cji

        # Print the symmetrized matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(C, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [*row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".1f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Elastic constant matrix (lower) and error (upper) (GPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Make full square matrix
        for i in range(6):
            for j in range(i):
                C[i][j] = C[j][i]
        data["Cij"] = C

        # Invert to get compliance
        tmp = np.array(C)
        S = np.linalg.inv(tmp).tolist()
        data["Sij"] = S

        # Print the compliance matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(S, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [1000 * v for v in row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".1f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Compliance matrix (1/TPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # The polycrystalline moduli

        # Voigt
        Kv = ((C[0][0] + C[1][1] + C[2][2]) + 2 * (C[0][1] + C[1][2] + C[0][2])) / 9
        Gv = (
            (C[0][0] + C[1][1] + C[2][2])
            - (C[0][1] + C[1][2] + C[0][2])
            + 3 * (C[3][3] + C[4][4] + C[5][5])
        ) / 15
        Ev = 9 * Kv * Gv / (3 * Kv + Gv)
        mu_v = (3 * Kv - 2 * Gv) / (6 * Kv + 2 * Gv)

        data["Kv"] = Kv
        data["Gv"] = Gv
        data["Ev"] = Ev
        data["mu_v"] = mu_v

        # Reuss
        Kr = 1 / ((S[0][0] + S[1][1] + S[2][2]) + 2 * (S[0][1] + S[1][2] + S[0][2]))
        Gr = 15 / (
            4 * (S[0][0] + S[1][1] + S[2][2])
            - 4 * (S[0][1] + S[1][2] + S[0][2])
            + 3 * (S[3][3] + S[4][4] + S[5][5])
        )
        Er = 9 * Kr * Gr / (3 * Kr + Gr)
        mu_r = (3 * Kr - 2 * Gr) / (6 * Kr + 2 * Gr)

        data["Kr"] = Kr
        data["Gr"] = Gr
        data["Er"] = Er
        data["mu_r"] = mu_r

        # Hill
        Kh = (Kv + Kr) / 2
        Gh = (Gv + Gr) / 2
        Eh = 9 * Kh * Gh / (3 * Kh + Gh)
        mu_h = (3 * Kh - 2 * Gh) / (6 * Kh + 2 * Gh)

        data["Kh"] = Kh
        data["Gh"] = Gh
        data["Eh"] = Eh
        data["mu_h"] = mu_h

        # And print as a table
        table = {
            "Modulus": ["Bulk (K)", "Shear (G)", "Young (E)", "Poisson ratio"],
            "Voigt": [f"{Kv:.1f}", f"{Gv:.1f}", f"{Ev:.1f}", f"{mu_v:.3f}"],
            "Reuss": [f"{Kr:.1f}", f"{Gr:.1f}", f"{Er:.1f}", f"{mu_r:.3f}"],
            "Hill": [f"{Kh:.1f}", f"{Gh:.1f}", f"{Eh:.1f}", f"{mu_h:.3f}"],
        }

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Polycrystalline Moduli (GPa) and Poisson Ratio"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Put any requested results into variables or tables
        self.store_results(configuration=configuration, data=data)

    def create_parser(self):
        """Setup the command-line / config file parser"""
        parser_name = "thermomechanical-step"
        parser = getParser()

        # Remember if the parser exists ... this type of step may have been
        # found before
        parser_exists = parser.exists(parser_name)

        # Create the standard options, e.g. log-level
        super().create_parser(name=parser_name)

        if not parser_exists:
            # Any options for thermomechanical step itself
            parser.add_argument(
                parser_name,
                "--graph-formats",
                default=tuple(),
                choices=("html", "png", "jpeg", "webp", "svg", "pdf"),
                nargs="+",
                help="extra formats to write for graphs",
            )
            parser.add_argument(
                parser_name,
                "--graph-fontsize",
                default=15,
                help="Font size in graphs, defaults to 15 pixels",
            )
            parser.add_argument(
                parser_name,
                "--graph-width",
                default=1024,
                help="Width of graphs in formats that support it, defaults to 1024",
            )
            parser.add_argument(
                parser_name,
                "--graph-height",
                default=1024,
                help="Height of graphs in formats that support it, defaults to 1024",
            )

        # Now need to walk through the steps in the subflowchart...
        self.subflowchart.reset_visited()
        node = self.subflowchart.get_node("1").next()
        while node is not None:
            node = node.create_parser()

        return self.next()

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.
        Returns
        -------
        str
            A description of the current step.
        """
        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        if P is None:
            P = self.parameters.values_to_dict()

        # Describe what we are going to do
        result = self.header + "\n\n"
        text = ""

        elastic = P["elastic constants"]
        step = P["step size"]
        if isinstance(elastic, bool) and elastic or elastic == "yes":
            text += (
                "The elastic constants will be calculated using a strain step of "
                f"{step}. "
            )
        elif self.is_expr(elastic):
            text += (
                f"The expression {elastic} will determine whether to calculate the "
                f"elastic constants. If so, a strain step of {step} will be used. "
            )

        spdef = P["state point definition"]
        if self.is_expr(spdef):
            text += (
                "The expression {spdef} will determine what state points will be used. "
            )
        elif spdef == "as given":
            text += (
                "The current structure will be used as is, with the temperature set "
                "in the subflowchart if needed."
            )
        elif spdef == "lists of Ps and Ts":
            text += (
                "The state points will be generated by using each pressure {P} for "
                "each temperature {T}."
            )
        else:
            text += "The state points given by {state points} will be used."

        result += str(__(text, indent=4 * " ", **P))
        result += "\n\n"

        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        text = ""
        while node is not None:
            try:
                text += __(node.description_text(), indent=8 * " ").__str__()
            except Exception as e:
                print(f"Error describing thermomechanical flowchart: {e} in {node}")
                logger.critical(
                    f"Error describing thermomechanical flowchart: {e} in {node}"
                )
                raise
            except Exception:
                print(
                    "Unexpected error describing thermomechanical flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                logger.critical(
                    "Unexpected error describing thermomechanical flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                raise
            text += "\n"
            node = node.next()

        result += text

        return result

    def run(self):
        """Run the Thermomechanical step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)

        # Get the values of the parameters, dereferencing any variables
        _P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Fix the formatting of units for printing...
        _PP = dict(_P)
        for key in _PP:
            if isinstance(_PP[key], units_class):
                _PP[key] = "{:~P}".format(_PP[key])

        # Print what we are doing
        printer.important(__(self.description_text(_PP), indent=self.indent))

        if _P["elastic constants"]:
            self._calculate_elastic_constants(_P)

        return next_node

    def _run_subflowchart(self, name=None):
        """Run the subflowchart for training.

        Parameters
        ----------
        name : str, default = None
            The name of the run, used to create the subdirectory and name in the output.
            The default of None indicates use the current directory as is.

        Returns
        -------
        results : {str: any}
            A dictionary of the results from the subflowchart
        """
        super().run(printer)

        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        job_handler = None
        out_handler = None
        if name is None:
            iter_dir = self.wd
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the nodes have the correct id
            self.set_subids(self._id)
        else:
            iter_dir = self.wd / name
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Find the handler for job.out and set the level up
            for handler in job.handlers:
                if (
                    isinstance(handler, logging.FileHandler)
                    and "job.out" in handler.baseFilename
                ):
                    job_handler = handler
                    job_level = job_handler.level
                    job_handler.setLevel(printing.JOB)
                elif isinstance(handler, logging.StreamHandler):
                    out_handler = handler
                    out_level = out_handler.level
                    out_handler.setLevel(printing.JOB)

            # Setup the output for this pass
            path = iter_dir / "Step.out"
            path.unlink(missing_ok=True)
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(printing.NORMAL)
            formatter = logging.Formatter(fmt="{message:s}", style="{")
            file_handler.setFormatter(formatter)
            job.addHandler(file_handler)

            # Ensure the nodes have the correct id
            self.set_subids((*self._id, name))

        # Get the first real node in the subflowchart
        first_node = self.subflowchart.get_node("1").next()

        # Set up the options for the subflowchart
        node = first_node
        self.subflowchart.reset_visited()
        while node is not None:
            node.all_options = self.all_options
            node = node.next()

        # Run through the steps in the subflowchart
        node = first_node
        try:
            while node is not None:
                try:
                    node = node.run()
                except DeprecationWarning as e:
                    printer.normal("\nDeprecation warning: " + str(e))
                    traceback.print_exc(file=sys.stderr)
                    traceback.print_exc(file=sys.stdout)
        except Exception as e:
            printer.job(f"Caught exception in subflowchart: {str(e)}")
            with open(self.wd / "stderr.out", "a") as fd:
                traceback.print_exc(file=fd)
            raise
        finally:
            if job_handler is not None:
                job_handler.setLevel(job_level)
            if out_handler is not None:
                out_handler.setLevel(out_level)

            # Remove any redirection of printing.
            if file_handler is not None:
                file_handler.close()
                job.removeHandler(file_handler)
                file_handler = None

        # Get the results
        paths = sorted(iter_dir.glob("**/Results.json"))
        if len(paths) == 0:
            if name is None:
                raise RuntimeError(
                    "There are no properties stored in properties.json "
                    f"for this step, running in {iter_dir}."
                )
            else:
                raise RuntimeError(
                    "There are no properties stored in properties.json "
                    f"for step {name} running in {iter_dir}."
                )
        data = {}
        for path in paths:
            with path.open() as fd:
                tmp = json.load(fd)
            time = datetime.fromisoformat(tmp["iso time"])
            data[time] = tmp
        times = sorted(data.keys())
        results = data[times[0]]

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return results

    def set_id(self, node_id=()):
        """Sequentially number the subnodes"""
        self.logger.debug("Setting ids for subflowchart {}".format(self))
        if self.visited:
            return None
        else:
            self.visited = True
            self._id = node_id
            self.set_subids(self._id)
            return self.next()

    def set_subids(self, node_id=()):
        """Set the ids of the nodes in the subflowchart"""
        self.subflowchart.reset_visited()
        node = self.subflowchart.get_node("1").next()
        n = 1
        while node is not None:
            node = node.set_id((*node_id, str(n)))
            n += 1
